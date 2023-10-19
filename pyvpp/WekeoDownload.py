import os
import zipfile
import rasterio
import deims
import geopandas as gpd
from hda import Client
from rasterio.merge import merge
from rasterio.mask import mask
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


# Login with .hdarc credentials functions
# Path to credentials file
file = os.path.join(os.path.expanduser('~'), '.hdarc')

def fillHda(user, password):
    """Create/Rewrite the .hdarc config file with user wekeo account data

    Args:
        user (str): Your Wekeo user
        password (str): Your Wekeo password
    """

    user = 'user: {}'.format(user)
    passx = 'password: {}'.format(password)

    lines = ['url: https://wekeo-broker.apps.mercator.dpi.wekeo.eu/databroker', user, passx]

    print(file)

    with open(file, 'w') as fp:
        fp.write('\n'.join(lines))
        
        
def delHdaInfo():
    """Function to delete personal info from .hdarc file
    """

    duser = 'user: '
    dpassx = 'password: '

    lines = ['url: https://wekeo-broker.apps.mercator.dpi.wekeo.eu/databroker', duser, dpassx]

    print(file)

    with open(file, 'w') as fp:
        fp.write('\n'.join(lines))

            
# Here starts the wekeo download class
class wekeo_download:

    
    def __init__(self, dataset, shape, dates, products):

        print('testing script')

        # Creatting the connection 
        self.conn = Client(debug=True)
        
        # Setting the output folder
        pyhdafolder = os.path.join(os.getcwd(), 'pyhda')
        if not os.path.exists(pyhdafolder):
            os.mkdir(pyhdafolder)
            
        os.chdir(pyhdafolder)
            
        self.dataset = dataset
        self.shape = shape
        
        # Let's do the DEIMS part
        if self.shape.startswith('deimsid'):
            
            # Spanish joke with Don Quijote de a mancha 
            print('Con DEIMS hemos topado amigo Sancho...')
            id_ = self.shape.split('/')[-1]
            self.gdf = deims.getSiteBoundaries(id_)
            #self.bbox = self.gdf.bounds
            
            
        else:
            
            self.gdf = gpd.read_file(self.shape)
        
        self.crs = self.gdf.crs
        self.bbox = self.gdf.bounds
        self.bbox_ = [self.bbox['minx'][0], self.bbox['miny'][0], self.bbox['maxx'][0], self.bbox['maxy'][0]]
        
        
        # Getting the UTM zone
        if self.crs.is_geographic:
            
            utm_crs_list = query_utm_crs_info(
            datum_name=self.crs.name,
            area_of_interest=AreaOfInterest(
                west_lon_degree=self.bbox_[0], #-93.581543,
                south_lat_degree=self.bbox_[1], #42.032974,
                east_lon_degree=self.bbox_[2], #-93.581543,
                north_lat_degree=self.bbox_[3] #42.032974,
                ),
            )
            utm_crs = CRS.from_epsg(utm_crs_list[0].code)
            self.utm = utm_crs.srs
            self.gdf_proj = self.gdf.to_crs(self.utm)
            self.crs = self.gdf_proj.crs
            
        else:
            
            self.utm = self.crs
            self.gdf_proj = self.gdf
            
        #print(self.utm)  
        self.dates = dates
        self.products = products
        self.datasetlists = {'VPP_Index': "EO:EEA:DAT:CLMS_HRVPP_VI", 'VPP_ST': "EO:EEA:DAT:CLMS_HRVPP_ST", 'VPP_Pheno': 'EO:EEA:DAT:CLMS_HRVPP_VPP', 'SLSTR': "EO:ESA:DAT:SENTINEL-3:SL_2_LST___"}
        self.variables = {'VPP_Index': ['PPI', 'NDVI', 'LAI', 'FAPAR'],
                          'VPP_ST': ['PPI'], 
                          'VPP_Pheno': ['SOSD', 'SOSV', 'MAXD', 'MAXV', 'EOSD', 'EOSV'],
                          'SLSTR': ['SL_2_LST___']}
        

        '''Other PhenoMetrics availables in the dataset:
        ['MINV', 'MAXD', 'LENGTH', 'SOSD', 'QFLAG', 
        'EOSV', 'TPROD', 'MAXV', 'AMPL', 'SOSV', 'LSLOPE', 'EOSD', 'RSLOPE', 'SPROD']'''
               
              
        self.query_fix = {
              "datasetId": self.datasetlists[self.dataset],
              "boundingBoxValues": [
                {
                  "name": "bbox",
                  "bbox": [
                      self.bbox_[0], self.bbox_[1], self.bbox_[2], self.bbox_[3]          
                          ]
                }
              ],
              "dateRangeSelectValues": [
                        {
                          "name": "temporal_interval",
                          "start": self.dates[0],
                          "end": self.dates[1]
                        }
              ]}
            
        self.query_moving = {"stringChoiceValues": [
                {
                  "name": "productType",
                  "value": self.products[0]
                },
                        {
                  "name": "productGroupId",
                  "value": "s1"
                }
              ]
            }
        
        self.query_moving_ = {"stringChoiceValues": [
                {
                  "name": "productType",
                  "value": self.products[0]
                }                        
              ]
            }
           
        
    def download(self):
        """This method apply the downoad by sending the query 
        to the connetction with HDA API 
        """

        if self.dataset == 'VPP_Pheno':
            
            self.query = {**self.query_fix, **self.query_moving}
            
        else: 
            
            self.query = {**self.query_fix, **self.query_moving_}
            
            
        for p in self.products:

            try:
                print('Getting', p)

                self.query['stringChoiceValues'][0]['value'] = p
                matches = self.conn.search(self.query)
                print(matches)
                matches.download()

            except Exception as e:
                print(e)
                continue 
        
        
    def mosaic(self):
        """This method performs the mosaic with the Sentinel 2 tiles 
        grouped by variable and date. Also performs the cropping with 
        the GeoDataFrame boundaries
        """
        
        path = os.getcwd()
        
        rasters = {}
        for i in os.listdir(path): 
            if i.endswith('.tif'):

                year = i.split('_')[1][:8]       
                rasters[year] = {}
                
                
        for i in os.listdir(path): 
            if i.endswith('.tif'):
                year = i.split('_')[1][:8]
                phenometric = i.split('_')[-1].split('.')[0]
                rasters[year][phenometric]=[]

        for i in os.listdir(path): 
            if i.endswith('.tif'):
                year = i.split('_')[1][:8]
                phenometric = i.split('_')[-1].split('.')[0]
                tile = i.split('_')[3].split('-')[0]
                rasters[year][phenometric].append(os.path.join(path, i))
        
        
        for k, v in rasters.items():
            
            print(k,v)
    
            for i in v.keys():
            
                try:
                    # Mosaicking list, it turns empty after every loop
                    nrasters = []

                    rs = rasters[k][i]
                    print('RS', rs)
                    date = rs[0].split('_')[1][:8]
                    sat = rs[0].split('_')[2][:2]
                    tile = rs[0].split('_')[3].split('-')[0]
                    resolution = rs[0].split('_')[3].split('-')[1]
                    season = rs[0].split('_')[5]
                    phenometric = rs[0].split('_')[-1].split('.')[0]

                    out_mosaic = os.path.join(path, ('_').join(['mosaic', date, sat, resolution, season, phenometric, '.tif']))
                    out_mosaic_rec = os.path.join(path, ('_').join(['mosaic', date, sat, resolution, season, phenometric, 'rec.tif']))


                    for current in rs:
                        
                        src = rasterio.open(current)
                        nrasters.append(src)

                    mosaic, out_trans = merge(nrasters)

                    out_meta = src.meta.copy()

                    out_meta.update({"driver": "GTiff",
                        "height": mosaic.shape[1],
                        "width": mosaic.shape[2],
                        "transform": out_trans,
                        "crs": self.crs 
                    })


                    with rasterio.open(out_mosaic, "w", **out_meta) as dest:
                        dest.write(mosaic)

                    # Read Shape file. GeoDataFrame use instead of orginal idea with shapesfiles
                    shapes = [i for i in self.gdf_proj.geometry]

                    # Read imagery file
                    with rasterio.open(out_mosaic) as src_:
                        out_image, out_transform = rasterio.mask.mask(src_, shapes, crop=True)
                        out_meta = src_.meta


                    # Save clipped imagery
                    out_meta.update({"driver": "GTiff",
                                     "height": out_image.shape[1],
                                     "width": out_image.shape[2],
                                     "transform": out_transform})


                    with rasterio.open(out_mosaic_rec, "w", **out_meta) as dest:
                        dest.write(out_image)
                        
                except Exception as e:
                    print(e)
                    continue
                    
    def clean(self):
        """Keep only the mosaic_**_rec.tif files in the output folder
        """

        for i in os.listdir(os.getcwd()):
            if i.endswith('.tif') and not '_rec' in i:
                os.remove(os.path.join(os.getcwd(), i))

            elif i.endswith('.zip'):
                zip_ = os.path.join(os.getcwd(), i)
                with zipfile.ZipFile(zip_, 'r') as zip_ref:
                    zip_ref.extractall(os.getcwd())
                #Remove the original zip files
                os.remove(os.path.join(os.getcwd(), i))
            else:
                continue
                
    def run(self):
        """Run the whole process
        """

        print('Downloading images...')
        self.download()
        print('Mosaicking and clipping...')
        self.mosaic()
        print('cleaning the folder...')
        self.clean()