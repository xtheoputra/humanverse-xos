-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0011 — sapuan hapus akun, tahap 3–6
-- spec/07 6.5 (Stage B) · spec/01 "Prosedur hapus akun" · §12 · K-39
--
-- Tahap 3 (`DELETE FROM users` → cascade) tidak boleh dikerjakan peran api:
-- `hvx_app` sengaja TIDAK punya `DELETE` atas `users` (§10), dan RLS (§11)
-- tidak meloloskan baris pengguna lain. Sapuan dijalankan proses pekerja
-- (`hvx.pekerja`), sebagai anggota `hvx_pekerja`, lewat TIGA fungsi sempit —
-- satu per langkah — yang masing-masing sendiri menolak menyentuh akun yang
-- belum jatuh tempo. Pekerja yang dibajak tidak bisa menghapus akun aktif:
-- yang bisa dilakukannya hanya mempercepat yang memang sudah waktunya.
--
--   akun_jatuh_tempo        — SIAPA yang waktunya (hanya baca)
--   kunci_akun_jatuh_tempo  — kunci barisnya, periksa ulang; ditahan sampai commit
--   hapus_akun_jatuh_tempo  — tahap 5 · 3 · 6, satu transaksi
--
-- Tahap 4 (titik Qdrant) bukan SQL; pekerja mengerjakannya DI ANTARA kunci dan
-- hapus, selagi baris akunnya terkunci — `POST /me/restore` yang menyelip di
-- batas waktu menunggu, lalu mendapati akunnya sudah tidak ada (atau, bila
-- restore menang, sapuan mendapati akunnya aktif lagi dan berhenti sebelum
-- menyentuh Qdrant).
-- ════════════════════════════════════════════════════════════════════

-- Penyelaras vektor tidak lagi menyentuh akun yang menunggu dihapus. Tanpa ini,
-- penyematan ulang (kunci/penyemat diganti) bisa menulis titik baru ke Qdrant
-- DI ANTARA tahap 4 dan commit tahap 3 — titik yatim yang tak punya pemilik dan
-- tak bisa lagi dicari siapa pun. Restore mengembalikan akunnya `active`, dan
-- pekerjaan yang tertunda diselaraskan lagi di putaran berikutnya.
CREATE OR REPLACE FUNCTION memori_perlu_diselaraskan(p_model text, p_batas integer)
  RETURNS TABLE (user_id uuid)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT m.user_id
    FROM public.memories m
    JOIN public.users u ON u.id = m.user_id
    WHERE u.status <> 'pending_deletion'
      AND (m.deleted_at IS NOT NULL OR m.embedding_model IS DISTINCT FROM p_model)
    GROUP BY m.user_id
    ORDER BY min(m.updated_at), m.user_id
    LIMIT least(greatest(p_batas, 1), 1000)
  $$;

CREATE FUNCTION akun_jatuh_tempo(p_batas integer)
  RETURNS TABLE (user_id uuid, punya_titik boolean)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT u.id,
           EXISTS (SELECT 1 FROM public.memories m
                   WHERE m.user_id = u.id AND m.embedding_id IS NOT NULL)
    FROM public.users u
    WHERE u.status = 'pending_deletion' AND u.deletion_scheduled_at <= now()
    ORDER BY u.deletion_scheduled_at, u.id
    LIMIT least(greatest(p_batas, 1), 100)
  $$;
REVOKE ALL ON FUNCTION akun_jatuh_tempo(integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION akun_jatuh_tempo(integer) TO hvx_pekerja;

CREATE FUNCTION kunci_akun_jatuh_tempo(p_user_id uuid)
  RETURNS boolean
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
  BEGIN
    PERFORM 1 FROM public.users u
      WHERE u.id = p_user_id
        AND u.status = 'pending_deletion' AND u.deletion_scheduled_at <= now()
      FOR NO KEY UPDATE;
    RETURN FOUND;
  END
  $$;
REVOKE ALL ON FUNCTION kunci_akun_jatuh_tempo(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION kunci_akun_jatuh_tempo(uuid) TO hvx_pekerja;

CREATE FUNCTION hapus_akun_jatuh_tempo(p_user_id uuid, p_semu uuid)
  RETURNS boolean
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
  BEGIN
    IF p_semu IS NULL OR p_semu = p_user_id THEN
      RAISE EXCEPTION 'id semu wajib ada dan berbeda dari id akun';
    END IF;
    PERFORM 1 FROM public.users u
      WHERE u.id = p_user_id
        AND u.status = 'pending_deletion' AND u.deletion_scheduled_at <= now()
      FOR UPDATE;
    IF NOT FOUND THEN
      RETURN false;
    END IF;
    UPDATE public.audit_logs a
      SET user_id = p_semu,
          actor_id = replace(a.actor_id, p_user_id::text, p_semu::text),
          subject_id = replace(a.subject_id, p_user_id::text, p_semu::text),
          metadata = replace(a.metadata::text, p_user_id::text, p_semu::text)::jsonb
      WHERE a.user_id = p_user_id;
    DELETE FROM public.users WHERE id = p_user_id;
    INSERT INTO public.audit_logs (data_subject, actor_type, actor_id, user_id, action,
                                   subject_type, subject_id)
      VALUES ('user', 'system', 'sapuan-hapus-akun', p_semu, 'account.deleted',
              'user', p_semu::text);
    RETURN true;
  END
  $$;
REVOKE ALL ON FUNCTION hapus_akun_jatuh_tempo(uuid, uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hapus_akun_jatuh_tempo(uuid, uuid) TO hvx_pekerja;
