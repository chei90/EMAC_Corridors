import unittest
import os
from tests.config.definitions import ROOT_DIR
from app.app import App
from sdk.moveapps_io import MoveAppsIo
import pandas as pd
import movingpandas as mpd


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        os.environ['APP_ARTIFACTS_DIR'] = os.path.join(ROOT_DIR, 'tests/resources/output')
        self.sut = App(moveapps_io=MoveAppsIo())

    def test_app_returns_input(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 0,
            "graduation_lg": 5,
            "graduation_g": 10,
            "graduation_dg": 20,
            "graduation_blk": 30
        }

        # execute
        actual = self.sut.execute(data=expected, config=config)

        # verif
        self.assertEqual(expected, actual)

    def test_app_throws_on_invalid_white_graduation_value(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 7,
            "graduation_lg": 5,
            "graduation_g": 10,
            "graduation_dg": 20,
            "graduation_blk": 30
        }

        # execute & verify
        with self.assertRaises(ValueError) as _:
            self.sut.execute(data=expected, config=config)

    def test_app_throws_on_invalid_light_gray_graduation_value(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 0,
            "graduation_lg": 11,
            "graduation_g": 10,
            "graduation_dg": 20,
            "graduation_blk": 30
        }

        # execute & verify
        with self.assertRaises(ValueError) as _:
            self.sut.execute(data=expected, config=config)

    def test_app_throws_on_invalid_gray_graduation_value(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 7,
            "graduation_lg": 5,
            "graduation_g": 22,
            "graduation_dg": 20,
            "graduation_blk": 30
        }

        # execute & verify
        with self.assertRaises(ValueError) as _:
            self.sut.execute(data=expected, config=config)

    def test_app_throws_on_invalid_dark_gray_graduation_value(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 7,
            "graduation_lg": 5,
            "graduation_g": 10,
            "graduation_dg": 32,
            "graduation_blk": 30
        }

        # execute & verify
        with self.assertRaises(ValueError) as _:
            self.sut.execute(data=expected, config=config)

    def test_app_throws_on_invalid_black_graduation_value(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 7,
            "graduation_lg": 5,
            "graduation_g": 10,
            "graduation_dg": 20,
            "graduation_blk": 5
        }

        # execute & verify
        with self.assertRaises(ValueError) as _:
            self.sut.execute(data=expected, config=config)

    def test_app_throws_on_negative_gray_graduation_value(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {
            "rdp_resolution": 350,
            "grid_resolution": 2000,
            "graduation_white": 7,
            "graduation_lg": 5,
            "graduation_g": -10,
            "graduation_dg": 20,
            "graduation_blk": 30
        }

        # execute & verify
        with self.assertRaises(ValueError) as _:
            self.sut.execute(data=expected, config=config)