from sdk.moveapps_spec import hook_impl
from movingpandas import TrajectoryCollection
import logging

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

        rdpReduce = Reduce()
        reduced = rdpReduce(d)
        generate_map(reduced)
        return data
