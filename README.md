# PyVPP

Python package to download data from the [Pan European High Resolution Vegetation Phenology and Productivity](https://land.copernicus.eu/pan-european/biophysical-parameters/high-resolution-vegetation-phenology-and-productivity) part of the Copernicus Land Monitoring Service (CLMS). This script was originally made to download some phenometrics and vegetation indexes for some selected sites in the European Long Term Ecological Research Program ([eLTER](https://elter-ri.eu/)). 

The package is based in these python libraries:

- [HDA python package](https://pypi.org/project/hda/) to download data from [Wekeo](https://www.wekeo.eu/). 
- [Deims](https://pypi.org/project/deims/) is used to get the spatial boundaries of the eLTER sites.
- Fiona, Geopandas, Shapely and Rasterio are used (as always :)) to do the spatial parts.

The script takes a shapefile as input and get its bounding box to download all the data that intersect with the boundaries. Then it will download all the tiles and mosaic them by dates, when the mosaic is done it will crop the raster with the shapefile boundaries. Keeping in the ouptu folder just the "mosaic_selectedvariable_rec.tif" files. 

We think that it can be useful to other eLTER sites or for other people who just want to download data from Wekeo without have to worry about the mosaic and cropping process. 

Continue tomorrow :) 
