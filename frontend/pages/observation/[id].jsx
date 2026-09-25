import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";
import { LuArrowLeft, LuCircleCheck, LuCircleX, LuClock, LuMusic, LuImage } from "react-icons/lu";
import { fetcher, ErrorDisplay, LoadingDisplay, formatDate, formatConfidence } from "../../lib/utils";
import { VERIFICATION_STATUS, OBSERVATION_METHODS } from "../../lib/constants";

export default function ObservationDetail() {
  const router = useRouter();
  const { id } = router.query;

  const { data: obs, error, mutate } = useSWR(
    id ? `/observations/${id}` : null,
    fetcher
  );

  const updateStatus = async (newStatus) => {
    try {
      await fetch(`/observations/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ verification_status: newStatus }),
      });
      mutate(); // Ricarica i dati
    } catch (e) {
      alert("Errore durante l'aggiornamento dello stato");
    }
  };

  if (error) return <Layout><ErrorDisplay message={error.message} /></Layout>;
  if (!obs) return <Layout><LoadingDisplay message="Caricamento..." /></Layout>;

  const statusConfig = {
    confirmed: { label: "Confermata", color: "bg-success", icon: <LuCircleCheck /> },
    excluded: { label: "Esclusa", color: "bg-danger", icon: <LuCircleX /> },
    pending: { label: "In attesa", color: "bg-warning", icon: <LuClock /> },
  };

  const methodConfig = OBSERVATION_METHODS[obs.method] || OBSERVATION_METHODS.image;

  return (
    <Layout>
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-muted hover:text-primary transition mb-6"
      >
        <LuArrowLeft /> Torna alla Dashboard
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sezione Multimediale */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
          <div className="aspect-video bg-gray-100 flex items-center justify-center relative">
            {obs.method === "image" && obs.media_url ? (
              <img src={obs.media_url} alt={obs.species} className="w-full h-full object-contain" />
            ) : (
              <div className="text-center p-8">
                <div className={`${methodConfig.bgColor} p-6 rounded-full inline-block mb-4`}>
                  {methodConfig.icon === "music" ? (
                    <LuMusic className="w-12 h-12 text-blue-600" />
                  ) : (
                    <LuImage className="w-12 h-12 text-green-600" />
                  )}
                </div>
                <p className="text-gray-500">File Audio</p>
                <audio controls className="mt-4 w-full">
                  <source src={obs.media_url} type="audio/mpeg" />
                  Il tuo browser non supporta l'elemento audio.
                </audio>
              </div>
            )}
          </div>
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{obs.species}</h1>
            <p className="text-muted">{formatDate(obs.date_time)}</p>
          </div>
        </div>

        {/* Sezione Dettagli e Controllo */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 text-primary">Analisi IA</h2>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted">Affidabilità (Confidence)</span>
                  <span className="font-bold text-gray-900">{formatConfidence(obs.confidence)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-success h-full transition-all duration-500"
                    style={{ width: `${(obs.confidence ?? 0) * 100}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="p-4 bg-gray-50 rounded-xl">
                  <span className="block text-xs text-muted mb-1">Stazione</span>
                  <span className="font-medium">{obs.station_id}</span>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <span className="block text-xs text-muted mb-1">Metodo</span>
                  <span className="font-medium">{methodConfig.label}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 text-primary">Verifica Operatore</h2>
            <p className="text-sm text-muted mb-4">
              Stato attuale:
              <span className={` ml-2 px-2 py-1 rounded text-xs font-bold text-white ${statusConfig[obs.verification_status]?.color || "bg-gray-400"}`}>
                {statusConfig[obs.verification_status]?.label || "Sconosciuto"}
              </span>
            </p>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(statusConfig).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => updateStatus(key)}
                  className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                    obs.verification_status === key
                    ? `border-${config.color.split('-')[1]} shadow-inner ${config.color} text-white`
                    : "border-gray-100 hover:border-primary text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <div className="text-2xl mb-1">{config.icon}</div>
                  <span className="text-xs font-medium">{config.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}