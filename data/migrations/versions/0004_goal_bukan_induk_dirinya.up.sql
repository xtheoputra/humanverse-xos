-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0004 — goals: goal tidak boleh menjadi induk dirinya sendiri
-- spec/07 2.1 · spec/01 §2 (Goal Graph naskah 4 §9)
--
-- FK komposit (parent_id, user_id) → goals (id, user_id) diperiksa SESUDAH
-- barisnya ada, jadi baris yang menunjuk DIRINYA SENDIRI lolos — dan pohon goal
-- menjadi lingkaran yang tidak pernah berakhir. Lingkaran yang lebih panjang
-- tidak bisa terbentuk: `parent_id` tidak bisa diubah lewat API (spec/04), dan
-- goal baru hanya bisa menunjuk goal yang sudah ada.
-- ════════════════════════════════════════════════════════════════════

ALTER TABLE goals
  ADD CONSTRAINT goals_parent_not_self CHECK (parent_id <> id);
