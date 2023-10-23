#!/bin/bash

# Get a list of all service names defined in the Docker Compose file
SERVICES=$(docker compose config --services)

mkdir -p export/

# Loop through each service and export it as a tar archive
for SERVICE in $SERVICES; do
    # Get the container ID of the running service
    CONTAINER_ID=$(docker compose ps -q $SERVICE)

    echo "$SERVICE: $CONTAINER_ID"
    if [ -n "$CONTAINER_ID" ]; then
        # Export the container as a tar archive
        docker export $CONTAINER_ID > export/${SERVICE}_exported.tar
        echo "Container $SERVICE exported successfully."
    else
        echo "Container $SERVICE is not running or does not exist."
    fi
done