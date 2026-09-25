import React, { useState, useEffect } from "react";
import useSWR from "swr";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Cell } from "recharts";
import { useRouter } from "next/router";
import { jsonFetcher, buildFilterParams } from "../lib/utils";
import { CHART_COLORS, SPECIES_CATEGORIES } from "../lib/constants";

export default function SpeciesDistributionChart({ filters }) {
  const [speciesRef, setSpeciesRef] = useState({});
  const [loadingRef, setLoadingRef] = useState(true);
  const [errorRef, setErrorRef] = useState(null);

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

  if (error) return <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-red-500 transition-colors">Errore nel caricamento della distribuzione</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-gray-500 dark:text-gray-400 transition-colors">Caricamento dati...</div>;
  
  const counts = {};
  const speciesCategories = {};
  data.forEach((obs) => {
    const sp = obs.species || "Sconosciuta";
    counts[sp] = (counts[sp] || 0) + 1;
    
    let category = "normal";
    if (speciesRef.rare?.includes(sp)) category = "rare";
    else if (speciesRef.protected?.includes(sp)) category = "protected";
    else if (speciesRef.invasive?.includes(sp)) category = "invasive";
    
    speciesCategories[sp] = category;
  });

  const chartData = Object.entries(counts).map(([species, count]) => ({
    species,
    count,
    category: speciesCategories[species] || "normal"
  }));

  chartData.sort((a, b) => b.count - a.count);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
      <h2 className="text-lg font-semibold mb-4 text-primary dark:text-blue-400">
        Distribuzione osservazioni per specie
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart layout="vertical" data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
          <XAxis type="number" tick={{ fontSize: 12, fill: "currentColor" }} className="text-gray-500 dark:text-gray-400" />
          <YAxis
            type="category"
            dataKey="species"
            tick={{ fontSize: 12, fill: "currentColor" }}
            className="text-gray-500 dark:text-gray-400"
            width={120}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload || payload.length === 0) return null;
              const { species, count, category } = payload[0].payload;
              return (
                <div
                  className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-xl border-2 border-slate-200 dark:border-gray-600 flex flex-col items-start gap-2"
                  onClick={() => router.push(`/species/${encodeURIComponent(species)}`)}
                  style={{ cursor: "pointer", userSelect: "none", minWidth: "150px" }}
                >
                  <div className="font-bold text-gray-900 dark:text-white">{species}</div>
                  <div className="text-sm text-muted dark:text-gray-400">{count} osservazioni</div>
                  {!loadingRef && (
                    <div className="text-xs font-medium text-primary dark:text-blue-400">
                      Categoria: {SPECIES_CATEGORIES[category]?.label || category}
                    </div>
                  )}
                </div>
              );
            }}
          />
          <Bar 
            dataKey="count" 
            fill="#27ae60" 
            radius={[0, 4, 4, 0]} 
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
