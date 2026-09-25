import { useState, useEffect } from "react";
import useSWR from "swr";
import Layout from "../components/Layout";
import { fetcher, jsonFetcher, ErrorDisplay, LoadingDisplay, SPECIES_FILTER_OPTIONS } from "../lib/utils";
import { SPECIES_CATEGORIES } from "../lib/constants";
import { LuImage, LuMusic } from "react-icons/lu";

export default function SpeciesDistinct() {
  const [speciesRef, setSpeciesRef] = useState({});
  const [loadingRef, setLoadingRef] = useState(true);
  const [errorRef, setErrorRef] = useState(null);

  const [observations, setObservations] = useState([]);
  const [loadingObs, setLoadingObs] = useState(true);
  const [errorObs, setErrorObs] = useState(null);

  const [filterCategory, setFilterCategory] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedSpecies, setExpandedSpecies] = useState(new Set());
  const [speciesObservations, setSpeciesObservations] = useState({});
  const [loadingSpecies, setLoadingSpecies] = useState(new Set());

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

  const { data: swrObservations, error: swrError, isLoading: swrLoading } = useSWR(
    "/api/observations?limit=1000",
    fetcher
  );

  useEffect(() => {
    if (swrLoading) {
      setLoadingObs(true);
      setErrorObs(null);
    } else if (swrError) {
      setLoadingObs(false);
      setErrorObs(swrError.message);
    } else if (swrObservations) {
      setObservations(swrObservations);
      setLoadingObs(false);
      setErrorObs(null);
    }
  }, [swrObservations, swrError, swrLoading]);

  if (loadingRef || loadingObs) {
    return (
      <Layout>
        <LoadingDisplay message="Caricamento dati specie..." />
      </Layout>
    );
  }

  if (errorRef || errorObs) {
    return (
      <Layout>
        <ErrorDisplay
          message={errorRef ? "Impossibile caricare la lista di riferimento delle specie" : errorObs}
          onRetry={() => window.location.reload()}
        />
      </Layout>
    );
  }

  const speciesMap = new Map();
  observations.forEach((obs) => {
    const sp = obs.species;
    if (!sp) return;
    const current = speciesMap.get(sp) || { total: 0, image: 0, audio: 0 };
    current.total += 1;
    if (obs.method === "image") current.image += 1;
    else if (obs.method === "audio") current.audio += 1;
    speciesMap.set(sp, current);
  });

  const speciesList = Array.from(speciesMap.entries())
    .map(([species, counts]) => {
      let category = "normal";
      if (speciesRef.rare?.includes(species)) category = "rare";
      else if (speciesRef.protected?.includes(species)) category = "protected";
      else if (speciesRef.invasive?.includes(species)) category = "invasive";

      return {
        species,
        ...counts,
        category,
      };
    })
    .sort((a, b) => b.total - a.total);

  let filteredByCategory =
    filterCategory === "all"
      ? speciesList
      : speciesList.filter((s) => s.category === filterCategory);

  const filteredSpecies = filteredByCategory.filter(species =>
    species.species.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleExpanded = (species) => {
    setExpandedSpecies(prev => {
      const newSet = new Set(prev);
      if (newSet.has(species)) {
        newSet.delete(species);
      } else {
        newSet.add(species);
        setLoadingSpecies(prev => new Set([...prev, species]));
        fetcher(`/observations?species=${encodeURIComponent(species)}&limit=100`)
          .then((data) => {
            setSpeciesObservations(prev => ({
              ...prev,
              [species]: data
            }));
            setLoadingSpecies(prev => new Set([...prev].filter(s => s !== species)));
          })
          .catch((err) => {
            console.error(`Failed to load observations for ${species}:`, err);
            setLoadingSpecies(prev => new Set([...prev].filter(s => s !== species)));
          });
      }
      return newSet;
    });
  };

  return (
    <Layout>
      <div className="flex flex-col gap-8 p-4 lg:p-8 bg-gray-50 min-h-screen">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white md:text-3xl">
            Elenco delle specie osservate
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex flex-col md:flex-row gap-2">
              <label className="text-sm font-medium text-muted dark:text-gray-400">Filtra per categoria:</label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors"
              >
                {SPECIES_FILTER_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col md:flex-row gap-2">
              <label className="text-sm font-medium text-muted dark:text-gray-400">Cerca specie:</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Nome specie..."
                className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors"
              />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-6 transition-colors">
          {filteredSpecies.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-6">Nessuna specie trovata con i filtri selezionati</p>
          ) : (
            <div className="space-y-4">
              {filteredSpecies.map((sp) => {
                const isExpanded = expandedSpecies.has(sp.species);
                const isLoading = loadingSpecies.has(sp.species);
                const categoryConfig = SPECIES_CATEGORIES[sp.category] || SPECIES_CATEGORIES.normal;
                
                return (
                  <div key={sp.species} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden transition-colors">
                    <div className="flex items-center justify-between px-5 py-4 bg-gray-50 dark:bg-gray-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors" onClick={() => toggleExpanded(sp.species)}>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">{sp.species}</p>
                        <p className="text-sm text-muted dark:text-gray-400">
                          {sp.total} osservazioni totali
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${categoryConfig.color}`}>
                          {categoryConfig.label}
                        </span>
                        <div className="flex gap-2 text-sm">
                          <span className="flex items-center gap-1">
                            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            <span className="text-gray-600 dark:text-gray-300">{sp.image} foto</span>
                          </span>
                          <span className="flex items-center gap-1">
                            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                            <span className="text-gray-600 dark:text-gray-300">{sp.audio} audio</span>
                          </span>
                        </div>
                      </div>
                      <span className="text-xs text-muted dark:text-gray-400">
                        {isExpanded ? '▲' : '▼'}
                      </span>
                    </div>
                    {isExpanded && (
                      <div className="border-t border-gray-200 dark:border-gray-700">
                        {isLoading ? (
                          <div className="px-5 py-4 text-sm text-muted dark:text-gray-400">
                            Caricamento osservazioni...
                          </div>
                        ) : (
                          <div className="px-5 py-4">
                            {(speciesObservations[sp.species] || []).length === 0 ? (
                              <p className="text-gray-500 dark:text-gray-400 text-center py-2">Nessuna osservazione trovata</p>
                            ) : (
                              <div className="space-y-2">
                                {speciesObservations[sp.species].map((obs) => (
                                  <div key={obs.id} className="flex items-start gap-3 p-2 bg-gray-50 dark:bg-gray-700/50 rounded transition-colors">
                                    {obs.method === "image" && obs.media_url ? (
                                      <img
                                        src={obs.media_url}
                                        alt={`Foto di ${obs.species}`}
                                        className="w-16 h-16 object-cover rounded"
                                      />
                                    ) : (
                                      <LuMusic className="w-8 h-8 text-muted dark:text-gray-400" />
                                    )}
                                    <div className="flex-1">
                                      <p className="font-medium text-gray-900 dark:text-white">{obs.species}</p>
                                      <p className="text-sm text-muted dark:text-gray-400">
                                        {obs.method === "image" ? "Foto" : "Audio"} · 
                                        {new Date(obs.date_time).toLocaleString('it-IT', {
                                          day: '2-digit',
                                          month: '2-digit',
                                          year: 'numeric',
                                          hour: '2-digit',
                                          minute: '2-digit'
                                        })}
                                      </p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="mt-8 pt-4 border-t border-gray-200 dark:border-gray-700 text-sm text-muted dark:text-gray-400">
          <p>
            Dati aggiornati in tempo reale · Fonte: osservazioni dal backend
          </p>
        </div>
      </div>
    </Layout>
  );
}
