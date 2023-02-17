# PyVPP

Python package to download data from the [Pan European High Resolution Vegetation Phenology and Productivity](https://land.copernicus.eu/pan-european/biophysical-parameters/high-resolution-vegetation-phenology-and-productivity) part of the Copernicus Land Monitoring Service (CLMS). This script was originally made to download some phenometrics and vegetation indexes for some selected sites in the European Long Term Ecological Research Program ([eLTER](https://elter-ri.eu/)). 

<p align="center">
<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTt8DxTzQLF9HztgmOpvdLARFGV7RkbgaBunXl28suqw&s" 
        alt="Picture" 
        width="300" 
        height="200" 
        style="display: block; margin: 0 auto" />
</p>

## What we use
The package is based in these magnificient python libraries:

- [HDA python package](https://pypi.org/project/hda/) to download data from [Wekeo](https://www.wekeo.eu/). 
- [Deims](https://pypi.org/project/deims/) is a python package to get data from the Dynamic Ecological Information Management System - Site and dataset registry ([DEIMS-SDR](https://deims.org/)). We use this library to quickly get the spatial boundaries of the eLTER sites.
- Fiona, Geopandas, Shapely and Rasterio are used (as always :blush:) to do the spatial parts related with getting extents, reprojecting, mosaicking and clipping parts.

## What we do

The script accepts both as input, a shapefile or a deims id (**please remember to add "deimsid:yoursiteid" in case you use this option**), then it will read it as a Geodataframe, and it will download all the tiles that intersect the Bounding Box of the input boundaries. Once the tiles are downloaded it will mosaic them gruping by dates and products and it will crop the mosaics with the boundaries. Keeping in the ouptu folder (it will create a _/pyhda_ folder in your current working directory) just the "mosaic_selectedvariable_rec.tif" files. 

At the moment we only offer 2 datasets of all those available in wekeo:

1. VPP_Index (Vegetation Indices): EO:EEA:DAT:CLMS_HRVPP_VI
![Vegetation Indices](https://i.imgur.com/t53cPMC.png)

2. VPP_Pheno (Phenology and Productivity): EO:EEA:DAT:CLMS_HRVPP_VPP
![Phenology](https://i.imgur.com/BaLKr5s.png)

 Just a little of the whole catalog offered in Wekeo (you can have a look [here](https://pn-csw.apps.mercator.dpi.wekeo.eu/elastic-csw/service?service=CSW&request=GetRecords&version=2.0.2&ElementSetName=summary&resultType=results&maxRecords=100)), but they are the only 2 that are interested for us in this project that is linked with Phenology. 

 It's very likely that we will add more datasets in the near future. Even better, if you find this package interesting and want to add some more datasets, please fell free to do it (and maybe share that with us with a Pull Requests :wink:)

## Why a package

As we said, this is intended to be used for eLTER sites managers and/or researchers, but it could be used to download data for any part of the globe (where data exists, of course). So we consider that this script could be useful for people moreover eLTER network. Besides, we think that have a python package to import it, is an approach more "friendly to use" than having a long script to copy and paste in different enviroments. 

## How to use it

Very easy, just import the library, select your input shape or deims id site, select the dates and the variables and launch the process with .run(). The typical workflow, once installed, would be like that:

```
import pyvpp

# Just replace the second parameter (deimsid for /path/to/yor/shapefile.shp) for your local shapefile in case you want to use a shape.
MyWekeo = pyvpp.wekeo_download("VPP_Index", "deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2", ['2018-01-01', '2018-06-30'], ['LAI', 'FAPAR'])
MyWekeo.run()
```
The upper code will do the whole process for Doñana Long-Term Socio-ecological Research Platform (you can paste the link in a browser if you are curious) and just remain the LAI and FAPAR variables cropped with Doñana boundaries in the /pyhda folder. 
There's also the possibility to keep the original Sentinel 2 tiles (this product are based in Sentinel 2 images, sorry, maybe I have should said this before) in your folder. 

In that case you maybe want to run the process once by once, what can be done in the next way:

```
import pyvpp

MyWekeo = pyvpp.wekeo_download("VPP_Index", "deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2", ['2018-01-01', '2018-06-30'], ['LAI', 'FAPAR'])
# Do the download
MyWekeo.download()
# Do the mosaics and cropping
MyWekeo.mosaic()
# Cleaning folder of original tiles and whole mosaics
MyWekeo.clean()
```
