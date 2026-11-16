// Godzina odjazdu z GTFS jako godzina zegarowa. GTFS liczy czas od początku doby kursu,
// więc "24:48:00" to 00:48 następnego dnia: { time: "00:48", isNextDay: true }.
export function formatDepartureTime(gtfsTime) {
  const [hours, minutes] = gtfsTime.split(":").map(Number);
  const clockHours = String(hours % 24).padStart(2, "0");
  const clockMinutes = String(minutes).padStart(2, "0");
  return { time: `${clockHours}:${clockMinutes}`, isNextDay: hours >= 24 };
}
