#!/bin/bash

# Requires a transitfeeds.com API key for downloading GTFS feeds
# Get an API key here: http://transitfeeds.com/api/
API_KEY=""

# Run sample jobs for each state
for GEOID in $(cat cities.csv | cut -d, -f1); do

    docker run --rm \
        -v /home/$USER/resources/graphs/:/resources/graphs/ \
        -v /home/$USER/resources/inputs/:/resources/inputs/ \
        -e BUFFER_SIZE_M=100000 \
        -e API_KEY="$API_KEY" \
        -e GEOID=$GEOID \
        snowdfs/otp-resources

done
