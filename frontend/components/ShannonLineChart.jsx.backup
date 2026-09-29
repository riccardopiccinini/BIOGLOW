import useSWR from "swr";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { formatShortDate, fetcher, buildFilterParams } from "../lib/utils";
import { CHART_COLORS, CHART_DEFAULTS } from "../lib/constants";

export default function ShannonLineChart({ interval = "month", filters = {} }) {
  const params = buildFilterParams(filters, { interval });

  const { data, error } = useSWR(
    `/observations/shannon-time?${params.toString()}`,
    fetcher
  );

  if (error) return <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-red-500 transition-colors">Errore nel caricamento dei dati Shannon</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-gray-500 dark:text-gray-400 transition-colors">Caricamento dati...</div>;

  const chartData = data.map((d) => ({
    date: d.date ? formatShortDate(d.date) : "N/A",
    value: d.value ?? 0,
  }));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
      <h2 className="text-lg font-semibold mb-4 text-primary dark:text-blue-400">
        Andamento indice di Shannon ({interval === "month" ? "mensile" : "settimanale"})
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12, fill: "currentColor" }} 
            className="text-gray-500 dark:text-gray-400"
          />
          <YAxis 
            tick={{ fontSize: 12, fill: "currentColor" }} 
            className="text-gray-500 dark:text-gray-400"
          />
          <Tooltip
            contentStyle={{ 
              backgroundColor: "var(--bg-card, #fff)", 
              borderColor: "#e5e7eb", 
              borderRadius: "8px",
              color: "currentColor"
            }}
            className="dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            formatter={(value) => [typeof value === 'number' ? value.toFixed(3) : value, "Shannon"]}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={CHART_COLORS.primary}
            strokeWidth={2}
            dot={{ fill: CHART_COLORS.primary, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
