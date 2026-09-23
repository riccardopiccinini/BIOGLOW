import { SiTimer, SiLeaf, SiUsers } from "react-icons/si";

export default function StatsCard({ totalObservations, speciesCount, shannonIndex }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      {/* Totale osservazioni */}
      <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-primary">
        <div className="flex items-center gap-2 mb-1">
          <SiTimer className="text-primary h-5 w-5" />
          <span className="text-sm font-medium text-muted">Totale osservazioni</span>
        </div>
        <p className="text-3xl font-bold text-gray-900">{totalObservations}</p>
      </div>

      {/* Specie distinte */}
      <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-success">
        <div className="flex items-center gap-2 mb-1">
          <SiLeaf className="text-success h-5 w-5" />
          <span className="text-sm font-medium text-muted">Specie distinte</span>
        </div>
        <p className="text-3xl font-bold text-gray-900">{speciesCount}</p>
      </div>

      {/* Indice di Shannon */}
      <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-warning">
        <div className="flex items-center gap-2 mb-1">
          <SiUsers className="text-warning h-5 w-5" />
          <span className="text-sm font-medium text-muted">Indice di Shannon</span>
        </div>
        <p className="text-3xl font-bold text-gray-900">
          {shannonIndex?.toFixed(3) ?? "N/A"}
        </p>
      </div>
    </div>
  );
}