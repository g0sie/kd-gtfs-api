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

function NearestStationLayer({ onShowDepartures }) {
  const { clickedPoint, nearestStation, status, findNearestStation, clearNearestStation } =
    useNearestStation();

  useMapEvents({ click: (event) => findNearestStation(event.latlng.wrap()) });

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
          onShowDepartures={onShowDepartures}
          onClose={clearNearestStation}
        />
      )}
    </>
  );
}

function NearestStationMarker({ station, onShowDepartures, onClose }) {
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
      {/* "remove" przychodzi przy każdym zamknięciu: krzyżykiem, Esc albo kliknięciem w mapę obok.
          Kliknięcie w mapę zamyka popup przed uruchomieniem nowego szukania, więc nowy wynik
          nie zostaje wyczyszczony. */}
      <Popup position={[lat, lon]} eventHandlers={{ remove: onClose }}>
        <strong>{name}</strong>
        <br />
        Najbliższa stacja, {formatDistance(distanceMeters)}
        <br />
        <button
          type="button"
          className="popup-button"
          onClick={() => onShowDepartures(station.properties)}
        >
          Pokaż odjazdy
        </button>
      </Popup>
    </>
  );
}

export default NearestStationLayer;
