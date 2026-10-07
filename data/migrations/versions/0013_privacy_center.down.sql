-- Migrasi 0013 turun — fungsi hapus event dibuang; sapuan hapus akun kembali ke bentuk 0011
-- (`ip_hash` jejak audit akun yang dihapus tidak dikosongkan).
DROP FUNCTION hapus_event_pengguna(text[], text, uuid);

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
