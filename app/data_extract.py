import numpy as np

class DataExtractor:

    def __init__(self, timestamp_key = "timestamps", 
                 individual_key = "individual.local.identifier",
                 geometry_key = "geometry") -> None:
        
        self.__timestamp_key = timestamp_key
        self.__individual_key = individual_key
        self.__geometry_key = geometry_key


    def __call__(self, trajectory_collection):


        for trajectory in trajectory_collection.trajectories:
            df_columns = trajectory.df.columns.values

            ts_index = np.where(df_columns == self.__timestamp_key)[0][0]
            geo_index = np.where(df_columns == self.__geometry_key)[0][0]
            individual_index = np.where(df_columns == self.__individual_key)[0][0]

            first_id = None
            data = []
            for row in trajectory.df.values:

                id = row[individual_index]
                ts = row[ts_index]
                geo = row[geo_index]

                if first_id is None:
                    first_id = id

                if first_id != id:
                    raise ValueError("Multiple individual IDs in one trajectory!")
                
                data.append([ts, geo.x, geo.y])

            yield (first_id, data)
