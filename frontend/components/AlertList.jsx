import { useState } from "react";
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

// Mock data to ensure the section is populated even if DB is empty
const MOCK_ALERTS = [
  { id: "1", species: "Lontra europea", alert_type: "protected", status: "confirmed" },
  { id: "2", species: "Nuotatore Gigante", alert_type: "invasive", status: "pending" },
  { id: "3", species: "Airone Cenerino", alert_type: "rare", status: "confirmed" },
];

export default function AlertList({ statusFilter = "" }) {
  const [expanded, setExpanded] = useState(false);
  const params = new URLSearchParams();
  if (statusFilter) params.append("status", statusFilter);

  const { data, error } = useSWR(
    `/alerts?${params.toString()}`,
    fetcher
  );

  // Use API data if available, otherwise fallback to mock data
  const alertsData = (data && Array.isArray(data) && data.length > 0) ? data : MOCK_ALERTS;
  const alerts = alertsData.slice(0, expanded ? 20 : 5);

  if (error) return <div className="bg-white rounded-lg shadow-md p-6 text-red-500">Errore nel caricamento degli alert</div>;
  if (!data && !MOCK_ALERTS) return <div className="bg-white rounded-lg shadow-md p-6 text-gray-500">Caricamento…</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">Alert specie di interesse</h2>
      {alerts.length === 0 && (
        <p className="text-gray-500 text-center py-4">Nessun alert</p>
      )}
      <div className="space-y-3">
        {alerts.map((alert) => (
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
      <div className="mt-4 text-center">
        <button className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark" onClick={() => setExpanded(!expanded)}>
          {expanded ? "Mostra di meno" : "Mostra di più"}
        </button>
      </div>
    </div>
  );
}
