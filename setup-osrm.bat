@echo off
REM Setup OSRM with Portugal data for Windows
REM This downloads and processes OpenStreetMap data for OSRM

echo.
echo 🗺️  Setting up OSRM with Portugal data...
echo.

if not exist "osrm-data" (
    mkdir osrm-data
)

cd osrm-data

if not exist "portugal-latest.osm.pbf" (
    echo 📥 Downloading Portugal OpenStreetMap data...
    echo This may take a few minutes (~500MB)...
    REM Using curl if available, otherwise wget
    curl -L --progress-bar -o portugal-latest.osm.pbf https://download.geofabrik.de/europe/portugal-latest.osm.pbf
    if %errorlevel% neq 0 (
        echo Error downloading file. Make sure you have curl installed.
        cd ..
        exit /b 1
    )
    echo ✓ Download complete
) else (
    echo ✓ Portugal data already exists
)

echo.
echo ⚙️  Processing with OSRM...
echo This may take 10-15 minutes on first run...
echo.

REM Extract
echo Step 1/3: Extracting...
docker run --rm -v "%cd%:/data" osrm/osrm-backend:v5.27.1 osrm-extract -p /opt/car.lua /data/portugal-latest.osm.pbf

REM Partition
echo Step 2/3: Partitioning...
docker run --rm -v "%cd%:/data" osrm/osrm-backend:v5.27.1 osrm-partition /data/portugal-latest.osrm

REM Customize
echo Step 3/3: Customizing...
docker run --rm -v "%cd%:/data" osrm/osrm-backend:v5.27.1 osrm-customize /data/portugal-latest.osrm

echo.
echo ✓ OSRM data ready!
echo.
echo Next steps:
echo 1. Run: docker-compose up --build
echo 2. OSRM will be available at: http://localhost:5000
echo 3. Your backend will use: http://osrm:5000 (internally)
echo.

cd ..
