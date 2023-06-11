import folium
import webbrowser
import csv
from datetime import datetime
import numpy as np
from sklearn.cluster import KMeans
from rdp import rdp
from pathlib import Path

from dataEnvironment import DataEnvironment

data_path = r"D:\Download\Cathartes aura MPIAB Cuba.csv"

env = DataEnvironment(data_path)
data = {}

scale_fac = 350

print("loading data")
with open(data_path, 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    next(reader)        

    coordinates_str = [[row[env.timestamp_index], row[env.latitude_index], row[env.longitude_index], row[env.individual_index]] for row in reader]

    for ts, lat, lon, inv in coordinates_str:
        if inv not in data:
            data[inv] = []

        try:
            date = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")

            data[inv].append([date, float(lat), float(lon)])
        except ValueError:
            pass

print("reduce segments")
parsed_data = {}
for key, value in data.items():
    lat = [x[1] for x in value]
    lon = [x[2] for x in value]

    data = np.array((list(zip(lat, lon))))

    TO_METERS = 1 / 110_000
    # for i in [1 * TO_METERS, 10 * TO_METERS, 20 * TO_METERS, 40 * TO_METERS, 70 * TO_METERS, 100 * TO_METERS, 1000 * TO_METERS, 10_000 * TO_METERS]:
    #     data2 = rdp(reduction, i)
    #     print(len(data2))

    data2 = rdp(data, scale_fac * TO_METERS)
    print("Reduced from {} to {}".format(len(data), len(data2)))

    parsed_data[key] = data2

from generate_map import generate_map

print("generate map")
generate_map(parsed_data, resolution_in_m=2000, graduation=[3, 7, 12, 19, 25], print_lines=False)