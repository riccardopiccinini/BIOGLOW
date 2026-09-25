/**
 * Shared constants for the Monitor Secchia Dashboard
 * Centralizes configuration to avoid duplication across components
 */

/**
 * Verification status configurations
 */
export const VERIFICATION_STATUS = {
  confirmed: {
    label: "Confermata",
    color: "bg-success text-white",
    bgColor: "bg-success",
    borderColor: "border-success",
    icon: "check",
  },
  excluded: {
    label: "Esclusa",
    color: "bg-danger text-white",
    bgColor: "bg-danger",
    borderColor: "border-danger",
    icon: "x",
  },
  pending: {
    label: "In attesa",
    color: "bg-warning text-white",
    bgColor: "bg-warning",
    borderColor: "border-warning",
    icon: "clock",
  },
};

/**
 * Alert type configurations
 */
export const ALERT_TYPES = {
  protected: {
    label: "Protetta",
    chartColor: "#3498db",
    color: "bg-blue-100 text-blue-800",
    borderColor: "border-blue-200",
    bgColor: "bg-blue-50",
  },
  invasive: {
    label: "Invasiva",
    chartColor: "#e74c3c",
    color: "bg-red-100 text-red-800",
    borderColor: "border-red-200",
    bgColor: "bg-red-50",
  },
};

/**
 * Species category configurations (used in species-distinct page)
 */
export const SPECIES_CATEGORIES = {
  rare: {
    label: "Rara",
    chartColor: "#9b59b6",
    color: "bg-purple-100 text-purple-800",
    description: "Specie rara o minacciata",
  },
  protected: {
    label: "Protetta",
    chartColor: "#3498db",
    color: "bg-blue-100 text-blue-800",
    description: "Specie protetta per legge",
  },
  invasive: {
    label: "Invasiva",
    chartColor: "#e74c3c",
    color: "bg-red-100 text-red-800",
    borderColor: "border-red-200",
    description: "Specie invasiva aliena",
  },
  normal: {
    label: "Normale",
    chartColor: "#95a5a6",
    color: "bg-gray-100 text-gray-800",
    description: "Specie comune",
  },
};

/**
 * Method configurations
 */
export const OBSERVATION_METHODS = {
  image: {
    label: "Foto",
    icon: "image",
    color: "bg-green-500",
    chartColor: "#10b981",
    bgColor: "bg-green-50",
    borderColor: "border-green-100",
  },
  audio: {
    label: "Audio",
    icon: "music",
    color: "bg-blue-500",
    chartColor: "#3b82f6",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-100",
  },
};

/**
 * Station status configurations (for map)
 */
export const STATION_STATUS = {
  alto: {
    label: "Biodiversità Alta",
    color: "bg-success",
    borderColor: "border-success",
    description: "Indice Shannon > 2.0",
  },
  medio: {
    label: "Biodiversità Media",
    color: "bg-warning",
    borderColor: "border-warning",
    description: "Indice Shannon 1.0 - 2.0",
  },
  basso: {
    label: "Biodiversità Bassa",
    color: "bg-danger",
    borderColor: "border-danger",
    description: "Indice Shannon < 1.0",
  },
};

/**
 * Chart color palette
 */
export const CHART_COLORS = {
  primary: "#3498db",
  success: "#27ae60",
  warning: "#f39c12",
  danger: "#e74c3c",
  purple: "#9b59b6",
  teal: "#16a085",
  orange: "#e67e22",
  gray: "#95a5a6",
};

/**
 * Chart default configurations
 */
export const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  tooltip: {
    backgroundColor: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    padding: "8px",
  },
  grid: {
    strokeDasharray: "3 3",
    stroke: "#e5e7eb",
  },
  axis: {
    tick: { fontSize: 12, fill: "#6b7280" },
  },
};

/**
 * Default filter options for select components
 */
export const FILTER_OPTIONS = {
  method: [
    { value: "", label: "Tutti" },
    { value: "image", label: "Foto" },
    { value: "audio", label: "Audio" },
  ],
  speciesCategory: [
    { value: "all", label: "Tutte" },
    { value: "normal", label: "Normali" },
    { value: "rare", label: "Rare" },
    { value: "protected", label: "Protette" },
    { value: "invasive", label: "Invasive" },
  ],
};

/**
 * API endpoint paths
 */
export const API_ENDPOINTS = {
  observations: "/observations",
  observationsStats: "/observations/stats",
  shannonTime: "/observations/shannon-time",
  shannonTimeDetail: "/observations/shannon-time-detail",
  observation: (id) => `/observations/${id}`,
  alerts: "/alerts",
  stations: "/stations",
  station: (id) => `/stations/${id}`,
  speciesReference: "/docs/species_reference.json",
};

/**
 * Page route paths
 */
export const ROUTES = {
  home: "/",
  stations: "/stations",
  station: (id) => `/station/${id}`,
  species: "/species",
  speciesDistinct: "/species-distinct",
  speciesDetail: (species) => `/species/${encodeURIComponent(species)}`,
  observationsByMethod: "/observations-by-method",
  methodDetail: (method) => `/method/${method}`,
  observation: (id) => `/observation/${id}`,
};

/**
 * Default pagination limits
 */
export const PAGINATION = {
  defaultLimit: 5,
  expandedLimit: 20,
  maxLimit: 1000,
};

/**
 * UI constants
 */
export const UI = {
  animationDuration: 200,
  transitionClass: "transition-all duration-200",
  cardShadow: "shadow-md",
  cardBorder: "border border-gray-200",
  cardRadius: "rounded-lg",
  cardPadding: "p-6",
};