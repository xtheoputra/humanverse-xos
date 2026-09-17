-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0003 — auth_lookup_for_login(email): login di bawah RLS
-- spec/07 1.1 · spec/01 §12 · K-19
--
-- RLS `users` tidak meloloskan pencarian akun sebelum pengguna dikenali, dan
-- tidak boleh dilonggarkan. Fungsi SECURITY DEFINER yang sempit menjawab satu
-- pertanyaan untuk satu email, hanya bagi hvx_app.
-- ════════════════════════════════════════════════════════════════════

CREATE FUNCTION auth_lookup_for_login(p_email citext)
  RETURNS TABLE (id uuid, password_hash text, status text)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT u.id, u.password_hash, u.status
    FROM public.users u
    WHERE u.email = p_email AND u.deleted_at IS NULL
  $$;
REVOKE ALL ON FUNCTION auth_lookup_for_login(citext) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION auth_lookup_for_login(citext) TO hvx_app;
