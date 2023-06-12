from sdk.moveapps_spec import hook_impl
from movingpandas import TrajectoryCollection
import logging

import fiona
import pandas as pd
import geopandas as gpd
import movingpandas as mpd
from shapely.geometry import mapping

from app.data_extract import DataExtractor
from app.reduce import Reduce
from app.generate_map import generate_map

class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io

    @staticmethod
    def check_config(config):
        def check_for_key_and_value(key, value):
            if key not in config:
                config[key] = value

            if config[key] < 0:
                config[key] = value

        check_for_key_and_value('rdp_resolution', 350)
        check_for_key_and_value('grid_resolution', 2000)
        check_for_key_and_value('graduation_white', 0)
        check_for_key_and_value('graduation_lg', 1)
        check_for_key_and_value('graduation_g', 2)
        check_for_key_and_value('graduation_dg', 3)
        check_for_key_and_value('graduation_blk', 4)

        w_leq_lg = config['graduation_white'] <= config["graduation_lg"]
        lg_leq_g = config['graduation_lg'] <= config["graduation_g"]
        g_leq_dg = config['graduation_g'] <= config["graduation_dg"]
        dg_leq_blk = config['graduation_dg'] <= config["graduation_blk"]

        if not w_leq_lg:
            raise ValueError("White graduation setting has to be lesser or equal to light gray graduation")
        if not lg_leq_g:
            raise ValueError("Light gray graduation setting has to be lesser or equal to gray graduation")
        if not g_leq_dg:
            raise ValueError("Gray graduation setting has to be lesser or equal to dark gray graduation")
        if not dg_leq_blk:
            raise ValueError("Dark gray graduation setting has to be lesser or equal to black graduation")
        
        return config

    def save_polygon(self, data):
        schema = {
            'geometry': 'Polygon',
            'properties': {'label': 'int'},
        }

        corridors_shape_path = self.moveapps_io.create_artifacts_file('corridors.shp')
        with fiona.open(corridors_shape_path, 'w', 'ESRI Shapefile', schema) as c:
                for i in data.keys():
                    if i == 0:
                        continue
                    
                    try:
                        for poly in data[i].geoms:
                            if poly.geom_type != "Polygon":
                                continue
                            
                            c.write(
                                {
                                    'geometry': mapping(poly),
                                    'properties': { 'label': i }
                                }
                            )
                    except AttributeError:
                        c.write(
                            {
                                'geometry': mapping(data[i]),
                                'properties': { 'label': i }
                            }
                        )

    @hook_impl
    def execute(self, data: TrajectoryCollection, config: dict) -> TrajectoryCollection:
        """Your app code goes here"""
        logging.info(f'Welcome to the {config}')

        config = App.check_config(config)

        extractor = DataExtractor()
        d = [x for x in extractor(data)]
        # return some useful data for next apps in the workflow

        rdpReduce = Reduce(config['rdp_resolution'])
        reduced = rdpReduce(d)
        map, polygon_data = generate_map(reduced, resolution_in_m=config['grid_resolution'], \
                           graduation= [
                               int(config['graduation_white']),
                               int(config['graduation_lg']),
                               int(config['graduation_g']),
                               int(config['graduation_dg']),
                               int(config['graduation_blk'])
                           ])

        map.save(self.moveapps_io.create_artifacts_file('corridors_map.html'))
        self.save_polygon(polygon_data)

        return data