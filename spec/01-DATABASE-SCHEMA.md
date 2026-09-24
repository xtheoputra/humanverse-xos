# 01 — Database Schema (PostgreSQL, V0)

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Diturunkan dari naskah 5 §31 (19 tabel) + naskah 6 (`events`, `agents`,
> `agent_tools`) + 1 usulan (`human_states`). Total **23 tabel**.

Target: **PostgreSQL 16**. Ekstensi: `citext` (email tanpa peduli huruf
besar-kecil).

> 🔧 **`pgcrypto` dicabut 16 Sep 2026.** Berkas ini semula memasangnya *“untuk
> `gen_random_uuid()`”* — fungsi itu sudah bawaan PostgreSQL sejak versi 13.
> Diperiksa di PostgreSQL 16 sungguhan: tidak satu pun bawaan kolom bergantung
> pada `pgcrypto`, dan ekstensinya bisa dilepas dengan 23 tabel tetap bekerja.
> Ketergantungan yang tidak dipakai hanya menambah hal yang bisa gagal saat
> dipasang dan dilepas.

---

## 🔧 Presedensi ketika sebuah tabel didefinisikan lebih dari sekali (K-4)

> Ditambahkan 9 September 2026 — **keputusan didelegasikan K-4**, menutup
> **E-156** / [#151](../../issues/151).

Sensus menemukan **19 nama tabel yang didefinisikan lebih dari sekali** lintas
fase — `agent_capabilities` dan `agent_trust_scores` masing-masing **empat
kali** ([`../docs/SENSUS-TABEL.md`](../docs/SENSUS-TABEL.md)). Aturannya:

1. **Kalau namanya ada di berkas ini, definisi berkas ini yang berlaku.**
2. Kalau tidak, **definisi fase paling awal** yang kanonik.
3. Fase berikutnya boleh **menambah kolom**; tidak boleh **mendefinisikan
   ulang** bentuk yang sudah ada.

⚠️ Ini **tidak menambah atau mengubah satu tabel pun di V0** — jumlahnya tetap
**23**. Ia hanya menetapkan siapa yang menang kalau nama yang sama muncul lagi
di fase berikutnya.

---


## Konvensi

| Hal | Aturan |
|---|---|
| Nama tabel | `snake_case`, **jamak** |
| Kunci utama | `id uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| Waktu | `timestamptz`, disimpan UTC. Kolom tanggal lokal pengguna (`for_date`) pakai `date`: tanggal lokal **perangkat** saat hal itu terjadi — tidak pernah diturunkan dari cap waktu UTC, dan **tidak** dari `profiles.timezone` (perangkat yang bepergian bisa berada di zona lain). `profiles.timezone` menjawab *“hari ini”* pengguna — rentetan 2.4 (🔧 E-176: semula *“`date` + `profiles.timezone`”*, terbaca seolah tanggalnya dihitung dari zona profil) |
| Jejak baris | setiap tabel punya `created_at`, dan `updated_at` bila barisnya bisa berubah |
| Hapus | `deleted_at timestamptz` pada tabel berisi tulisan pengguna; sisanya hapus keras |
| Uang | `numeric(12,6)` — jangan `float` |
| Skor 0–1 | `numeric(4,3)` + `CHECK (x >= 0 AND x <= 1)` |
| Enum | `text` + `CHECK (... IN (...))`, **bukan** tipe `ENUM` PostgreSQL — supaya nilai baru tidak butuh migrasi tipe |

---

## Awalan

```sql
CREATE EXTENSION IF NOT EXISTS citext;

-- dipakai semua tabel yang punya updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$ LANGUAGE plpgsql;

-- B-40 · peran APLIKASI: bukan superuser, bukan pemilik tabel, tanpa BYPASSRLS.
-- NOLOGIN — peran login api (mis. `hvx_api`) dibuat di luar migrasi dan
-- dijadikan anggotanya. Peran berlaku sekluster, jadi turun TIDAK melepasnya.
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hvx_app') THEN
    CREATE ROLE hvx_app NOLOGIN;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;  -- dibuat migrasi lain di klaster yang sama, di antara cek dan CREATE
END $$;

-- RLS · pengguna yang sedang dilayani transaksi ini. Aplikasi mengisinya per
-- transaksi: SELECT set_config('hvx.user_id', '<uuid>', true). Tidak diisi →
-- NULL → kebijakan RLS tidak meloloskan satu baris pun (gagal-tertutup).
CREATE OR REPLACE FUNCTION app_current_user_id() RETURNS uuid
  LANGUAGE sql STABLE
  AS $$ SELECT nullif(current_setting('hvx.user_id', true), '')::uuid $$;
```

> 🔧 **Dua objek di atas ditambahkan 17 Sep 2026 — B-40 dan keputusan pemilik
> H-27** (*“data masing-masing pengguna milik pribadi user”*). `hvx_app` adalah
> peran yang dipakai api; hak aksesnya ditulis tabel demi tabel di §10, dan RLS
> di §11 memakai `app_current_user_id()` untuk membatasinya pada baris
> pengguna yang sedang dilayani.

---

## 1 · Identity

```sql
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
```

> 🔧 **`preferences jsonb`, bukan kolom tetap.** Naskah 1–5 belum sepakat isi
> profil (issue #2); jsonb menahan keputusan itu tanpa memblokir V0. Begitu
> #2 dijawab, kolom yang sering dibaca dipromosikan jadi kolom nyata.

```sql
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
  created_at     timestamptz NOT NULL DEFAULT now(),
  -- spec/07 1.4 · B-22 · naskah 12 §8.9 (Why · Scope · Duration) — migrasi 0002
  purpose        text NOT NULL CHECK (purpose ~ '^[a-z][a-z0-9_]{0,62}$'),
  data_scopes    text[] NOT NULL DEFAULT '{}',
  expires_at     timestamptz
);
CREATE INDEX consents_user_kind_idx ON consents (user_id, kind, created_at DESC);
CREATE INDEX consents_user_purpose_idx ON consents (user_id, purpose, created_at DESC);
```

> Riwayat persetujuan **append-only** — baris lama tidak diubah, pencabutan
> ditulis sebagai baris baru. Itu yang membuat *"kapan dia setuju apa"* bisa
> dijawab setahun kemudian (naskah 5 §25 *Consent management*).
>
> 🔧 **`purpose` · `data_scopes` · `expires_at` — spec/07 1.4, B-22
> ([#59](../../issues/59)), 17 Sep 2026 (migrasi 0002).** Naskah 12 §8.9 memberi
> persetujuan sembilan sifat; tiga yang tidak punya kolom — **Why/Purpose**,
> **What/Scope**, **Duration** — kini punya. Aturan pembatasan tujuan §8.10
> menjadi satu operasi himpunan yang dijalankan mesin
> (`identity.boleh_dipakai_untuk`): **tiap tujuan pemakaian wajib punya
> persetujuan, dan persetujuan TERAKHIR dari TIAP jenis (`kind`) yang pernah
> dicatat untuk tujuan itu wajib `granted`, belum kedaluwarsa, dan
> `data_scopes`-nya mencakup data yang dipakai** — tanpa itu, ditolak. Satu
> jenis dicabut = tujuannya tertutup: `terms` dan `privacy` sama-sama bertujuan
> `service`, dan versi pertama (*“terakhir per tujuan”*) membiarkan persetujuan
> `terms` yang lebih baru menutupi pencabutan `privacy` (tinjauan Sprint 1).
> ⚠️ `terms` dan `privacy` dicatat **tanpa** `data_scopes` — badan `register`
> [`04`](04-API-CONTRACTS.md) tidak memberinya — jadi pertanyaan `service`
> **dengan** cakupan data selalu ditolak: gagal-tertutup sampai kosakata cakupan
> diputuskan (#59 butir 2).
> `purpose` berbentuk `snake_case` bebas (`fitness_recommendation` di naskah);
> kosakata finalnya keputusan pemilik (#59 butir 2), bukan `CHECK` di sini.
> Menolak `model_training` **tidak mengurangi layanan** (#59).

```sql
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
```

> Lima `action` diambil persis dari naskah 4 §15 (Read/Write/Execute/Share/
> Delete). `decision='ask'` sebagai default adalah penerapan janji *"Act selalu
> di bawah kontrol pengguna"* — issue #5 tinggal menetapkan risk level mana
> yang boleh `allow` otomatis.

---

## 2 · Goals & Habits

```sql
-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE goals (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  parent_id   uuid,                                          -- Goal Graph naskah 4 §9
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
  deleted_at  timestamptz,
  -- B-41: baris anak hanya boleh menunjuk induk milik pengguna yang SAMA.
  UNIQUE (id, user_id),
  FOREIGN KEY (parent_id, user_id) REFERENCES goals (id, user_id)
    ON DELETE SET NULL (parent_id),
  -- spec/07 2.1 — FK diperiksa SESUDAH barisnya ada: tanpa ini goal bisa menjadi
  -- induk dirinya sendiri, dan pohonnya lingkaran (migrasi 0004).
  CONSTRAINT goals_parent_not_self CHECK (parent_id <> id)
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
  goal_id      uuid NOT NULL,
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title        text NOT NULL,
  position     integer NOT NULL DEFAULT 0,
  status       text NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','in_progress','done','skipped')),
  due_date     date,
  completed_at timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (goal_id, user_id) REFERENCES goals (id, user_id) ON DELETE CASCADE
);
CREATE INDEX goal_milestones_goal_idx ON goal_milestones (goal_id, position);
```

> `parent_id` yang menunjuk ke tabelnya sendiri adalah **Goal Graph** naskah 4
> §9 (`LIFE GOAL → Career → Skills → Learning → Habit`) — cukup dengan satu
> kolom, tanpa Neo4j.
>
> 🔧 **B-41 — FK komposit `(induk_id, user_id)`, 17 Sep 2026.** Sebelas FK
> satu kolom (`goal_id`, `parent_id`, `habit_id`, `source_event_id`,
> `conversation_id` ×2, `agent_run_id` ×2, `recommendation_id`,
> `parent_run_id`) semula membiarkan baris anak milik pengguna B menunjuk
> induk milik pengguna A. Diukur: milestone B menempel ke goal A — diterima —
> lalu **ikut terhapus** saat A menghapus goal-nya. Kini tiap induk membawa
> `UNIQUE (id, user_id)` dan tiap anak menunjuknya dengan **pasangan**
> kolom, sehingga basis data sendiri yang menolak. `ON DELETE SET NULL
> (kolom)` (PostgreSQL 15+) mengosongkan hanya kolom induk, bukan `user_id`.
>
> 🔧 **`goals_parent_not_self` — 24 Sep 2026, migrasi 0004 (spec/07 2.1).** FK
> komposit di atas diperiksa **sesudah** barisnya ada, jadi goal yang menunjuk
> **dirinya sendiri** lolos — dan pohon goal menjadi lingkaran yang tidak pernah
> berakhir. Lingkaran yang lebih panjang tidak bisa terbentuk: `parent_id` tidak
> bisa diubah lewat API ([`04`](04-API-CONTRACTS.md)), dan goal baru hanya bisa
> menunjuk goal yang sudah ada.

```sql
-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE habits (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  goal_id          uuid,
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
  deleted_at       timestamptz,
  UNIQUE (id, user_id),
  FOREIGN KEY (goal_id, user_id) REFERENCES goals (id, user_id)
    ON DELETE SET NULL (goal_id)
);
CREATE INDEX habits_user_status_idx ON habits (user_id, status) WHERE deleted_at IS NULL;

