#!/bin/bash

# Requires a transitfeeds.com API key for downloading GTFS feeds
# Get an API key here: http://transitfeeds.com/api/
API_KEY="example_key"

for GEOID in $(cat counties.csv); do

    docker run --rm -it \
        -v /home/"$USER"/blocks/resources/graphs/:/resources/graphs/ \
        -v /home/"$USER"/blocks/resources/inputs/:/resources/inputs/ \
        -e BUFFER_SIZE_M=100000 \
        -e API_KEY="$API_KEY" \
        -e GEOID="$GEOID" \
        snowdfs/otp-resources

done
