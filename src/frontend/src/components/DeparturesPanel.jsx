import { useState } from "react";
import { useDepartures } from "../hooks/useDepartures.js";
import { formatDate } from "../utils/formatDate.js";
import { formatDepartureTime } from "../utils/formatDepartureTime.js";

const STATUS_MESSAGES = {
  loading: "Wczytywanie odjazdów…",
  error: "Nie udało się pobrać odjazdów.",
  "not-found": "Nie znaleziono stacji.",
};

// Pole <input type="time"> daje "HH:MM", a API przyjmuje "HH:MM:SS". Przy samej dacie
// wysyłamy północ, bo domyślna godzina API (teraz) ucięłaby odjazdy z początku wybranego dnia.
function toApiTime(inputTime, inputDate) {
  if (inputTime) {
    return `${inputTime}:00`;
  }
  return inputDate ? "00:00:00" : "";
}

// feed: zakres rozkładu z GET /feed albo null, gdy się wczytuje lub nie udało się go pobrać.
function DeparturesPanel({ station, feed, onClose }) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const { status, data } = useDepartures(station.id, { date, time: toApiTime(time, date) });

  return (
    <aside className="departures-panel" aria-label="Odjazdy">
      <header className="departures-header">
        <div>
          <h2>{station.name}</h2>
          {status === "success" && <p>Odjazdy z dnia {formatDate(data.date)}</p>}
        </div>
        <button
          type="button"
          className="close-button"
          onClick={onClose}
          aria-label="Zamknij panel odjazdów"
        >
          ×
        </button>
      </header>

      <div className="departures-filters">
        <label>
          Data
          <input
            type="date"
            value={date}
            min={feed?.start_date}
            max={feed?.end_date}
            onChange={(event) => setDate(event.target.value)}
          />
        </label>
        <label>
          Godzina
          <input type="time" value={time} onChange={(event) => setTime(event.target.value)} />
        </label>
        <button
          type="button"
          onClick={() => {
            setDate("");
            setTime("");
          }}
          disabled={!date && !time}
        >
          Teraz
        </button>
      </div>
      <p className="departures-hint">
        Puste pola: dzisiejsza data i aktualna godzina.
        <br />
        Sama data: odjazdy od początku dnia.
        {feed && (
          <>
            <br />
            Rozkład obowiązuje od {formatDate(feed.start_date)} do {formatDate(feed.end_date)}.
          </>
        )}
      </p>

      {status === "success" ? (
        <DeparturesTable departures={data.departures} />
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

function DeparturesTable({ departures }) {
  if (departures.length === 0) {
    return <p role="status">Brak odjazdów od wybranej godziny w tym dniu.</p>;
  }

  return (
    <table className="departures-table">
      <thead>
        <tr>
          <th>Godzina</th>
          <th>Linia</th>
          <th>Kierunek</th>
        </tr>
      </thead>
      <tbody>
        {departures.map((departure) => {
          const { time, isNextDay } = formatDepartureTime(departure.departure_time);
          return (
            <tr key={departure.trip_id}>
              <td>
                {time}
                {isNextDay && (
                  <span className="next-day" title="Kurs z wybranego dnia, odjazd po północy">
                    następnego dnia
                  </span>
                )}
              </td>
              <td>{departure.line}</td>
              <td>{departure.headsign}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default DeparturesPanel;
