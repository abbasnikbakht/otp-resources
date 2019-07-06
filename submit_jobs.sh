#!/bin/bash

###### SETUP ######

# Set working directories
GRAPHS_DIR=/home/$USER/resources/graphs/  # save pbf, gtfs, and location files
INPUTS_DIR=/home/$USER/resources/inputs/  # save shapefiles, raw osm

# Requires a transitfeeds.com API key for downloading GTFS feeds
# Get an API key here: http://transitfeeds.com/api/
API_KEY="9e99e97a-f205-414e-9078-af5b2868e9fd"  # transitfeeds.com API key
BUFFER_SIZE_M=100000                            # buffer around county (meters)
MAX_CONTAINERS=8                               # max containers to run simul.


###### SUBMIT JOBS ######

# Create a filename for remaining jobs
remaining_file=/tmp/RESOURCE-remaining.txt

# Get jobs remaining by comparing full county list to dirs in graphs dir
# Write remaining jobs to random $remaining_file file
comm -13 \
    <(ls $GRAPHS_DIR | sort) \
    <(cat counties.csv | sort) \
    > $remaining_file

echo "There are $(cat $remaining_file | wc -l) counties remaining"

# While there are less than N containers running, spin up more
while [ $(cat $remaining_file | wc -l) ]; do
    while [ $(docker ps | wc -l) -lt $MAX_CONTAINERS ]; do

    # Get last line of $remaining_file file
    GEOID=$(awk '/./{line=$0} END{print line}' $remaining_file)
    echo "Now running GEOID: $GEOID"

    # Run job
    docker run -d --rm -it \
        -v $GRAPHS_DIR:/resources/graphs/ \
        -v $INPUTS_DIR:/resources/inputs/ \
        -e BUFFER_SIZE_M=$BUFFER_SIZE_M \
        -e API_KEY="$API_KEY" \
        -e GEOID="$GEOID" \
        snowdfs/otp-resources

    # Remove last line of $remaining_file file
    sed -i '$ d' $remaining_file

    done
done
