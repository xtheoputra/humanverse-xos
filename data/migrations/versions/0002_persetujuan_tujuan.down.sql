-- Migrasi 0002 turun — kolom tujuan persetujuan dilepas, TANPA CASCADE.
DROP INDEX consents_user_purpose_idx;

ALTER TABLE consents
  DROP COLUMN expires_at,
  DROP COLUMN data_scopes,
  DROP COLUMN purpose;
