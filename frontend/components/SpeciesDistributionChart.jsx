import useSWR from "swr";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

const fetcher = (url) => fetch(url).then((r) => r.json());

export default function SpeciesDistributionChart({ filters }) {
  const params = new URLSearchParams();
  if (filters.station) params.append("station_id", filters.station);
  if (filters.method) params.append("method", filters.method);
  if (filters.startDate) params.append("start", filters.startDate);
  if (filters.endDate) params.append("end", filters.endDate);
  params.append("limit", "1000");

  const { data, error } = useSWR(
    `/observations?${params.toString()}`,
    fetcher
  );

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento della distribuzione</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento…</div>;

  // conta per specie
  const counts = {};
  data.forEach((obs) => {
    const sp = obs.species || "Sconosciuta";
    counts[sp] = (counts[sp] || 0) + 1;
  });
  const chartData = Object.entries(counts).map(([species, count]) => ({
    species,
    count,
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">
        Distribuzione osservazioni per specie
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" tick={{ fontSize: 12, fill: "#6b7280" }} />
          <YAxis
            type="category"
            dataKey="species"
            tick={{ fontSize: 12, fill: "#6b7280" }}
            width={120}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
            formatter={(value) => [value, "osservazioni"]}
          />
          <Bar dataKey="count" fill="#27ae60" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}