import { useState } from "react";
import { useRouter } from "next/router";
import useSWR from "swr";
import { jsonFetcher, buildFilterParams } from "../lib/utils";
import { ALERT_TYPES, VERIFICATION_STATUS } from "../lib/constants";

export default function AlertList({ statusFilter = "" }) {
  const [expanded, setExpanded] = useState(false);
  const router = useRouter();
  const params = buildFilterParams({}, { status: statusFilter });

  const { data, error } = useSWR(
    `/alerts?${params.toString()}`,
    jsonFetcher
  );

  // Now we only use real data from the server. No more mocks.
  const alertsData = (data && Array.isArray(data)) ? data : [];

  // Filter: only protected and invasive
  const filteredAlerts = alertsData.filter(a => a.alert_type === 'protected' || a.alert_type === 'invasive');
  const alerts = filteredAlerts.slice(0, expanded ? 20 : 5);

  if (error) return <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-red-500 transition-colors">Errore nel caricamento degli alert</div>;
  if (!data) return <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-gray-500 dark:text-gray-400 transition-colors">Caricamento dati...</div>;

  const getAlertTypeStyle = (type) => {
    if (type === 'protected') return "bg-blue-600 text-white";
    if (type === 'invasive') return "bg-red-600 text-white";
    return "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300";
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
      <h2 className="text-lg font-semibold mb-4 text-primary dark:text-blue-400">Alert specie di interesse</h2>
      {alerts.length === 0 && (
        <p className="text-gray-500 dark:text-gray-400 text-center py-4">Nessun alert</p>
      )}
      <div className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            onClick={() => router.push(`/species/${encodeURIComponent(alert.species)}`)}
            className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:shadow-md transition cursor-pointer"
          >
            <div>
              <p className="font-medium text-gray-900 dark:text-white">{alert.species}</p>
              <span className={`px-2 py-0.5 text-xs font-bold rounded ${getAlertTypeStyle(alert.alert_type)}`}>
                {ALERT_TYPES[alert.alert_type]?.label || alert.alert_type}
              </span>
            </div>
            <span className={`px-3 py-1 text-xs font-medium rounded ${VERIFICATION_STATUS[alert.status]?.color || "bg-muted text-white"}`}>
              {VERIFICATION_STATUS[alert.status]?.label || "Sconosciuto"}
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
