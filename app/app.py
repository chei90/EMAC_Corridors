from sdk.moveapps_spec import hook_impl
from movingpandas import TrajectoryCollection
import logging

import fiona
import os
import shutil
from shapely.geometry import mapping

from app.data_extract import DataExtractor
from app.reduce import Reduce
from app.generate_map import generate_map

class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io

    @staticmethod
    def check_config(config):
        """
        This function ensures that the passed config dict contains only valid
        values and that all keys are present

        :param config: Dict[string, string] - the dictionary to validate
        """
        def check_for_key_and_value(key, value):
            """
            Checks if confing contains key, if no add key with default value.

            If the key is present, check if the value is OK
            """
            if key not in config:
                config[key] = value

            elif config[key] < 0:
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

    def save_polygon(self, data, crs):
        """
        Experimental: Tries to save data to a shapefile using fiona engine

        :param data: Dict[int, Multipolygon/Polygon] - The polygon data with its bin
        """

        def swap_mapping(map):
            polygon_exterior = map['coordinates']

            res = []
            for coordinates in polygon_exterior:
                tmp = tuple((x[1], x[0]) for x in coordinates)
                res.append(tmp)

            map['coordinates'] = tuple(res)
            return map



        schema = {
            'geometry': 'Polygon',
            'properties': {'label': 'int'},
        }

        # corridors_shape_path = self.moveapps_io.create_artifacts_file('corridors.shp')
        corridors_shape_folder = self.moveapps_io.create_artifacts_file('shapefile')
        if os.path.exists(corridors_shape_folder):
            shutil.rmtree(corridors_shape_folder)
        os.mkdir(corridors_shape_folder)

        shape_output_path = self.moveapps_io.create_artifacts_file('shapefile/corridors.shp')
        with fiona.open(shape_output_path, 'w', 'ESRI Shapefile', schema, crs=crs) as c:
                for i in data.keys():
                    if i == 0:
                        continue
                    
                    try:
                        for poly in data[i].geoms:
                            if poly.geom_type != "Polygon":
                                continue
                            
                            c.write(
                                {
                                    'geometry': swap_mapping(mapping(poly)),
                                    'properties': { 'label': i }
                                }
                            )
                    except AttributeError:
                        c.write(
                            {
                                'geometry': swap_mapping(mapping(data[i])),
                                'properties': { 'label': i }
                            }
                        )
        
        shutil.make_archive(self.moveapps_io.create_artifacts_file('corridors.shp'), "zip", corridors_shape_folder)
        shutil.rmtree(corridors_shape_folder)

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
        self.save_polygon(polygon_data, data.trajectories[0].crs)

        return data