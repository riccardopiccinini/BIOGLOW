import useSWR from "swr";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { useRouter } from "next/router";
import { jsonFetcher, buildFilterParams } from "../lib/utils";
import { CHART_COLORS, SPECIES_CATEGORIES } from "../lib/constants";

export default function SpeciesDistributionChart({ filters }) {
  const [speciesRef, setSpeciesRef] = useState({});
  const [loadingRef, setLoadingRef] = useState(true);
  const [errorRef, setErrorRef] = useState(null);

  // Load species reference
  useEffect(() => {
    setLoadingRef(true);
    jsonFetcher("/docs/species_reference.json")
      .then((data) => {
        setSpeciesRef(data);
        setLoadingRef(false);
      })
      .catch((err) => {
        console.warn("Failed to load species reference:", err);
        setSpeciesRef({ rare: [], protected: [], invasive: [] });
        setLoadingRef(false);
      });
  }, []);
  const router = useRouter();
  const params = buildFilterParams(filters, { limit: "1000" });

  const { data, error } = useSWR(
    `/observations?${params.toString()}`,
    jsonFetcher
  );

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento della distribuzione</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento dati...</div>;
  
  const counts = {};
  const speciesCategories = {}; // To track category for each species
  data.forEach((obs) => {
    const sp = obs.species || "Sconosciuta";
    counts[sp] = (counts[sp] || 0) + 1;
    
    // Determine category from species reference
    let category = "normal";
    if (speciesRef.rare?.includes(sp)) category = "rare";
    else if (speciesRef.protected?.includes(sp)) category = "protected";
    else if (speciesRef.invasive?.includes(sp)) category = "invasive";
    
    speciesCategories[sp] = category;
  });

  // Convert counts to chart data array
  const chartData = Object.entries(counts).map(([species, count]) => ({
    species,
    count,
    category: speciesCategories[species] || "normal"
  }));

  // Sort by count descending
  chartData.sort((a, b) => b.count - a.count);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">
        Distribuzione osservazioni per specie
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart layout="vertical" data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" tick={{ fontSize: 12, fill: "#6b7280" }} />
          <YAxis
            type="category"
            dataKey="species"
            tick={{ fontSize: 12, fill: "#6b7280" }}
            width={120}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "8px" }}
            content={({ active, payload }) => {
              if (!active || !payload || payload.length === 0) return null;
              const { species, count, category } = payload[0].payload;
              return (
                <div
                  className="flex flex-col items-start gap-2"
                  onClick={() => router.push(`/species/${encodeURIComponent(species)}`)}
                  style={{ cursor: "pointer", userSelect: "none" }}
                >
                  <div className="font-medium">{species}</div>
                  <div className="text-sm text-muted">{count} osservazioni</div>
                  {!loadingRef && speciesRef[category] && (
                    <div className="text-xs text-muted">
                      Categoria: {SPECIES_CATEGORIES[category]?.label || category}
                    </div>
                  )}
                </div>
              );
            }}
          />
          <Bar 
            dataKey="count" 
            fill={(bar) => {
              const category = bar.data.category || 'normal';
              const categoryConfig = SPECIES_CATEGORIES[category] || SPECIES_CATEGORIES.normal;
              return categoryConfig.chartColor;
            }} 
            radius={[0, 4, 4, 0]} 
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
