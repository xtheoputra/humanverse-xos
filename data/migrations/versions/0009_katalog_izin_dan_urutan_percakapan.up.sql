-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0009 — dua ketidakcocokan yang ditemukan tinjauan kontrak Sprint 4
-- spec/07 4.2 · 4.8 · K-29 · E-209 · E-210
--
-- (1) `agent_tools.permission` = aksi mesin izin untuk jenis tool-nya —
--     `read` · `write` · `execute` (`kind: agent`), sama dengan yang
--     ditanyakan gerbang risiko (`agents.AKSI_IZIN`). Migrasi 0007 memakai
--     bawaan kolom (`execute`) untuk semuanya: katalog menyatakan tool BACA
--     sebagai eksekusi, dan tidak ada yang membandingkannya. Kini
--     `agents.pastikan_katalog` membandingkannya — api menolak mulai bila
--     berbeda.
-- (2) `GET /conversations` terurut `(created_at, id)` — kursor keyset yang
--     tidak bergeser saat percakapan lain menerima pesan. Indeks 0001
--     menyusun `last_message_at`, yang tidak dipakai kueri mana pun.
-- ════════════════════════════════════════════════════════════════════

UPDATE agent_tools SET permission = 'read'
WHERE tool_name IN ('habit.list', 'habit.streak', 'goal.list', 'checkin.get', 'mood.recent',
                    'memory.search');
UPDATE agent_tools SET permission = 'write'
WHERE tool_name IN ('habit.complete', 'memory.write', 'recommendation.create');
UPDATE agent_tools SET permission = 'execute'
WHERE tool_name IN ('agent.coach', 'agent.habit', 'agent.memory');

DROP INDEX ai_conversations_user_idx;
CREATE INDEX ai_conversations_user_idx
  ON ai_conversations (user_id, created_at DESC, id DESC)
  WHERE deleted_at IS NULL;
