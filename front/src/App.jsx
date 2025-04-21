// App.jsx
import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Marker,
  Popup,
  useMap,
  useMapEvents
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

// Fix Leaflet icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png"
});

// Custom location marker icon
const customLocationIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// FlyToCity: Smooth animation when center changes
function FlyToCity({ center }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, 13, { duration: 1.5 });
  }, [map, center]);
  return null;
}

// MapClickHandler: Handle map clicks for custom location
function MapClickHandler({ onLocationSelect }) {
  useMapEvents({ click: (e) => onLocationSelect(e.latlng) });
  return null;
}

// Legend component
function Legend() {
  return (
    <div className="legend">
      <h2>Legend</h2>
      <div className="legend-item"><div className="color-box" style={{backgroundColor: "#a1d99b"}} /><span>Residential</span></div>
      <div className="legend-item"><div className="color-box" style={{backgroundColor: "#fc9272"}} /><span>Commercial</span></div>
      <div className="legend-item"><div className="color-box" style={{backgroundColor: "#9ecae1"}} /><span>Mixed</span></div>
      <div className="legend-item"><div className="color-box" style={{backgroundColor: "#ccc"}} /><span>Other</span></div>
      <div className="legend-item"><div className="color-box" style={{backgroundColor: "#ff0000"}} /><span>Custom Location</span></div>
      <div className="legend-item"><div className="color-box" style={{backgroundColor: "#ff7800"}} /><span>City Clusters</span></div>
    </div>
  );
}

export default function App() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [points, setPoints] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [customLocation, setCustomLocation] = useState(null);
  const [viewMode, setViewMode] = useState('city');
  const [showPOIs, setShowPOIs] = useState(true);
  const [showClusters, setShowClusters] = useState(true);
  const [loading, setLoading] = useState(false);

  // Base API path routed by nginx
  const API_BASE = process.env.REACT_APP_API_URL || '/api';

  // Load available cities
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/cities`);
        const data = await res.json();
        if (data.cities) setCities(data.cities);
        setSelectedCity(data.cities?.[0] || null);
      } catch (err) {
        console.error("Error fetching cities:", err);
      }
    })();
  }, [API_BASE]);

  // Fetch POIs for city or custom location
  useEffect(() => {
    (async () => {
      if (!selectedCity && !customLocation) return;
      setLoading(true);
      try {
        let url;
        if (viewMode === 'city' && selectedCity) {
          url = `${API_BASE}/city/${encodeURIComponent(selectedCity.name)}/pois`;
        } else if (viewMode === 'custom' && customLocation) {
          url = `${API_BASE}/nearby?lat=${customLocation.lat}&lon=${customLocation.lng}&distance=1km`;
        }
        const res = await fetch(url);
        const data = await res.json();
        setPoints(data.pois || []);
      } catch (err) {
        console.error("Error fetching POIs:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [API_BASE, selectedCity, customLocation, viewMode]);

  // Fetch clusters for selected city
  useEffect(() => {
    (async () => {
      if (viewMode !== 'city' || !selectedCity) return;
      try {
        const res = await fetch(`${API_BASE}/clusters?city=${encodeURIComponent(selectedCity.name)}`);
        const data = await res.json();
        setClusters(data.clusters || []);
      } catch (err) {
        console.error("Error fetching clusters:", err);
      }
    })();
  }, [API_BASE, selectedCity, viewMode]);

  const handleLocationSelect = (latlng) => {
    setCustomLocation(latlng);
    setViewMode('custom');
  };

  const styleClusters = () => ({ color: '#ff7800', weight: 2, fillOpacity: 0.2 });

  return (
    <div className="app-container">
      <div className="left-panel">
        <h1>Interactive cities map</h1>
        <div className="view-mode-selector">
          <label><input type="radio" value="city" checked={viewMode === 'city'} onChange={() => setViewMode('city')} /> City View</label>
          <label><input type="radio" value="custom" checked={viewMode === 'custom'} onChange={() => setViewMode('custom')} /> Custom Location</label>
        </div>
        {viewMode === 'city' && (
          <select
            value={selectedCity?.name || ''}
            onChange={(e) => setSelectedCity(cities.find((c) => c.name === e.target.value))}
          >
            {cities.map((c) => (
              <option key={c.name} value={c.name}>
                {c.name}
              </option>
            ))}
          </select>
        )}
        {viewMode === 'custom' && customLocation && (
          <div className="custom-location-info">
            <p>Lat: {customLocation.lat.toFixed(6)}</p>
            <p>Lon: {customLocation.lng.toFixed(6)}</p>
          </div>
        )}
        {/* Layer toggles */}
        <div className="layer-toggles">
          <label><input type="checkbox" checked={showClusters} onChange={() => setShowClusters(!showClusters)} /> Show Clusters</label>
          <label><input type="checkbox" checked={showPOIs} onChange={() => setShowPOIs(!showPOIs)} /> Show POIs</label>
        </div>
        <Legend />
      </div>
      <div className="map-panel">
        <MapContainer
          center={
            viewMode === 'city' && selectedCity
              ? [selectedCity.lat, selectedCity.lon]
              : [55.7461773, 48.7506767]
          }
          zoom={13}
          className="leaflet-container"
        >
          {viewMode === 'city' && selectedCity && <FlyToCity center={[selectedCity.lat, selectedCity.lon]} />}
          {viewMode === 'custom' && customLocation && <FlyToCity center={[customLocation.lat, customLocation.lng]} />}
          <MapClickHandler onLocationSelect={handleLocationSelect} />
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap contributors" />

          {/* Render clusters */}
          {showClusters && clusters.map((hit, idx) => {
            const shape = hit._source?.shape;
            if (!shape || !shape.type || !shape.coordinates) return null;
            const geojson = {
              ...shape,
              type: shape.type.charAt(0).toUpperCase() + shape.type.slice(1)
            };
            return <GeoJSON key={idx} data={geojson} style={styleClusters()} />;
          })}

          {/* Render POIs */}
          {showPOIs && points.map((pt, i) => (
            <Marker key={i} position={[pt.location.lat, pt.location.lon]}>
              <Popup>
                <strong>{pt.name || 'Unnamed'}</strong><br />
                {pt.city && `City: ${pt.city}`}<br />
                {pt.categories && `Categories: ${pt.categories}`}<br />
                {pt.custom_tags && `Tags: ${Array.isArray(pt.custom_tags) ? pt.custom_tags.join(', ') : pt.custom_tags}`}
              </Popup>
            </Marker>
          ))}

          {customLocation && (
            <Marker position={[customLocation.lat, customLocation.lng]} icon={customLocationIcon}>
              <Popup>Custom Location<br />Click elsewhere to change</Popup>
            </Marker>
          )}
        </MapContainer>
        {loading && <div className="loading-overlay">Loading...</div>}
      </div>
    </div>
  );
}