-- @retention   : until-account-deleted
-- @who-can-set : user
-- @on-delete   : hard
CREATE TABLE habit_completions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data_subject text NOT NULL DEFAULT 'user'
                 CHECK (data_subject IN ('user','bystander','world','system')),
  habit_id      uuid NOT NULL,
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
  UNIQUE (habit_id, for_date),
  FOREIGN KEY (habit_id, user_id) REFERENCES habits (id, user_id) ON DELETE CASCADE
);
CREATE INDEX habit_completions_user_date_idx
  ON habit_completions (user_id, for_date DESC);
```

> `UNIQUE (habit_id, for_date)` mencegah pencatatan ganda saat aplikasi luring
> menyinkronkan ulang. `for_date` adalah **tanggal lokal**, bukan UTC —
> "workout hari Senin" harus tetap Senin bagi pengguna yang sedang di luar
> negeri.
>
> `adaptive_tiers` menyimpan **Adaptive Habit Engine** naskah 4 §34
> (`60 menit → 30 menit → mobility 10 menit`), dan `tier_used` mencatat tingkat
> mana yang benar-benar dijalankan. Tanpa kolom ini, "berhasil" jadi tidak
> punya arti yang sama antar hari.

---

## 3 · Catatan harian pengguna

```sql
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
```

> **`mood` sengaja TIDAK ikut di `human_states`.** Naskah 5 §9 membuangnya dari
> HumanState, dan itu benar: mood **dilaporkan pengguna** (tabel ini), bukan
> **ditaksir sistem**. Butir **E-34**.

```sql
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
```

> 🔧 **`safety_flag` saya tambahkan sendiri.** Journal masuk V0 sementara
> SafetyAgent tidak (issue #21). Kolom ini tidak menyelesaikan masalahnya —
> ia hanya memastikan **tempatnya sudah ada** ketika jalur eskalasi diputuskan,
> supaya tidak perlu migrasi tabel berisi tulisan paling sensitif pengguna.
> Selama #21 belum dijawab, nilainya tetap `NULL`.

```sql
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
```

> `source='inferred'` penting: begitu Behavior Engine mulai menyimpulkan
> aktivitas, harus bisa dibedakan mana yang **dicatat manusia** dan mana yang
> **ditebak sistem**. Tanpa itu, mesin akan belajar dari tebakannya sendiri.

---

## 4 · Event — tulang punggung

```sql
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
  UNIQUE (user_id, idempotency_key),
  UNIQUE (id, user_id)
);
CREATE INDEX events_user_time_idx    ON events (user_id, occurred_at DESC);
CREATE INDEX events_type_time_idx    ON events (event_type, occurred_at DESC);
CREATE INDEX events_subject_idx      ON events (subject_type, subject_id);
CREATE INDEX events_payload_gin      ON events USING gin (payload jsonb_path_ops);
```

> ⚠️ **Tabel ini tidak ada di 19 tabel V0 naskah 5 §31** — padahal §30
> menggambar *Event System* sebagai lapisan wajib V0 dan §7 berkata *"setiap
> aktivitas menjadi event"*. Butir **E-42**. Saya masukkan karena tanpa ini
> Behavior Engine di Sprint 5 tidak punya bahan.
>
> Tiga kolom yang menutup celah lama di bagian **D** audit:
> `schema_version` (versi), `occurred_at` vs `recorded_at` (urutan — kejadian
> luring bisa masuk belakangan), dan `idempotency_key` (event sama masuk dua
> kali tidak menggandakan apa pun).

---

## 5 · Memory

```sql
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

  source_event_id   uuid,
  valid_from        timestamptz NOT NULL DEFAULT now(),
  valid_until       timestamptz,                 -- NULL = masih berlaku
  last_reinforced_at timestamptz NOT NULL DEFAULT now(),

  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  deleted_at        timestamptz,
  FOREIGN KEY (source_event_id, user_id) REFERENCES events (id, user_id)
    ON DELETE SET NULL (source_event_id)
);
CREATE INDEX memories_user_kind_idx  ON memories (user_id, kind)  WHERE deleted_at IS NULL;
CREATE INDEX memories_user_scope_idx ON memories (user_id, scope) WHERE deleted_at IS NULL;
CREATE INDEX memories_active_idx     ON memories (user_id, last_reinforced_at DESC)
                                     WHERE deleted_at IS NULL AND valid_until IS NULL;
