from typing import Dict, Tuple
import numpy as np
from rdp import rdp

class Reduce:
    """
    Class performs RDP-Algorithm (segmentreduction on line) on trajectories
    """
    def __init__(self, rdp_scale: int = 350):
        """
        Creates an instance

        :param rdp_scale: The epsilon parameter of RDP algorithm, higher values will lead to more segments being 
                            discarded, smaller values will leave more segments in place 
        """
        self.__rdp_resolution = rdp_scale

    def __call__(self, data: Dict[int, Tuple[np.datetime64, float, float]]) -> Dict[int, Tuple[np.datetime64, float, float]]:
        """
        Performs the RDP algorithm on  data

        :param data: The input data for the algorithm
        """
        parsed_data = {}
        for key, value in data:
            lat = [x[2] for x in value]
            lon = [x[1] for x in value]

            data = np.array((list(zip(lat, lon))))

            TO_METERS = 1 / 110_000
            data2 = rdp(data, self.__rdp_resolution * TO_METERS)
            print("Reduced from {} to {}".format(len(data), len(data2)))

            parsed_data[key] = data2

        return parsed_data