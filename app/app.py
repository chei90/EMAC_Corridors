from sdk.moveapps_spec import hook_impl
from movingpandas import TrajectoryCollection
import logging

import pandas as pd
import geopandas as gpd
import movingpandas as mpd

from app.data_extract import DataExtractor
from app.reduce import Reduce
from app.generate_map import generate_map

class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io

    @hook_impl
    def execute(self, data: TrajectoryCollection, config: dict) -> TrajectoryCollection:
        """Your app code goes here"""
        logging.info(f'Welcome to the {config}')

        extractor = DataExtractor()
        d = [x for x in extractor(data)]
        # return some useful data for next apps in the workflow

        rdpReduce = Reduce(config['rdp_resolution'])
        reduced = rdpReduce(d)
        map = generate_map(reduced, resolution_in_m=config['grid_resolution'], \
                           graduation= [
                               int(config['graduation_white']),
                               int(config['graduation_lg']),
                               int(config['graduation_g']),
                               int(config['graduation_dg']),
                               int(config['graduation_blk'])
                           ])

        map.save(self.moveapps_io.create_artifacts_file('corridors_map.html'))

        return data