```

> 🔧 **Ini jawaban untuk issue #33 — dan jawabannya "keduanya".**
>
> `kind` menjawab **bagaimana** memori diambil: enam jenis naskah 5 §17.
> `scope` menjawab **siapa** boleh membacanya: nama scope di manifest §14,
> yang dipakai `permissions.scope`. Keduanya tidak bersaing; mereka menjawab
> pertanyaan berbeda dan sama-sama dibutuhkan.
>
> `confidence` + `evidence_count` adalah **Confidence Layer** §19 — bukan
> hiasan: `evidence_count = 0` berarti sistem **bertanya**, bukan menebak, dan
> itu sekaligus jawaban *cold start* (**B-1**).
>
> `valid_until` membuat memori bisa **kedaluwarsa tanpa dihapus** — *"dulu
> suka warna gelap"* tetap benar sebagai sejarah meski tidak berlaku lagi.

---

## 6 · Human State

```sql
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
```

Bentuk `metrics`:

```json
{
  "energy":    { "value": 0.62, "confidence": 0.71, "evidence_count": 18 },
  "focus":     { "value": 0.48, "confidence": 0.44, "evidence_count":  6 },
  "stress":    { "value": 0.34, "confidence": 0.22, "evidence_count":  2 }
}
```

> 🔧 **Ini jawaban untuk issue #2 — dengan cara menundanya tanpa biaya.**
> Lima model angka pengguna beredar (Behavior Genome 6 · Profile Engine 5 ·
> HumanState 7 · Dashboard 7 · DigitalTwin 8). `metrics jsonb` menampung
> semuanya; begitu pemilik memilih, metrik yang menetap dipromosikan jadi kolom
> nyata **tanpa membuang data lama**.
>
> `model_version` di kunci unik memungkinkan dua versi model dihitung
> berdampingan untuk hari yang sama — itu prasyarat evaluasi & rollback (§23).

---

## 7 · AI & rekomendasi

```sql
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
  deleted_at      timestamptz,
  UNIQUE (id, user_id)
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
  conversation_id uuid NOT NULL,
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role            text NOT NULL CHECK (role IN ('user','assistant','tool','system')),
  content         text NOT NULL,
  agent_run_id    uuid,                          -- FK ditambah setelah agent_runs dibuat
  model           text,
  tokens_in       integer,
  tokens_out      integer,
  latency_ms      integer,
  cost_usd        numeric(12,6),
  created_at      timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (conversation_id, user_id) REFERENCES ai_conversations (id, user_id)
    ON DELETE CASCADE
);
CREATE INDEX ai_messages_conversation_idx
  ON ai_messages (conversation_id, created_at);
