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

// Sample data
const citiesData = [
  {
    name: "Innopolis",
    center: [55.7461773, 48.7506767],
    geojson: {
      type: "FeatureCollection",
      features: [] // No predefined polygons for "Innopolis"
    }
  }
];

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
  useMapEvents({
    click: (e) => {
      onLocationSelect(e.latlng);
    }
  });
  return null;
}

// Legend component
function Legend() {
  return (
    <div className="legend">
      <h2>Legend</h2>
      <div className="legend-item">
        <div className="color-box" style={{ backgroundColor: "#a1d99b" }} />
        <span>Residential</span>
      </div>
      <div className="legend-item">
        <div className="color-box" style={{ backgroundColor: "#fc9272" }} />
        <span>Commercial</span>
      </div>
      <div className="legend-item">
        <div className="color-box" style={{ backgroundColor: "#9ecae1" }} />
        <span>Mixed</span>
      </div>
      <div className="legend-item">
        <div className="color-box" style={{ backgroundColor: "#ccc" }} />
        <span>Other</span>
      </div>
      <div className="legend-item">
        <div className="color-box" style={{ backgroundColor: "#ff0000" }} />
        <span>Custom Location</span>
      </div>
    </div>
  );
}

// Main App
export default function App() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [points, setPoints] = useState([]);
  const [customLocation, setCustomLocation] = useState(null);
  const [viewMode, setViewMode] = useState('city'); // 'city' or 'custom'
  const [loading, setLoading] = useState(false);

  // Fetch cities from the API
  useEffect(() => {
    async function fetchCities() {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost';
        const response = await fetch(`${apiUrl}/api/cities`);
        const data = await response.json();
        if (data.cities) {
          setCities(data.cities);
          if (data.cities.length > 0) {
            setSelectedCity(data.cities[0]);
          }
        }
      } catch (error) {
        console.error("Error fetching cities:", error);
      }
    }
    fetchCities();
  }, []);

  // Fetch points based on selected city or custom location
  useEffect(() => {
    async function fetchPoints() {
      if (!selectedCity && !customLocation) return;
      
      setLoading(true);
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost';
        let url;
        if (viewMode === 'city' && selectedCity) {
          url = `${apiUrl}/api/city/${selectedCity.name}/pois`;
        } else if (viewMode === 'custom' && customLocation) {
          url = `${apiUrl}/api/nearby?lat=${customLocation.lat}&lon=${customLocation.lng}&distance=1km`;
        }

        if (url) {
          const response = await fetch(url);
          const data = await response.json();
          if (data.pois) {
            setPoints(data.pois);
          }
        }
      } catch (error) {
        console.error("Error fetching points:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchPoints();
  }, [selectedCity, customLocation, viewMode]);

  const handleLocationSelect = (latlng) => {
    setCustomLocation(latlng);
    setViewMode('custom');
  };

  // Style polygons
  const styleDistricts = (feature) => {
    const districtType = feature.properties.type;
    let fillColor = "#ccc";
    if (districtType === "residential") fillColor = "#a1d99b";
    if (districtType === "commercial") fillColor = "#fc9272";
    if (districtType === "mixed") fillColor = "#9ecae1";

    return {
      fillColor,
      color: "#333",
      weight: 1,
      fillOpacity: 0.6
    };
  };

  return (
    <div className="app-container">
      {/* LEFT PANEL */}
      <div className="left-panel">
        <h1>Interactive cities map</h1>

        <div className="view-mode-selector">
          <label>
            <input
              type="radio"
              name="viewMode"
              value="city"
              checked={viewMode === 'city'}
              onChange={() => setViewMode('city')}
            />
            City View
          </label>
          <label>
            <input
              type="radio"
              name="viewMode"
              value="custom"
              checked={viewMode === 'custom'}
              onChange={() => setViewMode('custom')}
            />
            Custom Location
          </label>
        </div>

        {viewMode === 'city' && (
          <div className="city-selector">
            <label htmlFor="city-select">City:</label>
            <select
              id="city-select"
              value={selectedCity?.name || ''}
              onChange={(e) => {
                const city = cities.find((c) => c.name === e.target.value);
                setSelectedCity(city);
              }}
            >
              {cities.map((city) => (
                <option key={city.name} value={city.name}>
                  {city.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {viewMode === 'custom' && customLocation && (
          <div className="custom-location-info">
            <h3>Custom Location</h3>
            <p>Latitude: {customLocation.lat.toFixed(6)}</p>
            <p>Longitude: {customLocation.lng.toFixed(6)}</p>
          </div>
        )}

        <Legend />
      </div>

      {/* RIGHT PANEL: MAP */}
      <div className="map-panel">
        <MapContainer
          center={viewMode === 'city' && selectedCity ? [selectedCity.lat, selectedCity.lon] : [55.7461773, 48.7506767]}
          zoom={13}
          className="leaflet-container"
        >
          {viewMode === 'city' && selectedCity && (
            <FlyToCity center={[selectedCity.lat, selectedCity.lon]} />
          )}
          {viewMode === 'custom' && customLocation && (
            <FlyToCity center={[customLocation.lat, customLocation.lng]} />
          )}

          <MapClickHandler onLocationSelect={handleLocationSelect} />

          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
          />

          {/* Render markers for POIs */}
          {points.map((point, index) => (
            <Marker
              key={index}
              position={[point.location.lat, point.location.lon]}
            >
              <Popup>
                <strong>{point.Name || "Unnamed"}</strong>
                <br />
                {point.city && `City: ${point.city}`}
                <br />
                {point.Categories && `Categories: ${point.Categories}`}
                <br />
                {point.Custom && `Custom: ${Array.isArray(point.Custom) ? point.Custom.join(", ") : point.Custom}`}
              </Popup>
            </Marker>
          ))}

          {/* Render custom location marker */}
          {customLocation && (
            <Marker
              position={[customLocation.lat, customLocation.lng]}
              icon={customLocationIcon}
            >
              <Popup>
                <strong>Custom Location</strong>
                <br />
                Click elsewhere to change
              </Popup>
            </Marker>
          )}
        </MapContainer>
        {loading && <div className="loading-overlay">Loading...</div>}
      </div>
    </div>
  );
}
