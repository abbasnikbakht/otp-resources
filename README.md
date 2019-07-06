## OTP Resource Downloader

This is a Docker container designed to generate the files necessary to calculate Census block or tract-level distance matrices using OpenTripPlanner. It uses counties as a unit of work, taking a county FIPS code as input and saving outputs to `/resources/graphs/$GEOID/` inside the container (where $GEOID is the FIPS code of the county). 

### Inputs
The container takes the following inputs as Docker environmental variables, all arguments are required:

- GEOID (the five-digit, 2010 FIPS code for a U.S. county)
- API_KEY (a transitfeeds.com API key for getting GTFS feeds)
- BUFFER_SIZE_M (the size of the county buffer, in meters)

After being run, the container will download some intermediate files and save them to the `/resources/inputs/` directory in the container. This directory can be mapped from the host or from a Docker volume to get persistent storage for the input files (so that they don't need to be downloaded every time). See `submit_jobs_simple.sh` for a typical use case, where both the input and output directories are mounted from the host.

Inputs files saved to `/resources/inputs/` are structured in the following way (using GEOID=17031 as an example):

```
/resources/inputs/
├── buffers
│   └── 17031.geojson (buffered boundary of the $GEOID county)
├── osm
│   ├── north-america-latest.osm.pbf (Geofabrik download of the North America OSM file)
│   ├── tag_extract_all.pbf (OSM file with all tags for highway, cycleway, sidewalk, and busway; used for TRANSIT and WALK modes)
│   └── tag_extract_car.pbf (OSM file with highway and only specific tags, see misc/osm_tags_car.txt for list; used for CAR mode)
└── shapefiles
    ├── blocks
    │   ├── tl_2010_17_tabblock10.dbf (TIGER block shapefile DBF containing lat/lon centroid)
    │   └── tabblock2010_17_pophu.dbf (TIGER block shapefile DBF containing block population estimate)
    └── counties
        └── tl_2010_us_county10.shp (TIGER county shapefile used to generate buffers)
```

### Outputs
Upon being run, the container generates the following outputs and saves them to `/resources/graphs/$GEOID/`:

- GEOID-destinations-BLOCK.csv (block locations within the buffered county area)
- GEOID-origins-BLOCK.csv (block locations only within the GEOID)
- GEOID-destinations-TRACT.csv (tract locations within the buffered county area)
- GEOID-origins-TRACT.csv (tract locations only within the GEOID)
- osm/GEOID-car.pbf (a clipped OSM PBF of the buffered GEOID area with only car-passable OSM ways)
- osm/GEOID-all.pbf (a clipped OSM PBF of the buffered GEOID area with all OSM ways)
- transit_system_name.zip (multiple, all GTFS feed zips of systems that lie within the buffer area)

Output files are structured in the following way (using two GEOIDs as an example):

```
/resources/graphs/
├── 06037
│   ├── 06037-destinations.csv 
│   ├── 06037-origins.csv
│   ├── osm
│   │   ├── 06037-all.pbf
│   │   └── 06037-car.pbf
│   └── la-transit.zip
└── 17031
    ├── 17031-destinations.csv
    ├── 17031-origins.csv
    ├── osm
    │   ├── 17031-all.pbf
    │   └── 17031-car.pbf 
    ├── chicago-transit-authority.zip
    ├── janesville-transit-system.zip
    ├── metra.zip
    ├── pace.zip
    └── waukesha-metro-transit.zip

```

### Running Without Root

If you need to run this container but don't have the root privileges necessary to install Docker, try using [udocker](https://github.com/indigo-dc/udocker). There are only two changes required when using udocker:

1. Alias `docker` to the udocker executable
2. Manually create the directories that you plan to store resources in (udocker seems to have trouble creating new directories on the host)
