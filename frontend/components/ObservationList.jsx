import { useState } from "react";
import useSWR from "swr";
import { LuImage, LuMusic } from "react-icons/lu";
import { fetcher, buildFilterParams, formatDate, formatConfidence } from "../lib/utils";
import { VERIFICATION_STATUS } from "../lib/constants";

export default function ObservationList({ filters, data: passedData }) {
  const [expanded, setExpanded] = useState(false);

  // If data is passed as prop, use it; otherwise fetch from API
  const params = buildFilterParams(filters, {
    limit: expanded ? "20" : "5",
    order: "-date_time",
  });

  const { data, error } = useSWR(
    passedData ? null : `/observations?${params.toString()}`,
    fetcher
  );

  // Use passed data if available, otherwise use fetched data
  const observations = passedData ?? data;

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento delle osservazioni</div>;
  if (!passedData && (!data || !Array.isArray(data))) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento dati...</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">Ultime osservazioni</h2>
      <div className="space-y-3">
        {observations.length === 0 && (
          <p className="text-gray-500 text-center py-4">Nessuna osservazione trovata</p>
        )}
        {observations.map((obs) => (
          <a key={obs.id} href={`/observation/${obs.id}`} className="block">
            <div className="flex items-start gap-4 bg-gray-50 p-4 rounded-lg hover:shadow-md transition">
              {/* Anteprima immagine / icona audio */}
              <div className="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                {obs.method === "image" && obs.media_url ? (
                  <img
                    src={obs.media_url}
                    alt={`Foto di ${obs.species}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <LuMusic className="text-3xl text-muted" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-medium text-gray-900 truncate">{obs.species ?? "Specie sconosciuta"}</p>
                  <span className={`px-2 py-0.5 text-xs font-medium rounded ${VERIFICATION_STATUS[obs.verification_status]?.color || "bg-muted text-white"}`}>
                    {VERIFICATION_STATUS[obs.verification_status]?.label || "Sconosciuto"}
                  </span>
                </div>

                <p className="text-sm text-muted flex items-center gap-2">
                  <span className="flex items-center gap-1">
                    {obs.method === "image" ? <LuImage className="w-3 h-3" /> : <LuMusic className="w-3 h-3" />}
                    {obs.method === "image" ? "Foto" : "Audio"}
                  </span>
                  <span>·</span>
                  <span>{formatDate(obs.date_time)}</span>
                </p>

                {/* Confidence bar */}
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-muted mb-1">
                    <span>Confidenza</span>
                    <span>{formatConfidence(obs.confidence)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-success h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${(obs.confidence ?? 0) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>
      {!passedData && (
        <div className="mt-4 text-center">
          <button
            className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Mostra di meno" : "Mostra di più"}
          </button>
        </div>
      )}
    </div>
  );
}