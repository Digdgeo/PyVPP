import os
import zipfile
import requests
import rasterio
import deims
import geopandas as gpd
from hda import Client, Configuration  # Importamos Configuration también
from rasterio.merge import merge
from rasterio.mask import mask
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from pyproj import Transformer


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


class wekeo_download:
    
    def __init__(self, dataset, shape, dates, products, user, password):
        print('Initializing wekeo_download script...')

        self.user = user
        self.password = password

        # Obtener el token de acceso
        self.token = self.get_access_token()
        if not self.token:
            raise RuntimeError("Failed to authenticate and obtain access token.")

        # Crear la conexión
        conf = Configuration(user=user, password=password)
        self.conn = Client(config=conf)
        #self.conn = Client()

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
            self.bbox_utm = self.gdf.total_bounds
            transformer = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)
            minx, miny = transformer.transform(self.bbox_utm[0], self.bbox_utm[1])
            maxx, maxy = transformer.transform(self.bbox_utm[2], self.bbox_utm[3])
            self.bbox = [minx, miny, maxx, maxy]
            self.gdf_proj = self.gdf.to_crs("EPSG:4326")  # Proyectar a WGS84 (geográficas)
        else:
            self.bbox = self.gdf.total_bounds
            self.gdf_proj = self.gdf

        print(f"Converted bbox to geographic coordinates: {self.bbox}")

        self.dates = dates
        self.products = products
        self.datasetlists = {
            'VPP_Index': "EO:EEA:DAT:CLMS_HRVPP_VI", 
            'VPP_ST': "EO:EEA:DAT:CLMS_HRVPP_ST",
            'VPP_Pheno': 'EO:EEA:DAT:CLMS_HRVPP_VPP',
            'SLSTR': "EO:ESA:DAT:SENTINEL-3:SL_2_LST___"
        }

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
                'dataset_id': "EO:EEA:DAT:CLMS_HRVPP_VI",
                'productType': product,                
                'bbox': [-6.47514014469748, 36.870399417887654, -6.215630498836518, 37.12946619848626],
                'startdate': f"{self.dates[0]}T00:00:00.000Z",
                'enddate': f"{self.dates[1]}T23:59:59.999Z"
            }

            # Realizar búsqueda
            try:
                matches = self.conn.search(query)
                print(f"Matches response: {matches}")

                # Filtrar resultados por id que contenga 'T29'
                filtered_matches = [result for result in matches.results if "T29" in result['id']]
                print(f"Found {len(filtered_matches)} in zone T29")

                # Guardar el directorio actual
                original_dir = os.getcwd()
                try:
                    # Cambiar al directorio de destino
                    os.chdir(self.pyhda)

                    for match in filtered_matches:
                        print(f"Downloading product {match['id']} from {match['properties']['location']}")

                        # Realizar la descarga utilizando el método `download` de `matches`
                        try:
                            download_result = matches.download(match['id'])
                            print(f"Downloaded {match['id']} successfully.")
                        except Exception as download_error:
                            print(f"Failed to download {match['id']} due to: {download_error}")

                except Exception as e:
                    print(f"Error downloading {product}: {e}")
                
                finally:
                    # Volver al directorio original
                    os.chdir(original_dir)

            except Exception as e:
                print(f"Error downloading {product}: {e}")


    def filter_tiles(self):
        """
        Filtra los archivos TIFF para eliminar aquellos que pertenecen al huso 30.
        """
        print("Filtering tiles...")
        for root, _, files in os.walk(self.pyhda):
            for file in files:
                if file.endswith(".tif") and "T30" in file:
                    file_path = os.path.join(root, file)
                    print(f"Removing tile from huso 30: {file_path}")
                    os.remove(file_path)


    

    def mosaic_and_clip(self):

        # Recorrer subcarpetas dentro de `self.pyhda`
        self.filter_tiles()

        for folder in os.listdir(self.pyhda):
            subfolder_path = os.path.join(self.pyhda, folder)
            if os.path.isdir(subfolder_path):  # Verificar que es una carpeta
                rasters = {}

                # Agrupar por fecha y producto usando el nombre del archivo en cada subcarpeta
                for i in os.listdir(subfolder_path):
                    if i.endswith('.tif'):
                        date = i.split('_')[1][:8]  # Extraer la fecha (primeros 8 caracteres de la fecha)
                        product = i.split('_')[-1][:-4]  # Extraer el nombre del producto (el sufijo sin la extensión)

                        if date not in rasters:
                            rasters[date] = {}
                        if product not in rasters[date]:
                            rasters[date][product] = []

                        rasters[date][product].append(os.path.join(subfolder_path, i))

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
                                "crs": self.crs
                            })

                            # Definir nombres de archivo de salida en la carpeta principal `self.pyhda`
                            out_mosaic = os.path.join(self.pyhda, f"mosaic_{date}_{product}.tif")
                            out_mosaic_rec = os.path.join(self.pyhda, f"mosaic_{date}_{product}_rec.tif")

                            # Guardar el mosaico
                            with rasterio.open(out_mosaic, "w", **out_meta) as dest:
                                dest.write(mosaic)

                            # Convertir la geometría a los límites del CRS de salida (en caso de diferencias)
                            shapes = [self.gdf_proj.to_crs(out_meta['crs']).geometry.unary_union]

                            # Verificar que el recorte se va a hacer con el mismo CRS
                            print(f"CRS del shapefile para el recorte: {out_meta['crs']}")

                            # Realizar el recorte
                            with rasterio.open(out_mosaic) as src_:
                                out_image, out_transform = mask(src_, shapes, crop=True)
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

        """Keep only the mosaic_**_rec.tif files in the output folder and delete everything else."""

        for filename in os.listdir(self.pyhda):
            file_path = os.path.join(self.pyhda, filename)

            # Comprobar si el archivo es un .tif y si contiene ".rec" en el nombre
            if not (filename.endswith('.tif') and '.rec' in filename):
                # Si el archivo no cumple las condiciones, eliminarlo
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    elif os.path.isdir(file_path):
                        # Si es una carpeta, eliminar todo su contenido de manera recursiva
                        import shutil
                        shutil.rmtree(file_path)
                        print(f"Deleted directory: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
                
    def run(self):

        """Run the whole process
        """

        print('Downloading images...')
        self.download()
        print('Mosaicking and clipping...')
        self.mosaic_and_clip()
        print('cleaning the folder...')
        self.clean()