```

> `cost_usd` per pesan sejak V0 adalah penerapan **AI Cost Engine** (naskah 4
> §48). Tanpa dicatat sejak awal, biaya baru terlihat di tagihan bulanan —
> saat sudah terlambat.

```sql
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
  updated_at       timestamptz NOT NULL DEFAULT now(),
  UNIQUE (id, user_id)
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
  recommendation_id uuid NOT NULL,
  user_id           uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  action            text NOT NULL
                      CHECK (action IN ('accepted','rejected','ignored','modified','snoozed')),
  reason            text,
  outcome           jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (recommendation_id, user_id) REFERENCES recommendations (id, user_id)
    ON DELETE CASCADE
);
CREATE INDEX recommendation_feedback_user_idx
  ON recommendation_feedback (user_id, created_at DESC);
```

> 🔧 **Ini jawaban untuk issue #32.** `score` disimpan **0–1**; skala 100-poin
> (naskah 3) dan persen (naskah 2) keduanya bisa dikonversi ke sini tanpa
> kehilangan apa pun, sebaliknya tidak. `scoring_version` membuat rumus boleh
> berganti tanpa migrasi, dan `score_breakdown` menyimpan tiap komponen:
>
> ```json
> { "trend": 0.80, "preference": 0.95, "context": 0.92,
>   "weather": 0.90, "history": 0.87, "weights": "equal" }
> ```
>
> `rationale` adalah **Explainable AI** naskah 4 §29 — daftar alasan yang bisa
> ditampilkan apa adanya. `context_snapshot` membekukan konteks saat
> rekomendasi dibuat, supaya *"kenapa dulu kamu menyarankan ini"* masih bisa
> dijawab setelah cuacanya berubah.
>
> `action='modified'` dan `'snoozed'` melengkapi naskah 4 §24: memilih B
> setelah disarankan A **bukan** penolakan, dan menunda **bukan** mengabaikan.

---

## 8 · Agent registry & audit

```sql
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
```

> 🔧 **`risk_level` → `max_risk`, dan `requires_confirmation` dihapus
> (10 Sep 2026).** Bukan keputusan baru — penerapan dua keputusan yang sudah
> diambil dan tidak pernah sampai ke DDL:
> **[#52](../../issues/52)** memindahkan `requires_confirmation` ke Policy
> Engine, dan **H-21**/[#67](../../issues/67) memisahkan `R` (risiko **aksi**)
> dari `L` (otonomi **agent**) — sehingga satu angka pada baris agent tidak bisa
> berarti keduanya (**E-119** / [#97](../../issues/97)). Konfirmasi kini turunan
> dari `R` lewat tabel gerbang
> [`../arch/04`](../arch/04-DEPENDENCY-GRAPH.md) §3.
>
> ⚠️ **Bawaannya `0`, dan arahnya kebalikan dari [K-12](../docs/KEPUTUSAN-DIDELEGASIKAN.md).**
> K-12 menolak bawaan `risk_level: 0` untuk **tool**, sebab tool yang lupa diisi
> menjadi yang **paling tidak dijaga**. Di sini `max_risk` adalah **pagu**, jadi
> `0` berarti agent yang lupa diisi **tidak bisa memanggil tool apa pun di atas
> R0** — gagal dengan keras, bukan diam-diam.
> 💡 Prinsipnya sama, angkanya berlawanan: yang ditanyakan bukan *“berapa
> bawaannya”* melainkan ***“kalau seseorang lupa mengisinya, ke sisi mana ia
> jatuh?”***
>
> `autonomy.max_level`, `kill_condition`, dan `deploy` tetap di `manifest jsonb`
> sampai Phase 11 — belum ada gerbang V0 yang membacanya.
>
> 🔧 **Pagar blok kode di atas baru ditutup 16 Sep 2026.** Sampai hari itu
> catatan ini — 21 baris markdown — tertulis **di dalam** blok ` ```sql `
> tabel `agents`, sehingga DDL berkas ini tidak bisa dijalankan apa adanya.
> Ditemukan saat migrasi 0001 dibandingkan dengan berkas ini secara mesin
> (`tests/integration/test_migrasi.py`), yang kini menolak baris markdown di
> dalam blok SQL.

