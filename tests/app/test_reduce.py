import unittest
import os

import pandas as pd

from app.app import App
from app.data_extract import DataExtractor
from app.reduce import Reduce
from sdk.moveapps_io import MoveAppsIo
from tests.config.definitions import ROOT_DIR

class DataExtractTests(unittest.TestCase):

    def setUp(self) -> None:
        os.environ['APP_ARTIFACTS_DIR'] = os.path.join(ROOT_DIR, 'tests/resources/output')
        self.sut = App(moveapps_io=MoveAppsIo())

    def data_extract_keeps_individuals(self):
        # prepare
        input = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        # execute
        extractor = DataExtractor()
        actual = extractor(input)

        # verif
        pts = min(actual, key=lambda x: len(x[1]))
        red = Reduce()
        reduced = red(('id', pts))

        self.assertGreater(len(pts[1]), len(reduced[1]))        