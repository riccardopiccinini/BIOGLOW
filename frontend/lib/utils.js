/**
 * Shared utilities for the Monitor Secchia Dashboard
 * Centralizes common functions to avoid duplication across components
 */

import { format } from "date-fns";

/**
 * Standard fetcher for SWR - handles errors consistently
 */
export const fetcher = (url) => fetch(url).then((r) => {
  if (!r.ok) throw new Error("API error");
  return r.json();
});

/**
 * JSON-only fetcher (no error throwing on non-ok)
 */
export const jsonFetcher = (url) => fetch(url).then((r) => r.json());

/**
 * Build filter query parameters from filter object
 * @param {Object} filters - { station, method, startDate, endDate }
 * @param {Object} additionalParams - Extra params to append
 * @returns {URLSearchParams}
 */
export const buildFilterParams = (filters = {}, additionalParams = {}) => {
  const params = new URLSearchParams();

  if (filters.station) params.append("station_id", filters.station);
  if (filters.method) params.append("method", filters.method);
  if (filters.startDate) params.append("start", filters.startDate);
  if (filters.endDate) params.append("end", filters.endDate);

  // Append additional params
  Object.entries(additionalParams).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.append(key, value);
    }
  });

  return params;
};

/**
 * Format date for display (Italian locale)
 * @param {string|Date} dateStr - ISO date string or Date object
 * @param {string} pattern - date-fns format pattern
 * @returns {string} Formatted date or fallback
 */
export const formatDate = (dateStr, pattern = "dd/MM/yyyy HH:mm") => {
  if (!dateStr) return "Data non disponibile";
  try {
    return format(new Date(dateStr), pattern);
  } catch {
    return "Data non valida";
  }
};

/**
 * Format date for short display
 */
export const formatShortDate = (dateStr) => formatDate(dateStr, "dd MMM");

/**
 * Format confidence value as percentage string
 * @param {number} confidence - Value between 0 and 1
 * @returns {string} Formatted percentage
 */
export const formatConfidence = (confidence) => {
  if (confidence === undefined || confidence === null) return "0%";
  return `${(confidence * 100).toFixed(1)}%`;
};

/**
 * Get status configuration (label, color, icon)
 * @param {string} status - verification_status value
 * @returns {Object} Status configuration
 */
export const getStatusConfig = (status) => {
  const configs = {
    confirmed: { label: "Confermata", color: "bg-success text-white", bgColor: "bg-success", icon: null },
    excluded: { label: "Esclusa", color: "bg-danger text-white", bgColor: "bg-danger", icon: null },
    pending: { label: "In attesa", color: "bg-warning text-white", bgColor: "bg-warning", icon: null },
  };
  return configs[status] || { label: "Sconosciuto", color: "bg-muted text-white", bgColor: "bg-muted", icon: null };
};

/**
 * Get alert type configuration
 * @param {string} type - alert_type value
 * @returns {Object} Alert type configuration
 */
export const getAlertTypeConfig = (type) => {
  const configs = {
    protected: { label: "Protetta", color: "bg-blue-100 text-blue-800" },
    invasive: { label: "Invasiva", color: "bg-red-100 text-red-800" },
    rare: { label: "Rara", color: "bg-purple-100 text-purple-800" },
  };
  return configs[type] || { label: type, color: "bg-gray-100 text-gray-800" };
};

/**
 * Get species category configuration
 * @param {string} category - species category
 * @returns {Object} Category configuration
 */
export const getSpeciesCategoryConfig = (category) => {
  const configs = {
    rare: { label: "Rara", color: "bg-purple-100 text-purple-800" },
    protected: { label: "Protetta", color: "bg-blue-100 text-blue-800" },
    invasive: { label: "Invasiva", color: "bg-red-100 text-red-800" },
    normal: { label: "Normale", color: "bg-gray-100 text-gray-800" },
  };
  return configs[category] || configs.normal;
};

/**
 * Standard error component for consistent error display
 */
export const ErrorDisplay = ({ message = "Si è verificato un errore", onRetry }) => (
  <div className="flex items-center justify-center min-h-screen p-4">
    <div className="bg-white p-8 rounded-2xl shadow-xl border border-red-100 text-center max-w-md">
      <div className="text-red-500 text-5xl mb-4">⚠️</div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Errore</h2>
      <p className="text-muted mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-dark transition"
        >
          Riprova
        </button>
      )}
    </div>
  </div>
);

/**
 * Standard loading component
 */
export const LoadingDisplay = ({ message = "Caricamento dati..." }) => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="flex flex-col items-center gap-4">
      <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      <p className="text-lg text-muted animate-pulse">{message}</p>
    </div>
  </div>
);

/**
 * Species category filter options for select dropdowns
 */
export const SPECIES_FILTER_OPTIONS = [
  { value: "all", label: "Tutte" },
  { value: "normal", label: "Normali" },
  { value: "rare", label: "Rare" },
  { value: "protected", label: "Protette" },
  { value: "invasive", label: "Invasive" },
];

/**
 * Method filter options
 */
export const METHOD_FILTER_OPTIONS = [
  { value: "", label: "Tutti" },
  { value: "image", label: "Foto" },
  { value: "audio", label: "Audio" },
];

/**
 * Method label mapping
 */
export const METHOD_LABELS = {
  image: "Foto",
  audio: "Audio",
};

/**
 * Get method label from method value
 */
export const getMethodLabel = (method) => METHOD_LABELS[method] || method;

/**
 * Debounce function for search inputs
 */
export const debounce = (fn, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};