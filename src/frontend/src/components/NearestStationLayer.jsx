import { CircleMarker, Popup, useMapEvents } from "react-leaflet";
import { useNearestStation } from "../hooks/useNearestStation.js";
import { formatDistance } from "../utils/formatDistance.js";

const CLICKED_POINT_STYLE = {
  radius: 5,
  color: "#ffffff",
  weight: 2,
  fillColor: "#1565c0",
  fillOpacity: 1,
};

const NEAREST_STATION_STYLE = {
  radius: 10,
  color: "#000000",
  weight: 2,
  fillColor: "#d32f2f",
  fillOpacity: 1,
};

const STATUS_MESSAGES = {
  loading: "Szukam najbliższej stacji…",
  error: "Nie udało się znaleźć najbliższej stacji",
};

function NearestStationLayer() {
  const { clickedPoint, nearestStation, status, findNearestStation } = useNearestStation();

  useMapEvents({ click: (event) => findNearestStation(event.latlng) });

  return (
    <>
      {status !== "idle" && (
        <p
          className={`map-status${status === "error" ? " status-error" : ""}`}
          role={status === "error" ? "alert" : "status"}
        >
          {STATUS_MESSAGES[status]}
        </p>
      )}

      {/* bubblingMouseEvents: false, żeby kliknięcie w te znaczniki nie uruchamiało nowego wyszukiwania */}
      {clickedPoint && (
        <CircleMarker
          center={clickedPoint}
          pathOptions={CLICKED_POINT_STYLE}
          bubblingMouseEvents={false}
        />
      )}

      {nearestStation && (
        <NearestStationMarker
          key={`${clickedPoint}-${nearestStation.properties.id}`}
          station={nearestStation}
        />
      )}
    </>
  );
}

function NearestStationMarker({ station }) {
  // GeoJSON zapisuje współrzędne jako [lon, lat], a Leaflet oczekuje [lat, lon].
  const [lon, lat] = station.geometry.coordinates;
  const { name, distance_m: distanceMeters } = station.properties;

  // Popup z position nie jest przypięty do znacznika, więc otwiera się sam po zamontowaniu.
  // Klucz w komponencie nadrzędnym montuje go na nowo przy każdym wyniku.
  return (
    <>
      <CircleMarker
        center={[lat, lon]}
        pathOptions={NEAREST_STATION_STYLE}
        bubblingMouseEvents={false}
      />
      <Popup position={[lat, lon]}>
        <strong>{name}</strong>
        <br />
        Najbliższa stacja, {formatDistance(distanceMeters)}
      </Popup>
    </>
  );
}

export default NearestStationLayer;
