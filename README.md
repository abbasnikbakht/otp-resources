## OTP Resource Downloader

This is a Docker container designed to generate the files necessary to calculate Census block or tract-level distance matrices using OpenTripPlanner. It uses counties as a unit of work, taking a county FIPS code as input and saving outputs to `/resources/graphs/$GEOID/` inside the container (where $GEOID is the FIPS code of the county). 

### Inputs
The container takes the following inputs as Docker environmental variables:

- GEOID (the five-digit, 2010 FIPS code for a U.S. county)
- TYPE (either TRACT or BLOCK, the type of origin and destinations file to return) 
- API_KEY (a transitfeeds.com API key for getting GTFS feeds)
- BUFFER_SIZE_M (the size of the county buffer, in meters)

After being run, the container will download some intermediate files and save them to the `/resources/inputs/` directory in the container. This directory can be mapped from the host or from a Docker volume to get persistent storage for the input files (so that they don't need to be downloaded every time). See `submit_jobs.sh` for a typical use case, where both the input and output directories are mounted from the host.

Inputs files saved to `/resources/inputs/` are structured in the following way (using GEOID=17031 as an example):

```
/resources/inputs/
├── buffers
│   └── 17031.geojson (buffered boundary of the $GEOID county)
├── osm
│   ├── north-america-latest.osm.pbf (Geofabrik download of the North America OSM file)
│   └── tag_extract.pbf (North American OSM file with only specific tagged ways included, see docker/misc/osm_tags.txt for a list of included tags)
└── shapefiles
    ├── blocks
    │   ├── tl_2010_17_tabblock10.dbf (TIGER block shapefile DBF containing lat/lon centroid)
    │   └── tabblock2010_17_pophu.dbf (TIGER block shapefile DBF containing block population estimate)
    └── counties
        └── tl_2010_us_county10.shp (TIGER county shapefile used to generate buffers)
```

### Outputs
Upon being run, the container generates the following outputs and saves them to `/resources/graphs/$GEOID/`:

- GEOID-destinations.csv (all tract or block locations within the buffer area)
- GEOID-origins.csv (all tracts or block locations only within the GEOID)
- GEOID.pbf (a clipped OSM PBF of all the buffered GEOID area)
- transi_system_name.zip (multiple, all GTFS feed zips of systems that lie within the buffer area)

Output files are structured in the following way (using two GEOIDs as an example):

```
/resources/graphs/
├── 06037
│   ├── 06037-destinations.csv 
│   ├── 06037-origins.csv
│   ├── 06037.pbf
│   └── la-transit.zip
└── 17031
    ├── 17031-destinations.csv
    ├── 17031-origins.csv
    ├── 17031.pbf
    ├── chicago-transit-authority.zip
    ├── janesville-transit-system.zip
    ├── metra.zip
    ├── pace.zip
    └── waukesha-metro-transit.zip

```

### Notes

Output files are also saved as a tarball to `/resources/zipped/$GEOID.tar.gz`. This output may be preferable to use when using S3 or when storing files long-term.
