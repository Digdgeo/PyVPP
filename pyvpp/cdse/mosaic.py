# pyvpp/cdse/mosaic.py
"""
Per-band mosaicking and clipping for Sentinel-2 JP2 tiles.

Each band is processed independently: tiles are merged in their native
resolution and clipped to the AOI. Categorical bands (e.g. SCL) are merged
with nearest-neighbour resampling to preserve their integer class IDs.
"""
import os

import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.merge import merge


def mosaic_per_band(rasters_per_band, gdf_proj, outdir=".", categorical=None,
                    out_stem_fn=None):
    """
    Mosaic and clip a set of Sentinel-2 JP2 tiles, one output per band.

    Parameters
    ----------
    rasters_per_band : dict[str, list[str]]
        Mapping {band: [paths_to_jp2_tiles]}. Bands with an empty list are
        skipped with a warning.
    gdf_proj : geopandas.GeoDataFrame
        AOI in a projected CRS (used as cutline).
    outdir : str
        Directory where output GeoTIFFs are written.
    categorical : iterable[str] or None
        Band names that must be resampled with nearest-neighbour (e.g. {'SCL'}).
    out_stem_fn : callable(band) -> str or None
        Function that receives the band name and returns the output filename
        stem (without `.tif`). Defaults to ``lambda b: f"mosaic_{b}_rec"``.

    Returns
    -------
    dict[str, str]
        {band: output_geotiff_path} for every band that produced a mosaic.
    """
    categorical = set(categorical or ())
    if out_stem_fn is None:
        out_stem_fn = lambda b: f"mosaic_{b}_rec"
    os.makedirs(outdir, exist_ok=True)
    outputs = {}

    for band, rasters in rasters_per_band.items():
        if not rasters:
            print(f"⚠️  Band {band}: no JP2 tiles found, skipping.")
            continue

        # Within a single S2 date, tiles share the same grid alignment, so
        # rasterio.merge.merge does not actually resample. We still pass
        # nearest explicitly so categorical bands (SCL) round-trip safely if
        # ever resampling does kick in.
        srcs = [rasterio.open(r) for r in rasters]
        try:
            mosaic, out_trans = merge(srcs, resampling=Resampling.nearest)
            meta = srcs[0].meta.copy()
        finally:
            for s in srcs:
                s.close()

        meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
            "crs": gdf_proj.crs,
        })

        tmp_path = os.path.join(outdir, f"_mosaic_tmp_{band}.tif")
        with rasterio.open(tmp_path, "w", **meta) as dst:
            dst.write(mosaic)

        # Clip to the AOI cutline.
        shapes = list(gdf_proj.geometry)
        with rasterio.open(tmp_path) as src:
            out_img, out_tr = mask(src, shapes, crop=True)
            meta = src.meta.copy()

        meta.update({
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_tr,
        })

        out_path = os.path.join(outdir, f"{out_stem_fn(band)}.tif")
        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(out_img)

        os.remove(tmp_path)
        outputs[band] = out_path
        print(f"✅ {band}: {out_path}")

    return outputs


# ---------------------------------------------------------------------------
# Backward-compat helper.
# The previous version of this module exposed `mosaic_and_clip(rasters, gdf)`
# that produced a single multi-band `mosaic_rec.tif`. Old code (e.g. notebooks)
# may still import it; we keep a thin wrapper that routes to mosaic_per_band
# by treating the input list as a single "MIXED" band.
# ---------------------------------------------------------------------------
def mosaic_and_clip(rasters, gdf_proj, out_name="mosaic_rec.tif"):
    """Deprecated: use `mosaic_per_band` instead. Kept for backward compatibility."""
    import warnings
    warnings.warn(
        "mosaic_and_clip is deprecated; use mosaic_per_band for per-band outputs.",
        DeprecationWarning,
        stacklevel=2,
    )
    outdir = os.path.dirname(out_name) or "."
    band = os.path.splitext(os.path.basename(out_name))[0]
    result = mosaic_per_band({band: list(rasters)}, gdf_proj, outdir=outdir)
    # Rename to the requested out_name to mimic the old behaviour exactly.
    produced = result.get(band)
    if produced and produced != out_name:
        os.replace(produced, out_name)
        return out_name
    return produced
