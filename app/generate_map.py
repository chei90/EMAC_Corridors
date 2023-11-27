import numpy as np
import folium
import branca

from collections import Counter

from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

from app.sequence import SequenceBuilder
from app.gridmap import GridMap

MAX_GRADUATION_SIZE = 12

def determine_graduation(all_cells_stripped, individual_threshold):
    key_lengths = [len(value) for  value in all_cells_stripped.values()]

    occurances = dict(Counter(key_lengths))

    max_val = max(occurances.keys())
    min_val = min(occurances.keys())
    min_val = min_val if min_val >= individual_threshold else individual_threshold
    max_val = max_val if max_val > min_val else min_val

    grad_size = max_val - min_val + 1
    grad_size = grad_size if grad_size <= MAX_GRADUATION_SIZE else MAX_GRADUATION_SIZE

    #linear interpolation
    dif = max_val - min_val

    size_m_one = grad_size - 1
    increment = dif / (size_m_one if size_m_one > 0 else 1) #number of distinct colors

    return [int(min_val + x * increment) for x in range(grad_size)]

def generate_map(individual_and_data, resolution_in_m = 1000, individual_threshold = 2):
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

    graduation = determine_graduation(all_cells_stripped, individual_threshold)

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

    colormap = branca.colormap.linear.YlOrRd_09.scale(graduation[0], graduation[-1])

    if len(set(graduation)) > 1:
        colormap = colormap.to_step(index=graduation)
    colormap.caption = "Recorded individuals per cell"
    colormap.add_to(m)

    m.fit_bounds([builder.convert_back_to_deg(g.lower_left), builder.convert_back_to_deg(g.upper_right)])
    def add_to_map(polygon, i):
        coords = np.asarray(polygon.exterior.coords[:-1])
        plg = folium.Polygon(locations=coords, fill=True, color=colormap(graduation[i - 1]), fill_opacity=0.5)
        m.add_child(plg)

    for i in plg_per_label_processed.keys():
        if i == 0:
            continue

        try:
            for poly in plg_per_label_processed[i].geoms:
                if poly.geom_type != "Polygon":
                    continue

                add_to_map(poly, i)
        except AttributeError:
            add_to_map(plg_per_label_processed[i], i)
            pass

    return m, plg_per_label_processed, graduation