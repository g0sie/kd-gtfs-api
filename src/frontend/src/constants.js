// Dni wzorcowe do statystyk (docs/decisions.md, docs/reference-day.md).
export const WORKDAY_REFERENCE_DATE = "2026-11-24";
export const WEEKEND_REFERENCE_DATE = "2026-11-22";

// Klasy warstwy odcinków według kursów na dobę (trips_per_day). Dobrane pod zakres 4–160
// z docs/segments.md: w najwyższej klasie są promienie wychodzące z Wrocławia (102–160).
// min to dolna granica klasy, a górną wyznacza min następnej klasy. Skala niebieska,
// bo czerwienie i pomarańcze zlewały się z drogami na podkładzie OSM.
export const SEGMENT_CLASSES = [
  { min: 0, color: "#86b9d8", weight: 1.5 },
  { min: 15, color: "#6baed6", weight: 3 },
  { min: 30, color: "#3182bd", weight: 5 },
  { min: 60, color: "#08519c", weight: 8 },
  { min: 100, color: "#08306b", weight: 11 },
];
