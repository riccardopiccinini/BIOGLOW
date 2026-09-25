import { useState, useEffect } from "react";
import useSWR from "swr";
import Layout from "../components/Layout";
import { fetcher, getStatusConfig } from "../lib/utils";

export default function AdminPanel() {
  const { data: observations, error, mutate } = useSWR(
    "/observations?verification_status=pending&limit=100",
    fetcher
  );

  const updateStatus = async (id, status) => {
    try {
      await fetch(`/observations/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ verification_status: status }),
      });
      mutate(); // Refresh the list
    } catch (err) {
      alert("Errore durante l'aggiornamento dello stato");
    }
  };

  if (error) return <Layout><div className="p-8 text-red-500">Errore nel caricamento delle osservazioni.</div></Layout>;
  if (!observations) return <Layout><div className="p-8">Caricamento...</div></Layout>;

  return (
    <Layout>
      <div className="p-4 lg:p-8 bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors">
        <header className="mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">Pannello Validazione</h1>
          <p className="text-muted dark:text-gray-400">Conferma o escludi le identificazioni automatiche</p>
        </header>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead className="bg-gray-50 dark:bg-gray-700/50 text-xs uppercase text-gray-500 dark:text-gray-400 font-bold">
              <tr>
                <th className="px-6 py-4">Specie</th>
                <th className="px-6 py-4">Confidenza</th>
                <th className="px-6 py-4">Metodo</th>
                <th className="px-6 py-4">Data</th>
                <th className="px-6 py-4 text-right">Azioni</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {observations.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-muted dark:text-gray-400">
                    Nessuna osservazione in attesa di validazione.
                  </td>
                </tr>
              ) : (
                observations.map((obs) => (
                  <tr key={obs.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{obs.species}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                        {(obs.confidence * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted dark:text-gray-400 capitalize">{obs.method}</td>
                    <td className="px-6 py-4 text-sm text-muted dark:text-gray-400">{new Date(obs.date_time).toLocaleDateString()}</td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button 
                        onClick={() => updateStatus(obs.id, "confirmed")}
                        className="px-3 py-1 text-xs font-bold rounded bg-green-500 text-white hover:bg-green-600 transition"
                      >
                        Conferma
                      </button>
                      <button 
                        onClick={() => updateStatus(obs.id, "excluded")}
                        className="px-3 py-1 text-xs font-bold rounded bg-red-500 text-white hover:bg-red-600 transition"
                      >
                        Escludi
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
