import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Środek mapy mniej więcej nad Dolnym Śląskiem.
const LOWER_SILESIA_CENTER = [51.0, 16.4];
const INITIAL_ZOOM = 8;

const OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const OSM_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

function StationMap() {
  return (
    <MapContainer
      center={LOWER_SILESIA_CENTER}
      zoom={INITIAL_ZOOM}
      className="station-map"
    >
      <TileLayer url={OSM_TILE_URL} attribution={OSM_ATTRIBUTION} />
    </MapContainer>
  );
}

export default StationMap;
