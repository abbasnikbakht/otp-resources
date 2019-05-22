#!/bin/bash

API_KEY="sample-api-key"

for GEOID in 17031; do
    docker run -it \
        -v /home/"$USER"/resources/outputs/:/resources/outputs/ \
        -v /home/"$USER"/resources/inputs/:/resources/inputs/ \
        -e BUFFER_SIZE_M=100000 \
        -e API_KEY="$API_KEY" \
        -e TYPE=BLOCK \
        -e GEOID="$GEOID" \
        otp-resources
done
