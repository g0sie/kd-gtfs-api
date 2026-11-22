import { useState } from "react";
import {
  FEED_END,
  FEED_START,
  WEEKEND_REFERENCE_DATE,
  WORKDAY_REFERENCE_DATE,
} from "../constants.js";
import { useStats } from "../hooks/useStats.js";
import { formatDate } from "../utils/formatDate.js";
import DeparturesByHourChart from "./DeparturesByHourChart.jsx";

const STATUS_MESSAGES = {
  loading: "Wczytywanie statystyk…",
  error: "Nie udało się pobrać statystyk.",
};

const REFERENCE_DAYS = [
  { label: "Dzień roboczy (24.11)", date: WORKDAY_REFERENCE_DATE },
  { label: "Weekend (22.11)", date: WEEKEND_REFERENCE_DATE },
];

function StatsPanel({ onClose }) {
  const [date, setDate] = useState("");
  const { status, data } = useStats(date);
  // Bez wybranej daty API liczy dla swojego dnia domyślnego, więc zaznaczamy dzień z odpowiedzi.
  const shownDate = date || data?.date;

  return (
    <aside className="stats-panel" aria-label="Statystyki">
      <header className="stats-header">
        <div>
          <h2>Statystyki</h2>
          {status === "success" && <p>Dzień {formatDate(data.date)}</p>}
        </div>
        <button
          type="button"
          className="close-button"
          onClick={onClose}
          aria-label="Zamknij panel statystyk"
        >
          ×
        </button>
      </header>

      <div className="stats-filters">
        {REFERENCE_DAYS.map((day) => (
          <button
            key={day.date}
            type="button"
            aria-pressed={shownDate === day.date}
            onClick={() => setDate(day.date)}
          >
            {day.label}
          </button>
        ))}
        <label>
          Data
          <input
            type="date"
            value={date}
            min={FEED_START}
            max={FEED_END}
            onChange={(event) => setDate(event.target.value)}
          />
        </label>
      </div>
      <p className="stats-hint">
        Rozkład obowiązuje od {formatDate(FEED_START)} do {formatDate(FEED_END)}.
      </p>

      {status === "success" ? (
        <StatsContent stats={data} />
      ) : (
        <p
          className={status === "loading" ? undefined : "status-error"}
          role={status === "loading" ? "status" : "alert"}
        >
          {STATUS_MESSAGES[status]}
        </p>
      )}
    </aside>
  );
}

function StatsContent({ stats }) {
  return (
    <>
      <dl className="stats-numbers">
        <div>
          <dt>Kursy</dt>
          <dd>{stats.trips_count.toLocaleString("pl-PL")}</dd>
        </div>
        <div>
          <dt>Stacje</dt>
          <dd>{stats.stations_count.toLocaleString("pl-PL")}</dd>
        </div>
      </dl>

      <h3>Odjazdy w ciągu doby</h3>
      <DeparturesByHourChart departuresByHour={stats.departures_by_hour} />

      <h3>Stacje z największą liczbą odjazdów</h3>
      <ol className="top-stations">
        {stats.top_stations.map((station) => (
          <li key={station.id}>
            <span>{station.name}</span>
            <span>{station.departures_per_day.toLocaleString("pl-PL")}</span>
          </li>
        ))}
      </ol>
    </>
  );
}

export default StatsPanel;
