import os
import requests
import zipfile

from .auth import get_cdse_token
from .utils import load_shape
from .mosaic import mosaic_per_band


# Native resolution of every band Sen2Cor publishes inside an L2A SAFE bundle.
# Used to (a) validate the user's `bands=` argument and (b) decide which
# IMG_DATA/R{XX}m subfolder to walk for each band.
BAND_RESOLUTION = {
    # 10 m bands
    "B02": "10m", "B03": "10m", "B04": "10m", "B08": "10m",
    # 20 m bands (B8A is the narrow NIR; SCL is the Scene Classification Layer)
    "B01": "20m", "B05": "20m", "B06": "20m", "B07": "20m",
    "B8A": "20m", "B11": "20m", "B12": "20m", "SCL": "20m",
}

# SCL is categorical (class IDs 0..11), so it must be merged/resampled with
# nearest-neighbour rather than the default average/bilinear.
CATEGORICAL_BANDS = {"SCL"}

# Human-readable band aliases used in output filenames (Landsat-style convention).
BAND_ALIAS = {
    "B01": "b01_coastal",
    "B02": "b02_blue",
    "B03": "b03_green",
    "B04": "b04_red",
    "B05": "b05_re1",
    "B06": "b06_re2",
    "B07": "b07_re3",
    "B08": "b08_nir",
    "B8A": "b8a_nir",
    "B11": "b11_swir1",
    "B12": "b12_swir2",
    "SCL": "scl",
}


