-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0010 — users.deletion_scheduled_at
-- spec/07 6.5 · spec/01 "Prosedur hapus akun"
--
-- Alur hapus akun enam tahap butuh penanda WAKTU untuk tenggang 30 hari:
-- tahap 1 mengisi `deletion_scheduled_at = now()+30 hari`, sapuan pemeliharaan
-- (tahap 3) menghapus akun yang `deletion_scheduled_at <= now()`, dan restore
-- mengosongkannya. `deleted_at` tidak dipakai untuk ini — ia menyaring GET /me
-- (`deleted_at IS NULL`), dan akun yang menunggu dihapus harus tetap terbaca
-- supaya bisa dibatalkan. Kolom di ujung tabel (ordinal cocok dengan spec/01).
-- ════════════════════════════════════════════════════════════════════

ALTER TABLE users
  ADD COLUMN deletion_scheduled_at timestamptz;
