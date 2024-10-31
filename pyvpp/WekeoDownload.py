import os
import time
import shutil
import zipfile
import requests
import rasterio
import deims
import geopandas as gpd
from hda import Client, Configuration
from rasterio.merge import merge
from rasterio.mask import mask
from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import box  # Añade esta línea


def create_hdarc(user, password):
    """
    Crea un archivo .hdarc con las credenciales proporcionadas.
    
    :param user: Nombre de usuario de Wekeo.
    :param password: Contraseña de Wekeo.
    """
    hdarc_content = f"""
    {{
        "user": "{user}",
        "password": "{password}"
    }}
    """

    # Guardar el contenido en el archivo .hdarc en el directorio del usuario
    home_directory = os.path.expanduser("~")
    hdarc_path = os.path.join(home_directory, ".hdarc")

    with open(hdarc_path, "w") as hdarc_file:
        hdarc_file.write(hdarc_content.strip())
    print(f"Archivo .hdarc creado en: {hdarc_path}")


def delete_hdarc():
    """
    Elimina el archivo .hdarc del directorio del usuario si existe.
    """
    home_directory = os.path.expanduser("~")
    hdarc_path = os.path.join(home_directory, ".hdarc")

    if os.path.exists(hdarc_path):
        os.remove(hdarc_path)
        print(f"Archivo .hdarc eliminado de: {hdarc_path}")
    else:
        print("No se encontró el archivo .hdarc.")


def get_utm_zones(geometry):
    """
    Obtiene una lista de husos UTM que cubren la geometría proporcionada.
    
    :param geometry: Geometría (shapely geometry).
    :return: Lista de husos UTM (ejemplo: ['T29', 'T30']).
    """
    utm_zones = set()
    minx, miny, maxx, maxy = geometry.bounds
    lons = [minx, maxx]
    for lon in lons:
        utm_zone_number = int((lon + 180) / 6) % 60 + 1
        utm_zone = f"T{utm_zone_number:02d}"
        utm_zones.add(utm_zone)
    return list(utm_zones)


