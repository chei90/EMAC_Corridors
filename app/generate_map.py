import numpy as np
import folium

from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

from app.sequence import SequenceBuilder
from app.gridmap import GridMap

def determine_graduation(all_cells_stripped):
    key_lengths = [len(value) for  value in all_cells_stripped.values()]

    from collections import Counter
    occurances = dict(Counter(key_lengths))

    max_val = int(max(occurances.keys()) * 0.9)
    min_val = min(occurances.keys())

    #linear interpolation
    dif = max_val - min_val
    increment = dif / (5 - 1) #number of distinct colors

    return [int(min_val + x * increment) for x in range(5)]

def generate_map(individual_and_data, resolution_in_m = 1000, graduation = [2, 5, 10, 20, 30]):
    """
    The do it all function

    :param individual_and_data: A map that contains the trajectory for every individual
    :param resolution_in_m: The resolution of the raster in meters
    :param graduation: The borders of each bin:
        [2, 5, 10, 20, 30] means 
            * discard every cell that has fewer than 2 individuals
            * color every cell white that has between [2, 5[ individuals
            * color every cell light gray that has between [5, 10[ individuals
            * color every cell gray that has between [10, 20[ individuals
            * color every cell dark gray that has between [20, 30[ individuals
            * color every cell black that has between [30, inf[ individuals
    """
    
    #Trace all cells along each trajectory line segment    
    all_cells_stripped = {}
    builder = SequenceBuilder(resolution_in_m)
    for individual, data in individual_and_data.items():
        for i in range(len(data) - 1):

            start = data[i]
            stop = data[i + 1]

            seq = builder.create(start, stop)
            res = set(seq.calculate_cells())

            for r in res:
                if r not in all_cells_stripped:
                    all_cells_stripped[r] = set()

                all_cells_stripped[r].add(individual)

    graduation = determine_graduation(all_cells_stripped)

    """
     Skip - white- lg- mg-dg- blk
     graduation = [5, 10, 17, 26, 38]

     would mean, discard every cell that has less than 5 individuals passing through it, 
     color every cell that has more than or equal to 26 individuals, but less than 38 
     passing through it, black
    """
    black = "black"
    darkgray = "gray" # gray is actually darker than darkgray :)
    midgray = "darkgray"
    lightgray = "lightgray"
    white = "white"
    colors_ordered = [white, lightgray, midgray, darkgray, black]

    # Create a raster 
    g = GridMap(all_cells_stripped)
    data = g.fill(graduation)

    # compute the convex hull of every rastered polygon
    print("Building hull")
    plg_per_label = {}
    for i, (label, plg) in enumerate(g.generate_polygons(data)):
        pts = []
        for point in plg:
            corners = builder.get_edges_from_cell(point)
            for corner in corners:
               pts.append(corner)

        transformed_pts = [corner for point in plg for corner in builder.get_edges_from_cell(point)]
        ch = ConvexHull(transformed_pts)

        hull = []

        for vertex in ch.vertices:
            hull.append(transformed_pts[vertex])

        if label not in plg_per_label:
            plg_per_label[label] = []

        plg_per_label[label].append(hull)

    
    # unify all polygons as due to the convex hull algorithm there may be polygons 
    # of identical label nested inside other polygons with the same label
    print("Processing geometries - union")
    plg_per_label_processed = {}
    for i in plg_per_label.keys():
        if i == 0:
            continue
        
        res = None
        for plg in plg_per_label[i]:
            if res is None:
                res = Polygon(plg)
            else:
                res = res.union(Polygon(plg))

        plg_per_label_processed[i] = res

    # calculate the difference of the higher labeled polygons
    # basically, if a black polygon is overlapping with a dark gray one,
    # the dark gray portion that is overlapped by black gets cut out
    print("Processing geometries - difference")
    keys = sorted(plg_per_label_processed.keys())
    for i in range(1, len(keys) + 1):
        
        # starting with 1 and counting backwards...
        my_index = keys[-i]

        for j in range(0, len(keys) - i):
            current = keys[j]
            plg_per_label_processed[current] = plg_per_label_processed[current].difference(plg_per_label_processed[my_index])

    # generate the map
    m = folium.Map(start=[0,0])
    m.fit_bounds([builder.convert_back_to_deg(g.lower_left), builder.convert_back_to_deg(g.upper_right)])
    def add_to_map(polygon):
        coords = np.asarray(polygon.exterior.coords[:-1])
        plg = folium.Polygon(locations=coords, fill=True, color=colors_ordered[i - 1], fill_opacity=0.5)
        m.add_child(plg)

    for i in plg_per_label_processed.keys():
        if i == 0:
            continue

        try:
            for poly in plg_per_label_processed[i].geoms:
                if poly.geom_type != "Polygon":
                    continue

                add_to_map(poly)
        except AttributeError:
            add_to_map(plg_per_label_processed[i])
            pass

    return m, plg_per_label_processed