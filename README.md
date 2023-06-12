# Movement Corridor Detection

MoveApps

Github repository: https://github.com/chei90/EMAC_Corridors

## Description

This app is about detecting corridors of animal movement. The current output of this app is a html file (containing a map, can be opened with browser) that highlights areas where more individuals have traversed through. The darker the color, the more individuals were recorded.

### EuroDeer Roe deer in Italy 2005-2008
![EuroDeer](documentation/euro_deer_20m_res.jpg)

### North Sea population tracks of greater white-fronted geese 2014-2017 (data from Klzsch et al. 2019)
![White-fronted geese](documentation/geese.jpg)

## Documentation

1. The input data is stripped from all unwanted data. Only the individual id, the timestamp and position are kept.
2. The trajectories are simplified by using [Ramer-Douglas-Peucker-Algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm). The magnitude of simplification can be controlled via the *Rdp Epsilon* parameter. As described in the Settings section.
3. The trajectories are 

### Input data

The app expects a TrajectoryCollection whose GeoDataFrames contain the following columns: 

* **timestamps** - column containing the time when the data point was recorded
* **individual.local.identifier** - column containing the distinct individual id
* **geometry** - point geometry (lon, lat), the gps/surface position where the data was recorded

### Output data
This app produces multiple polygons that denote the different passage corridors. Since TrajectoryCollection doesn't support polygons, the data has to be provided as artifact (downloadable content). See below. 

In consequence: the output data of this app is not intended to be processed further. The app outputs the input data.

### Artifacts

* **corridors_map.html** - Can be opened with the browser. Contains an OpenStreetmap with the computation results as overlays. 
* **Shapefile** - To use the resulting data in further computations a shapefile as artifact is planned, but not yet implemented.

### Settings 
All settings values are positive integers, so negative values are not allowed.

* **Rdp Epsilon** - The Ramer-Douglas-Peucker-Algorithm is used to reduce the trajectories point count, hence improving the computation time. Greater values will reduce the point count per trajectory, smaller values will preserve more points. Think of it like, remove every point from the trajectory that is closer to a given start/end segment than N meters.
* **Grid resolution** - The resolution of the raster (in meters) that is used to bin different individuals traversing map segments. Smaller values will make the result more fine grained, but will probably the avg amount of captured individuals per raster cell (its smaller now). Result of very small values (e.g. 50 meters) will look more like the input trajectories. Reducing the grid size will increase computation time.
* **Graduation white** - The minimum number of captured individuals per grid cell to appear as white polygon on the map. Grid cells with an individual count lower than this number will not appear. This value has to be lower than, or equal to the graduation light gray value. 
* **Graduation light gray** - The minimum number of captured individuals per grid cell to appear as light gray polygon on the map. Grid cells with an individual count lower than this number fall in the previous graduation. This value has to be lower than, or equal to the graduation gray value and larger than or equal to the graduation white value.
* **Graduation gray** - The minimum number of captured individuals per grid cell to appear as gray polygon on the map. Grid cells with an individual count lower than this number fall in the previous graduation. This value has to be lower than, or equal to the graduation dark gray value and larger than or equal to the graduation light gray value.
* **Graduation dark gray** - The minimum number of captured individuals per grid cell to appear as dark gray polygon on the map. Grid cells with an individual count lower than this number fall in the previous graduation. This value has to be lower than, or equal to the graduation black value and larger than or equal to the graduation gray value.
* **Graduation black** - The minimum number of captured individuals per grid cell to appear as black polygon on the map. Grid cells with an individual count lower than this number fall in the previous graduation. This value has to be larger than or equal to the graduation dark gray value.

### Null or error handling

If the graduation criteria is not met, an Exception will be thrown:
> GraduationWhite <= GraduationLightGray <= GraduationGray <= GraduationDarkGray <= GraduationBlack