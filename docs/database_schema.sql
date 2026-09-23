-- Supabase schema for Monitor Secchia
CREATE TABLE IF NOT EXISTS osservazioni (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    species text,
    category text,
    method text,
    media_url text,
    date_time timestamptz,
    station_id text,
    confidence real,
    verification_status text,
    source text,
    source_update_date timestamptz,
    habitat_zone text,
    coordinates jsonb,
    quality text
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_osservazioni_date ON osservazioni (date_time);
CREATE INDEX IF NOT EXISTS idx_osservazioni_species ON osservazioni (species);
CREATE INDEX IF NOT EXISTS idx_osservazioni_station ON osservazioni (station_id);

-- Alerts table for species of interest
CREATE TABLE IF NOT EXISTS alerts (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    species text NOT NULL,
    observation_id uuid REFERENCES osservazioni(id),
    alert_type text CHECK (alert_type IN ('rare','protected','invasive')),
    status text DEFAULT 'pending',
    created_at timestamptz DEFAULT now()
);

