-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0001 — V0: 23 tabel · spec/01-DATABASE-SCHEMA.md
--
-- Isinya SELURUH blok ```sql di spec/01, berurutan, tanpa diubah. Kesamaannya
-- tidak dijaga ingatan melainkan uji: tests/integration/test_migrasi.py
-- menjalankan berkas ini dan DDL spec/01 ke dua basis data terpisah, lalu
-- membandingkan katalognya bagian per bagian (KUERI_KATALOG di uji itu — yang
-- dibandingkan DAN yang sengaja tidak, tertulis di docstring-nya).
--
-- Tiap CREATE TABLE membawa `data_subject` + tiga anotasi retensi (K-16);
-- tools/periksa_dokumen.py P-1 · P-2 · P-3 membaca berkas ini juga.
-- ════════════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS citext;

-- dipakai semua tabel yang punya updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$ LANGUAGE plpgsql;

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE users (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  email           citext NOT NULL UNIQUE,
  password_hash   text   NOT NULL,              -- argon2id
  status          text   NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','suspended','pending_deletion')),
  email_verified_at timestamptz,
  last_login_at   timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz
);
CREATE INDEX users_status_idx ON users (status) WHERE deleted_at IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE profiles (
  user_id      uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  display_name text NOT NULL,
  timezone     text NOT NULL DEFAULT 'UTC',     -- IANA, mis. 'Asia/Jakarta'
  locale       text NOT NULL DEFAULT 'id-ID',
  birth_year   smallint CHECK (birth_year BETWEEN 1900 AND 2100),
  avatar_url   text,
  preferences  jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE consents (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  kind           text NOT NULL,                 -- 'terms','privacy','ai_processing','location',...
  policy_version text NOT NULL,
  granted        boolean NOT NULL,
  source         text NOT NULL DEFAULT 'app'
                   CHECK (source IN ('app','import','admin')),
  granted_at     timestamptz,
  revoked_at     timestamptz,
  created_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX consents_user_kind_idx ON consents (user_id, kind, created_at DESC);

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE permissions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  subject_type  text NOT NULL CHECK (subject_type IN ('agent','tool','integration')),
  subject_id    text NOT NULL,                  -- 'fashion-agent', 'weather.get'
  scope         text NOT NULL,                  -- 'wardrobe', 'fashion_preferences'
  action        text NOT NULL
                  CHECK (action IN ('read','write','execute','share','delete')),
  decision      text NOT NULL DEFAULT 'ask'
                  CHECK (decision IN ('allow','deny','ask')),
  expires_at    timestamptz,                    -- NULL = selamanya; 'allow once' pakai ini
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, subject_type, subject_id, scope, action)
);
CREATE INDEX permissions_lookup_idx
  ON permissions (user_id, subject_id, scope, action);

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE goals (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  parent_id   uuid REFERENCES goals(id) ON DELETE SET NULL,  -- Goal Graph naskah 4 §9
  title       text NOT NULL,
  description text,
  domain      text CHECK (domain IN
                ('career','health','finance','learning','social','lifestyle','other')),
  status      text NOT NULL DEFAULT 'active'
                CHECK (status IN ('active','paused','achieved','dropped')),
  target_date date,
  achieved_at timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  deleted_at  timestamptz
);
CREATE INDEX goals_user_status_idx ON goals (user_id, status) WHERE deleted_at IS NULL;
CREATE INDEX goals_parent_idx      ON goals (parent_id) WHERE parent_id IS NOT NULL;

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE goal_milestones (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  goal_id      uuid NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title        text NOT NULL,
  position     integer NOT NULL DEFAULT 0,
  status       text NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','in_progress','done','skipped')),
  due_date     date,
  completed_at timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX goal_milestones_goal_idx ON goal_milestones (goal_id, position);

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE habits (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  goal_id          uuid REFERENCES goals(id) ON DELETE SET NULL,
  title            text NOT NULL,
  period           text NOT NULL DEFAULT 'week'
                     CHECK (period IN ('day','week','month')),
  target_count     smallint NOT NULL DEFAULT 1 CHECK (target_count > 0),
  schedule         jsonb NOT NULL DEFAULT '{}'::jsonb,  -- {"weekdays":[1,3,5],"time":"18:00"}
  adaptive_tiers   jsonb NOT NULL DEFAULT '[]'::jsonb,  -- naskah 4 §34
  status           text NOT NULL DEFAULT 'active'
                     CHECK (status IN ('active','paused','archived')),
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now(),
  deleted_at       timestamptz
);
CREATE INDEX habits_user_status_idx ON habits (user_id, status) WHERE deleted_at IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE habit_completions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  habit_id      uuid NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
  user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  for_date      date NOT NULL,                  -- tanggal LOKAL pengguna
  status        text NOT NULL
                  CHECK (status IN ('done','skipped','partial')),
  tier_used     smallint,                       -- indeks adaptive_tiers yang dipakai
  note          text,
  source        text NOT NULL DEFAULT 'manual'
                  CHECK (source IN ('manual','auto','import')),
  completed_at  timestamptz NOT NULL DEFAULT now(),
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (habit_id, for_date)
);
CREATE INDEX habit_completions_user_date_idx
  ON habit_completions (user_id, for_date DESC);

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE daily_checkins (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  for_date     date NOT NULL,
  energy       smallint CHECK (energy BETWEEN 1 AND 5),
  focus        smallint CHECK (focus  BETWEEN 1 AND 5),
  sleep_hours  numeric(3,1) CHECK (sleep_hours BETWEEN 0 AND 24),
  note         text,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, for_date)
);

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE mood_entries (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  occurred_at timestamptz NOT NULL DEFAULT now(),
  valence     smallint NOT NULL CHECK (valence BETWEEN 1 AND 5),
  label       text,                              -- 'cemas', 'lega', ...
  note        text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  deleted_at  timestamptz
);
CREATE INDEX mood_entries_user_time_idx
  ON mood_entries (user_id, occurred_at DESC) WHERE deleted_at IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE journal_entries (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  occurred_at timestamptz NOT NULL DEFAULT now(),
  title       text,
  body        text NOT NULL,
  word_count  integer NOT NULL DEFAULT 0,
  safety_flag text CHECK (safety_flag IN ('none','review','crisis')),
  safety_checked_at timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  deleted_at  timestamptz
);
CREATE INDEX journal_entries_user_time_idx
  ON journal_entries (user_id, occurred_at DESC) WHERE deleted_at IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE activities (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  kind             text NOT NULL,                -- 'workout','meal','learning','meeting',...
  occurred_at      timestamptz NOT NULL,
  ended_at         timestamptz,
  duration_seconds integer CHECK (duration_seconds >= 0),
  source           text NOT NULL DEFAULT 'manual'
                     CHECK (source IN ('manual','wearable','integration','inferred')),
  payload          jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at       timestamptz NOT NULL DEFAULT now(),
  deleted_at       timestamptz,
  CHECK (ended_at IS NULL OR ended_at >= occurred_at)
);
CREATE INDEX activities_user_time_idx  ON activities (user_id, occurred_at DESC);
CREATE INDEX activities_user_kind_idx  ON activities (user_id, kind, occurred_at DESC);

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE events (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  event_type      text NOT NULL,                 -- 'habit.completed'
  schema_version  smallint NOT NULL DEFAULT 1,
  occurred_at     timestamptz NOT NULL,          -- kapan TERJADI
  recorded_at     timestamptz NOT NULL DEFAULT now(),  -- kapan MASUK sistem
  source          text NOT NULL DEFAULT 'app'
                    CHECK (source IN ('app','agent','integration','backfill')),
  idempotency_key text NOT NULL,
  subject_type    text,                          -- 'habit','goal','journal'
  subject_id      uuid,
  payload         jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, idempotency_key)
);
CREATE INDEX events_user_time_idx    ON events (user_id, occurred_at DESC);
CREATE INDEX events_type_time_idx    ON events (event_type, occurred_at DESC);
CREATE INDEX events_subject_idx      ON events (subject_type, subject_id);
CREATE INDEX events_payload_gin      ON events USING gin (payload jsonb_path_ops);

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE memories (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  kind              text NOT NULL CHECK (kind IN
                      ('working','episodic','semantic','behavioral',
                       'preference','procedural')),
  scope             text NOT NULL,               -- 'fashion_preferences','wardrobe',...

  content           text NOT NULL,
  summary           text,
  embedding_id      text,                        -- id titik di Qdrant; NULL = belum di-embed

  confidence        numeric(4,3) NOT NULL DEFAULT 0.500
                      CHECK (confidence BETWEEN 0 AND 1),
  evidence_count    integer NOT NULL DEFAULT 1 CHECK (evidence_count >= 0),
  model_version     text,

  source_event_id   uuid REFERENCES events(id) ON DELETE SET NULL,
  valid_from        timestamptz NOT NULL DEFAULT now(),
  valid_until       timestamptz,                 -- NULL = masih berlaku
  last_reinforced_at timestamptz NOT NULL DEFAULT now(),

  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  deleted_at        timestamptz
);
CREATE INDEX memories_user_kind_idx  ON memories (user_id, kind)  WHERE deleted_at IS NULL;
CREATE INDEX memories_user_scope_idx ON memories (user_id, scope) WHERE deleted_at IS NULL;
CREATE INDEX memories_active_idx     ON memories (user_id, last_reinforced_at DESC)
                                     WHERE deleted_at IS NULL AND valid_until IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE human_states (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  for_date      date NOT NULL,
  metrics       jsonb NOT NULL DEFAULT '{}'::jsonb,
  model_version text NOT NULL,
  computed_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, for_date, model_version)
);
CREATE INDEX human_states_user_date_idx ON human_states (user_id, for_date DESC);

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE ai_conversations (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  title           text,
  started_at      timestamptz NOT NULL DEFAULT now(),
  last_message_at timestamptz,
  message_count   integer NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz
);
CREATE INDEX ai_conversations_user_idx
  ON ai_conversations (user_id, last_message_at DESC NULLS LAST)
  WHERE deleted_at IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE ai_messages (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  conversation_id uuid NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role            text NOT NULL CHECK (role IN ('user','assistant','tool','system')),
  content         text NOT NULL,
  agent_run_id    uuid,                          -- FK ditambah setelah agent_runs dibuat
  model           text,
  tokens_in       integer,
  tokens_out      integer,
  latency_ms      integer,
  cost_usd        numeric(12,6),
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ai_messages_conversation_idx
  ON ai_messages (conversation_id, created_at);

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE recommendations (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  agent_id         uuid,                         -- FK ke agents, ditambah di bawah
  agent_run_id     uuid,
  domain           text NOT NULL,                -- 'habit','goal','wellbeing'
  subject_type     text,                         -- 'habit','goal'
  subject_id       uuid,

  title            text NOT NULL,
  body             text,

  score            numeric(4,3) CHECK (score BETWEEN 0 AND 1),
  scoring_version  text NOT NULL DEFAULT 'v1',
  score_breakdown  jsonb NOT NULL DEFAULT '{}'::jsonb,
  confidence       numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
  rationale        jsonb NOT NULL DEFAULT '[]'::jsonb,
  context_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,

  status           text NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','shown','accepted','rejected','expired')),
  shown_at         timestamptz,
  expires_at       timestamptz,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX recommendations_user_status_idx
  ON recommendations (user_id, status, created_at DESC);

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE recommendation_feedback (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  recommendation_id uuid NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
  user_id           uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  action            text NOT NULL
                      CHECK (action IN ('accepted','rejected','ignored','modified','snoozed')),
  reason            text,
  outcome           jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX recommendation_feedback_user_idx
  ON recommendation_feedback (user_id, created_at DESC);

-- @retention   : forever
-- @who-can-set : system
-- @on-delete   : not-applicable
CREATE TABLE agents (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'system'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  name                  text NOT NULL,               -- 'coach-agent'
  version               text NOT NULL,               -- '1.0.0'
  kind                  text NOT NULL DEFAULT 'core'
                          CHECK (kind IN ('core','domain','third_party')),
  status                text NOT NULL DEFAULT 'draft'
                          CHECK (status IN ('draft','active','deprecated','disabled')),
  max_risk              smallint NOT NULL DEFAULT 0     -- 🔧 PAGU risiko aksi (H-21)
                          CHECK (max_risk BETWEEN 0 AND 4),
  manifest              jsonb NOT NULL,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now(),
  UNIQUE (name, version)
);
CREATE UNIQUE INDEX agents_one_active_idx
  ON agents (name) WHERE status = 'active';

-- @retention   : forever
-- @who-can-set : system
-- @on-delete   : not-applicable
CREATE TABLE agent_tools (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'system'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  agent_id    uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  tool_name   text NOT NULL,                    -- 'weather.get'
  permission  text NOT NULL DEFAULT 'execute'
                CHECK (permission IN ('read','write','execute')),
  constraints jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (agent_id, tool_name)
);

-- @retention   : until-account-deleted
-- @who-can-set : system
-- @on-delete   : hard
CREATE TABLE agent_runs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  agent_id        uuid NOT NULL REFERENCES agents(id),
  agent_version   text NOT NULL,
  conversation_id uuid REFERENCES ai_conversations(id) ON DELETE SET NULL,
  parent_run_id   uuid REFERENCES agent_runs(id) ON DELETE SET NULL,

  trigger         text NOT NULL CHECK (trigger IN ('user','schedule','event','agent')),
  status          text NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running','succeeded','failed','blocked','cancelled')),

  tools_used      text[] NOT NULL DEFAULT '{}',
  memory_scopes   text[] NOT NULL DEFAULT '{}',
  model_used      text,
  risk_level      smallint CHECK (risk_level BETWEEN 0 AND 4),
  confirmed_by_user boolean,

  decision        jsonb NOT NULL DEFAULT '{}'::jsonb,
  confidence      numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
  error           jsonb,

  tokens_in       integer,
  tokens_out      integer,
  cost_usd        numeric(12,6),
  latency_ms      integer,
  started_at      timestamptz NOT NULL DEFAULT now(),
  finished_at     timestamptz
);
CREATE INDEX agent_runs_user_time_idx  ON agent_runs (user_id, started_at DESC);
CREATE INDEX agent_runs_agent_idx      ON agent_runs (agent_id, started_at DESC);
CREATE INDEX agent_runs_parent_idx     ON agent_runs (parent_run_id)
                                       WHERE parent_run_id IS NOT NULL;

ALTER TABLE ai_messages
  ADD CONSTRAINT ai_messages_agent_run_fk
  FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id) ON DELETE SET NULL;
ALTER TABLE recommendations
  ADD CONSTRAINT recommendations_agent_fk
  FOREIGN KEY (agent_id) REFERENCES agents(id),
  ADD CONSTRAINT recommendations_run_fk
  FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id) ON DELETE SET NULL;

-- @retention   : forever
-- @who-can-set : system
-- @on-delete   : anonymise
CREATE TABLE audit_logs (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  occurred_at  timestamptz NOT NULL DEFAULT now(),
  actor_type   text NOT NULL CHECK (actor_type IN ('user','agent','system','admin')),
  actor_id     text NOT NULL,
  user_id      uuid,                             -- SENGAJA tanpa FK; lihat catatan
  action       text NOT NULL,                    -- 'permission.granted','data.exported'
  subject_type text,
  subject_id   text,
  request_id   text,
  ip_hash      text,                             -- hash, bukan IP mentah
  metadata     jsonb NOT NULL DEFAULT '{}'::jsonb,

  -- arch/06 §6 sebagai CHECK, bukan sebagai NOT NULL kolom:
  -- `audit_logs` satu-satunya tabel V0 yang barisnya bisa milik
  -- pengguna ATAU milik sistem, jadi `data_subject` di sini sifat
  -- BARIS. Tanpa CHECK ini, RLS `user_id = current_user` meloloskan
  -- NULL pada sebagian konfigurasi.
  CHECK ((data_subject = 'user') = (user_id IS NOT NULL))
);
CREATE INDEX audit_logs_user_time_idx   ON audit_logs (user_id, occurred_at DESC);
CREATE INDEX audit_logs_action_time_idx ON audit_logs (action, occurred_at DESC);

REVOKE UPDATE, DELETE ON audit_logs FROM PUBLIC;

CREATE TRIGGER users_set_updated_at             BEFORE UPDATE ON users             FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER profiles_set_updated_at          BEFORE UPDATE ON profiles          FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER permissions_set_updated_at       BEFORE UPDATE ON permissions       FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER goals_set_updated_at             BEFORE UPDATE ON goals             FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER goal_milestones_set_updated_at   BEFORE UPDATE ON goal_milestones   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER habits_set_updated_at            BEFORE UPDATE ON habits            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER daily_checkins_set_updated_at    BEFORE UPDATE ON daily_checkins    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER journal_entries_set_updated_at   BEFORE UPDATE ON journal_entries   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER memories_set_updated_at          BEFORE UPDATE ON memories          FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER recommendations_set_updated_at   BEFORE UPDATE ON recommendations   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER agents_set_updated_at            BEFORE UPDATE ON agents            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
