# Commit: Migrate to OpenStreetMap OSRM servers with profile differentiation

**Date:** 2025-11-07  
**Author:** Development Team

## Changes Made

- **Migrated from public OSRM to OpenStreetMap's profile-specific OSRM servers**
  - Previously used `router.project-osrm.org` which returned identical routes for foot/car/bike profiles
  - Now uses profile-specific servers that properly differentiate based on transportation mode:
    - `https://routing.openstreetmap.de/routed-foot/...` - Pedestrian routes (slower)
    - `https://routing.openstreetmap.de/routed-bike/...` - Bicycle routes (medium speed)
    - `https://routing.openstreetmap.de/routed-car/...` - Car routes (fastest)

- **Updated routing service configuration**
  - Added `OSRM_SERVERS` dictionary with pre-processed server endpoints
  - Changed URL construction to use profile-specific base URLs
  - Removed dependency on `OSRM_BASE_URL` environment variable

- **Updated tests to validate profile differentiation**
  - Modified `test_routing_profiles.py` to use new server endpoints
  - Tests now confirm different durations for each profile (foot ~5x slower than car)

- **Simplified Docker configuration**
  - Removed custom OSRM setup scripts (no longer needed)
  - Updated docker-compose.yml to use public API (no local container required)

## Files Modified

- `backend/services/routing.py` - Updated OSRM server configuration
- `backend/tests/test_routing_profiles.py` - Updated test URLs and logic
- `docker-compose.yml` - Removed OSRM local service configuration

## Tests Added/Updated

- `tests/test_routing_profiles.py` - Now passes all tests:
  - ✓ Foot profile returns valid data
  - ✓ Bike profile returns valid data
  - ✓ Car profile returns valid data
  - ✓ Different profiles return different durations (FOOT: 98.8s, BIKE: 45.1s, CAR: 20.3s)
  - ✓ Car is faster than foot (4.9x speed ratio)

## How to Test

1. **Verify API responsiveness:**
   ```bash
   curl "https://routing.openstreetmap.de/routed-foot/route/v1/foot/-8.732629,37.086282;-8.731954,37.086547?overview=false&steps=true"
   ```

2. **Run profile differentiation tests:**
   ```bash
   cd backend
   python -m pytest tests/test_routing_profiles.py -v
   ```

3. **Manual test in Postman:**
   - Use endpoint: `POST /api/route`
   - Parameters: `origin_lat=37.086282, origin_lon=-8.732629, dest_lat=37.086547, dest_lon=-8.731954`
   - Response should show pedestrian-friendly instructions with realistic times

4. **Compare different profiles (optional):**
   - Run `python ../test_osrm_profiles.py` from project root to verify server responsiveness

## Notes

- **Performance:** OpenStreetMap servers may be slightly slower than the public OSRM during peak hours, but profile differentiation is more important for accurate navigation
- **Accuracy:** Times are now realistic based on transportation mode (pedestrians: ~1.4 m/s, bikes: ~4 m/s, cars: ~15 m/s)
- **Free & Open Source:** Uses community-maintained OSRM servers with no authentication required
- **Future improvement:** Could add support for switching profiles at runtime if needed for multi-modal routing

## Impact

NaviAcess now provides **accurate, mode-specific navigation** with realistic travel times. Pedestrians get longer but proper routes, improving the accessibility experience for visually impaired users.
