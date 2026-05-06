# PyVPP

Python package to download and preprocess vegetation products from Copernicus services:
- **HR-VPP** (High Resolution Vegetation Phenology and Productivity) via WEkEO
- **Sentinel-2 L2A** raw data via CDSE (Copernicus Data Space Ecosystem)

[![PyPI version](https://badge.fury.io/py/pyvpp.svg)](https://badge.fury.io/py/pyvpp)

## ⚠️ IMPORTANT - VPP_Index Dataset Currently Unavailable (January 2025)

**The `VPP_Index` dataset (EO:EEA:DAT:CLMS_HRVPP_VI) currently returns 404 errors on WEkEO.**

This dataset, which contained daily vegetation indices (LAI, FAPAR, NDVI, PPI), appears to have been discontinued or moved since 2024.

### ✅ Datasets that ARE working:
- **`VPP_ST`** (Seasonal Trajectories): Contains PPI, QFLAG
- **`VPP_Pheno`** (Phenology & Productivity): Contains SOSD, MAXD, EOSD, LENGTH, AMPL, TPROD, etc.

### 🔧 If you needed VPP_Index:
- **For PPI** → Use `VPP_ST`
- **For phenology parameters** → Use `VPP_Pheno`
- **For LAI, FAPAR, NDVI** → Currently not available via PyVPP (see alternatives below)

See [DATASETS_AVAILABLE.md](DATASETS_AVAILABLE.md) for more details.

---

## Installation

```bash
pip install pyvpp
```

## Quick Start

PyVPP supports two main workflows:

### A. HR-VPP Products (WEkEO)

#### 1. Configure your WEkEO credentials

```python
import pyvpp

# Create .hdarc file with your credentials
pyvpp.create_hdarc("your_wekeo_username", "your_wekeo_password")
```

#### 2. Download HR-VPP data

##### Phenology parameters (RECOMMENDED - WORKING)

```python
import pyvpp

# Download phenology parameters (annual products)
downloader = pyvpp.wekeo_download(
    dataset='VPP_Pheno',  # ✅ Working
    shape='path/to/your/area.shp',  # or DEIMS ID
    dates=['2020-01-01', '2020-12-31'],
    products=['SOSD', 'MAXD', 'EOSD', 'LENGTH']
)

downloader.run()
```

##### Seasonal Trajectories - PPI (RECOMMENDED - WORKING)

```python
import pyvpp

# Download PPI (Plant Phenology Index) every 10 days
downloader = pyvpp.wekeo_download(
    dataset='VPP_ST',  # ✅ Working
    shape='path/to/your/area.shp',
    dates=['2020-01-01', '2020-12-31'],
    products=['PPI', 'QFLAG']
)

downloader.run()
```

##### Vegetation Indices (⚠️ CURRENTLY NOT AVAILABLE)

```python
import pyvpp

# ⚠️ WARNING: This dataset is currently returning 404 errors
# VPP_Index (LAI, FAPAR, NDVI) is not available as of January 2025
downloader = pyvpp.wekeo_download(
    dataset='VPP_Index',  # ⚠️ Returns 404 error
    shape='path/to/your/area.shp',
    dates=['2020-01-01', '2020-12-31'],
    products=['LAI', 'FAPAR']  # Not available
)

# This will fail with: 404 Client Error
```

---

### B. Sentinel-2 Raw Data (CDSE)

**New in v0.4.0**: Download Sentinel-2 L2A products directly from CDSE.

#### 1. Configure CDSE credentials

You have three options:

**Option 1: Configuration file (recommended)**
```bash
mkdir -p ~/.pyvpp
cat > ~/.pyvpp/config.toml << EOF
[cdse]
user = "your_email@example.com"
password = "your_password"
EOF
```

**Option 2: Environment variables**
```bash
export CDSE_USER="your_email@example.com"
export CDSE_PASSWORD="your_password"
```

**Option 3: Direct in code**
```python
from pyvpp.cdse import load_cdse_credentials
# Credentials passed directly to CDSEDownload
```

Register at: https://dataspace.copernicus.eu/

#### 2. Download Sentinel-2 data

**L2A - Bottom of Atmosphere (Default - Atmospherically Corrected)**
```python
from pyvpp import CDSEDownload

# Download Sentinel-2 L2A products (recommended for most use cases)
downloader = CDSEDownload(
    shape='path/to/your/area.shp',  # or DEIMS ID
    dates=('2023-06-01', '2023-06-30'),
    bands=['B04', 'B08'],  # Red, NIR
    outdir='sentinel2_data',
    processing_level='L2A',  # Default: atmospherically corrected
    utm_zone='30T'  # Optional: filter by UTM zone
)

# Run full pipeline: search -> download -> mosaic -> clip
downloader.run()
```

**L1C - Top of Atmosphere (No Atmospheric Correction - for ACOLITE, etc.)**
```python
from pyvpp import CDSEDownload

# Download Sentinel-2 L1C products (TOA reflectance)
# Useful for custom atmospheric correction (ACOLITE, Sen2Cor, etc.)
downloader = CDSEDownload(
    shape='path/to/your/area.shp',
    dates=('2023-06-01', '2023-06-30'),
    bands=['B04', 'B08'],
    outdir='sentinel2_L1C',
    processing_level='L1C'  # Top of Atmosphere
)

downloader.run()
```

**Output**: one mosaic per requested band **per acquisition date**, organized
in subfolders `<outdir>/YYYYMMDD_s2msi/`. Files are named
`YYYYMMDD_s2msi_<alias>.tif` (e.g. `20230610_s2msi_b04_red.tif`).
Each band is delivered in its native resolution (10 m or 20 m);
the SCL band keeps its uint8 dtype.

**Processing Level Comparison:**
- `L2A` (default): Bottom of Atmosphere - atmospherically corrected, ready for analysis
- `L1C`: Top of Atmosphere - raw reflectance, use for custom atmospheric correction with tools like ACOLITE

#### Available Sentinel-2 bands

Reflectance bands (any combination of resolutions can be requested in a single call):

| Band  | Alias        | Resolution | Description                   |
|-------|--------------|------------|-------------------------------|
| `B02` | `b02_blue`   | 10 m       | Blue                          |
| `B03` | `b03_green`  | 10 m       | Green                         |
| `B04` | `b04_red`    | 10 m       | Red                           |
| `B08` | `b08_nir`    | 10 m       | NIR (broad, 842 nm)           |
| `B01` | `b01_coastal`| 20 m       | Coastal aerosol               |
| `B05` | `b05_re1`    | 20 m       | Red-edge 1                    |
| `B06` | `b06_re2`    | 20 m       | Red-edge 2                    |
| `B07` | `b07_re3`    | 20 m       | Red-edge 3                    |
| `B8A` | `b8a_nir`    | 20 m       | NIR (narrow, 865 nm)          |
| `B11` | `b11_swir1`  | 20 m       | SWIR 1                        |
| `B12` | `b12_swir2`  | 20 m       | SWIR 2                        |

Cloud / scene-classification mask (L2A only):

| Band  | Alias  | Resolution | Description                                        |
|-------|--------|------------|----------------------------------------------------|
| `SCL` | `scl`  | 20 m       | Sen2Cor Scene Classification Layer (categorical)   |

Example use cases:
```python
# NDVI calculation
CDSEDownload(shape='area.shp', dates=('2023-01-01', '2023-12-31'), bands=['B04', 'B08'])

# RGB visualization
CDSEDownload(shape='area.shp', dates=('2023-01-01', '2023-12-31'), bands=['B02', 'B03', 'B04'])

# Water mask / turbidity (mixes 10 m + 20 m + categorical SCL)
CDSEDownload(
    shape='area.shp',
    dates=('2023-01-01', '2023-12-31'),
    bands=['B02', 'B03', 'B04', 'B08', 'B11', 'B12', 'SCL'],
)
```

---

## Available Datasets & Products

### ✅ VPP_Pheno (Vegetation Phenology & Productivity)
**Status**: Working  
**Products**: 
- SOSD (Start of Season Date)
- EOSD (End of Season Date)
- MAXD (Maximum Date)
- MINV (Minimum Value)
- MAXV (Maximum Value)
- AMPL (Amplitude)
- LENGTH (Length of Season)
- LSLOPE (Left Slope)
- RSLOPE (Right Slope)
- SPROD (Seasonal Productivity)
- TPROD (Total Productivity)
- SOSV (Start of Season Value)
- EOSV (End of Season Value)

### ✅ VPP_ST (Seasonal Trajectories)
**Status**: Working  
**Products**:
- PPI (Plant Phenology Index)
- QFLAG (Quality Flag)

### ⚠️ VPP_Index (Vegetation Indices)
**Status**: NOT AVAILABLE (404 Error as of January 2025)  
**Products** (no longer accessible):
- ~~LAI (Leaf Area Index)~~
- ~~FAPAR (Fraction of Absorbed Photosynthetically Active Radiation)~~
- ~~NDVI (Normalized Difference Vegetation Index)~~
- ~~PPI (now available in VPP_ST)~~

### ✅ SLSTR (Sentinel-3 Land Surface Temperature)
**Status**: Working  
**Products**: SL_2_LST___

## Using DEIMS IDs

You can use DEIMS site IDs instead of shapefiles:

```python
downloader = pyvpp.wekeo_download(
    dataset='VPP_Pheno',
    shape='deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2',
    dates=['2020-01-01', '2020-12-31'],
    products=['SOSD', 'MAXD']
)
```

## Step-by-step workflow

PyVPP performs the following operations:

1. Downloads all Sentinel-2 tiles that intersect your area of interest
2. Filters tiles by UTM zone
3. Creates mosaics for each date and product
4. Clips mosaics to your exact boundaries
5. Saves final products as `mosaic_YYYYMMDD_PRODUCT_rec.tif`
6. Cleans up intermediate files

## Advanced Usage

### Use credentials directly (without .hdarc)

```python
downloader = pyvpp.wekeo_download(
    dataset='VPP_Pheno',
    shape='area.shp',
    dates=['2020-01-01', '2020-12-31'],
    products=['SOSD'],
    user='your_username',      # Direct credentials
    password='your_password'
)
```

### Clean old .hdarc format

If you have an old .hdarc file (pre-March 2024):

```python
import pyvpp
pyvpp.clean_old_hdarc()  # Removes obsolete 'url:' line
```

### Step-by-step execution

```python
# Execute steps individually
downloader.download()        # Only download
downloader.mosaic_and_clip() # Only mosaic and clip
downloader.clean()           # Only clean intermediate files
```

## Alternatives for LAI, FAPAR, NDVI

Since VPP_Index is currently unavailable, here are alternatives:

### 1. Google Earth Engine (Recommended)
```javascript
// Calculate NDVI from Sentinel-2
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate('2020-01-01', '2020-12-31')
  .filterBounds(geometry);

var addNDVI = function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
};
```

### 2. Sentinel Hub
https://www.sentinel-hub.com/
- Pre-computed LAI, FAPAR, NDVI available

### 3. Copernicus Global Land Service
https://land.copernicus.eu/global/products/
- 300m resolution (not 10m like HR-VPP)

### 4. Calculate from Sentinel-2 directly
```python
import rasterio
import numpy as np

# NDVI = (NIR - Red) / (NIR + Red)
with rasterio.open('sentinel2.tif') as src:
    red = src.read(4)  # Band 4
    nir = src.read(8)  # Band 8
    ndvi = (nir - red) / (nir + red)
```

## Troubleshooting

### Error 404: Dataset not found

If you get a 404 error with VPP_Index:
```
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: 
https://gateway.prod.wekeo2.eu/hda-broker/api/v1/datasets/EO:EEA:DAT:CLMS_HRVPP_VI
```

**Solution**: Use `VPP_Pheno` or `VPP_ST` instead (see examples above).

### Authentication failed

```python
# Recreate your .hdarc file
import pyvpp
pyvpp.create_hdarc("username", "password")
```

### No matches found

This usually means:
1. Date range is outside available data
2. Area of interest has no coverage
3. Product name is misspelled

Check the [official documentation](https://land.copernicus.eu/pan-european/biophysical-parameters/high-resolution-vegetation-phenology-and-productivity) for data availability.

## Requirements

- Python >= 3.9
- requests >= 2.28
- geopandas >= 0.12
- rasterio >= 1.3
- pyproj >= 3.4
- shapely >= 1.8
- deims >= 3.1
- fiona >= 1.8.20
- hda >= 2.18 (for WEkEO only)

## Documentation & Support

- **HR-VPP Documentation**: https://land.copernicus.eu/pan-european/biophysical-parameters/high-resolution-vegetation-phenology-and-productivity
- **WEkEO Help Center**: https://help.wekeo.eu/
- **PyVPP Repository**: https://github.com/Digdgeo/PyVPP
- **Report Issues**: https://github.com/Digdgeo/PyVPP/issues

## Citation

If you use PyVPP in your research, please cite:

```
García-Díaz, D. (2025). PyVPP: Python package for HR-VPP data access and processing.
https://github.com/Digdgeo/PyVPP
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### v1.0.0 (Current)
- **Per-date output**: mosaics organized in `YYYYMMDD_s2msi/` subfolders, one per acquisition date
- **Landsat-style naming**: `YYYYMMDD_s2msi_<alias>.tif` (e.g. `20230610_s2msi_b04_red.tif`)
- **Red-edge bands**: B05, B06, B07, B8A now fully supported
- **Token auto-refresh**: prevents `401 Unauthorized` on long download sessions
- **Resume support**: already-extracted SAFE directories are skipped on re-run
- **geopandas >= 0.14** required (fixes fiona 1.10+ compatibility)

### v0.4.0
- Added CDSE (Copernicus Data Space Ecosystem) support for Sentinel-2 L2A/L1C
- New module `pyvpp.cdse` with `CDSEDownload` class
- Multi-resolution support (10 m + 20 m + SCL in a single call)
- Per-band output files in native resolution
- Authentication via config file, env vars, or direct credentials

### v0.1.9
- Fixed `.hdarc` format for HDA API v2.18+
- Added `create_hdarc()`, `clean_old_hdarc()`, `delete_hdarc()` helpers

---

**Last updated**: May 2026
**Status**: VPP_ST ✅ | VPP_Pheno ✅ | VPP_Index ⚠️ (unavailable) | CDSE Sentinel-2 ✅
