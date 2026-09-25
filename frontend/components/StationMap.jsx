import React from 'react';
import { useRouter } from 'next/router';

export default function StationMap() {
  const router = useRouter();
  // Dati simulati per le stazioni
  const stations = [
    { id: 'SECCHIA-01', name: 'Stazione Nord', index: 2.45, status: 'alto', x: '20%', y: '30%' },
    { id: 'SECCHIA-02', name: 'Stazione Centro', index: 1.82, status: 'medio', x: '50%', y: '50%' },
    { id: 'SECCHIA-03', name: 'Stazione Sud', index: 1.10, status: 'basso', x: '80%', y: '70%' },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'alto': return 'bg-success';
      case 'medio': return 'bg-warning';
      case 'basso': return 'bg-danger';
      default: return 'bg-gray-400';
    }
  };

  const handleStationClick = (id) => {
    // Fixed path: /station/ instead of /stations/ to match the folder structure
    router.push(`/station/${id}`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">Mappa Biodiversità Stazioni</h2>
      <div className="relative w-full h-64 bg-blue-50 rounded-xl border-2 border-dashed border-blue-200 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center opacity-20">
          <span className="text-blue-400 font-bold text-xl uppercase tracking-widest">Mappa Area Secchia</span>
        </div>

        {stations.map((s) => (
          <div
            key={s.id}
            className="absolute group cursor-pointer"
            style={{ left: s.x, top: s.y }}
            onClick={() => handleStationClick(s.id)}
          >
            <div className={`w-4 h-4 rounded-full ${getStatusColor(s.status)} ring-4 ring-white shadow-sm transition-transform hover:scale-150`} />
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              <div className="bg-gray-900 text-white text-xs py-1 px-2 rounded shadow-lg">
                <strong>{s.id}</strong>: {s.index}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 flex justify-center gap-4 text-xs text-muted">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-success" /> Biodiversità Alta
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-warning" /> Biodiversità Media
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-danger" /> Biodiversità Bassa
        </div>
      </div>
    </div>
  );
}
