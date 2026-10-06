-- Migrasi 0011 turun — tiga fungsi sapuan dibuang; penyelaras kembali ke bentuk 0006.
DROP FUNCTION hapus_akun_jatuh_tempo(uuid, uuid);
DROP FUNCTION kunci_akun_jatuh_tempo(uuid);
DROP FUNCTION akun_jatuh_tempo(integer);

CREATE OR REPLACE FUNCTION memori_perlu_diselaraskan(p_model text, p_batas integer)
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
