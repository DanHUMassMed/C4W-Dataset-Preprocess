#!/bin/bash
set -e

CONTAINER_NAME="nominatim"

# Stop container if it exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Removing existing container: ${CONTAINER_NAME}"
    docker rm -f ${CONTAINER_NAME}
fi

# Run fresh container
docker run -it \
  --shm-size=1g \
  -v ./data:/data \
  -e PBF_PATH=/data/massachusetts-latest.osm.pbf \
  -p 8080:8080 \
  --name ${CONTAINER_NAME} \
  mediagis/nominatim:5.2