This pipeline contains code to replicate the plots in:

"Driver Surge Pricing." Nikhil Garg and Hamid Nazerzadeh. Management Science, 2021. URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3390346.

If you use the code in this directory, please cite the above work.

**Data source**: https://data.world/ride-austin/ride-austin-june-6-april-13

**Usage instructions**:
1. Download data from above link (Rides_DataA.csv, Rides_DataB.csv) and put in data/rideaustin/ folder
1. Create a plots/ folder in home directory
1. Run code as outlined below for various purposes. In general, pipeline.py contains a pipeline to run the analyses and data-preprocessing. The pipeline function takes in as input a settings dictionary, with several examples in settings.py.

**To obtain a clean version of the dataset** with merged rows and errors replaced:
1. Run pipeline(settings_server_preprocessing)

**To replicate all plots in paper from scratch**:
1. Run pipeline(settings_server_2months). (warning: default settings use 55 cores, to do the matching in parallel. With this many cores, the code takes a few hours.)
1. Run pipeline(settings_plotting_2months). This code will use the output of the above command and generate the plots.


/data_preprocessing/
- **create_clean_polygons_file.py**: takes the polygon.csv from online and closes the polygons so that they define fixed areas. Also selects a subset of the polygons that have less overlap. This code is not used in the current analysis.
- **merge_locations.py**: takes the clean rides file and converts the trip origin/destination longitude/latitude locations to the polygons. This step is time-consuming. This code is not used in the current analysis.
- **create_clean_rides_file.py**: merges Rides_DataA.csv, Rides_DataB.csv, and converts time-zones, and replaces incorrect values with NaN.
