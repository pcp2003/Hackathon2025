#!/bin/bash
# Download and process OSM data for OSRM
# This script downloads Portugal map data and prepares it for OSRM

set -e

echo "🗺️  Setting up OSRM with Portugal data..."

# Create osrm-data directory if it doesn't exist
mkdir -p osrm-data
cd osrm-data

# Download Portugal OSM data (PBF format)
echo "📥 Downloading Portugal OpenStreetMap data..."
if [ ! -f "portugal-latest.osm.pbf" ]; then
    wget -q --show-progress https://download.geofabrik.de/europe/portugal-latest.osm.pbf
    echo "✓ Download complete"
else
    echo "✓ Portugal data already exists"
fi

# Process with OSRM (this requires Docker)
echo "⚙️  Processing with OSRM (using Docker)..."
docker run --rm \
    -v $(pwd):/data \
    osrm/osrm-backend:v5.27.1 \
    osrm-extract -p /opt/car.lua /data/portugal-latest.osm.pbf

docker run --rm \
    -v $(pwd):/data \
    osrm/osrm-backend:v5.27.1 \
    osrm-partition /data/portugal-latest.osrm

docker run --rm \
    -v $(pwd):/data \
    osrm/osrm-backend:v5.27.1 \
    osrm-customize /data/portugal-latest.osrm

echo "✓ OSRM data ready!"
echo ""
echo "Next steps:"
echo "1. Run: docker-compose up --build"
echo "2. OSRM will be available at: http://localhost:5000"
echo "3. Your backend will use: http://osrm:5000 (internally)"
