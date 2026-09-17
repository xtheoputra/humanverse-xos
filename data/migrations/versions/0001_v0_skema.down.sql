-- Migrasi 0001 turun — mengembalikan basis data ke keadaan sebelum 0001.
--
-- Satu DROP TABLE untuk ke-23 tabel sekaligus: PostgreSQL menyelesaikan
-- ketergantungan FK di antara tabel yang disebut bersama. TANPA CASCADE —
-- kalau ada objek lain yang bergantung pada tabel V0, turun harus GAGAL
-- dengan keras, bukan menghapus objek itu diam-diam.

DROP TABLE
  audit_logs,
  agent_runs,
  agent_tools,
  agents,
  recommendation_feedback,
  recommendations,
  ai_messages,
  ai_conversations,
  human_states,
  memories,
  events,
  activities,
  journal_entries,
  mood_entries,
  daily_checkins,
  habit_completions,
  habits,
  goal_milestones,
  goals,
  permissions,
  consents,
  profiles,
  users;

DROP FUNCTION set_updated_at();
DROP FUNCTION app_current_user_id();

-- `citext` SENGAJA tidak dilepas. 0001 memasangnya dengan IF NOT EXISTS, jadi
-- ia tidak bisa tahu apakah ekstensinya ADA sebelum 0001. Versi pertama
-- melepasnya — dan diukur: pada basis data yang sudah memakai citext, turun
-- GAGAL; pada yang sudah memasangnya tanpa memakai, turun diam-diam
-- mencabutnya. Ekstensi milik basis data, bukan milik migrasi ini.
--
-- Peran `hvx_app` juga SENGAJA tidak dilepas, dengan alasan yang lebih kuat:
-- peran berlaku untuk seluruh KLASTER, bukan satu basis data. Basis data lain
-- di klaster yang sama (uji sekali pakai, lingkungan lain) bisa sedang
-- memakainya. Hak aksesnya di basis data ini ikut hilang bersama tabelnya, dan
-- kebijakan RLS ikut hilang bersama tabel yang memilikinya.
