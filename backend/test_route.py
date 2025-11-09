#!/usr/bin/env python3
"""
Test script for /api/route endpoint
"""
import asyncio
import sys
sys.path.insert(0, '/c/Users/pedro/programas/Hackathon2025/backend')

from api.navigation import get_route
from services.routing import calculate_route

async def test_route():
    """Test the route calculation with valid parameters"""
    try:
        # Test with Lisbon coordinates (38.7, -9.1) to same location
        result = await get_route(
            origin_lat=38.7,
            origin_lon=-9.1,
            dest_lat=38.8,
            dest_lon=-9.0
        )
        print("✅ Route test passed!")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_route())
    sys.exit(0 if success else 1)
