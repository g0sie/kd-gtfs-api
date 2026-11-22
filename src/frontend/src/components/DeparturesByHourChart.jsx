import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const AFTER_MIDNIGHT_HOUR = 24;

// Podpisy co 4 godziny: przy co 3 podpis „21” nachodził w panelu 360 px na „po północy”.
function formatHourTick(hour) {
  if (hour === AFTER_MIDNIGHT_HOUR) {
    return "po północy";
  }
  return hour % 4 === 0 ? String(hour) : "";
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
