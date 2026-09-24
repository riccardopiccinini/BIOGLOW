import { useRouter } from 'next/router';
import useSWR from 'swr';
import { useState } from 'react';
import { format } from 'date-fns';
import { LuImage, LuMusic } from 'react-icons/lu';

const fetcher = (url) => fetch(url).then(r => r.json());

export default function ObservationDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [updating, setUpdating] = useState(false);
  const { data: obs, error } = useSWR(id ? `/observations/${id}` : null, fetcher);

  const updateStatus = async (newStatus) => {
    if (!id) return;
    setUpdating(true);
    try {
      const res = await fetch(`/observations/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ verification_status: newStatus }),
      });
      if (!res.ok) throw new Error('Errore aggiornamento');
      // Refetch data
      router.replace(router.asPath);
    } catch (e) {
      console.error(e);
    } finally {
      setUpdating(false);
    }
  };

  if (error) return <div className="p-6 text-red-500">Errore nel caricamento dell'osservazione</div>;
  if (!obs) return <div className="p-6 text-gray-500">Caricamento…</div>;

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-4">Dettaglio osservazione</h1>
      <div className="flex gap-4 mb-4">
        <div className="w-48 h-48 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
          {obs.method === 'image' && obs.media_url ? (
            <img src={obs.media_url} alt={`Foto di ${obs.species}`} className="w-full h-full object-cover" />
          ) : (
            <LuMusic className="text-4xl text-muted" />
          )}
        </div>
        <div className="flex-1">
          <p className="font-medium text-gray-900 text-lg">{obs.species}</p>
          <p className="text-sm text-muted">
            {obs.method === 'image' ? 'Foto' : 'Audio'} • {obs.date_time ? format(new Date(obs.date_time), 'dd/MM/yyyy HH:mm') : 'Data non disponibile'}
          </p>
          <p className="mt-2">
            <span className="font-semibold">Confidenza:</span> {(obs.confidence ?? 0).toFixed(2)}
          </p>
          <p className="mt-2">
            <span className="font-semibold">Stato:</span> {obs.verification_status}
          </p>
        </div>
      </div>
      <div className="flex gap-4">
        <button
          disabled={updating}
          onClick={() => updateStatus('confirmed')}
          className="px-4 py-2 bg-success text-white rounded hover:bg-success-dark"
        >
          Conferma
        </button>
        <button
          disabled={updating}
          onClick={() => updateStatus('excluded')}
          className="px-4 py-2 bg-danger text-white rounded hover:bg-danger-dark"
        >
          Escludi
        </button>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 bg-muted text-white rounded"
        >
          Indietro
        </button>
      </div>
    </div>
  );
}
