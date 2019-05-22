#!/bin/bash
for GEOID in 17031; do
    docker run -it \
        -v /home/snow/resources/outputs/:/resources/outputs/ \
        -v /home/snow/resources/inputs/:/resources/inputs/ \
        -e BUFFER_SIZE_M=100000 \
        -e API_KEY=$API_KEY \
        -e TYPE=BLOCK \
        -e GEOID=$GEOID \
        otp-resources
done
