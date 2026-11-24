import { useCallback, useEffect, useRef, useState } from "react";
import { fetchNearestStation } from "../api.js";

// Szuka najbliższej stacji dla wskazanego punktu. Status: "idle", "loading" albo "error".
export function useNearestStation() {
  const [clickedPoint, setClickedPoint] = useState(null);
  const [nearestStation, setNearestStation] = useState(null);
  const [status, setStatus] = useState("idle");
  const controllerRef = useRef(null);

  useEffect(() => () => controllerRef.current?.abort(), []);

  const findNearestStation = useCallback(({ lat, lng }) => {
    // Przerywa poprzednie zapytanie, żeby spóźniona odpowiedź nie nadpisała nowej.
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setClickedPoint([lat, lng]);
    setNearestStation(null);
    setStatus("loading");

    fetchNearestStation(lat, lng, controller.signal)
      .then((station) => {
        setNearestStation(station);
        setStatus(station ? "idle" : "error");
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setStatus("error");
        }
      });
  }, []);

  // Usuwa z mapy punkt kliknięcia i znalezioną stację.
  const clearNearestStation = useCallback(() => {
    controllerRef.current?.abort();
    setClickedPoint(null);
    setNearestStation(null);
    setStatus("idle");
  }, []);

  return { clickedPoint, nearestStation, status, findNearestStation, clearNearestStation };
}
