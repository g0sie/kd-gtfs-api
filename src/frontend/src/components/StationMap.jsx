import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Środek mapy mniej więcej nad Dolnym Śląskiem.
const LOWER_SILESIA_CENTER = [51.0, 16.4];
const INITIAL_ZOOM = 8;

const OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const OSM_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

const STATION_MARKER_STYLE = {
  radius: 6,
  color: "#000000",
  weight: 1,
  fillColor: "#f6c32f",
  fillOpacity: 1,
};

function StationMap({ stations }) {
  return (
    <MapContainer
      center={LOWER_SILESIA_CENTER}
      zoom={INITIAL_ZOOM}
      className="station-map"
    >
      <TileLayer url={OSM_TILE_URL} attribution={OSM_ATTRIBUTION} />
      {stations.features.map((station) => {
        // GeoJSON zapisuje współrzędne jako [lon, lat], a Leaflet oczekuje [lat, lon].
        const [lon, lat] = station.geometry.coordinates;
        return (
          <CircleMarker
            key={station.properties.id}
            center={[lat, lon]}
            pathOptions={STATION_MARKER_STYLE}
          >
            <Popup>{station.properties.name}</Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}

export default StationMap;
