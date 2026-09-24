-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0006 — memori_perlu_diselaraskan(): memories → Qdrant
-- spec/07 3.5–3.7 · spec/01 §12 · K-19
--
-- Penyelaras vektor (proses pekerja) menyemat memori baru, menyemat ulang
-- memori yang isinya berubah, dan menghapus titik memori yang dihapus — untuk
-- SEMUA pengguna. RLS `memories` tidak meloloskannya, dan tidak boleh
-- dilonggarkan. Fungsi sempit: hanya-baca, hanya `user_id` yang punya
-- pekerjaan (isinya dibaca di transaksi PEMILIKNYA), berbatas.
-- ════════════════════════════════════════════════════════════════════

CREATE FUNCTION memori_perlu_diselaraskan(p_model text, p_batas integer)
  RETURNS TABLE (user_id uuid)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT m.user_id
    FROM public.memories m
    WHERE m.deleted_at IS NOT NULL OR m.model_version IS DISTINCT FROM p_model
    GROUP BY m.user_id
    ORDER BY min(m.updated_at), m.user_id
    LIMIT least(greatest(p_batas, 1), 1000)
  $$;
REVOKE ALL ON FUNCTION memori_perlu_diselaraskan(text, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memori_perlu_diselaraskan(text, integer) TO hvx_app;
