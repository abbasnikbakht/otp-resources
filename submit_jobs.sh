#!/bin/bash

API_KEY="example_key"

for GEOID in 42101; do
    docker run -it \
        -v /home/"$USER"/resources/inputs/:/resources/inputs/ \
        -v /home/"$USER"/resources/graphs/:/resources/graphs/ \
        -v /home/"$USER"/resources/zipped/:/resources/zipped/ \
        -e BUFFER_SIZE_M=100000 \
        -e API_KEY="$API_KEY" \
        -e TYPE=TRACT \
        -e GEOID="$GEOID" \
        otp-resources
done
