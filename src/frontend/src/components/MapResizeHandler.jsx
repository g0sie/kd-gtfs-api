import { useEffect } from "react";
import { useMap } from "react-leaflet";

// Leaflet sam reaguje tylko na zmianę rozmiaru okna. Gdy obok mapy pojawia się panel,
// kontener mapy się zwęża i bez invalidateSize część mapy zostaje szara.
function MapResizeHandler() {
  const map = useMap();

  useEffect(() => {
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(map.getContainer());
    return () => observer.disconnect();
  }, [map]);

  return null;
}

export default MapResizeHandler;
