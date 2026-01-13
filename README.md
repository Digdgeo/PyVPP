# PyVPP

Python package to download and preprocess High Resolution Vegetation Phenology and Productivity products (HR-VPP) from Copernicus Land Monitoring Service.

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

### 1. Configure your WEkEO credentials

```python
import pyvpp

# Create .hdarc file with your credentials
pyvpp.create_hdarc("your_wekeo_username", "your_wekeo_password")
```

### 2. Download data

#### Option A: Phenology parameters (RECOMMENDED - WORKING)

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

#### Option B: Seasonal Trajectories - PPI (RECOMMENDED - WORKING)

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

#### Option C: Vegetation Indices (⚠️ CURRENTLY NOT AVAILABLE)

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

- Python >= 3.8
- hda >= 2.18
- geopandas >= 0.8.2
- rasterio >= 1.3
- deims >= 4.0

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

### v0.1.9 (Current)
- Updated .hdarc format for new HDA API (March 2024+)
- Added direct credential support
- Improved error handling
- Added helper functions: create_hdarc(), clean_old_hdarc(), delete_hdarc()
- **Note**: VPP_Index dataset currently unavailable (404 error)

### v0.1.8
- Previous stable version
- Works with old HDA API (pre-March 2024)

---

**Last updated**: January 2025  
**Status**: VPP_ST ✅ | VPP_Pheno ✅ | VPP_Index ⚠️ (unavailable)
