import { useEffect, useState } from "react";
import { fetchDepartures } from "../api.js";

// Pobiera odjazdy ze stacji. Status: "loading", "success", "not-found" (404) albo "error".
export function useDepartures(stationId, { date, time }) {
  const requestKey = `${stationId}|${date}|${time}`;
  const [result, setResult] = useState({ requestKey: null });

  useEffect(() => {
    const key = `${stationId}|${date}|${time}`;
    const controller = new AbortController();
    fetchDepartures(stationId, { date, time }, controller.signal)
      .then((data) => setResult({ requestKey: key, status: "success", data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          const status = error.status === 404 ? "not-found" : "error";
          setResult({ requestKey: key, status });
        }
      });
    // Zmiana stacji lub parametrów przerywa poprzednie zapytanie, żeby stara odpowiedź
    // nie nadpisała nowej.
    return () => controller.abort();
  }, [stationId, date, time]);

  // Wynik dla innych parametrów jest nieaktualny, więc do czasu odpowiedzi pokazujemy ładowanie.
  if (result.requestKey !== requestKey) {
    return { status: "loading", data: null };
  }
  return { status: result.status, data: result.data ?? null };
}
