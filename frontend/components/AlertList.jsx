import useSWR from "swr";

const fetcher = (url) => fetch(url).then((r) => r.json());

const typeLabels = {
  rare: "Rara",
  protected: "Protetta",
  invasive: "Invasiva",
};

const statusStyles = {
  confirmed: "bg-success text-white",
  excluded: "bg-danger text-white",
  pending: "bg-warning text-white",
};

const statusLabels = {
  confirmed: "Confermata",
  excluded: "Esclusa",
  pending: "In attesa",
};

const typeColors = {
  rare: "bg-purple-100 text-purple-800",
  protected: "bg-blue-100 text-blue-800",
  invasive: "bg-red-100 text-red-800",
};

export default function AlertList({ statusFilter = "" }) {
  const params = new URLSearchParams();
  if (statusFilter) params.append("status", statusFilter);

  const { data, error } = useSWR(
    `/alerts?${params.toString()}`,
    fetcher
  );

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento degli alert</div>;
  if (!data || !Array.isArray(data)) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento…</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">Alert specie di interesse</h2>
      {data.length === 0 && (
        <p className="text-gray-500 text-center py-4">Nessun alert</p>
      )}
      <div className="space-y-3">
        {data.map((alert) => (
          <div key={alert.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">{alert.species}</p>
              <span className={`px-2 py-0.5 text-xs font-medium rounded ${typeColors[alert.alert_type] || "bg-gray-100 text-gray-700"}`}>
                {typeLabels[alert.alert_type] || alert.alert_type}
              </span>
            </div>
            <span className={`px-3 py-1 text-xs font-medium rounded ${statusStyles[alert.status] || "bg-muted text-white"}`}>
              {statusLabels[alert.status] || "Sconosciuto"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}