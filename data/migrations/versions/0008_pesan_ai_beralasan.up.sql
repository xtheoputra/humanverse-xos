-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0008 — ai_messages.confidence + rationale
-- spec/07 4.8 · spec/04 *AI* · E-194
--
-- spec/04 menjanjikan `confidence` dan `rationale` di SETIAP balasan AI
-- (Confidence Layer §19, Explainable AI naskah 4 §29) — tetapi hanya SSE
-- `done` yang membawanya: riwayat `GET /conversations/{id}/messages` tidak
-- punya tempat untuk keduanya, jadi balasan yang dibaca ulang kehilangan
-- alasannya. `agent_runs` bukan tempatnya: alasan adalah kalimat untuk
-- pengguna (tulisan yang ikut terhapus bersama percakapannya), bukan
-- metadata audit.
-- ════════════════════════════════════════════════════════════════════

ALTER TABLE ai_messages
  ADD COLUMN confidence numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
  ADD COLUMN rationale  jsonb NOT NULL DEFAULT '[]'::jsonb;
