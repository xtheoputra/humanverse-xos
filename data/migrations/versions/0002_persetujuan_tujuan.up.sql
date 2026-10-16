-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0002 — consents: purpose · data_scopes · expires_at
-- spec/07 1.4 · B-22 (#59) · naskah 12 §8.9 (Why · Scope · Duration)
--
-- Bentuk akhirnya ada di spec/01 bagian Identity; tests/integration/
-- test_migrasi.py membandingkan katalog spec/01 dengan head migrasi.
--
-- `purpose` NOT NULL tanpa bawaan: tidak ada tujuan yang benar untuk
-- ditebak. Aman karena V0 belum pernah punya satu baris consents pun.
-- ════════════════════════════════════════════════════════════════════

ALTER TABLE consents
  ADD COLUMN purpose     text NOT NULL CHECK (purpose ~ '^[a-z][a-z0-9_]{0,62}$'),
  ADD COLUMN data_scopes text[] NOT NULL DEFAULT '{}',
  ADD COLUMN expires_at  timestamptz;

CREATE INDEX consents_user_purpose_idx ON consents (user_id, purpose, created_at DESC);
