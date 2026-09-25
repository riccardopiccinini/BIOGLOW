import useSWR from "swr";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { useRouter } from "next/router";
import { LuMusic, LuImage } from "react-icons/lu";

const fetcher = (url) => fetch(url).then((r) => {
  if (!r.ok) throw new Error("API error");
  return r.json();
});

export default function MethodDistributionChart({ filters }) {
  const router = useRouter();
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
  if (!data || !Array.isArray(data)) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento dati...</div>;

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
          <Tooltip
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "8px" }}
            content={({ active, payload }) => {
              if (active === null || payload.length === 0) return null;
              const { name } = payload[0].payload;
              const method = name === "Audio" ? "audio" : "image";
              return (
                <div
                  className="flex flex-col items-start gap-2"
                  onClick={() => router.push(`/method/${method}`)}
                  style={{ cursor: "pointer", userSelect: "none" }}
                >
                  <div className="font-medium">{name}</div>
                  <div className="text-sm text-muted">{payload[0].value} osservazioni</div>
                </div>
              );
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-6 flex flex-wrap justify-center gap-4">
        <button 
          onClick={() => router.push("/method/audio")}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition shadow-sm"
        >
          <LuMusic className="w-4 h-4" />
          Vedi tutti gli Audio
        </button>
        <button 
          onClick={() => router.push("/method/image")}
          className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition shadow-sm"
        >
          <LuImage className="w-4 h-4" />
          Vedi tutte le Foto
        </button>
      </div>
    </div>
  );
}
