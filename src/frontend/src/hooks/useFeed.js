import { useEffect, useState } from "react";
import { fetchFeed } from "../api.js";

// Pobiera raz zakres obowiązywania rozkładu. Status: "loading", "success" albo "error".
export function useFeed() {
  const [result, setResult] = useState({ status: "loading", data: null });

  useEffect(() => {
    // Przerywa zapytanie, gdy komponent zniknie (np. podwójne wywołanie w StrictMode).
    const controller = new AbortController();
    fetchFeed(controller.signal)
      .then((data) => setResult({ status: "success", data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setResult({ status: "error", data: null });
        }
      });
    return () => controller.abort();
  }, []);

  return result;
}