```sql
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
```

> `agents_one_active_idx` menegakkan **satu versi aktif per agent** — itu yang
> membuat *automatic rollback* (§23) punya arti: aktifkan versi lama, versi
> baru turun status.
>
> ⚠️ `agents` dan `agent_tools` **tidak ada di 19 tabel V0** §31, padahal
> `agent_runs` di daftar itu jelas menunjuk sebuah agent. Naskah 6 memintanya.
> Butir **E-42**.

```sql
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
  conversation_id uuid,
  parent_run_id   uuid,

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
  finished_at     timestamptz,
  UNIQUE (id, user_id),
  FOREIGN KEY (conversation_id, user_id) REFERENCES ai_conversations (id, user_id)
    ON DELETE SET NULL (conversation_id),
  FOREIGN KEY (parent_run_id, user_id) REFERENCES agent_runs (id, user_id)
    ON DELETE SET NULL (parent_run_id)
);
CREATE INDEX agent_runs_user_time_idx  ON agent_runs (user_id, started_at DESC);
CREATE INDEX agent_runs_agent_idx      ON agent_runs (agent_id, started_at DESC);
CREATE INDEX agent_runs_parent_idx     ON agent_runs (parent_run_id)
                                       WHERE parent_run_id IS NOT NULL;

ALTER TABLE ai_messages
  ADD CONSTRAINT ai_messages_agent_run_fk
  FOREIGN KEY (agent_run_id, user_id) REFERENCES agent_runs (id, user_id)
    ON DELETE SET NULL (agent_run_id);
ALTER TABLE recommendations
  ADD CONSTRAINT recommendations_agent_fk
  FOREIGN KEY (agent_id) REFERENCES agents(id),
  ADD CONSTRAINT recommendations_run_fk
  FOREIGN KEY (agent_run_id, user_id) REFERENCES agent_runs (id, user_id)
    ON DELETE SET NULL (agent_run_id);
```

