import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import './Map.css';

export const Map = ({ destination, currentLocation, route }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize map
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView([40.7128, -74.0060], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(mapInstanceRef.current);
    }

    const map = mapInstanceRef.current;
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        map.removeLayer(layer);
      }
    });

    // Add current location
    if (currentLocation) {
      L.circleMarker([currentLocation.latitude, currentLocation.longitude], {
        radius: 8,
        fillColor: '#007bff',
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8,
      })
        .addTo(map)
        .bindPopup('Your Location');
    }

    // Add destination
    if (destination) {
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
    if (route && route.steps && route.steps.length > 0) {
      // For visualization, create a simple polyline
      const routeCoords = [];
      if (currentLocation) {
        routeCoords.push([currentLocation.latitude, currentLocation.longitude]);
      }
      if (destination) {
        routeCoords.push([destination.latitude, destination.longitude]);
      }

      if (routeCoords.length > 1) {
        L.polyline(routeCoords, {
          color: '#007bff',
          weight: 3,
          opacity: 0.7,
        }).addTo(map);
      }
    }

    // Fit bounds
    if (currentLocation && destination) {
      const bounds = L.latLngBounds(
        [currentLocation.latitude, currentLocation.longitude],
        [destination.latitude, destination.longitude]
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [currentLocation, destination, route]);

  return <div ref={mapRef} className="map-container"></div>;
};

export default Map;
