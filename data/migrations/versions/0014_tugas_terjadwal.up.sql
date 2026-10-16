-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0014 — tugas terjadwal per jam lokal pengguna
-- spec/08 7.3 · spec/01 §7 (scheduled_runs) · §10 · §11 · §12
--
-- Tugas malam V1 (agregat 8.x, hasil prediksi 10.1, Weekly Review 11.4) berjalan
-- TEPAT SEKALI per pengguna per hari LOKAL-nya. Tepat sekali dijamin basis data:
-- proses pekerja mengklaim (user_id, task, for_date) dengan INSERT di transaksi
-- yang SAMA dengan kerjanya — kerja yang gagal membatalkan klaimnya, pekerja kedua
-- yang serentak tertahan indeks unik lalu mendapati klaimnya sudah ada.
-- ════════════════════════════════════════════════════════════════════

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE scheduled_runs (
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  task         text NOT NULL CHECK (task ~ '^[a-z][a-z0-9-]{0,39}$'),
  for_date     date NOT NULL,
  ran_at       timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, task, for_date)
);

GRANT SELECT, INSERT, DELETE ON scheduled_runs TO hvx_app;

ALTER TABLE scheduled_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY scheduled_runs_own_rows ON scheduled_runs USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());

-- Tugas terjadwal (spec/08 7.3): SIAPA yang tugas `p_tugas`-nya jatuh tempo menurut jam
-- LOKAL-nya sendiri (`profiles.timezone`) — hari ini dan kemarin, supaya pekerja yang
-- berhenti sebentar, atau pengguna yang pindah zona ke timur, tidak melewatkan hari;
-- tidak pernah sebelum hari akunnya dibuat. Hanya akun aktif. Zona yang tak dikenal
-- PostgreSQL membuat pengguna itu dilewati — bukan menggagalkan semua pengguna. Hanya
-- baca: klaimnya ditulis di bawah RLS pemiliknya. Dibaca per halaman, kursor
-- `(p_setelah_tanggal, p_setelah_user)`: kerja yang gagal membatalkan klaimnya, jadi baris
-- yang sama tetap jatuh tempo — tanpa kursor, `batas` pengguna yang selalu gagal menahan
-- semua pengguna di belakangnya selamanya (tinjauan kontrak S7, K2).
CREATE FUNCTION tugas_jatuh_tempo(
  p_tugas text, p_menit integer, p_batas integer,
  p_setelah_tanggal date DEFAULT '-infinity',
  p_setelah_user uuid DEFAULT '00000000-0000-0000-0000-000000000000'
)
  RETURNS TABLE (user_id uuid, for_date date)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    WITH zona AS MATERIALIZED (SELECT name FROM pg_catalog.pg_timezone_names)
    SELECT u.id, h.for_date
    FROM public.users u
    JOIN public.profiles p ON p.user_id = u.id
    LEFT JOIN zona z ON z.name = p.timezone
    CROSS JOIN LATERAL (SELECT now() AT TIME ZONE z.name AS lokal) w
    CROSS JOIN LATERAL (
      SELECT (w.lokal::date - k) AS for_date FROM generate_series(0, 1) AS k
    ) h
    WHERE u.status = 'active'
      AND h.for_date >= (u.created_at AT TIME ZONE z.name)::date
      AND w.lokal >= h.for_date + make_interval(mins => p_menit)
      AND (h.for_date, u.id) > (p_setelah_tanggal, p_setelah_user)
      AND NOT EXISTS (
        SELECT 1 FROM public.scheduled_runs r
        WHERE r.user_id = u.id AND r.task = p_tugas AND r.for_date = h.for_date
      )
    ORDER BY h.for_date, u.id
    LIMIT least(greatest(p_batas, 1), 500)
  $$;
REVOKE ALL ON FUNCTION tugas_jatuh_tempo(text, integer, integer, date, uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION tugas_jatuh_tempo(text, integer, integer, date, uuid) TO hvx_pekerja;
