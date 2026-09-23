import useSWR from "swr";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { format } from "date-fns";

const fetcher = (url) => fetch(url).then((r) => {
  if (!r.ok) throw new Error("API error");
  return r.json();
});

export default function ShannonLineChart({ interval = "month" }) {
  const { data, error } = useSWR(
    `/observations/shannon-time?interval=${interval}`,
    fetcher
  );

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento dei dati Shannon</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento…</div>;

  // data atteso: [{ date: "2026-09-01T00:00:00Z", value: 1.23 }, ...]
  const chartData = data.map((d) => ({
    date: d.date ? format(new Date(d.date), "dd MMM") : "N/A",
    value: d.value ?? 0,
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">
        Andamento indice di Shannon ({interval === "month" ? "mensile" : "settimanale"})
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#6b7280" }} />
          <YAxis tick={{ fontSize: 12, fill: "#6b7280" }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
            formatter={(value) => [typeof value === 'number' ? value.toFixed(3) : value, "Shannon"]}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#3498db"
            strokeWidth={2}
            dot={{ fill: "#3498db", strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
