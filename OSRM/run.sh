#!/bin/bash
docker run -it \
--shm-size=1g \
-v ./data:/data \
-e PBF_PATH=/data/massachusetts-latest.osm.pbf \
-p 8080:8080 \
--name nominatim \
mediagis/nominatim:5.2

