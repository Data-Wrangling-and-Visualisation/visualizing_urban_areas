// App.jsx
import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Marker,
  Popup,
  useMap
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css"; // <-- Our CSS from above

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
    </div>
  );
}

// Main App
export default function App() {
  const [selectedCity, setSelectedCity] = useState(citiesData[0]);
  const [points, setPoints] = useState([]); // State to store points from the API

  // Fetch points from the API
  useEffect(() => {
    async function fetchPoints() {
      try {
        const response = await fetch("http://localhost:8000/points"); // Replace with your API URL
        const data = await response.json();
        if (data.points) {
          setPoints(data.points);
        } else {
          console.error("Error fetching points:", data.error);
        }
      } catch (error) {
        console.error("Error fetching points:", error);
      }
    }
    fetchPoints();
  }, []);

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

        <div className="city-selector">
          <label htmlFor="city-select">City:</label>
          <select
            id="city-select"
            value={selectedCity.name}
            onChange={(e) => {
              const city = citiesData.find((c) => c.name === e.target.value);
              setSelectedCity(city);
            }}
          >
            {citiesData.map((city) => (
              <option key={city.name} value={city.name}>
                {city.name}
              </option>
            ))}
          </select>
        </div>

        <Legend />
      </div>

      {/* RIGHT PANEL: MAP */}
      <div className="map-panel">
        <MapContainer
          center={selectedCity.center}
          zoom={13}
          className="leaflet-container"
        >
          <FlyToCity center={selectedCity.center} />

          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
          />

          <GeoJSON data={selectedCity.geojson} style={styleDistricts} />

          {/* Render markers for Innopolis */}
          {selectedCity.name === "Innopolis" &&
            points.map((point, index) => {
              if (!point.Latitude || !point.Longitude) {
                console.warn("Invalid point data:", point); // Debugging
                return null;
              }
              return (
                <Marker
                  key={index}
                  position={[point.Latitude, point.Longitude]}
                >
                  <Popup>
                    <strong>{point.Name || "Unnamed"}</strong>
                    <br />
                    Categories: {point.Categories}
                    <br />
                    Custom: {Array.isArray(point.Custom) ? point.Custom.join(", ") : point.Custom}
                  </Popup>
                </Marker>
              );
            })}
        </MapContainer>
      </div>
    </div>
  );
}
