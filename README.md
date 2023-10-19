# PyVPP

Python package to download data from the [Pan European High Resolution Vegetation Phenology and Productivity](https://land.copernicus.eu/pan-european/biophysical-parameters/high-resolution-vegetation-phenology-and-productivity) part of the Copernicus Land Monitoring Service ([CLMS](https://land.copernicus.eu/)). This package have been developed within the framework of the [eLTER H2020](https://elter-ri.eu/) and [SUMHAL](https://lifewatcheric-sumhal.csic.es/descripcion-del-proyecto/) projects, as  a  tool  aimed  at  scientists  and  managers  of  the  sites  integrated  in  the  eLTER  network,  for  which  long-term  phenology  monitoring  can  be  assessed. 
         
![](https://i.imgur.com/Sv9LfYj.png)

## What we use
The package is based in these magnificient python libraries:

- [HDA python package](https://pypi.org/project/hda/) to download data from [Wekeo](https://www.wekeo.eu/). 
- [Deims](https://pypi.org/project/deims/) is a python package to get data from the Dynamic Ecological Information Management System - Site and dataset registry ([DEIMS-SDR](https://deims.org/)). We use this library to quickly get the spatial boundaries of the eLTER sites.
- [PyProj](https://pypi.org/project/pyproj/), [Geopandas](https://pypi.org/project/geopandas/) and [Rasterio](https://pypi.org/project/rasterio/) are used (as always :blush:) to do the spatial parts related with getting extents, reprojecting, mosaicking and clipping.

## What we do

The script accepts both as input, a shapefile or a deims id (**please remember to add "deimsid:yoursiteid" in case you use this option**), then it will read it as a Geodataframe, and it will download all the tiles that intersect the Bounding Box of the input boundaries. Once the tiles are downloaded it will mosaic them gruping by dates and products and it will crop the mosaics with the boundaries. Keeping in the ouptu folder (it will create a _/pyhda_ folder in your current working directory) just the "_mosaic_selectedvariable_rec.tif_" files. 

At the moment we offer 4 datasets:

1. ### **VPP_Index (Vegetation Indices): EO:EEA:DAT:CLMS_HRVPP_VI**

![Vegetation Indices](https://i.imgur.com/hJ4ORqr.png)

2. ### **VPP_Pheno (Phenology and Productivity): EO:EEA:DAT:CLMS_HRVPP_VPP**

![Phenology](https://i.imgur.com/L3xuXb1.png)

3. ### **VPP_Seasonal Trajectories (Vegetation Indices): EO:EEA:DAT:CLMS_HRVPP_ST**

![Vegetation Indices ST](https://i.imgur.com/vBTpYiC.png)

4. ### **Land Surface Temperature Radiometer (SLSTR: EO:ESA:DAT:SENTINEL-3:SL_2_LST___**

![LST](https://i.imgur.com/68y4zLF.png)

 Just a little of the whole catalog offered in Wekeo (you can have a look [here](https://pn-csw.apps.mercator.dpi.wekeo.eu/elastic-csw/service?service=CSW&request=GetRecords&version=2.0.2&ElementSetName=summary&resultType=results&maxRecords=100)), but they are the ones that we are interested in. 

 It's very likely that we will add more datasets in the near future. Even better, if you find this package helpful and you want to add some more datasets, please feel free to do it (and maybe share that with us with a Pull Requests :wink:)

## Why a package

As we said, this is intended to be used for eLTER sites managers and/or researchers, but it could be used to download data for any part of the globe (where data exists, of course). So we consider that this script could be profited for people moreover eLTER network. Plus, we think that have a python package to import it, is an approach more "friendly to use" than having a long script to copy and paste in different enviroments. 

## How to use it

Very easy, just import the library, select your input shape or deims id site, select the dates and the variables and launch the process with .run(). The typical workflow, once installed, would be like that:

```python
import pyvpp

# Just replace the second parameter (deimsid for /path/to/yor/shapefile.shp) for your local shapefile in case you want to use a shape.
MyWekeo = pyvpp.wekeo_download("VPP_Index", "deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2", ['2018-01-01', '2018-06-30'], ['LAI', 'FAPAR'])
MyWekeo.run()
```
The upper code will do the whole process for Doñana Long-Term Socio-ecological Research Platform (you can paste the link in a browser if you are curious) and just remain the LAI and FAPAR variables cropped with Doñana boundaries in the /pyhda folder. 
There's also the possibility to keep the original Sentinel 2 tiles (this product are based in Sentinel 2 images, sorry, maybe I have should said this before) in your folder. 

In that case you maybe want to run the process once by once, what can be done in the next way:

```python
import pyvpp

MyWekeo = pyvpp.wekeo_download("VPP_Index", "deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2", ['2018-01-01', '2018-06-30'], ['LAI', 'FAPAR'])
# Do the download
MyWekeo.download()
# Do the mosaics and cropping
MyWekeo.mosaic()
# Cleaning folder of original tiles and whole mosaics
MyWekeo.clean()
```

You can find the list of variables availables in these 2 datasets in Wekeo, but we work with the 4 vegetation indices:

 1. **PPI**, Plant Phenology Index
 2. **NDVI**, Normalized Difference vegetation Index
 3. **LAI**, Leaf Area Index,
 4. **FAPAR**, Fraction of Absorbed Photosynthetically Active Radiation
 
 And just with these phenometrics (but you could download any of the availables, just be sure to type correctly their names):
 
 1. **SOSD**, Start of the season Day of the Year
 2. **SOSV**, Start of the season Value of Vegetation Index
 3. **MAXD**, Maximun of the season Day of the Year
 4. **MAXV**, Maximun of the season Value of Vegetation Index
 5. **EOSD**, End of the season Day of the Year
 6. **EOSV**, End of the season Value of the Vegetation Index

 For the Seasonal Trajectories the only one product is the 10 days improved PPI index:

 1. **PPI**, Plant Phenology Index

And last, for the SLSTR the only product available is the Land Surface Temperature:

1. **SL_2_LST___**, Land Surface Temperature


 ## Important info! (specially for **Datalab** users)

 The download from Wekeo needs a token generated taken into account a config file where yuour user and password are stored (please, read [this](https://www.wekeo.eu/docs/hda-python-lib)). If you are running this in your local PC, just cerate your .hdarc file with your personal info and forget about it. But, if you run this in the Datalab (This is just for eLTER users), maybe you don't feel comfortable with the idea of having your credentials stored in the Datalab. Plus, if you don't delete this file and someone runs the script, the data will be downloaded with your account. Not a big deal, but it better to solve that.

 So, we have add a couple of functions to fix this. _fillHda()_ and _delHdaInfo()_. These functions are imported when you import the script, so the only thing you need to do is this:
 
```python
# This will create or rewrite in case that it already exists, the .hdarc with your credentials in the home folder.
# This should be the first thing that you do before run the WekeoDownload process
fillHda("youruser", "yourpassword")
```

```python
# And just be sure to run the del funciton when you are done. This will left the .hdarc but without any credentials in it, just white spaces waiting for the next fillHda() call.
# This should be the last thing that you do before exit your datalab session.
delHdaInfo()  
```

## ToDo

To do for you: **Please, don't forget download and delete the Pyhda folder in case you are in the Datalab**. 