> **`agent_runs` ADALAH AI Audit Trail** naskah 5 §24 — `tools_used`,
> `memory_scopes`, `decision`, `confidence` persis seperti contoh JSON di sana.
> Yang **tidak** disimpan: chain-of-thought mentah. Itu keputusan pemilik, dan
> skema ini menegakkannya dengan tidak menyediakan kolomnya.
>
> `parent_run_id` merekam Orchestrator yang memanggil agent lain (§13) —
> satu permintaan pengguna bisa jadi pohon eksekusi yang bisa ditelusuri.

```sql
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
```

> **`user_id` di sini sengaja TANPA foreign key.** Kalau ada `ON DELETE
> CASCADE`, menghapus akun akan menghapus jejak auditnya — dan jejak itulah
> yang membuktikan penghapusan benar dilakukan. Kalau ada FK tanpa cascade,
> penghapusan akun jadi mustahil.
>
> Ini titik temu **C-9** (hak hapus vs jejak audit). Aturannya:
> **audit menyimpan bahwa sesuatu terjadi, bukan isi dari yang terjadi.**
> `bigint identity` dipakai, bukan uuid, karena tabel ini hanya pernah
> ditambah dan dibaca berurutan waktu.

---

## 9 · Pemicu `updated_at`

```sql
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
```

> 🔴 **Ditambahkan 16 Sep 2026 — dan ketiadaannya bukan kerapian.** Bagian
> *Awalan* mendefinisikan `set_updated_at()` dengan komentar *“dipakai semua
> tabel yang punya `updated_at`”* — tetapi sampai hari itu **tidak ada satu
> pun `CREATE TRIGGER`** di berkas ini. Sebelas tabel punya kolom
> `updated_at`; tanpa pemicu, kolom itu **tetap berisi waktu pembuatan
> selamanya**, dan setiap penulis `repository.py` harus *ingat* mengisinya
> sendiri. Itu aturan tanpa penjaga dalam bentuk yang paling kecil.
>
> Ditemukan dengan menulis migrasi 0001 — bukan dengan membaca berkas ini
> (pola **E-42**). `tests/integration/test_migrasi.py` kini menuntut
> **tiap tabel ber-`updated_at` punya pemicunya**, jadi tabel ke-24 tidak
> bisa lupa.

---

## 10 · Hak akses peran aplikasi (B-40)

```sql
-- `hvx_app` hanya mendapat yang dibutuhkan aplikasi, tabel demi tabel.
-- Tabel tanpa GRANT tidak tersentuh sama sekali: lupa = gagal keras, bukan bocor.

-- tulisan pengguna: baca · tulis · ubah · hapus (hak hapus nyata — naskah 5 §26)
GRANT SELECT, INSERT, UPDATE, DELETE ON
  permissions, goals, goal_milestones, habits, habit_completions,
  daily_checkins, mood_entries, journal_entries, activities,
  memories, human_states, ai_conversations, recommendations
  TO hvx_app;

-- akun & profil: baris dihapus prosedur hapus akun (CASCADE dari users), bukan aplikasi
GRANT SELECT, INSERT, UPDATE ON users, profiles TO hvx_app;

-- hanya-tambah: riwayat persetujuan · event (02 aturan C) · pesan AI · umpan balik · audit
GRANT SELECT, INSERT ON
  consents, events, ai_messages, recommendation_feedback, audit_logs
  TO hvx_app;

-- audit AI: status run berubah (running → succeeded); barisnya tidak pernah dihapus aplikasi
GRANT SELECT, INSERT, UPDATE ON agent_runs TO hvx_app;

-- katalog sistem: dikelola migrasi
GRANT SELECT ON agents, agent_tools TO hvx_app;
```

> 🛑 **B-40 — ditutup 17 Sep 2026.** Sampai hari itu api tersambung sebagai
> **superuser pemilik tabel**, sehingga `REVOKE UPDATE, DELETE ON audit_logs
> FROM PUBLIC` tidak menghalangi apa pun — diverifikasi: `UPDATE` & `DELETE`
> lolos, dan superuser melewati RLS. Kini api tersambung sebagai anggota
> `hvx_app`, **menolak mulai** kalau perannya superuser, `BYPASSRLS`, atau
> pemilik tabel (`platform.pastikan_peran_aplikasi`), dan tiap baris hak akses
> di atas dijaga `tests/integration/test_kepemilikan_data.py`.
>
> ⚠️ **Yang sengaja tidak diberikan:** `DELETE` pada `users` (tahap 3 prosedur
> hapus akun dijalankan peran pemeliharaan, bukan aplikasi — tugas 6.5) dan
> `UPDATE`/`DELETE` pada tabel hanya-tambah. Hapus kategori `events` di Privacy
> Center (6.4) butuh jalur tersendiri; ia tidak boleh dibuka dengan melebarkan
> `GRANT` di sini.

