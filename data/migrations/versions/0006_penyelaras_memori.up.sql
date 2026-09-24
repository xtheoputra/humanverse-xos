-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0006 — memori_perlu_diselaraskan(): memories → Qdrant
-- spec/07 3.5–3.7 · spec/01 §12 · K-19
--
-- Penyelaras vektor (proses pekerja) menyemat memori baru, menyemat ulang
-- memori yang isinya berubah, dan menghapus titik memori yang dihapus — untuk
-- SEMUA pengguna. RLS `memories` tidak meloloskannya, dan tidak boleh
-- dilonggarkan. Fungsi sempit: hanya-baca, hanya `user_id` yang punya
-- pekerjaan (isinya dibaca di transaksi PEMILIKNYA), berbatas, dan hanya untuk
-- peran `hvx_pekerja` (lihat 0005).
--
-- `embedding_model`: penyemat yang vektornya cocok dengan isi saat ini — kolom
-- sendiri, bukan `model_version` (tempat ambang keyakinan #34, arch/README;
-- tinjauan kontrak Sprint 3, K4).
-- ════════════════════════════════════════════════════════════════════

ALTER TABLE memories ADD COLUMN embedding_model text;

CREATE FUNCTION memori_perlu_diselaraskan(p_model text, p_batas integer)
  RETURNS TABLE (user_id uuid)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT m.user_id
    FROM public.memories m
    WHERE m.deleted_at IS NOT NULL OR m.embedding_model IS DISTINCT FROM p_model
    GROUP BY m.user_id
    ORDER BY min(m.updated_at), m.user_id
    LIMIT least(greatest(p_batas, 1), 1000)
  $$;
REVOKE ALL ON FUNCTION memori_perlu_diselaraskan(text, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memori_perlu_diselaraskan(text, integer) TO hvx_pekerja;
