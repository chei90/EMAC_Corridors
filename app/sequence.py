import math

class SequenceBuilder:
    DEG_TO_KM = 111.1
    DEG_TO_M = DEG_TO_KM * 1000

    def __init__(self, resolution_in_m) -> None:
        self.__resolution_in_ms = SequenceBuilder.DEG_TO_M / resolution_in_m

    def create(self, start, stop):
        return Sequence(self.__resolution_in_ms, start, stop)
    
    def convert_back_to_deg(self, pt):
        return [pt[0] / self.__resolution_in_ms, pt[1] / self.__resolution_in_ms]
    
    def get_edges_from_cell(self, pt):
        left_bottom = pt

        left_top = [x for x in pt]
        left_top[1] += 1

        top_right = [x for x in pt]
        top_right[0] += 1
        top_right[1] += 1

        bottom_right = [x for x in pt]
        bottom_right[0] += 1

        return [self.convert_back_to_deg(left_bottom), 
                self.convert_back_to_deg(left_top),
                self.convert_back_to_deg(top_right), 
                self.convert_back_to_deg(bottom_right)]
class Sequence:

    def __init__(self, resolution, start, stop) -> None:
        self.__start = start
        self.__stop = stop
        self.__resolution = resolution
        self.__scaled_start = [self.__start[0] * self.__resolution, self.__start[1] * self.__resolution]
        self.__scaled_end = [self.__stop[0] * self.__resolution, self.__stop[1] * self.__resolution]

    @staticmethod
    def convert_to_cell(pt):
        cell_x = int(pt[0])
        cell_y = int(pt[1])

        if pt[0] < 0:
            cell_x -= 1

        if pt[1] < 0:
            cell_y -= 1

        return cell_x, cell_y

    def calculate_cells(self):
        cell_x, cell_y = Sequence.convert_to_cell(self.__scaled_start)

        yield (cell_x, cell_y)

        cell_x_end, cell_y_end = Sequence.convert_to_cell(self.__scaled_end)
    	
        current_start = self.__scaled_start
        while cell_x_end != cell_x or cell_y_end != cell_y:
            
            reached_break = False

            for id, (edge_start, edge_end) in enumerate(Sequence.get_edges(cell_x, cell_y)):
                intersect, pt = Sequence.intersect(current_start,  self.__scaled_end, edge_start, edge_end)

                # dont intersect the old intersection edge again
                if math.isclose(pt[0], current_start[0], rel_tol=1e-15) and math.isclose(pt[1], current_start[1]):
                    continue

                if intersect:
                    cell_x, cell_y = Sequence.convert_to_cell(pt)
                    current_start = pt

                    if id == 0 and cell_x >= 0:
                        cell_x -= 1

                    if id == 1 and cell_y < 0:
                        cell_y += 1

                    if id == 2 and cell_y >= 0:
                        cell_y -= 1

                    if id == 3 and cell_x < 0:
                        cell_x += 1

                    yield (cell_x, cell_y)

                    reached_break = True
                    break
            
            if not reached_break:
                print("No intersection found! Skipping")
                break


    @staticmethod
    def get_edges(cell_x, cell_y):
        def increment(val):
            if True:
                return val + 1
            else:
                return val - 1  
               
        #left bottom to left top
        yield [[cell_x, cell_y], [cell_x, increment(cell_y)]]
        #left top to right top
        yield [[cell_x, increment(cell_y)], [increment(cell_x), increment(cell_y)]]
        #left bottom to right bottom
        yield [[cell_x, cell_y], [increment(cell_x), cell_y]]
        #right bottom to right top
        yield [[increment(cell_x), cell_y], [increment(cell_x), increment(cell_y)]]


    @staticmethod
    def intersect(a_start, a_end, b_start, b_end):

        x1x2 = a_start[0] - a_end[0]
        y1y2 = a_start[1] - a_end[1]

        x1x3 = a_start[0] - b_start[0]
        y1y3 = a_start[1] - b_start[1]

        x3x4 = b_start[0] - b_end[0]
        y3y4 = b_start[1] - b_end[1]

        d = x1x2 * y3y4 - y1y2 * x3x4

        if d == 0:
            return (False, [0,0])
        
        t = (x1x3 * y3y4 - y1y3 * x3x4) / d
        u = -(x1x2 * y1y3 - y1y2 * x1x3) / d

        if t < 0 or t > 1:
            return (False, [0,0])
        
        if u >= 0 and u <= 1:
            return (True, [
                    b_start[0] + u * (b_end[0] - b_start[0]),
                    b_start[1] + u * (b_end[1] - b_start[1])
                ])
        
        return (False, [0,0])