---

## 11 · Row-Level Security — data tiap pengguna milik pribadinya (H-27)

```sql
-- Peran aplikasi hanya melihat & menulis baris pengguna yang sedang dilayani
-- transaksi (app_current_user_id()). Pemilik tabel — peran migrasi — tidak
-- terkena RLS, sengaja: migrasi dan pemeliharaan. Aplikasi tidak pernah memakainya.

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_own_row ON users
  USING (id = app_current_user_id()) WITH CHECK (id = app_current_user_id());

ALTER TABLE profiles                ENABLE ROW LEVEL SECURITY;
ALTER TABLE consents                ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions             ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE goal_milestones         ENABLE ROW LEVEL SECURITY;
ALTER TABLE habits                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE habit_completions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_checkins          ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood_entries            ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries         ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities              ENABLE ROW LEVEL SECURITY;
ALTER TABLE events                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories                ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_states            ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations        ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages             ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations         ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs              ENABLE ROW LEVEL SECURITY;

CREATE POLICY profiles_own_rows                ON profiles                USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY consents_own_rows                ON consents                USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY permissions_own_rows             ON permissions             USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY goals_own_rows                   ON goals                   USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY goal_milestones_own_rows         ON goal_milestones         USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY habits_own_rows                  ON habits                  USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY habit_completions_own_rows       ON habit_completions       USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY daily_checkins_own_rows          ON daily_checkins          USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY mood_entries_own_rows            ON mood_entries            USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY journal_entries_own_rows         ON journal_entries         USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY activities_own_rows              ON activities              USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY events_own_rows                  ON events                  USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY memories_own_rows                ON memories                USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY human_states_own_rows            ON human_states            USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY ai_conversations_own_rows        ON ai_conversations        USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY ai_messages_own_rows             ON ai_messages             USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY recommendations_own_rows         ON recommendations         USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY recommendation_feedback_own_rows ON recommendation_feedback USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());
CREATE POLICY agent_runs_own_rows              ON agent_runs              USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());

-- audit_logs: pengguna membaca jejaknya sendiri; aplikasi menambah baris milik
-- pengguna yang dilayani ATAU baris sistem (user_id NULL — CHECK tabel memastikan
-- data_subject baris itu bukan 'user'). Tidak ada kebijakan UPDATE/DELETE.
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_logs_read_own ON audit_logs FOR SELECT
  USING (user_id = app_current_user_id());
CREATE POLICY audit_logs_append ON audit_logs FOR INSERT
  WITH CHECK (user_id IS NULL OR user_id = app_current_user_id());
```

> 🔑 **Keputusan pemilik 17 Sep 2026 (H-27): *“data milik satu pengguna harus
> milik pengguna tersebut, data masing-masing pengguna milik pribadi user.”***
> Tiga lapis menegakkannya, dan tidak satu pun bergantung pada ingatan penulis
> `repository.py`:
>
> | Lapis | Menjaga | Penegak |
> |---|---|---|
> | **RLS** (§11) | pengguna A tidak pernah **membaca, mengubah, atau menulis** baris pengguna B — bahkan kalau `WHERE user_id = …` terlupa di kueri | `test_kepemilikan_data.py` · 21 tabel |
> | **FK komposit** (B-41) | baris anak tidak pernah menunjuk **induk milik pengguna lain** — FK PostgreSQL tidak menerapkan RLS, jadi RLS saja tidak cukup | idem · 11 relasi |
> | **peran aplikasi** (§10, B-40) | tidak ada yang melewati kedua lapis di atas: api bukan superuser, bukan pemilik, tanpa `BYPASSRLS` | idem + api menolak mulai |
>
> ⚠️ **Harga yang diakui:** tiap kueri aplikasi wajib berjalan di dalam
> transaksi yang mengisi `hvx.user_id` (`platform.transaksi_pengguna`).
> Kueri yang lupa **tidak melihat apa pun** — gagal-tertutup, bukan bocor.
> Yang butuh melihat lintas pengguna **sebelum** pengguna dikenali (mencari akun
> saat login) atau **lintas akun** (sapuan hapus akun 6.5) memakai fungsi
> `SECURITY DEFINER` yang sempit, satu per kebutuhan — bukan pelonggaran
> kebijakan.

---

## 12 · Fungsi `SECURITY DEFINER` — satu per kebutuhan lintas RLS

```sql
-- Login (spec/07 1.1): mencari akun per email SEBELUM pengguna dikenali — RLS
-- `users` (§11) tidak meloloskannya, dan memang tidak boleh dilonggarkan.
-- Sempit: satu email persis, tiga kolom, tanpa akun terhapus. search_path
-- dipatok supaya objek dengan nama sama di skema lain tidak bisa dibajak.
CREATE FUNCTION auth_lookup_for_login(p_email citext)
  RETURNS TABLE (id uuid, password_hash text, status text)
  LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public, pg_temp
  AS $$
    SELECT u.id, u.password_hash, u.status
    FROM public.users u
    WHERE u.email = p_email AND u.deleted_at IS NULL
  $$;
REVOKE ALL ON FUNCTION auth_lookup_for_login(citext) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION auth_lookup_for_login(citext) TO hvx_app;
```

