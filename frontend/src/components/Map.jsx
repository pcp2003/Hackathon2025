import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { MAP_CONFIG } from '../utils/constants';

// Helper function to validate coordinates
const isValidCoordinate = (location) => {
  if (!location) return false;
  return location.latitude !== null && location.latitude !== undefined && 
         location.longitude !== null && location.longitude !== undefined;
};

export const Map = ({ destination, currentLocation, route }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const resizeObserverRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) return;

    if (mapInstanceRef.current) {
      setTimeout(() => {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.invalidateSize(true);
        }
      }, 50);
      
      setTimeout(() => {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.invalidateSize(true);
        }
      }, 200);
    }
  }, [destination, currentLocation, route]);

  useEffect(() => {
    // Don't initialize if we don't have essential data with valid coordinates
    if (!mapRef.current || !isValidCoordinate(destination)) return;

    // Initialize map
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView(
        [destination.latitude, destination.longitude],
        MAP_CONFIG.DEFAULT_ZOOM
      );
      L.tileLayer(MAP_CONFIG.TILE_LAYER, {
        attribution: MAP_CONFIG.TILE_ATTRIBUTION,
        maxZoom: MAP_CONFIG.MAX_ZOOM,
        updateWhenIdle: true,
      }).addTo(mapInstanceRef.current);
      
      setTimeout(() => {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.invalidateSize(true);
        }
      }, 300);

      if (!resizeObserverRef.current && mapRef.current) {
        resizeObserverRef.current = new ResizeObserver(() => {
          if (mapInstanceRef.current) {
            mapInstanceRef.current.invalidateSize(true);
          }
        });
        resizeObserverRef.current.observe(mapRef.current);
      }
    }

    const map = mapInstanceRef.current;
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        map.removeLayer(layer);
      }
    });

    // Add current location
    if (isValidCoordinate(currentLocation)) {
      L.circleMarker([currentLocation.latitude, currentLocation.longitude], {
        radius: 8,
        fillColor: '#3b82f6',
        color: '#06b6d4',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
      })
        .addTo(map)
        .bindPopup('Your Location');
    }

    // Add destination
    if (isValidCoordinate(destination)) {
      L.marker([destination.latitude, destination.longitude], {
        icon: L.icon({
          iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="red" width="32" height="32"><circle cx="12" cy="12" r="10"/></svg>',
          iconSize: [32, 32],
          iconAnchor: [16, 32],
        }),
      })
        .addTo(map)
        .bindPopup('Destination');
    }

    // Add route
    if (route && route.route_coordinates && route.route_coordinates.length > 0) {
      // Use the actual route coordinates from the backend
      L.polyline(route.route_coordinates, {
        color: '#3b82f6',
        weight: 4,
        opacity: 0.8,
      }).addTo(map);
    } else if (route && route.steps && route.steps.length > 0) {
      // Fallback: create a simple polyline if route_coordinates not available
      const routeCoords = [];
      if (currentLocation) {
        routeCoords.push([currentLocation.latitude, currentLocation.longitude]);
      }
      if (destination) {
        routeCoords.push([destination.latitude, destination.longitude]);
      }

      if (routeCoords.length > 1) {
        L.polyline(routeCoords, {
          color: '#3b82f6',
          weight: 4,
          opacity: 0.8,
        }).addTo(map);
      }
    }

    // Fit bounds
    if (isValidCoordinate(currentLocation) && isValidCoordinate(destination)) {
      const bounds = L.latLngBounds(
        [currentLocation.latitude, currentLocation.longitude],
        [destination.latitude, destination.longitude]
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    }

    return () => {
      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect();
      }
    };
  }, [currentLocation, destination, route]);

  return <div ref={mapRef} className="map-container"></div>;
};

export default Map;
