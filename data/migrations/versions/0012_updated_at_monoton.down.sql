-- Migrasi 0012 turun — kembali ke `now()` apa adanya (bentuk 0001).
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$ LANGUAGE plpgsql;
