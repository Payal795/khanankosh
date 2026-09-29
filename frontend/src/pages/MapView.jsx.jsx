import { useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import L from "leaflet";

function Fit({ feature }) {
  const map = useMap();
  useEffect(() => { if (feature) map.flyToBounds(L.geoJSON(feature).getBounds(), { padding: [30, 30], duration: 1.2 }); }, [feature, map]);
  return null;
}

export default function MapView({ fields, selectedId, onSelect, layers, active, opacity, water }) {
  const selected = fields?.features.find((f) => f.properties.id === selectedId);
  const style = (f) => {
    const on = f.properties.id === selectedId;
    return { color: on ? "#1c2b22" : f.properties.featured ? "#b5651d" : "#6b7a6f", weight: on ? 3 : 1, fillOpacity: on ? 0.02 : 0.15, fillColor: "#b5651d" };
  };
  return (
    <MapContainer center={[22.5, 80]} zoom={5} className="map" preferCanvas>
      <TileLayer attribution="Tiles &copy; Esri" url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" />
      {fields && (
        <GeoJSON key={selectedId || "none"} data={fields} style={style}
          onEachFeature={(f, l) => { l.bindTooltip(`${f.properties.name} (${f.properties.state})`, { sticky: true }); l.on("click", () => onSelect(f.properties.id)); }} />
      )}
      {active.map((k) => layers?.[k] && <TileLayer key={k} url={layers[k]} opacity={opacity} zIndex={400} />)}
      {water && <TileLayer url={water} opacity={0.85} zIndex={410} />}
      <Fit feature={selected} />
    </MapContainer>
  );
}