class wekeo_download:
    
    def __init__(self, dataset, shape, dates, products):

        print('Initializing wekeo_download script...')

        #self.user = user
        #self.password = password

        # Obtener el token de acceso
        #self.token = self.get_access_token()
        #if not self.token:
            #raise RuntimeError("Failed to authenticate and obtain access token.")

        # Crear la conexión
        #conf = Configuration(user=user, password=password)
        #self.conn = Client(config=conf)
        self.conn = Client()

        # Crear la carpeta de salida y continuar la inicialización
        self.pyhda = os.path.join(os.getcwd(), 'pyhda')
        os.makedirs(self.pyhda, exist_ok=True)
        #os.chdir(pyhdafolder)
        
        self.dataset = dataset
        self.shape = shape

        # Manejar DEIMS o shapefiles proporcionados por el usuario
        if self.shape.startswith('deimsid'):
            print('Con DEIMS hemos topado amigo Sancho...')
            id_ = self.shape.split('/')[-1]
            self.gdf = deims.getSiteBoundaries(id_)
        else:
            self.gdf = gpd.read_file(self.shape)

        self.crs = self.gdf.crs
        self.bbox = self.gdf.bounds
        self.bbox_utm = [self.bbox['minx'][0], self.bbox['miny'][0], self.bbox['maxx'][0], self.bbox['maxy'][0]]

        # Convertir la caja delimitadora a coordenadas geográficas (EPSG:4326) si es necesario
        if not self.crs.is_geographic:
            self.gdf_proj = self.gdf.to_crs("EPSG:4326")  # Proyectar a WGS84 (geográficas)
        else:
            self.gdf_proj = self.gdf

        self.bbox = list(self.gdf_proj.total_bounds)
        print(f"Converted bbox to geographic coordinates: {self.bbox}")

        self.geometry = self.gdf_proj.geometry.unary_union  # Geometría unificada
        self.utm_zones = get_utm_zones(self.geometry)
        print(f"Husos UTM para el AOI: {self.utm_zones}")

        self.dates = dates
        self.products = products
        self.datasetlists = {
            'VPP_Index': "EO:EEA:DAT:CLMS_HRVPP_VI", 
            'VPP_ST': "EO:EEA:DAT:CLMS_HRVPP_ST",
            'VPP_Pheno': 'EO:EEA:DAT:CLMS_HRVPP_VPP',
            'SLSTR': "EO:ESA:DAT:SENTINEL-3:SL_2_LST___"
        }
        self.dataset_name = self.datasetlists[self.dataset]

    def get_access_token(self):
        """Obtener el token de acceso de la API de Wekeo"""
        url = "https://gateway.prod.wekeo2.eu/hda-broker/gettoken"
        payload = {"username": self.user, "password": self.password}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"Access token obtained: {token}")
            return token
        else:
            print(f"Failed to obtain access token. Response: {response.status_code} {response.text}")
            return None

    def download(self):
        for product in self.products:
            print(f'Getting product: {product}')
            query = {
                'dataset_id': self.dataset_name,
                'productType': product,
                'bbox': self.bbox,
                'startdate': f"{self.dates[0]}T00:00:00.000Z",
                'enddate': f"{self.dates[1]}T23:59:59.999Z"
            }

            try:
                matches = self.conn.search(query)
                print(f"Matches response: {matches}")

                print(f"Found {len(matches.results)} matches for product: {product}.")

                # Descargar todos los productos encontrados
                matches.download(download_dir=self.pyhda)
                print(f"Downloaded all products for {product} successfully.")

            except Exception as e:
                print(f"Error downloading {product}: {e}")




    def filter_tiles(self):

        """
        Filtra los archivos TIFF para mantener solo aquellos que pertenecen a los husos UTM de interés.
        """
        print("Filtering tiles...")
        for root, _, files in os.walk(self.pyhda):
            for file in files:
                if file.endswith(".tif"):
                    # Si el archivo no pertenece a ninguno de los husos UTM de interés, se elimina
                    if not any(utm_zone in file for utm_zone in self.utm_zones):
                        file_path = os.path.join(root, file)
                        print(f"Removing tile not in UTM zones {self.utm_zones}: {file_path}")
                        os.remove(file_path)


    

    def mosaic_and_clip(self):

        # Filtrar solo los archivos en self.pyhda que corresponden a los tiles T29
        self.filter_tiles()

        # Diccionario para agrupar rasters por fecha y producto
        rasters = {}

        # Agrupar por fecha y producto usando el nombre del archivo
        for file in os.listdir(self.pyhda):
            if file.endswith('.tif'):
                date = file.split('_')[1][:8]  # Extraer la fecha
                product = file.split('_')[-1][:-4]  # Extraer el nombre del producto

                if date not in rasters:
                    rasters[date] = {}
                if product not in rasters[date]:
                    rasters[date][product] = []

                rasters[date][product].append(os.path.join(self.pyhda, file))

        # Crear mosaicos y recortar para cada grupo de fecha y producto
        for date, products in rasters.items():
            for product, paths in products.items():
                try:
                    print(f"Mosaicking and clipping for date {date} and product {product}...")
                    # Crear una lista de fuentes de raster
                    nrasters = [rasterio.open(path) for path in paths]

                    # Crear el mosaico
                    mosaic, out_trans = merge(nrasters)

                    # Actualizar metadatos para el archivo de salida
                    out_meta = nrasters[0].meta.copy()
                    out_meta.update({
                        "driver": "GTiff",
                        "height": mosaic.shape[1],
                        "width": mosaic.shape[2],
                        "transform": out_trans,
                        "crs": nrasters[0].crs  # Asegurar que el CRS está definido
                    })

                    # Definir nombres de archivo de salida
                    out_mosaic = os.path.join(self.pyhda, f"mosaic_{date}_{product}.tif")
                    out_mosaic_rec = os.path.join(self.pyhda, f"mosaic_{date}_{product}_rec.tif")

                    # Guardar el mosaico
                    with rasterio.open(out_mosaic, "w", **out_meta) as dest:
                        dest.write(mosaic)

                    # Re-proyectar la geometría al CRS del raster
                    site_geom = self.gdf.to_crs(out_meta['crs']).geometry.unary_union

                    # Verificar la superposición
                    raster_geom = box(*out_meta['transform'] * (0, 0),
                                      *out_meta['transform'] * (out_meta['width'], out_meta['height']))

                    if not raster_geom.intersects(site_geom):
                        print(f"La geometría y el raster no se superponen para la fecha {date} y producto {product}.")
                        continue  # Saltar al siguiente

                    # Realizar el recorte
                    with rasterio.open(out_mosaic) as src_:
                        out_image, out_transform = mask(src_, [site_geom], crop=True)
                        out_meta = src_.meta

                    # Actualizar metadatos para el archivo recortado
                    out_meta.update({
                        "driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform
                    })

                    # Guardar el archivo recortado
                    with rasterio.open(out_mosaic_rec, "w", **out_meta) as dest:
                        dest.write(out_image)

                except Exception as e:
                    print(f"Error processing date {date} and product {product}: {e}")
                    continue


                    
    def clean(self):
        
        """Keep only the .rec.tif files in the output folder and delete everything else."""

        for filename in os.listdir(self.pyhda):
            file_path = os.path.join(self.pyhda, filename)

            # Si es un directorio, eliminarlo por completo
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {file_path}")
            # Si es un archivo y no cumple la condición de ".rec.tif", eliminarlo
            if not filename.endswith('_rec.tif'):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

                
    def run(self):

        """Run the whole process
        """

        print('Downloading images...')
        self.download()
        print('Mosaicking and clipping...')
        self.mosaic_and_clip()
        print('cleaning the folder...')
        self.clean()
