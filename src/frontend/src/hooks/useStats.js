import { useEffect, useState } from "react";
import { fetchStats } from "../api.js";

// Pobiera statystyki dla dnia. Status: "loading", "success" albo "error".
export function useStats(date) {
  const [result, setResult] = useState({ requestKey: null });

  useEffect(() => {
    const controller = new AbortController();
    fetchStats(date, controller.signal)
      .then((data) => setResult({ requestKey: date, status: "success", data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setResult({ requestKey: date, status: "error" });
        }
      });
    // Zmiana daty przerywa poprzednie zapytanie, żeby stara odpowiedź nie nadpisała nowej.
    return () => controller.abort();
  }, [date]);

  // Wynik dla innej daty jest nieaktualny, więc do czasu odpowiedzi pokazujemy ładowanie.
  if (result.requestKey !== date) {
    return { status: "loading", data: null };
  }
  return { status: result.status, data: result.data ?? null };
}
