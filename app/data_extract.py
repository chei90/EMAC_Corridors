import numpy as np

class DataExtractor:
    """
    This class is used to extract 'relevant' (from the perspective of the algorithm) data
    from the TrajectoryCollection.
    """

    def __call__(self, trajectory_collection):
        """
        Performs extraction on passed TrajectoryCollection
        """

        for trajectory in trajectory_collection.trajectories:
            df_columns = trajectory.df.columns.values

            timestamp_key = trajectory.df.timestamp.name
            geo_key = trajectory.df.geometry.name
            individual_key = trajectory.df.individual_local_identifier.name

            ts_index = np.where(df_columns == timestamp_key)[0][0]
            geo_index = np.where(df_columns == geo_key)[0][0]
            individual_index = np.where(df_columns == individual_key)[0][0]

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
