#!/bin/bash

# Warning about overwriting files
echo "=========================================="
echo "WARNING: This command will OVERWRITE existing files!"
echo "It does NOT merge data with existing content."
echo ""
echo "Any translations, extra added items in the gamedata, or custom"
echo "modifications in JSON files will be LOST unless you merge them manually."
echo "=========================================="
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 1
fi
echo ""

# Build the Docker image
echo "Building assets-build image..."
docker build -t assets-build ./assets

# Find networks containing "nitro"
echo "Finding Docker networks containing 'nitro'..."
NITRO_NETWORKS=$(docker network ls --format "{{.Name}}" | grep -i nitro)

if [ -z "$NITRO_NETWORKS" ]; then
    echo "Warning: No networks containing 'nitro' found"
    NETWORK_ARGS=""
else
    echo "Found networks: $NITRO_NETWORKS"
    # Create network arguments for each found network
    NETWORK_ARGS=""
    for network in $NITRO_NETWORKS; do
        NETWORK_ARGS="$NETWORK_ARGS --network $network"
    done
fi

# Run the container
echo "Running assets-build container..."
MSYS_NO_PATHCONV=1 docker run --rm \
    -v "$(pwd)/assets/configuration.json:/app/configuration.json" \
    -v "$(pwd)/assets/assets:/app/assets" \
    $NETWORK_ARGS \
    assets-build "$@"

echo "Container execution completed"

echo ""
echo "=========================================="
echo "NEXT STEPS: Merge data and update translations"
echo "=========================================="
echo ""
echo "1. Merge items and update badges:"
echo "   cd assets/"
echo "   python ./merge_items.py"
echo "   python ./badge_name_update.py -f"
echo ""
echo "2. Update translations:"
echo "   cd ./assets/translation && \\"
echo "   python FurnitureDataTranslator.py && \\"
echo "   python SQLGenerator.py && \\"
echo "   python external_text.py --domain <TLD>"
echo ""
echo "=========================================="
