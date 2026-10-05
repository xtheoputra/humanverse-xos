-- Migrasi 0010 turun — penanda jadwal hapus akun dibuang.
ALTER TABLE users
  DROP COLUMN deletion_scheduled_at;
