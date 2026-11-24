import { SEGMENT_CLASSES } from "../constants.js";

// Klasa odcinka (kolor i grubość) dla liczby kursów na dobę.
export function segmentClass(tripsPerDay) {
  return SEGMENT_CLASSES.findLast((candidate) => tripsPerDay >= candidate.min);
}

// Podpis klasy w legendzie: "do 14", "15–29", …, "100 i więcej".
export function segmentClassLabel(index) {
  const { min } = SEGMENT_CLASSES[index];
  const next = SEGMENT_CLASSES[index + 1];
  if (!next) {
    return `${min} i więcej`;
  }
  if (index === 0) {
    return `do ${next.min - 1}`;
  }
  return `${min}–${next.min - 1}`;
}
