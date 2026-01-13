# PyVPP Examples

This directory contains example scripts demonstrating different use cases for PyVPP.

## Files

### basic_usage.py

Comprehensive example script showing multiple ways to use PyVPP:

1. Using `.hdarc` file for credentials
2. Passing credentials directly
3. Step-by-step execution
4. Secure usage in Jupyter/shared environments

**To run:**

```bash
# Edit the script to add your WEkEO credentials first
python basic_usage.py
```

## Quick Examples

### Example 1: Download Phenology Data

```python
import pyvpp

# Configure credentials
pyvpp.create_hdarc("your_username", "your_password")

# Download phenology metrics
downloader = pyvpp.wekeo_download(
    dataset='VPP_Pheno',
    shape='deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2',
    dates=['2020-01-01', '2020-12-31'],
    products=['SOSD', 'MAXD', 'EOSD']
)

downloader.run()
```

### Example 2: Download Vegetation Indices

```python
import pyvpp

# Using direct credentials (no .hdarc file)
downloader = pyvpp.wekeo_download(
    dataset='VPP_Index',
    shape='/path/to/your/area.shp',
    dates=['2019-06-01', '2019-09-30'],
    products=['LAI', 'FAPAR', 'NDVI'],
    user='your_username',
    password='your_password'
)

downloader.run()
```

### Example 3: Step-by-Step Processing

```python
import pyvpp

downloader = pyvpp.wekeo_download(
    dataset='VPP_ST',
    shape='deimsid:https://deims.org/your-site',
    dates=['2021-01-01', '2021-12-31'],
    products=['PPI'],
    user='username',
    password='password'
)

# Execute step by step
print("Downloading...")
downloader.download()

print("Creating mosaics...")
downloader.mosaic_and_clip()

print("Cleaning up...")
downloader.clean()

print(f"Done! Files are in {downloader.pyhda}")
```

### Example 4: Jupyter Notebook Safe Usage

```python
import pyvpp

# Create temporary credentials
pyvpp.create_hdarc("username", "password")

try:
    downloader = pyvpp.wekeo_download(
        dataset='VPP_Index',
        shape='area.shp',
        dates=['2020-01-01', '2020-12-31'],
        products=['LAI']
    )
    downloader.run()
finally:
    # Always clean up
    pyvpp.delete_hdarc()
```

## Available Datasets and Products

### VPP_Index (Vegetation Indices)
- `LAI`: Leaf Area Index
- `FAPAR`: Fraction of Absorbed PAR
- `FCOVER`: Vegetation Cover Fraction
- `NDVI`: Normalized Difference Vegetation Index

### VPP_Pheno (Phenology)
- `SOSD`, `SOSV`: Start of Season
- `MAXD`, `MAXV`: Maximum of Season
- `EOSD`, `EOSV`: End of Season
- `LENGTH`, `AMPL`: Season characteristics
- `SPROD`, `TPROD`: Productivity

### VPP_ST (Seasonal Trajectories)
- `PPI`: Plant Phenology Index
- `QFLAG`: Quality Flags

### SLSTR (Temperature)
- `SL_2_LST___`: Land Surface Temperature

## Tips

1. **Large downloads**: For large areas or long time periods, the download may take considerable time. Consider:
   - Breaking into smaller time periods
   - Using a smaller area for testing first

2. **Disk space**: Make sure you have enough disk space. Unprocessed tiles can be several GB.

3. **WEkEO limits**: The API has rate limits (typically 100 images/hour). Plan accordingly.

4. **UTM zones**: The script automatically filters tiles to keep only relevant UTM zones for your area.

## Need Help?

- Check the main [README.md](../README.md)
- See the [CHANGELOG.md](../CHANGELOG.md) for recent changes
- Report issues: https://github.com/Digdgeo/PyVPP/issues