class CDSEDownload:
    """
    Download Sentinel-2 L1C/L2A products from the Copernicus Data Space Ecosystem.

    For each band requested, the downloader produces one mosaic GeoTIFF
    `mosaic_<BAND>_rec.tif` in `outdir`, clipped to the AOI and in the band's
    native resolution (10 m or 20 m). Multi-resolution downloads are supported
    in a single call (e.g. bands=['B04','B11','SCL']).
    """

    def __init__(
        self,
        shape,
        dates,
        bands,
        outdir="cdse_data",
        utm_zone=None,
        processing_level="L2A",   # 'L2A' (BOA) or 'L1C' (TOA)
    ):
        self.shape = shape
        self.dates = dates
        self.bands = bands
        self.outdir = outdir
        self.utm_zone = utm_zone
        self.processing_level = processing_level.upper()

        if self.processing_level not in ("L1C", "L2A"):
            raise ValueError(
                f"processing_level must be 'L1C' or 'L2A', got '{processing_level}'"
            )

        # Validate bands up front so the user gets a useful error before any
        # network calls, not deep inside download() with an empty result.
        unknown = [b for b in self.bands if b not in BAND_RESOLUTION]
        if unknown:
            raise ValueError(
                f"Unknown band(s) {unknown}. "
                f"Supported: {sorted(BAND_RESOLUTION)}"
            )
        if self.processing_level == "L1C" and "SCL" in self.bands:
            raise ValueError("SCL is only available in L2A products.")

        os.makedirs(self.outdir, exist_ok=True)

        self.token = get_cdse_token()
        self.gdf, self.gdf_proj = load_shape(self.shape)

        self.products = []

    def search(self):
        """Search Sentinel-2 products in CDSE that intersect the AOI."""
        start, end = self.dates
        geom = self.gdf.geometry.iloc[0].envelope.wkt
        product_type = "MSIL2A" if self.processing_level == "L2A" else "MSIL1C"

        url = (
            "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
            "$filter="
            "Collection/Name eq 'SENTINEL-2' and "
            f"contains(Name,'{product_type}') and "
            f"ContentDate/Start ge {start}T00:00:00.000Z and "
            f"ContentDate/End le {end}T23:59:59.999Z and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{geom}')"
        )

        print(f"Searching for Sentinel-2 {self.processing_level} products...")
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        self.products = r.json()["value"]

        if self.utm_zone is not None:
            before = len(self.products)
            self.products = [
                p for p in self.products if f"T{self.utm_zone}" in p["Name"]
            ]
            print(
                f"Filtered products by UTM zone {self.utm_zone}: "
                f"{before} → {len(self.products)}"
            )

        return self.products

    def _refresh_token(self):
        """Obtain a fresh CDSE access token (tokens expire in ~10 min)."""
        self.token = get_cdse_token()

    def download(self):
        """
        Download SAFE products for self.products and return a dict
        {band: [list_of_jp2_paths]} ready to be passed to mosaic_per_band().

        Already-extracted SAFE directories are skipped automatically, so
        re-running after a partial failure picks up where it left off.
        Token is refreshed before each product to survive long download sessions.
        """
        for i, p in enumerate(self.products, 1):
            pid = p["Id"]
            name = p["Name"]
            safe_dir = os.path.join(self.outdir, name)

            if os.path.isdir(safe_dir):
                print(f"  [{i}/{len(self.products)}] {name} — ya existe, saltando")
                continue

            print(f"  [{i}/{len(self.products)}] Descargando {name} ...")
            self._refresh_token()

            zip_path = os.path.join(self.outdir, f"{name}.zip")
            url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({pid})/$value"

            with requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                stream=True,
            ) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            with zipfile.ZipFile(zip_path) as z:
                z.extractall(self.outdir)
            os.remove(zip_path)

        return self._collect_jp2_paths()

    def _collect_jp2_paths(self):
        """
        Walk the extracted SAFE bundles and group JP2 files by date and band.

        Returns
        -------
        dict[str, dict[str, list[str]]]
            {date_str: {band: [absolute_path_to_jp2, ...]}}
            date_str is 'YYYYMMDD' extracted from the SAFE product name.
            Paths within each band list are sorted for deterministic mosaicking.
        """
        by_res = {}
        for b in self.bands:
            by_res.setdefault(BAND_RESOLUTION[b], []).append(b)

        # Find all SAFE directories directly under outdir and extract their date.
        # SAFE name format: S2A_MSIL2A_20230610T110621_N0510_R137_T29SQA_...SAFE
        safe_dirs = [
            d for d in os.listdir(self.outdir)
            if d.endswith(".SAFE") and os.path.isdir(os.path.join(self.outdir, d))
        ]

        rasters_by_date = {}
        for safe_name in safe_dirs:
            date = safe_name.split("_")[2][:8]  # '20230610T110621'[:8]
            if date not in rasters_by_date:
                rasters_by_date[date] = {b: [] for b in self.bands}

            safe_path = os.path.join(self.outdir, safe_name)
            for root, _, files in os.walk(safe_path):
                for res, res_bands in by_res.items():
                    if f"IMG_DATA/R{res}" not in root.replace("\\", "/"):
                        continue
                    for f in files:
                        if not f.endswith(".jp2"):
                            continue
                        for b in res_bands:
                            # JP2 names: 'T29SQB_20230612T110629_B04_10m.jp2'
                            # '_<BAND>_' avoids false positives (B08 vs B8A).
                            if f"_{b}_" in f:
                                rasters_by_date[date][b].append(
                                    os.path.join(root, f)
                                )
                                break

        for date in rasters_by_date:
            for b in self.bands:
                rasters_by_date[date][b].sort()

        for date, rasters_per_band in sorted(rasters_by_date.items()):
            print(f"  {date}:")
            for b in self.bands:
                n = len(rasters_per_band[b])
                print(f"    {b} ({BAND_RESOLUTION[b]}): {n} JP2 file(s)")

        return rasters_by_date

    def run(self):
        """Full pipeline: search → download → mosaic per band per date → clip."""
        self.search()
        rasters_by_date = self.download()
        for date, rasters_per_band in sorted(rasters_by_date.items()):
            print(f"\nMosaicando fecha {date} ...")
            date_dir = os.path.join(self.outdir, f"{date}_s2msi")
            mosaic_per_band(
                rasters_per_band,
                self.gdf_proj,
                outdir=date_dir,
                categorical=CATEGORICAL_BANDS,
                out_stem_fn=lambda b, d=date: f"{d}_s2msi_{BAND_ALIAS[b]}",
            )
