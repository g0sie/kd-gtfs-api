import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { Pane, Polyline, Popup } from "react-leaflet";
import {
  SEGMENT_CLASSES,
  WEEKEND_REFERENCE_DATE,
  WORKDAY_REFERENCE_DATE,
} from "../constants.js";
import { useSegments } from "../hooks/useSegments.js";
import { formatDate } from "../utils/formatDate.js";
import { segmentClass, segmentClassLabel } from "../utils/segmentClass.js";

// Własny pane pod domyślnym overlayPane (z-index 400), w którym są znaczniki stacji.
// Bez niego linie dodane po włączeniu warstwy leżałyby na stacjach i zasłaniały je przed kliknięciem.
const SEGMENTS_PANE = "segments";
const SEGMENTS_PANE_STYLE = { zIndex: 350 };

const REFERENCE_DAYS = [
  { label: "Dzień roboczy (24.11)", date: WORKDAY_REFERENCE_DATE },
  { label: "Weekend (22.11)", date: WEEKEND_REFERENCE_DATE },
];

function FrequencyLayer() {
  const [date, setDate] = useState("");
  const { status, data } = useSegments(date);

  return (
    <>
      <Pane name={SEGMENTS_PANE} style={SEGMENTS_PANE_STYLE}>
        {status === "success" &&
          data.features.map((segment) => <SegmentLine key={segmentKey(segment)} segment={segment} />)}
      </Pane>
      <FrequencyLegend
        status={status}
        shownDate={date || data?.date}
        onSelectDate={setDate}
      />
    </>
  );
}

function segmentKey(segment) {
  const { from_station_id: fromId, to_station_id: toId } = segment.properties;
  return `${fromId}-${toId}`;
}

function SegmentLine({ segment }) {
  // GeoJSON zapisuje współrzędne jako [lon, lat], a Leaflet oczekuje [lat, lon].
  const positions = segment.geometry.coordinates.map(([lon, lat]) => [lat, lon]);
  const {
    from_station_name: fromName,
    to_station_name: toName,
    trips_per_day: tripsPerDay,
  } = segment.properties;
  const { color, weight } = segmentClass(tripsPerDay);

  return (
    <Polyline
      positions={positions}
      pathOptions={{ color, weight, opacity: 0.9 }}
      bubblingMouseEvents={false}
    >
      <Popup>
        <strong>
          {fromName} – {toName}
        </strong>
        <br />
        Kursy na dobę: {tripsPerDay}
      </Popup>
    </Polyline>
  );
}

function FrequencyLegend({ status, shownDate, onSelectDate }) {
  const legendRef = useRef(null);

  // Legenda leży w kontenerze mapy, więc kliknięcia i przewijanie trzeba zatrzymać,
  // żeby nie uruchamiały szukania najbliższej stacji ani nie przybliżały mapy.
  useEffect(() => {
    L.DomEvent.disableClickPropagation(legendRef.current);
    L.DomEvent.disableScrollPropagation(legendRef.current);
  }, []);

  return (
    <div className="frequency-legend" ref={legendRef}>
      <h2>Kursy na dobę</h2>
      {status === "success" && shownDate && <p>Dzień {formatDate(shownDate)}</p>}
      {status === "loading" && <p role="status">Wczytywanie odcinków…</p>}
      {status === "error" && (
        <p className="status-error" role="alert">
          Nie udało się pobrać odcinków.
        </p>
      )}

      <ul>
        {SEGMENT_CLASSES.map((segmentClassItem, index) => (
          <li key={segmentClassItem.min}>
            <span
              className="legend-line"
              style={{ background: segmentClassItem.color, height: segmentClassItem.weight }}
            />
            {segmentClassLabel(index)}
          </li>
        ))}
      </ul>

      <div className="legend-days">
        {REFERENCE_DAYS.map((day) => (
          <button
            key={day.date}
            type="button"
            aria-pressed={shownDate === day.date}
            onClick={() => onSelectDate(day.date)}
          >
            {day.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default FrequencyLayer;
