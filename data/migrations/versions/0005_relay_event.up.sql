-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0005 — events_untuk_relay(): kotak keluar event → Redis Streams
-- spec/07 3.3 · spec/01 §12 · K-19
--
-- Relay membaca event SEMUA pengguna, urut waktu masuk. RLS `events` tidak
-- meloloskannya tanpa pengguna transaksi, dan tidak boleh dilonggarkan.
-- Fungsi sempit: hanya-baca, empat kolom RUJUKAN (bukan isi payload), berbatas.
--
-- Hanya peran `hvx_pekerja` yang boleh memanggilnya — BUKAN `hvx_app`: peran
-- api menghadap internet, dan injeksi SQL di sana akan membaca linimasa semua
-- pengguna lewat fungsi ini (tinjauan keamanan Sprint 3, S4). Peran login
-- proses pekerja anggota keduanya; peran login api hanya `hvx_app`.
-- ════════════════════════════════════════════════════════════════════

-- NOLOGIN, berlaku sekluster (seperti `hvx_app` di 0001) — turun TIDAK melepasnya.
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hvx_pekerja') THEN
    CREATE ROLE hvx_pekerja NOLOGIN;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;  -- dibuat migrasi lain di klaster yang sama, di antara cek dan CREATE
END $$;

CREATE FUNCTION events_untuk_relay(p_sesudah timestamptz, p_sesudah_id uuid, p_batas integer)
  RETURNS TABLE (id uuid, user_id uuid, event_type text, recorded_at timestamptz)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT e.id, e.user_id, e.event_type, e.recorded_at
    FROM public.events e
    WHERE (e.recorded_at, e.id) > (p_sesudah, p_sesudah_id)
    ORDER BY e.recorded_at, e.id
    LIMIT least(greatest(p_batas, 1), 1000)
  $$;
REVOKE ALL ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) TO hvx_pekerja;
