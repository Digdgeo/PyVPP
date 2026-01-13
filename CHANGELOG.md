# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
