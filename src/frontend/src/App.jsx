import { useEffect, useState } from "react";
import StationMap from "./components/StationMap.jsx";
import { API_URL, fetchStations } from "./api.js";

function App() {
  const [stations, setStations] = useState(null);
  const [error, setError] = useState(null);

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

  return <StationMap stations={stations} />;
}

export default App;
