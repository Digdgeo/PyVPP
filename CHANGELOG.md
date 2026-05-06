# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-06

### ✨ Added
- **Per-date output**: mosaics are now organized by acquisition date under
  `<outdir>/YYYYMMDD_s2msi/`, one subfolder per date.
- **Red-edge bands**: `B05`, `B06`, `B07` and `B8A` now fully supported
  alongside the existing 10 m and SWIR bands.
- **Consistent band naming**: output filenames follow the Landsat-style
  convention `YYYYMMDD_s2msi_<alias>.tif` (e.g. `20230610_s2msi_b05_re1.tif`).
  Band aliases: `b02_blue`, `b03_green`, `b04_red`, `b05_re1`, `b06_re2`,
  `b07_re3`, `b08_nir`, `b8a_nir`, `b11_swir1`, `b12_swir2`, `scl`.
- **Token auto-refresh**: CDSE access token is renewed before every product
  download, preventing `401 Unauthorized` errors on long sessions (tokens
  expire in ~10 min, downloads take much longer).
- **Resume after partial failure**: `download()` skips already-extracted
  SAFE directories, so re-running after a network interruption picks up
  where it left off without re-downloading.
- **`mosaic_per_band` naming hook**: new `out_stem_fn` parameter lets callers
  control the output filename stem without subclassing.

### 🔧 Changed
- Minimum `geopandas` version bumped to `>=0.14` (fixes `fiona.path`
  compatibility issue with fiona 1.10+).
- `CDSEDownload.download()` now returns `dict[str, dict[str, list[str]]]`
  (`{date: {band: [jp2_paths]}}`), grouped by acquisition date.

### 🗑️ Deprecated
- `mosaic_and_clip` still emits a `DeprecationWarning`; no further changes.

## [0.4.0] - 2026-05-05

### ✨ Added
- **CDSE module** (`pyvpp.cdse`): download Sentinel-2 L1C/L2A products directly
  from the Copernicus Data Space Ecosystem.
- `CDSEDownload` class with AOI search (shapefile or DEIMS ID), UTM zone
  filter, automatic mosaicking and clipping.
- Multi-resolution support: any combination of 10 m bands (B02, B03, B04, B08)
  and 20 m bands (B01, B05–B07, B8A, B11, B12) in a single call.
- Scene Classification Layer (`SCL`) as a first-class band (L2A only),
  merged with nearest-neighbour resampling to preserve its categorical
  class IDs.
- Per-band output: each requested band produces its own
  `mosaic_<BAND>_rec.tif`, in its native resolution and dtype.
- Authentication via env vars (`CDSE_USER` / `CDSE_PASSWORD`),
  `~/.pyvpp/config.toml`, or direct credentials.

### 🔧 Changed
- Project layout reorganised into submodules: `pyvpp.wekeo` (HR-VPP via WEkEO,
  unchanged behaviour) and `pyvpp.cdse` (new).
- Minimum Python version bumped to 3.9.

### 🐛 Fixed
- Fixed a broken import in `pyvpp.cdse.auth` that prevented the CDSE module
  from loading (`from pyvpp.config` → `from pyvpp.cdse.config`).

### 🗑️ Deprecated
- `pyvpp.cdse.mosaic.mosaic_and_clip` (single-mosaic, multi-band output).
  Use `mosaic_per_band` instead. The old function still works but emits a
  `DeprecationWarning`.

## [0.1.9] - 2025-01-13

### 🔴 CRITICAL Changes
- **Fixed `.hdarc` file format**: Changed from JSON to plain text format required by HDA API v2.18+
  - Old (incorrect): `{"user": "...", "password": "..."}`
  - New (correct): `user: ...\npassword: ...`

### ✨ Added
- New function `create_hdarc(user, password)`: Creates `.hdarc` file with correct format
- New function `clean_old_hdarc()`: Removes obsolete `url:` line from pre-March 2024 `.hdarc` files
- New function `delete_hdarc()`: Removes `.hdarc` file for secure credential cleanup
- Support for passing credentials directly to `wekeo_download()` via `user` and `password` parameters
- Better error handling with full traceback output for debugging
- Explicit file closing for rasterio objects to prevent resource leaks

### 🔧 Changed
- Updated `download()` method to include `itemsPerPage` and `startIndex` in queries for better pagination
- Improved connection handling with automatic `.hdarc` cleaning on initialization
- Enhanced documentation with migration guide and multiple usage examples
- Updated README with comprehensive examples for different use cases

### 📚 Documentation
- Added detailed migration guide from v0.1.8
- Added examples for Jupyter notebooks and shared environments
- Added verification script to check installation and configuration
- Added quick reference card for common issues
- Added `DATASETS_AVAILABLE.md` with detailed dataset status information
- **Important note**: VPP_Index dataset (EO:EEA:DAT:CLMS_HRVPP_VI) currently unavailable (404 error)

### 🐛 Fixed
- Fixed authentication issues caused by incorrect `.hdarc` format
- Fixed connection errors with old `.hdarc` files containing `url:` line
- Fixed potential resource leaks by explicitly closing rasterio datasets
- Improved error messages for better debugging

### 🔒 Security
- Added `delete_hdarc()` function for secure credential cleanup in shared environments
- Improved credential management with direct credential passing option

### ⚠️ Known Issues
- **VPP_Index dataset unavailable**: The dataset `EO:EEA:DAT:CLMS_HRVPP_VI` returns 404 errors on WEkEO
  - Products affected: LAI, FAPAR, NDVI (daily vegetation indices)
  - Workaround: Use `VPP_ST` for PPI or `VPP_Pheno` for phenological parameters
  - See README.md and DATASETS_AVAILABLE.md for alternatives

## [0.1.8] - 2023-10-19

### Added
- Last version using old HDA library format
- Support for SLSTR dataset
- Basic error handling

### Changed
- Updated dependencies versions

## [0.1.7] - 2023-02-22

### Added
- Initial stable release
- Support for VPP_Index, VPP_Pheno, and VPP_ST datasets
- DEIMS-SDR integration
- Automatic tile mosaicking and clipping
- Basic documentation

## Migration from 0.1.8 to 0.1.9

If you're upgrading from version 0.1.8, follow these steps:

### 1. Update libraries
```bash
pip install --upgrade hda pyvpp
```

### 2. Update your `.hdarc` file

**Option A: Using the helper function (recommended)**
```python
import pyvpp
pyvpp.create_hdarc("your_username", "your_password")
```

**Option B: Manual update**
Change your `~/.hdarc` file from:
```json
{
  "user": "your_username",
  "password": "your_password"
}
```

To:
```
user: your_username
password: your_password
```

### 3. Or use direct credentials
```python
downloader = pyvpp.wekeo_download(
    dataset="VPP_Pheno",
    shape="area.shp",
    dates=['2020-01-01', '2020-12-31'],
    products=['SOSD', 'MAXD'],
    user="your_username",     # NEW
    password="your_password"  # NEW
)
```

### 4. Update dataset usage if needed

If you were using `VPP_Index`:
- For PPI → Use `VPP_ST`
- For phenological parameters → Use `VPP_Pheno`
- For LAI, FAPAR, NDVI → Currently not available (see alternatives in README)

For detailed migration instructions and alternatives, see:
- README.md
- DATASETS_AVAILABLE.md

## Links

- **GitHub**: https://github.com/Digdgeo/PyVPP
- **PyPI**: https://pypi.org/project/pyvpp/
- **Issues**: https://github.com/Digdgeo/PyVPP/issues
- **Documentation**: https://github.com/Digdgeo/PyVPP/blob/main/README.md
