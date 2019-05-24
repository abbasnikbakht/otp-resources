## OTP Resource Downloader

This is a container designed to download the resources necessary to create block or tract-level distance matrices using OpenTripPlanner.

### Inputs
The container takes the following inputs as Docker environmental variables:

- GEOID (the five-digit FIPS code for a U.S. county)
- TYPE (either TRACT or BLOCK, the type of origin and destinations file to return) 
- API_KEY (a transitfeeds.com API key for getting GTFS feeds)
- BUFFER_SIZE_M (the size of the county buffer, in meters)

Inputs files are structured in the following way (using GEOID=17031 as an example):

```
/resources/inputs/
├── buffers
│   └── 17031.geojson
├── osm
│   ├── north-america-latest.osm.pbf
│   └── tag_extract.pbf
└── shapefiles
    ├── blocks
    │   ├── tl_2010_17_tabblock10.dbf
    │   └── tabblock2010_17_pophu.dbf
    └── counties
        └── tl_2010_us_county10.shp (and dependencies)
```

### Outputs
The container generates the following outputs:

- GEOID-destinations.csv (all tract or block locations within the buffer area)
- GEOID-origins.csv (all tracts or block locations only within the GEOID)
- GEOID.pbf (a clipped OSM PBF of all the buffered GEOID area)
- GTFSFEED.zip (multiple, all GTFS feed zips of systems that lie within the buffer area)

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

Both the input and output directories can be mapped to a local directory or Docker volume in order to create persistent input/output storage. An example of this setup is provided as `submit_jobs.sh`.
