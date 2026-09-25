import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { STATION_STATUS } from "../lib/constants";

export default function StationMap() {
  const router = useRouter();
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/stations`)
      .then((res) => {
        if (!res.ok) throw new Error("Impossible caricare le stazioni");
        return res.json();
      })
      .then((data) => {
        setStations(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load stations:", err);
        setStations([]);
        setLoading(false);
        setError(err);
      });
  }, []);

  const getStatusConfig = (shannon) => {
    if (shannon >= 2.0) return STATION_STATUS.alto;
    if (shannon >= 1.0) return STATION_STATUS.medio;
    return STATION_STATUS.basso;
  };

  const getPosition = (lat, lng) => {
    const x = ((lng - 10.80) / (11.00 - 10.80)) * 100;
    const y = ((44.80 - lat) / (44.95 - 44.80)) * 100;
    return { x: `${x}%`, y: `${y}%` };
  };

  const handleStationClick = (station) => {
    router.push(`/station/${station.id}`);
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
        <h2 className="text-lg font-semibold mb-4 text-primary dark:text-blue-400">Mappa Biodiversità Stazioni</h2>
        <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
          Caricamento mappa...
        </div>
      </div>
    );
  }

  if (error && stations.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
        <h2 className="text-lg font-semibold mb-4 text-primary dark:text-blue-400">Mappa Biodiversità Stazioni</h2>
        <div className="flex items-center justify-center h-64 text-red-500">
          Errore nel caricamento della mappa
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
      <h2 className="text-lg font-semibold mb-4 text-primary dark:text-blue-400">Mappa Biodiversità Stazioni</h2>
      <div className="relative w-full h-96 bg-blue-50 dark:bg-gray-700 rounded-xl border-2 border-dashed border-blue-200 dark:border-gray-600 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center opacity-10">
          <span className="text-blue-400 font-bold text-xl uppercase tracking-widest">Mappa Area Secchia</span>
        </div>

        {stations.map((station) => {
          const shannon = station.shannon || 0;
          const obsCount = station.obs_count || 0;
          const statusConfig = getStatusConfig(shannon);
          const { x, y } = getPosition(station.lat, station.lon);
          
          // HEATMAP LOGIC:
          // Size based on observation count (between 12px and 32px)
          const size = Math.max(12, Math.min(32, 12 + (obsCount / 5)));
          
          return (
            <div
              key={station.id}
              className="absolute group cursor-pointer"
              style={{ left: x, top: y }}
              onClick={() => handleStationClick(station)}
            >
              <div 
                className={`rounded-full ${statusConfig.color} ring-4 ring-white dark:ring-gray-800 shadow-md transition-all duration-200 hover:scale-125`}
                style={{ width: `${size}px`, height: `${size}px`, marginLeft: `-${size/2}px`, marginTop: `-${size/2}px` }}
              >
                {shannon >= 2.0 && (
                  <div className="absolute inset-0 rounded-full ring-2 ring-white dark:ring-gray-800 animate-pulse opacity-50" />
                )}
              </div>
              
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 opacity-0 group-hover:opacity-100 transition-opacity w-64 z-10">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 p-4 space-y-3 transition-colors">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{station.name}</p>
                      <p className="text-sm text-muted dark:text-gray-400">{station.id}</p>
                    </div>
                    <div className={`px-2 py-1 text-xs rounded-full ${statusConfig.color} bg-opacity-20`}>
                      {statusConfig.label}
                    </div>
                  </div>
                  
                  <div className="border-t border-gray-200 dark:border-gray-600 pt-3">
                    <div className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                      <div className="flex justify-between">
                        <span>Osservazioni:</span>
                        <span className="font-medium">{obsCount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Indice Shannon:</span>
                        <span className="font-medium">{shannon.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Coordinate:</span>
                        <span className="font-mono">{station.lat.toFixed(4)}°N, {station.lon.toFixed(4)}°E</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-3">
                    <button
                      onClick={() => handleStationClick(station)}
                      className="w-full bg-primary text-white px-3 py-1.5 rounded text-sm hover:bg-primary/90 transition"
                    >
                      Vai ai dettagli
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 flex flex-col space-y-3 text-xs text-muted dark:text-gray-400">
        <div className="flex items-center gap-3 font-medium text-gray-600 dark:text-gray-300">
          Legenda:
        </div>
        <div className="flex flex-wrap gap-4">
          {Object.entries(STATION_STATUS).map(([key, config]) => (
            <div key={key} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${config.color}`} />
              <span>{config.label}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
          <div className="flex justify-between">
            <span>Dimensione cerchio: numero osservazioni</span>
            <span className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-primary/20" />
              <span>Stazione attiva</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
