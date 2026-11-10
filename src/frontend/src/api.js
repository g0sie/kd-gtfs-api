// Adres API z pliku .env (VITE_API_URL). Bez niego (lub gdy jest pusty) front zakłada API
// uruchomione lokalnie. Ukośnik na końcu jest obcinany, żeby nie powstało "//stations".
export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

// Zwraca wszystkie stacje jako GeoJSON FeatureCollection (kontrakt: GET /stations).
export async function fetchStations(signal) {
  const response = await fetch(`${API_URL}/stations`, { signal });
  if (!response.ok) {
    throw new Error(`API zwróciło status ${response.status}`);
  }
  return response.json();
}
