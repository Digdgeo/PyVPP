# HR-VPP Datasets Status (January 2025)

## 📊 Status Summary

| Dataset | ID | Status | Last Verified |
|---------|----|---------|--------------------|
| VPP_Pheno | EO:EEA:DAT:CLMS_HRVPP_VPP | ✅ Working | January 2025 |
| VPP_ST | EO:EEA:DAT:CLMS_HRVPP_ST | ✅ Working | January 2025 |
| VPP_Index | EO:EEA:DAT:CLMS_HRVPP_VI | ❌ Not available (404) | January 2025 |
| SLSTR | EO:ESA:DAT:SENTINEL-3:SL_2_LST___ | ✅ Working | - |

## ⚠️ VPP_Index - Currently Unavailable

### What happened?

The dataset `EO:EEA:DAT:CLMS_HRVPP_VI` containing daily vegetation indices (LAI, FAPAR, NDVI, PPI) **returns 404 error** since approximately 2024.

### What did it contain?

- **LAI** - Leaf Area Index
- **FAPAR** - Fraction of Absorbed Photosynthetically Active Radiation
- **NDVI** - Normalized Difference Vegetation Index
- **PPI** - Plant Phenology Index (now available in VPP_ST)
- **QFLAG2** - Quality Flag

### Discontinued dataset characteristics:
- Resolution: 10m
- Frequency: Daily
- Projection: UTM/WGS84
- Period: 2017 - 2024 (approximately)

### Will it come back?

**Unknown**. There is no official information about whether it:
1. Was permanently discontinued
2. Is under maintenance
3. Was moved to another ID
4. Is being restructured

### What to do in the meantime?

#### Option 1: Use PPI from VPP_ST
```python
import pyvpp

downloader = pyvpp.wekeo_download(
    dataset='VPP_ST',  # ✅ Works
    shape='area.shp',
    dates=['2020-01-01', '2020-12-31'],
    products=['PPI']  # Plant Phenology Index
)
```

PPI is an index specifically designed for vegetation phenology and can serve as an alternative to NDVI for some analyses.

#### Option 2: Calculate from Sentinel-2
```python
import rasterio
import numpy as np

# Download Sentinel-2 Level-2A
# Calculate NDVI: (NIR - Red) / (NIR + Red)
with rasterio.open('S2_L2A.tif') as src:
    red = src.read(4)   # Band B4 (665nm)
    nir = src.read(8)   # Band B8 (842nm)
    
    ndvi = np.where(
        (nir + red) != 0,
        (nir - red) / (nir + red),
        0
    )
```

#### Option 3: Google Earth Engine
```javascript
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate('2020-01-01', '2020-12-31')
  .filterBounds(geometry);

var addIndices = function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var evi = image.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
      'NIR': image.select('B8'),
      'RED': image.select('B4'),
      'BLUE': image.select('B2')
  }).rename('EVI');
  
  return image.addBands(ndvi).addBands(evi);
};

var s2_indices = s2.map(addIndices);
```

#### Option 4: Sentinel Hub
https://www.sentinel-hub.com/

Offers pre-computed LAI, FAPAR, NDVI from Sentinel-2.

#### Option 5: Copernicus Global Land Service
https://land.copernicus.eu/global/products/

- LAI: https://land.copernicus.eu/global/products/lai
- FAPAR: https://land.copernicus.eu/global/products/fapar

**⚠️ Limitation**: 300m resolution (not 10m like HR-VPP)

## ✅ VPP_Pheno - Phenology & Productivity

### Status: Working ✅

### Dataset ID
```python
'EO:EEA:DAT:CLMS_HRVPP_VPP'
```

### Available Products

| Product | Full Name | Description |
|----------|-----------------|-------------|
| SOSD | Start of Season Date | Date of start of season |
| EOSD | End of Season Date | Date of end of season |
| MAXD | Maximum Date | Date of maximum value |
| MINV | Minimum Value | Minimum PPI value |
| MAXV | Maximum Value | Maximum PPI value |
| AMPL | Amplitude | Amplitude (MAXV - MINV) |
| LENGTH | Length of Season | Season length |
| LSLOPE | Left Slope | Slope at start (green-up) |
| RSLOPE | Right Slope | Slope at end (senescence) |
| SPROD | Seasonal Productivity | Seasonal productivity |
| TPROD | Total Productivity | Total productivity |
| SOSV | Start of Season Value | Value at start of season |
| EOSV | End of Season Value | Value at end of season |
| QFLAG | Quality Flag | Quality indicator |

