-- Migrasi 0008 turun — kolom keyakinan & alasan pesan AI dibuang.
ALTER TABLE ai_messages
  DROP COLUMN rationale,
  DROP COLUMN confidence;
