-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0013 — Privacy Center: hapus per kategori sampai ke event
-- spec/07 6.4 · spec/01 §10 · §12 · K-42 · C-31 · C-34
--
-- `events` hanya-tambah bagi peran api (spec/02 aturan C, spec/01 §10): `hvx_app`
-- sengaja tanpa `UPDATE`/`DELETE`, dan §10 melarang membukanya dengan melebarkan
-- GRANT. Tetapi naskah 11 §7.25 menuntut *“tidak boleh hanya menghapus row di
-- PostgreSQL”* — hapus data atas permintaan pemiliknya ikut membuang riwayat
-- event-nya. Satu fungsi sempit menjadi jalur itu: hanya event milik pengguna
-- yang SEDANG DILAYANI transaksi (`app_current_user_id()`), hanya jenis yang
-- disebut, dan — bila diminta — hanya satu subjek. Tanpa pengguna yang dilayani,
-- ia tidak menghapus apa pun.
--
-- Event tetap TIDAK BISA DIUBAH oleh siapa pun lewat api; yang dibuka hanya
-- PENGHAPUSAN atas permintaan pemiliknya (naskah 11 §7.25: *event boleh dihapus
-- atas permintaan pemiliknya, tidak boleh diubah oleh sistem*).
-- ════════════════════════════════════════════════════════════════════

CREATE FUNCTION hapus_event_pengguna(p_jenis text[], p_subjek_tipe text, p_subjek_id uuid)
  RETURNS integer
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
  DECLARE
    v_pengguna uuid := public.app_current_user_id();
    v_jumlah integer;
  BEGIN
    IF v_pengguna IS NULL THEN
      RAISE EXCEPTION 'hapus_event_pengguna: tidak ada pengguna yang dilayani transaksi ini'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    IF (p_subjek_tipe IS NULL) <> (p_subjek_id IS NULL) THEN
      RAISE EXCEPTION 'hapus_event_pengguna: subjek wajib tipe DAN id, atau keduanya kosong';
    END IF;
    DELETE FROM public.events e
      WHERE e.user_id = v_pengguna
        AND e.event_type = ANY(p_jenis)
        AND (p_subjek_id IS NULL
             OR (e.subject_type = p_subjek_tipe AND e.subject_id = p_subjek_id));
    GET DIAGNOSTICS v_jumlah = ROW_COUNT;
    RETURN v_jumlah;
  END
  $$;
REVOKE ALL ON FUNCTION hapus_event_pengguna(text[], text, uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hapus_event_pengguna(text[], text, uuid) TO hvx_app;

-- C-34 (diputuskan 7 Okt 2026, K-46): jejak audit akun yang dihapus tetap ada
-- sebagai BUKTI (id semu), tetapi `ip_hash` — HMAC jaringan klien — dikosongkan.
-- Tujuan keamanan yang membenarkannya (GDPR Recital 49) berakhir bersama akunnya;
-- yang tersisa tidak lagi bisa dipertemukan dengan akun lain lewat jaringan yang sama.
CREATE OR REPLACE FUNCTION hapus_akun_jatuh_tempo(p_user_id uuid, p_semu uuid)
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
          metadata = replace(a.metadata::text, p_user_id::text, p_semu::text)::jsonb,
          ip_hash = NULL
      WHERE a.user_id = p_user_id;
    DELETE FROM public.users WHERE id = p_user_id;
    INSERT INTO public.audit_logs (data_subject, actor_type, actor_id, user_id, action,
                                   subject_type, subject_id)
      VALUES ('user', 'system', 'sapuan-hapus-akun', p_semu, 'account.deleted',
              'user', p_semu::text);
    RETURN true;
  END
  $$;

-- C-31 (K-46): hapus jurnal kini hapus KERAS. Jurnal yang SUDAH dihapus-lunak sebelum
-- migrasi ini tidak boleh menginap: barisnya dan event `journal.created`-nya dibuang (memori
-- turunannya sudah dikosongkan saat itu, K-27; penyelaras membuang titiknya). Tidak bisa
-- dibalik — dan memang tidak boleh: pemiliknya sudah meminta tulisan itu dihapus.
DELETE FROM events e USING journal_entries j
  WHERE e.event_type = 'journal.created' AND e.subject_type = 'journal'
    AND e.subject_id = j.id AND e.user_id = j.user_id AND j.deleted_at IS NOT NULL;
DELETE FROM journal_entries WHERE deleted_at IS NOT NULL;
