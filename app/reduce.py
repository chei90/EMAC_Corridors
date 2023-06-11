from typing import Dict, Tuple
import numpy as np
from rdp import rdp

class Reduce:

    def __init__(self, rdp_scale: int = 350):
        self.__rdp_resolution = rdp_scale

    def __call__(self, data: Dict[int, Tuple[np.datetime64, float, float]], rdp_resolution: int = 350) -> Dict[int, Tuple[np.datetime64, float, float]]:
        
        parsed_data = {}
        for key, value in data:
            lat = [x[2] for x in value]
            lon = [x[1] for x in value]

            data = np.array((list(zip(lat, lon))))

            TO_METERS = 1 / 110_000
            # for i in [1 * TO_METERS, 10 * TO_METERS, 20 * TO_METERS, 40 * TO_METERS, 70 * TO_METERS, 100 * TO_METERS, 1000 * TO_METERS, 10_000 * TO_METERS]:
            #     data2 = rdp(reduction, i)
            #     print(len(data2))

            print("Starting reduction of {}".format(len(data)))
            data2 = rdp(data, self.__rdp_resolution * TO_METERS)
            print("Reduced from {} to {}".format(len(data), len(data2)))

            parsed_data[key] = data2

        return parsed_data