import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const AFTER_MIDNIGHT_HOUR = 24;

// Podpisy co 3 godziny, żeby 25 słupków zmieściło się w wąskim panelu.
function formatHourTick(hour) {
  if (hour === AFTER_MIDNIGHT_HOUR) {
    return "po północy";
  }
  return hour % 3 === 0 ? String(hour) : "";
}

function formatHourLabel(hour) {
  if (hour === AFTER_MIDNIGHT_HOUR) {
    return "Po północy (od 24:00 doby kursu)";
  }
  return `${hour}:00–${hour}:59`;
}

function DeparturesByHourChart({ departuresByHour }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={departuresByHour} margin={{ top: 8, right: 28, bottom: 0, left: -16 }}>
        <XAxis
          dataKey="hour"
          interval={0}
          tickFormatter={formatHourTick}
          tick={{ fontSize: 12 }}
        />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip
          labelFormatter={formatHourLabel}
          formatter={(value) => [value, "Odjazdy"]}
        />
        <Bar dataKey="departures" fill="#1565c0" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default DeparturesByHourChart;
