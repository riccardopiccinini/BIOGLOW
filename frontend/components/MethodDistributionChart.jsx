import useSWR from "swr";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const fetcher = (url) => fetch(url).then((r) => {
  if (!r.ok) throw new Error("API error");
  return r.json();
});

export default function MethodDistributionChart({ filters }) {
  const params = new URLSearchParams();
  if (filters.station) params.append("station_id", filters.station);
  if (filters.startDate) params.append("start", filters.startDate);
  if (filters.endDate) params.append("end", filters.endDate);
  params.append("limit", "1000");

  const { data, error } = useSWR(
    `/observations?${params.toString()}`,
    fetcher
  );

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento dei metodi</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento…</div>;

  const counts = { audio: 0, image: 0 };
  data.forEach((obs) => {
    if (obs.method === "audio") counts.audio++;
    else if (obs.method === "image") counts.image++;
  });

  const chartData = [
    { name: "Audio", value: counts.audio, color: "#3498db" },
    { name: "Foto", value: counts.image, color: "#2ecc71" },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">Metodi di Raccolta</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
