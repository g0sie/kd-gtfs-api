// Zakres obowiązywania rozkładu (docs/decisions.md).
export const FEED_START = "2026-10-19";
export const FEED_END = "2026-12-12";

// Dni wzorcowe do statystyk (docs/decisions.md, docs/reference-day.md).
export const WORKDAY_REFERENCE_DATE = "2026-11-24";
export const WEEKEND_REFERENCE_DATE = "2026-11-22";

// Klasy warstwy odcinków według kursów na dobę (trips_per_day). Dobrane pod zakres 4–160
// z docs/segments.md: w najwyższej klasie są promienie wychodzące z Wrocławia (102–160).
// min to dolna granica klasy, a górną wyznacza min następnej klasy.
export const SEGMENT_CLASSES = [
  { min: 0, color: "#fdbb84", weight: 2 },
  { min: 15, color: "#fc8d59", weight: 3 },
  { min: 30, color: "#ef6548", weight: 4 },
  { min: 60, color: "#d7301f", weight: 6 },
  { min: 100, color: "#990000", weight: 8 },
];
