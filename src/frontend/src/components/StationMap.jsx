import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import FrequencyLayer from "./FrequencyLayer.jsx";
import MapResizeHandler from "./MapResizeHandler.jsx";
import NearestStationLayer from "./NearestStationLayer.jsx";

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

// Przy włączonej warstwie odcinków mniejsze znaczniki, żeby nie zasłaniały linii.
const SMALL_STATION_MARKER_STYLE = { ...STATION_MARKER_STYLE, radius: 4 };

function StationMap({ stations, onSelectStation, showSegments }) {
  const markerStyle = showSegments ? SMALL_STATION_MARKER_STYLE : STATION_MARKER_STYLE;

  return (
    <MapContainer
      center={LOWER_SILESIA_CENTER}
      zoom={INITIAL_ZOOM}
      className="station-map"
    >
      <TileLayer url={OSM_TILE_URL} attribution={OSM_ATTRIBUTION} />
      {showSegments && <FrequencyLayer />}
      {stations.features.map((station) => {
        // GeoJSON zapisuje współrzędne jako [lon, lat], a Leaflet oczekuje [lat, lon].
        const [lon, lat] = station.geometry.coordinates;
        return (
          <CircleMarker
            key={station.properties.id}
            center={[lat, lon]}
            pathOptions={markerStyle}
            bubblingMouseEvents={false}
            eventHandlers={{ click: () => onSelectStation(station.properties) }}
          >
            <Popup>{station.properties.name}</Popup>
          </CircleMarker>
        );
      })}
      <NearestStationLayer onShowDepartures={onSelectStation} />
      <MapResizeHandler />
    </MapContainer>
  );
}

export default StationMap;
