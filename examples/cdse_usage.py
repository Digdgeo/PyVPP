#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example: Download Sentinel-2 data using CDSE.

Demonstrates how to download Sentinel-2 L2A and L1C products from the
Copernicus Data Space Ecosystem (CDSE), including 10 m bands, 20 m bands
and the Scene Classification Layer (SCL).

For each requested band, the pipeline produces one mosaic GeoTIFF named
`mosaic_<BAND>_rec.tif`, clipped to the AOI and in the band's native
resolution (10 m or 20 m).
"""

from pyvpp import CDSEDownload


# Example 1: NDVI (10 m only)
print("Example 1: Download Sentinel-2 L2A (10 m bands for NDVI)")
print("-" * 60)
CDSEDownload(
    shape='path/to/your/area.shp',
    dates=('2023-06-01', '2023-06-30'),
    bands=['B04', 'B08'],          # Red, NIR
    outdir='sentinel2_ndvi',
).run()
# Output: sentinel2_ndvi/mosaic_B04_rec.tif, mosaic_B08_rec.tif

print()


# Example 2: Mixed-resolution download (10 m + 20 m + SCL)
# Useful for water-mask / turbidity workflows that need SWIR + a cloud mask.
print("Example 2: Mix 10 m, 20 m and SCL in a single call")
print("-" * 60)
CDSEDownload(
    shape='path/to/your/area.shp',
    dates=('2023-06-01', '2023-06-30'),
    bands=['B02', 'B03', 'B04', 'B08', 'B11', 'B12', 'SCL'],
    outdir='sentinel2_water',
    utm_zone=29,                   # Force tiles from UTM zone 29
).run()
# Output: one mosaic per band in its native resolution.
# - mosaic_B02_rec.tif … mosaic_B08_rec.tif at 10 m
# - mosaic_B11_rec.tif, mosaic_B12_rec.tif at 20 m
# - mosaic_SCL_rec.tif at 20 m (uint8, categorical, nearest-neighbour merge)

print()


# Example 3: DEIMS site as AOI
print("Example 3: Use a DEIMS site ID instead of a shapefile")
print("-" * 60)
CDSEDownload(
    shape='deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2',
    dates=('2023-05-01', '2023-05-31'),
    bands=['B04', 'B08'],
    outdir='sentinel2_deims',
).run()

print()


# Example 4: L1C TOA (no atmospheric correction — use ACOLITE / Sen2Cor / etc.)
print("Example 4: Download L1C (TOA) for custom atmospheric correction")
print("-" * 60)
CDSEDownload(
    shape='path/to/your/area.shp',
    dates=('2023-06-01', '2023-06-30'),
    bands=['B02', 'B03', 'B04', 'B08'],
    outdir='sentinel2_L1C_acolite',
    processing_level='L1C',
).run()
# Note: SCL is not available in L1C products and will be rejected at __init__.

print()


# Example 5: Step-by-step execution (search/download/mosaic separately)
print("Example 5: Step-by-step pipeline")
print("-" * 60)
dl = CDSEDownload(
    shape='path/to/your/area.shp',
    dates=('2023-07-01', '2023-07-15'),
    bands=['B04', 'B11', 'SCL'],
    outdir='sentinel2_manual',
)

products = dl.search()
print(f"Found {len(products)} products")

rasters_per_band = dl.download()  # dict {band: [jp2_paths]}

from pyvpp.cdse.cdse import CATEGORICAL_BANDS
from pyvpp.cdse.mosaic import mosaic_per_band
mosaic_per_band(
    rasters_per_band,
    dl.gdf_proj,
    outdir=dl.outdir,
    categorical=CATEGORICAL_BANDS,
)

print()
print("All examples completed.")
print("=" * 60)
print()
print("Notes:")
print("- Configure CDSE credentials first: env vars CDSE_USER/CDSE_PASSWORD,")
print("  ~/.pyvpp/config.toml, or pass them directly via load_cdse_credentials.")
print("- processing_level: 'L2A' (default, BOA) or 'L1C' (TOA).")
print("- Supported bands: B01–B08, B8A, B11, B12 (reflectance) and SCL (L2A only).")
print("- See https://dataspace.copernicus.eu/ for CDSE documentation.")
