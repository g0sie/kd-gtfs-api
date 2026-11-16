// Odległość w metrach jako tekst: "850 m" albo "1,5 km".
export function formatDistance(meters) {
  const roundedMeters = Math.round(meters);
  if (roundedMeters < 1000) {
    return `${roundedMeters} m`;
  }
  const kilometers = (meters / 1000).toFixed(1).replace(".", ",");
  return `${kilometers} km`;
}
