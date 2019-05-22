#!/bin/bash
for GEOID in 17031; do
    docker run -it \
        -v /home/snow/otp-resources/outputs/:/resources/outputs/ \
        -v /home/snow/otp-resources/inputs/:/resources/inputs/ \
        -e TYPE=TRACT \
        -e GEOID=$GEOID \
        otp-resources

done