> 🔑 **Kenapa fungsi, bukan kebijakan RLS yang lebih longgar** (17 Sep 2026,
> spec/07 1.1, **K-19**). Login harus membaca `password_hash` akun yang
> belum dikenali — kebijakan `users` yang meloloskan itu akan meloloskannya
> untuk SEMUA kueri aplikasi, termasuk kueri yang lupa. Fungsi ini hanya
> menjawab satu pertanyaan, untuk satu email, dan hanya `hvx_app` yang boleh
> memanggilnya (`EXECUTE` dicabut dari `PUBLIC` — bawaan PostgreSQL
> memberikannya ke semua orang).
>
> `tests/integration/test_kepemilikan_data.py` menuntut: tiap fungsi
> `SECURITY DEFINER` di skema `public` ada di **daftar izin** uji itu, punya
> `search_path` terpatok, dan **tidak** bisa dieksekusi `PUBLIC`. Fungsi ke-2
> berarti baris baru di daftar itu — dan alasan di bagian ini.

---

## Prosedur hapus akun

Menutup janji *Delete* di Privacy Center (naskah 5 §26) tanpa merusak audit:

| Tahap | Tindakan |
|---|---|
| 1 | `users.status = 'pending_deletion'`, sesi dicabut, agent berhenti melayani |
| 2 | Tenggang **30 hari** — pengguna masih bisa membatalkan |
| 3 | `DELETE FROM users` → cascade menghapus profil, goal, habit, jurnal, mood, memori, percakapan, rekomendasi, event, human_states |
| 4 | Titik embedding di Qdrant dihapus berdasarkan `memories.embedding_id` yang dikumpulkan **sebelum** tahap 3 |
| 5 | `audit_logs` **tetap**, dengan `user_id` diacak jadi id semu satu arah; isinya sudah metadata saja |
| 6 | Satu baris audit terakhir: `action='account.deleted'` |

> ⚠️ Tahap 4 adalah jebakan paling mudah terlewat: **Qdrant tidak ikut
> cascade.** Kumpulkan `embedding_id` lebih dulu, atau titik memori pengguna
> akan tertinggal di sana selamanya.

---

## Ringkasan 23 tabel

| # | Tabel | Sumber | V0 |
|---|---|---|---|
| 1 | `users` | §31 | ✅ Sprint 1 |
| 2 | `profiles` | §31 | ✅ Sprint 1 |
| 3 | `consents` | §31 | ✅ Sprint 1 |
| 4 | `permissions` | §31 | ✅ Sprint 1 |
| 5 | `goals` | §31 | ✅ Sprint 2 |
| 6 | `goal_milestones` | §31 | ✅ Sprint 2 |
| 7 | `habits` | §31 | ✅ Sprint 2 |
| 8 | `habit_completions` | §31 | ✅ Sprint 2 |
| 9 | `daily_checkins` | §31 | ✅ Sprint 2 |
| 10 | `mood_entries` | §31 | ✅ Sprint 2 |
| 11 | `journal_entries` | §31 | ✅ Sprint 3 |
| 12 | `activities` | §31 | ✅ Sprint 3 |
| 13 | `memories` | §31 | ✅ Sprint 3 |
| 14 | `events` | ⚠️ naskah 6 — **tidak ada di §31** | ✅ Sprint 3 |
| 15 | `agents` | ⚠️ naskah 6 — **tidak ada di §31** | ✅ Sprint 4 |
| 16 | `agent_tools` | ⚠️ naskah 6 — **tidak ada di §31** | ✅ Sprint 4 |
| 17 | `agent_runs` | §31 | ✅ Sprint 4 |
| 18 | `ai_conversations` | §31 | ✅ Sprint 4 |
| 19 | `ai_messages` | §31 | ✅ Sprint 4 |
| 20 | `human_states` | 🔧 usulan — §9 butuh tempat | ✅ Sprint 5 |
| 21 | `recommendations` | §31 | ✅ Sprint 5 |
| 22 | `recommendation_feedback` | §31 | ✅ Sprint 5 |
| 23 | `audit_logs` | §31 | ✅ Sprint 1 |

**19** tabel dari daftar pemilik §31 + **3** dari naskah 6 + **1** usulan
(`human_states`) = **23 tabel**.

Tidak ada tabel untuk fitur di luar V0. `wardrobe_items`, `outfits`,
`sleep_records`, `workouts`, `skills`, `projects`, dan `notifications` disebut
di naskah 5 §5 tetapi tidak ada di V0 — menulis skemanya sekarang berarti
mengunci tebakan.
