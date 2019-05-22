FROM python:3.6-slim-stretch

ADD misc/ /tmp/

RUN apt-get update && \
    apt-get install -y \
        zip wget git \
        build-essential \
        make \
        gcc \
        locales \
        libgdal20 libgdal-dev \
        rapidjson-dev libboost-program-options-dev \
        libgeos++-dev libsparsehash-dev \
        libbz2-dev zlib1g-dev libexpat1-dev cmake && \
    \
    echo "===> Installing protozero" && \
    git clone https://github.com/mapbox/protozero && \
    cd protozero && mkdir build && cd build && \
    cmake .. && make && make install && \
    cd ../.. && rm -rf protozero && \
    \
    echo "===> Installing osmium" && \
    git clone https://github.com/osmcode/libosmium && \
    cd libosmium && mkdir build && cd build && \
    cmake .. && make && make install && \
    cd ../.. && rm -rf libosmium && \
    \
    echo "===> Installing osmium-tool" && \
    git clone https://github.com/osmcode/osmium-tool && \
    cd osmium-tool && mkdir build && cd build && \
    cmake .. && make && make install && \
    cd ../.. && rm -rf osmium-tool && \
    \
    echo "===> Install python libraries" && \
    python -m pip install numpy cython --no-binary numpy,cython && \
    python -m pip install \
        "rasterio>=1.0a12" fiona shapely \
        --pre --no-binary rasterio,fiona,shapely && \
    python -m pip install -r /tmp/requirements.txt && \
    python -m pip uninstall -y cython && \
    \
    echo "===> Installing libspatialindex" && \
    git clone https://github.com/libspatialindex/libspatialindex && \
    cd libspatialindex && cmake . && make && make install && \
    easy_install Rtree && \
    cd .. && rm -r libspatialindex && \
    \
    echo "===> Cleaning up" && \
    rm -r /root/.cache/pip && \
    apt-get remove -y --purge libgdal-dev make gcc git build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* 

RUN dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

RUN mkdir /resources/ && \
    mkdir /resources/scripts &&\
    mkdir /resources/outputs/ && \
    mkdir /resources/inputs/ && \
    mkdir /resources/inputs/osm && \
    mkdir /resources/inputs/buffers && \
    mkdir /resources/inputs/shapefiles && \
    mkdir /resources/inputs/shapefiles/blocks && \
    mkdir /resources/inputs/shapefiles/counties 

ENV LC_ALL C.UTF-8
ADD scripts/ /resources/scripts/
RUN chmod +x /resources/scripts/01_get_geoid.sh

CMD ["/bin/bash" "-c" "/resources/scripts/01_get_geoid.sh"]


