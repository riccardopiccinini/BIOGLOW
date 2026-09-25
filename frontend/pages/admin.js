import { useState, useEffect } from "react";
import useSWR from "swr";
import Layout from "../components/Layout";
import { fetcher } from "../lib/utils";
import Link from "next/link";

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
      mutate(); 
    } catch (err) {
      alert("Errore durante l'aggiornamento dello stato");
    }
  };

  if (error) return <Layout><div className="p-8 text-red-500">Errore nel caricamento delle osservazioni.</div></Layout>;
  if (!observations) return <Layout><div className="p-8">Caricamento...</div></Layout>;

  return (
    <Layout>
      <div className="p-4 lg:p-8 bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors">
        <header className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Pannello Validazione</h1>
            <p className="text-muted dark:text-gray-400">Conferma o escludi le identificazioni automatiche per pulire il dataset</p>
          </div>
          <Link 
            href="/" 
            className="px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition"
          >
            Torna alla Dashboard
          </Link>
        </header>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-colors">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h2 className="font-bold text-gray-900 dark:text-white">Osservazioni in attesa</h2>
            <span className="px-3 py-1 rounded-full bg-warning/20 text-warning text-xs font-bold">
              {observations.length} da revisionare
            </span>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-gray-50 dark:bg-gray-700/50 text-xs uppercase text-gray-500 dark:text-gray-400 font-bold">
                <tr className="border-b border-gray-200 dark:border-gray-700">
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
                    <td colSpan="5" className="px-6 py-12 text-center text-muted dark:text-gray-400 italic">
                      Tutto pulito! Nessuna osservazione in attesa di validazione.
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
                          className="px-3 py-1 text-xs font-bold rounded bg-green-500 text-white hover:bg-green-600 transition shadow-sm"
                        >
                          Conferma
                        </button>
                        <button 
                          onClick={() => updateStatus(obs.id, "excluded")}
                          className="px-3 py-1 text-xs font-bold rounded bg-red-500 text-white hover:bg-red-600 transition shadow-sm"
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
      </div>
    </Layout>
  );
}
