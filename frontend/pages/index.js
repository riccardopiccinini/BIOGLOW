import useSWR from 'swr';

const fetcher = (url) => fetch(url).then((r) => r.json());

export default function Home() {
  const { data, error } = useSWR('http://127.0.0.1:8000/observations/stats', fetcher, { refreshInterval: 5000 });

  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Failed to load data: {error.message}</div>;
  if (!data) return <div style={{ padding: '2rem' }}>Loading...</div>;

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1 style={{ color: '#2c3e50' }}>Monitor Secchia Dashboard</h1>
      <section style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', maxWidth: '400px' }}>
        <h2 style={{ color: '#34495e', marginTop: 0 }}>Statistical Overview</h2>
        <p><strong>Total observations:</strong> {data.total_observations}</p>
        <p><strong>Distinct species:</strong> {data.species_count}</p>
        <p><strong>Shannon index:</strong> {data.shannon_index?.toFixed(3) ?? 'N/A'}</p>
      </section>
    </main>
  );
}
