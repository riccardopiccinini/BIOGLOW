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

  const [filterCategory, setFilterCategory] = useState("all"); // all, rare, protected, invasive, normal
  const [searchTerm, setSearchTerm] = useState(""); // Search term for filtering species
  const [expandedSpecies, setExpandedSpecies] = useState(new Set()); // Track expanded species
  const [speciesObservations, setSpeciesObservations] = useState({}); // Store observations per species
  const [loadingSpecies, setLoadingSpecies] = useState(new Set()); // Track loading state per species

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
        setSpeciesRef({ rare: [], protected: [], invasive: [] }); // empty defaults
        setLoadingRef(false);
      });
  }, []);

  // Load observations with SWR for better caching and performance
  const { data: swrObservations, error: swrError, isLoading: swrLoading } = useSWR(
    "/api/observations?limit=5000",
    fetcher
  );

  // Update local state from SWR data
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

  // Aggregate observations by species
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

  // Convert to array and add category
  const speciesList = Array.from(speciesMap.entries())
    .map(([species, counts]) => {
      // Determine category from species_ref
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
    .sort((a, b) => b.total - a.total); // sort by total count descending

  // Apply category filter
  // When "all" is selected, show only protected and invasive species (hide rare and normal)
  let filteredByCategory =
    filterCategory === "all"
      ? speciesList.filter(s => s.category === 'protected' || s.category === 'invasive')
      : filterCategory === "normal"
      ? speciesList.filter((s) => s.category === "normal")
      : speciesList.filter((s) => s.category === filterCategory);

  // Apply search filter
  const filteredSpecies = filteredByCategory.filter(species =>
    species.species.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Function to toggle expanded state
  const toggleExpanded = (species) => {
    setExpandedSpecies(prev => {
      const newSet = new Set(prev);
      if (newSet.has(species)) {
        newSet.delete(species);
      } else {
        newSet.add(species);
        // Fetch observations for this species when expanded
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
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h1 className="text-2xl font-extrabold text-gray-900 md:text-3xl">
            Elenco delle specie osservate
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex flex-col md:flex-row gap-2">
              <label className="text-sm font-medium text-muted">Filtra per categoria:</label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
              >
                {SPECIES_FILTER_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col md:flex-row gap-2">
              <label className="text-sm font-medium text-muted">Cerca specie:</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Nome specie..."
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-md p-6">
          {filteredSpecies.length === 0 ? (
            <p className="text-gray-500 text-center py-6">Nessuna specie trovata con i filtri selezionati</p>
          ) : (
            <div className="space-y-4">
              {filteredSpecies.map((sp) => {
                const isExpanded = expandedSpecies.has(sp.species);
                const isLoading = loadingSpecies.has(sp.species);
                const categoryConfig = SPECIES_CATEGORIES[sp.category] || SPECIES_CATEGORIES.normal;
                
                return (
                  <div key={sp.species} className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="flex items-center justify-between px-5 py-4 bg-gray-50 cursor-pointer" onClick={() => toggleExpanded(sp.species)}>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{sp.species}</p>
                        <p className="text-sm text-muted">
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
                            <span>{sp.image} foto</span>
                          </span>
                          <span className="flex items-center gap-1">
                            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                            <span>{sp.audio} audio</span>
                          </span>
                        </div>
                      </div>
                      <span className="text-xs">
                        {isExpanded ? '▲' : '▼'}
                      </span>
                    </div>
                    {/* Expandable observations list */}
                    {isExpanded && (
                      <div className="border-t border-gray-200">
                        {isLoading ? (
                          <div className="px-5 py-4 text-sm text-muted">
                            Caricamento osservazioni...
                          </div>
                        ) : (
                          <div className="px-5 py-4">
                            {(speciesObservations[sp.species] || []).length === 0 ? (
                              <p className="text-gray-500 text-center py-2">Nessuna osservazione trovata</p>
                            ) : (
                              <div className="space-y-2">
                                {speciesObservations[sp.species].map((obs) => (
                                  <div key={obs.id} className="flex items-start gap-3 p-2 bg-gray-50 rounded">
                                    {obs.method === "image" && obs.media_url ? (
                                      <img
                                        src={obs.media_url}
                                        alt={`Foto di ${obs.species}`}
                                        className="w-16 h-16 object-cover rounded"
                                      />
                                    ) : (
                                      <LuMusic className="w-8 h-8 text-muted" />
                                    )}
                                    <div className="flex-1">
                                      <p className="font-medium text-gray-900">{obs.species}</p>
                                      <p className="text-sm text-muted">
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

        <div className="mt-8 pt-4 border-t border-gray-200 text-sm text-muted">
          <p>
            Dati aggiornati in tempo reale · Fonte: osservazioni dal backend
          </p>
        </div>
      </div>
    </Layout>
  );
}
