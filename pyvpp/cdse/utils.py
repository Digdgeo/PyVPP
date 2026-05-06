import geopandas as gpd


def load_shape(shape):
    """
    Load AOI geometry from a shapefile or DEIMS ID.

    Parameters
    ----------
    shape : str
        Path to shapefile or 'deimsid/UUID'

    Returns
    -------
    gdf : GeoDataFrame (EPSG:4326)
    gdf_proj : GeoDataFrame (projected CRS, UTM based on centroid)
    """

    # -------------------------
    # DEIMS site
    # -------------------------
    if shape.startswith("deimsid"):
        try:
            import deims
        except ImportError:
            raise ImportError(
                "To use a DEIMS ID, you must install the `deims` package:\n"
                "    pip install deims"
            )

        site_id = shape.split("/")[-1]

        # This returns a GeoDataFrame
        gdf = deims.getSiteBoundaries(site_id)

        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")

        else:
            gdf = gdf.to_crs("EPSG:4326")

    # -------------------------
    # Local shapefile
    # -------------------------
    else:
        gdf = gpd.read_file(shape)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            gdf = gdf.to_crs("EPSG:4326")

    # -------------------------
    # Project to UTM (centroid-based)
    # -------------------------
    centroid = gdf.geometry.iloc[0].centroid
    lon = centroid.x

    utm_zone = int((lon + 180) / 6) + 1
    epsg = 32600 + utm_zone

    gdf_proj = gdf.to_crs(epsg)

    return gdf, gdf_proj

