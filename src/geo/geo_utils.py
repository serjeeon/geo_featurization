import geopandas as gpd
import json
import numpy as np
import pandas as pd
import shapely

from h3 import h3
from scipy.spatial import cKDTree
from shapely.geometry import Point


def load_shp(filename):

    layer = gpd.read_file(filename)

    return layer


def get_hexagons_for_region(region_of_interest, resolution):

    boundary = shapely.ops.cascaded_union(region_of_interest['geometry'])
    if boundary.geom_type == 'MultiPolygon':
        region_of_interest_json = (gpd.GeoSeries(list(boundary)).to_json())
    elif boundary.geom_type == 'Polygon':
        region_of_interest_json = (gpd.GeoSeries(boundary).to_json())

    hexagons = pd.DataFrame()
    for feature in json.loads(region_of_interest_json)['features']:
        hexagons_part = pd.DataFrame(h3.polyfill(geo_json=feature['geometry'], res=resolution,
                                                 geo_json_conformant=True),
                                     columns=['hex_id'])
        hexagons = hexagons.append(hexagons_part, ignore_index=True)

    hexagons['geometry'] = (hexagons['hex_id']
                            .apply(lambda h: shapely.geometry.asPolygon(h3.h3_to_geo_boundary(h, geo_json=True))))
    hexagons_gdf = gpd.GeoDataFrame(hexagons, geometry='geometry')

    return hexagons_gdf


def save_geo_objects():
    raise NotImplementedError


def save_layer():
    raise NotImplementedError


def get_geo_object():
    raise NotImplementedError


def dist_from_points_to_nearest_point(points_from, points_to, dist_field_name):

    n_from = np.array(list(zip(points_from.geometry.x, points_from.geometry.y)))
    n_to = np.array(list(zip(points_to.geometry.x, points_to.geometry.y)))
    btree = cKDTree(n_to)
    dist, idx = btree.query(n_from, k=1)
    dist_gdf = pd.concat(
        [points_from.reset_index(drop=True), points_to.loc[idx, :].reset_index(drop=True),
         pd.Series(dist, name=dist_field_name)], axis=1)

    return dist_gdf
