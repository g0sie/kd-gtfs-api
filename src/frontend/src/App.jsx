import { lazy, Suspense, useEffect, useState } from "react";
import DeparturesPanel from "./components/DeparturesPanel.jsx";
import StationMap from "./components/StationMap.jsx";
import { API_URL, fetchStations } from "./api.js";

// Panel statystyk z Recharts ładuje się dopiero po otwarciu, żeby nie spowalniać startu mapy.
const StatsPanel = lazy(() => import("./components/StatsPanel.jsx"));

function App() {
  const [stations, setStations] = useState(null);
  const [error, setError] = useState(null);
  // Jeden stan na oba panele, żeby otwarcie jednego zamykało drugi:
  // null, { type: "departures", station } albo { type: "stats" }.
  const [openPanel, setOpenPanel] = useState(null);

  useEffect(() => {
    // Przerywa zapytanie, gdy komponent zniknie (np. podwójne wywołanie w StrictMode).
    const controller = new AbortController();
    fetchStations(controller.signal)
      .then(setStations)
      .catch((fetchError) => {
        if (fetchError.name !== "AbortError") {
          setError(fetchError);
        }
      });
    return () => controller.abort();
  }, []);

  if (error) {
    return (
      <div className="status-message status-error" role="alert">
        <p>Nie udało się pobrać stacji z API.</p>
        <p>
          Sprawdź, czy API działa pod adresem <code>{API_URL}</code>.
        </p>
      </div>
    );
  }

  if (!stations) {
    return <p className="status-message">Wczytywanie stacji…</p>;
  }

  return (
    <div className="app-layout">
      <div className="map-area">
        <StationMap
          stations={stations}
          onSelectStation={(station) => setOpenPanel({ type: "departures", station })}
        />
        <button
          type="button"
          className="stats-button"
          onClick={() => setOpenPanel({ type: "stats" })}
        >
          Statystyki
        </button>
      </div>
      {openPanel?.type === "departures" && (
        <DeparturesPanel station={openPanel.station} onClose={() => setOpenPanel(null)} />
      )}
      {openPanel?.type === "stats" && (
        <Suspense
          fallback={
            <aside className="stats-panel">
              <p role="status">Wczytywanie statystyk…</p>
            </aside>
          }
        >
          <StatsPanel onClose={() => setOpenPanel(null)} />
        </Suspense>
      )}
    </div>
  );
}

export default App;
