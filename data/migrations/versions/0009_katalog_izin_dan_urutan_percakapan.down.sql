-- Migrasi 0009 turun — indeks percakapan kembali ke `last_message_at`, izin katalog ke bawaan.
DROP INDEX ai_conversations_user_idx;
CREATE INDEX ai_conversations_user_idx
  ON ai_conversations (user_id, last_message_at DESC NULLS LAST)
  WHERE deleted_at IS NULL;

UPDATE agent_tools SET permission = 'execute';
