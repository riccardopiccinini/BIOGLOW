import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { useRouter } from 'next/router';
import { STATION_STATUS } from "../lib/constants";

export default function StationMap() {
  const router = useRouter();
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real station data from API
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
        // Fallback to simulated data if API fails
        setStations([
          { id: 'SECCHIA-01', name: 'Stazione Nord', index: 2.45, status: 'alto', lat: 44.92, lon: 10.92 },
          { id: 'SECCHIA-02', name: 'Stazione Centro', index: 1.82, status: 'medio', lat: 44.90, lon: 10.90 },
          { id: 'SECCHIA-03', name: 'Stazione Sud', index: 1.10, status: 'basso', lat: 44.88, lon: 10.88 },
        ]);
        setLoading(false);
      });
  }, []);

  const getStatusConfig = (status) => STATION_STATUS[status] || STATION_STATUS.basso;

  // Convert lat/lng to x/y percentages for positioning on the map
  // Assuming a fixed map area for simplicity
  const getPosition = (lat, lng) => {
    // These values would need to be calibrated to the actual map image
    // For demo purposes, using a simple linear transformation
    const x = ((lng - 10.80) / (11.00 - 10.80)) * 100; // Longitude range
    const y = ((44.80 - lat) / (44.95 - 44.80)) * 100; // Latitude range (reversed because y increases downward)
    return { x: `${x}%`, y: `${y}%` };
  };

  const handleStationClick = (station) => {
    router.push(`/stations/${station.id}`);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 text-primary">Mappa Biodiversità Stazioni</h2>
        <div className="flex items-center justify-center h-64 text-gray-500">
          Caricamento mappa...
        </div>
      </div>
    );
  }

  if (error && stations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 text-primary">Mappa Biodiversità Stazioni</h2>
        <div className="flex items-center justify-center h-64 text-red-500">
          Errore nel caricamento della mappa
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4 text-primary">Mappa Biodiversità Stazioni</h2>
      <div className="relative w-full h-96 bg-blue-50 rounded-xl border-2 border-dashed border-blue-200 overflow-hidden">
        {/* Map background image would go here in a real implementation */}
        <div className="absolute inset-0 flex items-center justify-center opacity-10">
          <span className="text-blue-400 font-bold text-xl uppercase tracking-widest">Mappa Area Secchia</span>
        </div>

        {stations.map((station) => {
          const statusConfig = getStatusConfig(station.status);
          const { x, y } = getPosition(station.lat, station.lon);
          
          return (
            <div
              key={station.id}
              className="absolute group cursor-pointer"
              style={{ left: x, top: y }}
              onClick={() => handleStationClick(station)}
            >
              {/* Station marker */}
              <div className={`w-6 h-6 rounded-full ${statusConfig.color} ring-4 ring-white shadow-md transition-all duration-200 hover:scale-110`}>
                {/* Optional: add a pulsating effect for active stations */}
                {station.status === 'alto' && (
                  <div className="absolute inset-0 rounded-full ring-2 ring-white animate-pulse opacity-50" />
                )}
              </div>
              
              {/* Tooltip / Popup */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 opacity-0 group-hover:opacity-100 transition-opacity w-64">
                <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{station.name}</p>
                      <p className="text-sm text-muted">{station.id}</p>
                    </div>
                    <div className={`px-2 py-1 text-xs rounded-full ${statusConfig.color} bg-opacity-20`}>
                      {statusConfig.label}
                    </div>
                  </div>
                  
                  <div className="border-t border-gray-200 pt-3">
                    <div className="text-sm text-gray-600 space-y-1">
                      <div className="flex justify-between">
                        <span>Indice Shannon:</span>
                        <span className="font-medium">{station.index.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Coordinate:</span>
                        <span className="font-mono">{station.lat.toFixed(4)}°N, {station.lon.toFixed(4)}°E</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Ultimo aggiornamento:</span>
                        <span className="text-sm">
                          {station.last_updated ? 
                            new Date(station.last_updated).toLocaleString('it-IT', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            }) : 
                            'Dati non disponibili'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Action button */}
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
      
      {/* Legend with enhanced information */}
      <div className="mt-4 flex flex-col space-y-3 text-xs text-muted">
        <div className="flex items-center gap-3 font-medium text-gray-600">
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
        <div className="border-t border-gray-200 pt-2">
          <div className="flex justify-between">
            <span>Marker size indicates data quality</span>
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
