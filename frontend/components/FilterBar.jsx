import { useState, useEffect } from "react";

export default function FilterBar({ value, onFilterChange }) {
  const [formValues, setFormValues] = useState(value);

  // Reset form values when the value prop changes (e.g., from URL)
  useEffect(() => {
    setFormValues(value);
  }, [value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onFilterChange(formValues);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-5 mb-6 space-y-4">
      <h3 className="text-lg font-semibold text-primary">Filtri</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stazione */}
        <div>
          <label className="block text-sm font-medium text-muted mb-1">Stazione</label>
          <input
            type="text"
            value={formValues.station}
            onChange={(e) => setFormValues({ ...formValues, station: e.target.value })}
            placeholder="es. SECCHIA-01"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
          />
        </div>

        {/* Metodo */}
        <div>
          <label className="block text-sm font-medium text-muted mb-1">Metodo</label>
          <select
            value={formValues.method}
            onChange={(e) => setFormValues({ ...formValues, method: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
          >
            <option value="">Tutti</option>
            <option value="image">Foto</option>
            <option value="audio">Audio</option>
          </select>
        </div>

        {/* Data inizio */}
        <div>
          <label className="block text-sm font-medium text-muted mb-1">Dal</label>
          <input
            type="date"
            value={formValues.startDate}
            onChange={(e) => setFormValues({ ...formValues, startDate: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
          />
        </div>

        {/* Data fine */}
        <div>
          <label className="block text-sm font-medium text-muted mb-1">Al</label>
          <input
            type="date"
            value={formValues.endDate}
            onChange={(e) => setFormValues({ ...formValues, endDate: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
          />
        </div>
      </div>

      <button
        type="submit"
        className="w-full sm:w-auto bg-primary text-white py-2 px-6 rounded-lg hover:bg-primary/90 transition font-medium"
      >
        Applica filtri
      </button>
    </form>
  );
}