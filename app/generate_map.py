import numpy as np
from app.sequence import SequenceBuilder
from app.gridmap import GridMap

def generate_map(individual_and_data, resolution_in_m = 1000, graduation = [2, 5, 10, 20, 30], print_lines = False, print_grid = False):
    all_cells_stripped = {}

    builder = SequenceBuilder(resolution_in_m)
    for individual, data in individual_and_data.items():
        for i in range(len(data) - 1):

            start = data[i]
            stop = data[i + 1]

            # print("{}: {}/{}".format(individual, i, length))

            seq = builder.create(start, stop)
            res = set(seq.calculate_cells())

            for r in res:
                if r not in all_cells_stripped:
                    all_cells_stripped[r] = set()

                all_cells_stripped[r].add(individual)

    black = "black"
    darkgray = "gray" # gray is actually darker than darkgray :)
    midgray = "darkgray"
    lightgray = "lightgray"
    white = "white"

    colors_ordered = [white, lightgray, midgray, darkgray, black]


    ordering = \
    {
        black: [],
        darkgray: [],
        midgray: [],
        lightgray: [],
        white: []
    }

    # Skip - white- lg- mg-dg- blk
    # graduation = [5, 10, 17, 26, 38]

    print("Building grid")
    for cell in all_cells_stripped:
        bounds = builder.get_edges_from_cell(cell)

        num_individuals = len(all_cells_stripped[cell])

        skip = graduation[0]
        if num_individuals < skip:
            continue

        color = white
        if num_individuals > graduation[1]:
            color = lightgray
        if num_individuals > graduation[2]:
            color = midgray
        if num_individuals > graduation[3]:
            color = darkgray
        if num_individuals > graduation[4]:
            color = black

        ordering[color].append(bounds)

    key_order = [white, lightgray, midgray, darkgray, black]

    g = GridMap(all_cells_stripped)
    data = g.fill(graduation)

    from scipy.spatial import ConvexHull

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

    from shapely.geometry import Polygon

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

    print("Processing geometries - difference")
    keys = sorted(plg_per_label_processed.keys())
    for i in range(1, len(keys) + 1):
        
        # starting with 1 and counting backwards...
        my_index = keys[-i]

        for j in range(0, len(keys) - i):
            current = keys[j]
            plg_per_label_processed[current] = plg_per_label_processed[current].difference(plg_per_label_processed[my_index])


    for i in plg_per_label_processed.keys():
        if i == 0:
            continue

        try:
            for poly in plg_per_label_processed[i].geoms:
                if poly.geom_type != "Polygon":
                    continue

                # add_to_map(poly)
        except AttributeError:
            # add_to_map(plg_per_label_processed[i])
            pass



