class GridMap:

    def __init__(self, cells) -> None:

        x_vals = [x[1] for x in cells.keys()]
        y_vals = [x[0] for x in cells.keys()]

        min_x = min(x_vals)
        max_x = max(x_vals) + 1

        min_y = min(y_vals)
        max_y = max(y_vals) + 1

        self.__min_x = min_x
        self.__min_y = min_y
        self.__max_x = max_x
        self.__max_y = max_y

        self.__width = max_x - min_x
        self.__height = max_y - min_y

        self.__input = cells

    @property
    def height(self):
        return self.__height

    @property
    def width(self):
        return self.__width

    @staticmethod
    def get_bin(value, bins):
        for i in range(len(bins)):

            if value < bins[i]:
                return i
            
        return len(bins)

    def fill(self, bins):
        
        data = [-1] * (self.__width * self.__height)
        for cell in self.__input.keys():

            x_id = cell[1] - self.__min_x
            y_id = cell[0] - self.__min_y
            # y_id = self.__height - y_id - 1

            data_id = x_id + (y_id * self.__width)
            data[data_id] = GridMap.get_bin(len(self.__input[cell]), bins)

        return data
    
    def generate_polygons(self, data):
        def index(x, y):
            return x + y * self.__width

        already_used = [False for x in range(len(data))]

        height = len(data) // self.__width
        height_m_one = height - 1
        for i in range(len(data)):

            if already_used[i]:
                continue

            my_val = data[i]
            if my_val == -1:
                continue

            queue = [i]
            polygon_points = []

            while len(queue) > 0:

                current = queue.pop()
                if already_used[current]:
                    continue

                cur_val = data[current]

                if cur_val != my_val:
                    continue

                polygon_points.append(current)
                already_used[current] = True

                x_id = current % self.__width
                y_id = current // self.__width

                if x_id > 0:
                    # we can check all to the left

                    x = x_id - 1
                    queue.append(index(x, y_id))

                    if y_id < height_m_one:
                        # we can go up
                        y = y_id + 1
                        queue.append(index(x, y))

                    if y_id > 0:
                        # we can go down
                        y = y_id - 1
                        queue.append(index(x, y))

                if x_id < self.__width - 1:
                    # we can check all to the right

                    x = x_id + 1
                    queue.append(index(x, y_id))

                    if y_id < height_m_one:
                        # we can go up
                        y = y_id + 1
                        queue.append(index(x, y))

                    if y_id > 0:
                        # we can go down
                        y = y_id - 1
                        queue.append(index(x, y))                    

                if y_id < height_m_one:
                    # we can go up
                    y = y_id + 1
                    queue.append(index(x_id, y))

                if y_id > 0:
                    # we can go down
                    y = y_id - 1
                    queue.append(index(x_id, y))

            if len(polygon_points) > 0:
                yield my_val, self.convert_polygon(polygon_points)


    def convert_polygon(self, points):

        res = []
        for pt in points:

            pt_x = pt % self.__width
            pt_y = pt // self.__width

            res.append([pt_y + self.__min_y, pt_x + self.__min_x])

        return res

