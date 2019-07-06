#!/bin/bash

# Requires a transitfeeds.com API key for downloading GTFS feeds
# Get an API key here: http://transitfeeds.com/api/
API_KEY="9e99e97a-f205-414e-9078-af5b2868e9fd"

# Run sample jobs for each state
for GEOID in $(cat seed.csv); do

    docker run --rm \
        -v /home/$USER/resources/graphs/:/resources/graphs/ \
        -v /home/$USER/resources/inputs/:/resources/inputs/ \
        -e BUFFER_SIZE_M=100000 \
        -e API_KEY="$API_KEY" \
        -e GEOID=$GEOID \
        snowdfs/otp-resources

done