### Characteristics
- **Frequency**: Annual
- **Resolution**: 10m
- **Projection**: UTM/WGS84
- **Period**: 2017 - present
- **Seasons**: Up to 2 seasons per year
- **Coverage**: EEA38 + UK

### Usage Example
```python
import pyvpp

downloader = pyvpp.wekeo_download(
    dataset='VPP_Pheno',
    shape='area.shp',
    dates=['2020-01-01', '2020-12-31'],
    products=['SOSD', 'MAXD', 'EOSD', 'LENGTH', 'AMPL', 'TPROD']
)

downloader.run()
```

### Use Cases
- Phenological analysis
- Vegetation productivity studies
- Crop monitoring
- Climate change impact
- Forest management

## ✅ VPP_ST - Seasonal Trajectories

### Status: Working ✅

### Dataset ID
```python
'EO:EEA:DAT:CLMS_HRVPP_ST'
```

### Available Products

| Product | Full Name | Description |
|----------|-----------------|-------------|
| PPI | Plant Phenology Index | Plant phenology index |
| QFLAG | Quality Flag | Quality indicator |

### Characteristics
- **Frequency**: Every 10 days (smoothed)
- **Resolution**: 10m
- **Projection**: UTM/WGS84
- **Period**: 2017 - present
- **Coverage**: EEA38 + UK

### Usage Example
```python
import pyvpp

downloader = pyvpp.wekeo_download(
    dataset='VPP_ST',
    shape='area.shp',
    dates=['2020-01-01', '2020-12-31'],
    products=['PPI', 'QFLAG']
)

downloader.run()
```

### Use Cases
- Vegetation vigor time series
- Anomaly detection
- Trend analysis
- Continuous vegetation monitoring

### What is PPI?

The **Plant Phenology Index (PPI)** is an index specifically designed to detect vegetation phenology. It is more sensitive to phenological changes than NDVI and is optimized for:
- Detecting start and end of season
- Following vegetative development
- Minimizing soil and atmospheric effects

## 🔄 LAEA Projections Available

LAEA (Lambert Azimuthal Equal Area) projection versions also exist for working with High Resolution Layers:

```python
# Currently NOT supported by PyVPP, but available on WEkEO
SEASONAL_TRAJECTORIES_LAEA = 'EO:EEA:DAT:CLMS_HRVPP_ST-LAEA'
VPP_PARAMS_LAEA = 'EO:EEA:DAT:CLMS_HRVPP_VPP-LAEA'
```

## 📞 Contact and Support

### Report dataset issues

1. **WEkEO Help Center**: https://help.wekeo.eu/
2. **Email**: copernicus@eea.europa.eu
3. **Forum**: https://forum.step.esa.int/

### Check current status

To verify if VPP_Index is available again:

```python
from hda import Client

client = Client()

try:
    info = client.dataset('EO:EEA:DAT:CLMS_HRVPP_VI')
    print("✅ Dataset available!")
    print(f"Title: {info.get('title')}")
except Exception as e:
    if "404" in str(e):
        print("❌ Dataset still unavailable (404)")
    else:
        print(f"⚠️ Error: {e}")
```

Or run the diagnostic script:
```bash
python verify_datasets.py
```

## 📚 References

- **Official HR-VPP Documentation**: https://land.copernicus.eu/pan-european/biophysical-parameters/high-resolution-vegetation-phenology-and-productivity
- **User Manual**: https://land.copernicus.eu/user-corner/technical-library/product-user-manual-of-vegetation-phenology-and-productivity-parameters-version-1
- **Algorithm Theoretical Basis Document**: https://land.copernicus.eu/user-corner/technical-library/product-user-manual-of-seasonal-trajectories
- **WEkEO Portal**: https://www.wekeo.eu/
- **Official EEA Notebooks**: https://github.com/eea/clms-hrvpp-tools-python

## ⏱️ Change History

| Date | Event |
|-------|--------|
| 2017-10 | HR-VPP Launch |
| 2021-08 | Official notebooks created |
| 2022-10 | Update v1.1 |
| 2024-03 | HDA API update |
| 2024-?? | VPP_Index stops working |
| 2025-01 | Status confirmed: VPP_Index → 404 |

---

**Last updated**: January 13, 2025  
**Next recommended check**: March 2025
