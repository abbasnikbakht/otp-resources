#!/bin/bash
for GEOID in 17031; do
    docker run -it \
        -v /home/snow/resources/outputs/:/resources/outputs/ \
        -v /home/snow/resources/inputs/:/resources/inputs/ \
        -v /home/snow/otp-resources/docker/scripts/:/tmp/scripts/ \
        -e TYPE=BLOCK \
        -e GEOID=$GEOID \
        otp-resources /bin/bash

done
