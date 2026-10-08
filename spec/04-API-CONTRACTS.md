# 04 — API Contracts (V0)

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).

REST, JSON, awalan **`/v1`**. Autentikasi `Authorization: Bearer <access_token>`.

> 🔧 **Diselaraskan 9 September 2026 (dari `/api/v1`).** Ini menuntaskan janji
> yang tercatat di komentar penutup [#38](../../issues/38) — *“yang menyimpang
> justru `spec/04` yang saya tulis `/api/v1/…`; itu bagian saya, akan
> diselaraskan”* — dan janji itu tidak pernah dijalankan. Standar penamaan
> pemilik sendiri ([`../docs/101`](../docs/101-L22-ENGINEERING-STANDARDS.md)
> Layer 22) menetapkan `/v1/fashion/outfits`, dan sensus atas seluruh `docs/`
> menemukan **111 rute `/v1/…` di 12 naskah, dan NOL `/api/v1`**.
> Endpoint di bawah ditulis tanpa awalan, jadi hanya baris ini yang berubah.

---

## Aturan lintas endpoint

| Hal | Aturan |
|---|---|
| Waktu | ISO-8601 UTC dengan `Z`. Tanggal lokal pengguna sebagai `YYYY-MM-DD`. |
| Id | uuid string. **Klien boleh membuat id sendiri** (dukungan luring). |
| Tulis | `POST`/`PATCH` **domain** menerima header `Idempotency-Key` — `[A-Za-z0-9_.:=-]{1,128}`, telanjang atau sebagai sf-string bertanda kutip (`"…"`, bentuk draf IETF; keduanya kunci yang sama). Kunci yang sama mengembalikan hasil yang sama — status **pertama** dan sumber daya yang ditulisnya **dibaca ulang saat itu**, bertanda `Idempotent-Replayed: true`; sumber daya yang sudah dihapus → `404`. Kunci yang sama dengan permintaan **lain** → `422 idempotency_key_reused`; saat permintaan pertama masih berjalan → `409 idempotency_in_progress` + `Retry-After`. Hanya hasil 2xx yang diingat (24 jam, **rujukan** — bukan isi: E-171), kuncinya **milik pengguna** — kunci yang sama dari dua pengguna tidak saling memutar ulang — dan tiap pengguna paling banyak **1.000 kunci baru per 24 jam** (`429`, [K-24](../docs/KEPUTUSAN-DIDELEGASIKAN.md)). **Tidak** untuk `/auth/*`: jawabannya memuat token, dan memutar ulang jawaban berarti menyimpan token mentah ([K-21](../docs/KEPUTUSAN-DIDELEGASIKAN.md)) — `refresh` yang diulang dengan token yang sama tetap **pemakaian ulang**. `PATCH /me/profile` dan `PATCH /me/notifications` idempoten dengan sendirinya; `POST /privacy/export` **tanpa** kunci — tidak menulis data domain, dan badannya sandi, yang tidak boleh ikut diingat 24 jam (K-43). ✅ **Diterapkan Sprint 2 (E-165)**: `platform.Idempoten`, dan `tests/unit/test_idempotensi_terpasang.py` menolak rute tulis domain yang tidak menerimanya |
| Halaman | `?limit=` (maks 100, bawaan 50) + `?cursor=`; balasan `{ items, next_cursor }` — `next_cursor` `null` di halaman terakhir. Kursor **keyset** `(waktu, id)`, opak bagi klien, dan milik **daftar asalnya**; kursor rusak — atau dari daftar lain — → `400 invalid_cursor`. Daftar tanpa `?cursor=` di bawah ini membalas `{ items }`, dan ukurannya dibatasi **saat menulis** (goal · milestone · habit — K-24), tidak pernah dipotong diam-diam |
| Saringan `status` | tanpa `?status=` = **semua** status yang belum dihapus; `?status=active` di contoh bukan bawaan |
| Galat | `{ "error": { "code", "message", "details"? } }` |
| Kode | `400` bentuk salah · `401` belum masuk · `403` izin ditolak · `404` · `409` bentrok · `413` badan terlalu besar · `422` aturan bisnis · `429` batas laju |
| Bentuk masukan | **Ketat**, tidak dikoersi (E-170): bilangan bulat hanya angka JSON bulat (bukan `true`, `"3"`, `3.0`); boolean hanya `true`/`false`; tanggal hanya string `YYYY-MM-DD`; waktu hanya string ISO-8601 **berzona**; kolom desimal (`sleep_hours`) angka JSON, masuk dan keluar. Tanggal dan waktu di badan, kueri, **dan** jalur: `1900-01-01` … `2999-12-31` (waktu: dalam UTC). Selainnya → `400` |
| Ukuran badan | paling besar **1 MiB** → selainnya `413 payload_too_large`, sebelum autentikasi dan sebelum badan dibaca (K-24) |
| Batas laju | `429 rate_limited` **selalu** dengan header `Retry-After` (detik bulat). Empat kunci: per IP di seluruh `/v1/*` (IPv6 per /64) · per pengguna di rute bersesi · `register` + `login` per IP · `login` **gagal** per akun (batas laju, bukan penguncian — **B-42**). Angkanya variabel `HVX_RATE_LIMIT_*` — [`../apps/api`](../apps/api/README.md) |
| Galat validasi | `400 invalid_request`; `details` hanya `loc` · `msg` · `type` — **masukan tidak pernah dipantulkan** (sandi yang salah bentuk tidak dikirim balik). `loc` hanya memuat nama yang **dinyatakan api** — kunci tak dikenal dari klien menjadi `*` — dan `msg` bawaan dipakai hanya untuk jenis galat yang pesannya tidak mengutip masukan; selainnya `Nilai tidak sah.` (E-174) |

---

## Identity

```
POST   /auth/register        { email, password, display_name, timezone, consents }  → 201 { user, tokens }
POST   /auth/login           { email, password }                          → 200 { user, tokens }
POST   /auth/refresh         { refresh_token }                            → 200 { tokens }
POST   /auth/logout                                                       → 204
GET    /me                                                                → 200 { user, profile }
PATCH  /me/profile           { display_name?, timezone?, locale?, preferences? }
GET    /me/notifications                         → 200 { types[], quiet_hours, daily_cap, delivery }   ✅ 6.3
PATCH  /me/notifications     { types?: { <jenis>: bool }, quiet_hours?: { start, end } | null }   → 200 (bentuk sama)   ✅ 6.3
DELETE /me                   { password }        → 202 { deletion_scheduled_at }   ✅ 6.5
POST   /me/restore                               → 200   (batal hapus, selama tenggang 30 hari)   ✅ 6.5
                                                 → 409 deletion_grace_expired  (tenggang habis)
```

> ✅ **`DELETE /me` dan `POST /me/restore` — 6.5, dikodekan 5–6 Okt 2026.** Keduanya
> pintu masuk alur hapus akun enam tahap, tugas [`07`](07-BACKLOG-V0.md) 6.5
> (semula ditandai ⏳ karena bukan bagian Sprint 1 — tinjauan Sprint 1). Alur itu
> mencabut semua sesi pengguna (`PenyimpanSesi.cabut_semua`): status akun hanya
> dibaca saat masuk dan saat penyegaran, jadi token akses yang sudah terbit hidup
> sampai kedaluwarsanya.
>
> * `DELETE /me` meminta sandi lagi (`403 invalid_credentials` bila salah) dan
>   idempoten: saat sudah `pending_deletion` ia mengembalikan jadwal yang ada, tanpa
>   menyetel ulang jam tenggang.
> * 🔧 **E-226 — sandi ulang berbagi jatah login gagal** (kode 7 Okt 2026, ditulis
>   di sini 8 Okt 2026). Tebakan sandi ulang — di sini
>   dan di `POST /privacy/export` · `DELETE /privacy/data/{category}` — memakai **jatah
>   login gagal akun itu** (kunci email sebagaimana `citext` mengenalinya), dipakai
>   **sebelum** sandinya dicocokkan dan dikosongkan bila cocok. Jatah habis →
>   `429 rate_limited` + `Retry-After`, juga dengan sandi yang benar — sama dengan
>   `login`. Versi pertama hanya dibatasi batas per pengguna (300/menit): token akses
>   yang dicuri cukup untuk menebak sandi ratusan kali per menit lewat pintu ini.
>   Penolakan tercatat di jejak audit pemiliknya (`account.deletion_rejected` ·
>   `data.export_rejected` · `data.deletion_rejected`).
> * 🔧 **E-233 — sandi ulang juga berbagi jatah per IP login** (8 Okt 2026, tinjauan keamanan
>   Sprint 5–6). Jatah per akun dikosongkan tiap kali sandinya benar, jadi satu akun bisa
>   memaksa argon2 64 MiB jauh lebih sering daripada pintu `login` (30 / 10 menit per IP).
>   Ketiga pintu sandi ulang kini memakai jatah **per IP yang sama dengan login**, sebelum
>   argon2 → `429 rate_limited` + `Retry-After`. Jatahnya dibagi dengan login — pengguna di
>   balik NAT yang sama berbagi, seperti untuk login.
> * Akun `pending_deletion` **boleh login** (`suspended` tidak) — satu-satunya jalan
>   membatalkan, karena `DELETE /me` mencabut semua sesinya. Selama tenggang asisten
>   **tidak melayani**: `POST /conversations/{id}/messages` dan `…/confirmations` →
>   `403 account_pending_deletion`; membaca tetap boleh.
> * `POST /me/restore` idempoten pada akun `active` (`200`, tanpa jejak kedua), tetapi
>   **hanya selama `deletion_scheduled_at` belum lewat**: sesudahnya
>   `409 deletion_grace_expired` — sapuan boleh membuang titik Qdrant-nya kapan saja
>   (E-216).
> * Penghapusannya sendiri (tahap 3–6) dikerjakan proses pekerja, bukan rute —
>   [`01`](01-DATABASE-SCHEMA.md) *Prosedur hapus akun*.

> 🔧 **`/me/notifications` ditambahkan 8 Okt 2026 — dikodekan 7 Okt (6.3, K-44).**
> [`07`](07-BACKLOG-V0.md) 6.3 meminta notifikasi *“bisa dimatikan per jenis”*; rute ini
> belum pernah ditulis di sini. V0 **tidak mengirim** notifikasi apa pun (A-28) — jawaban
> selalu `delivery: "none"`, supaya klien tidak menjanjikannya. Yang ada: pilihan
> pengguna, tersimpan, dan satu gerbang (`profile.keputusan_kirim` → `now` · `later` ·
> `silent`) yang wajib dilewati pengirim mana pun kelak.
>
> * `types[]` = `{ key, label, enabled, default, required }` untuk empat jenis V0:
>   `habit_reminder` (bawaan mati) · `weekly_review` (nyala) · `recommendation` (mati) ·
>   `account_security` (nyala, **`required`** — tidak bisa dimatikan, melewati jam tenang
>   dan pagu). `quiet_hours` bawaan `{ "start": "22:00", "end": "07:00" }` (boleh
>   melintasi tengah malam), `daily_cap` 10 (naskah 11 §11.17).
> * `PATCH` mengubah **hanya** jenis yang dikirim; `quiet_hours` tidak dikirim = tidak
>   diubah, `null` = tanpa jam tenang. Yang disimpan hanya pilihan pengguna, bukan
>   bawaannya — bawaan yang kelak berubah tetap berlaku bagi yang belum memilih.
>   Dua `PATCH` serentak untuk jenis berbeda tidak saling menimpa (kunci baris).
> * Galat: jam bukan `HH:MM`, nilai jenis bukan boolean, lebih dari 20 kunci, medan tak
>   dikenal → `400` · jenis tak dikenal → `422 unknown_notification_type` ·
>   `account_security: false` → `422 notification_required` · jam mulai = jam selesai →
>   `422 invalid_quiet_hours`.
> * Disimpan di `profiles.preferences.notifications`, dengan **satu penulis per kunci**:
>   `PATCH /me/profile` yang `preferences`-nya memuat `notifications` → `400`, dan
>   `PATCH /me/profile` yang mengganti `preferences` utuh **mempertahankan** pilihan
>   notifikasi yang tersimpan — klien yang mengirim preferensi lamanya tidak menimpa
>   pilihan yang baru disimpan perangkat lain.

> 🔧 **`consents` ditambahkan 17 Sep 2026 (E-164), saat tugas 1.1 ditulis.**
> [`07`](07-BACKLOG-V0.md) 1.4 menuntut persetujuan dicatat **saat daftar** —
> termasuk `purpose` dan `kind='model_training'` — tetapi badan pendaftaran di
> atas tidak punya tempat untuk jawabannya:
>
> ```
> consents: { policy_version, terms: true, privacy: true,
>             model_training?: { granted, data_scopes[] } }   ← tidak dikirim = DITOLAK
> ```
>
> `terms` dan `privacy` wajib `true`. `model_training` persetujuan **tersendiri**
> yang ditolak tanpa mengurangi layanan ([#59](../../issues/59)); `granted: true`
> wajib menyebut `data_scopes`. Ketiga jawaban tercatat — penolakan juga.
> Teks kebijakan dan kosakata `purpose` tetap milik pemilik (#59 butir 2).

| Rute | Galat yang dijanjikan |
|---|---|
| `register` | `400` bentuk salah — sandi di luar **15–128** karakter, timezone bukan nama IANA, medan tak dikenal · `409 email_taken` · `422 consent_required` · `422 password_rejected` + `details.reason` (`context` · `repetitive` · `sequential`) · `429` |
| `login` | `401 invalid_credentials` — **sama persis** untuk sandi salah dan email tak terdaftar · `403 account_not_active` · `429` per IP, dan per akun sesudah jatah login gagalnya habis — juga dengan sandi yang benar, juga bagi email tak terdaftar, dan bagi tiap ejaan yang basis data anggap email yang sama (huruf besar-kecil, juga Unicode: `vİctim@` = `victim@`) |
| `refresh` | `401 invalid_refresh_token` — token segar **berotasi**; token bekas yang dipakai lagi **mencabut seluruh sesi**; akun yang tidak lagi `active` → sesinya dicabut |
| rute bersesi | `401 unauthenticated` + `WWW-Authenticate: Bearer` — token palsu, kedaluwarsa, dan dicabut dijawab sama · `429` per pengguna |
| `PATCH /me/profile` | `400` untuk medan tak dikenal dan `null` eksplisit — tidak diabaikan diam-diam · `400` bila `preferences` memuat `notifications` (milik `PATCH /me/notifications`, K-44) |
| `DELETE /me` | `403 invalid_credentials` sandi salah · `429` sesudah jatah login gagal akun itu habis — juga dengan sandi yang benar (E-226) — atau jatah per IP login habis (E-233) |

---

## Goals & habits

```
GET    /goals                ?status=active&limit=&cursor=      → { items, next_cursor }
POST   /goals                { id?, title, description?, domain?, parent_id?, target_date? }   → 201
GET    /goals/{id}                            → memuat milestones[]
GET    /goals/{id}/tree                       → goal + children[] bersarang — satu kueri   🔧 2.1
PATCH  /goals/{id}           { title?, status?, target_date? }
DELETE /goals/{id}                            → 204 (soft delete)

POST   /goals/{id}/milestones { id?, title, position?, due_date? }   → 201
PATCH  /milestones/{id}       { status?, title?, due_date? }

GET    /habits               ?status=active&for_date=     → { items }; dengan for_date, tiap habit membawa day{}   🔧 2.2
POST   /habits               { id?, title, period, target_count, schedule?, goal_id?, adaptive_tiers? }
PATCH  /habits/{id}
DELETE /habits/{id}

POST   /habits/{id}/completions  { for_date, status, tier_used?, note? }   → 201
DELETE /habits/{id}/completions/{for_date}                                 → 204
GET    /habits/{id}/streak       → { current, longest, completion_rate_30d }
```

> 🔧 **`GET /goals/{id}/tree` ditambahkan 24 Sep 2026 (E-168), saat tugas 2.1
> ditulis.** [`07`](07-BACKLOG-V0.md) 2.1 menuntut *“pohon goal 3 tingkat terbaca
> dalam satu query”*, tetapi tidak satu rute pun di atas yang mengembalikan
> pohon — `GET /goals/{id}` hanya memuat milestone, dan klien yang ingin pohon
> terpaksa meminta goal satu per satu (N+1 lewat jaringan, bukan lewat basis
> data). Kini satu rute, satu CTE rekursif; kedalaman paling banyak **10
> tingkat**, ditegakkan **saat menulis** (`422 goal_tree_too_deep`) supaya
> pohon tidak pernah dipotong diam-diam saat dibaca.
>
> | Rute | Galat yang dijanjikan |
> |---|---|
> | `POST /goals` | `409 already_exists` (`id` buatan klien yang sudah ada) · `422 parent_not_found` (induk tidak ada, terhapus, atau milik pengguna lain — ketiganya sama; juga induk yang **sedang** dihapus serentak — E-172) · `422 goal_tree_too_deep` · `422 goal_limit_reached` (1.000 goal hidup per pengguna — K-24) · `400` bila `parent_id == id` |
> | `PATCH /goals/{id}` | `400` untuk medan di luar tiga di atas — **`parent_id` tidak bisa diubah**, jadi lingkaran tidak bisa terbentuk · `status: achieved` mengisi `achieved_at`, status lain mengosongkannya |
> | `DELETE /goals/{id}` | anak goal naik menjadi **akar** — sama dengan hapus-keras `spec/01` (`ON DELETE SET NULL (parent_id)`) — dan habit yang menautnya **dilepas** (`goal_id` → `null`, sama dengan `ON DELETE SET NULL (goal_id)`; E-172). Menghapus goal yang sudah dihapus → `404`: goal itu tidak ada lagi |
> | `…/milestones` · `/milestones/{id}` | `404` untuk goal terhapus; `status: done` mengisi `completed_at`; `id` buatan klien yang sudah ada → `409 already_exists`; `422 milestone_limit_reached` (100 per goal — K-24) |

> 🔧 **Bentuk habit yang ditegakkan (spec/07 2.2, 24 Sep 2026)** — semula hanya
> tersirat di contoh `spec/01`:
>
> | Medan | Aturan | Kenapa |
> |---|---|---|
> | `target_count` | `day` → tepat **1** · `week` → 1–7 · `month` → 1–31 | satu tanggal satu penyelesaian (`UNIQUE (habit_id, for_date)`): *“3× sehari”* tidak bisa dicatat, *“8× seminggu”* tidak pernah terpenuhi |
> | `schedule` | `{ weekdays?: [1..7] unik & terurut (ISO, 1 = Senin), time?: "HH:MM" }`; `weekdays` **hanya** untuk `period: day` | habit mingguan dihitung per periode, bukan per hari |
> | `adaptive_tiers` | paling banyak 5: `[{ label, minutes? }]`, indeks 0 = versi penuh (naskah 4 §34) | |
> | `PATCH` | paduan `period` × `target_count` × `schedule` diperiksa terhadap **baris tersimpan** → `422 invalid_habit` | badan `{period: "day"}` sah sendiri, tidak sah untuk habit `week`/3 |
> | `goal_id` | goal tidak ada / **dihapus** / milik pengguna lain → `422 goal_not_found` | FK komposit saja tidak melihat hapus-lunak — goal terhapus dulu bisa ditaut (E-172) |
> | jumlah | paling banyak **500** habit hidup per pengguna → `422 habit_limit_reached` (K-24) | `GET /habits` membalas SEMUANYA — dulu memotong di 500 tanpa tanda |
> | `DELETE` | hapus-lunak; menghapus habit yang sudah dihapus → `404` | beda dengan `DELETE …/completions/{for_date}`, yang menunjuk **keadaan** tanggal itu, bukan sumber daya |

> `POST .../completions` memakai `UNIQUE (habit_id, for_date)`. Kirim ulang
> tanggal yang sama mengembalikan **200 dengan baris yang sudah ada**, bukan
> `409` — pencatatan habit dari perangkat luring harus selalu aman diulang.
>
> 🔧 **Ditegakkan 24 Sep 2026 (spec/07 2.3):** baris lama dikembalikan **apa
> adanya**, dan **sebelum** aturan apa pun diperiksa ulang — ulangan identik
> sesudah tier habit dikurangi tetap `200`, bukan `422` (E-173); ulangan tidak
> menimpa; mengganti status berarti `DELETE` lalu `POST`. Habit `archived`
> tetap menerima catatan — pencatatan mundur untuk hari sebelum diarsipkan. `DELETE …/completions/{for_date}` juga idempoten (`204` walau tanggal
> itu tidak tercatat). `for_date` adalah tanggal lokal **perangkat**, jadi
> batasnya bukan zona profil: tanggal ditolak (`422 for_date_in_future`) hanya
> bila **belum terjadi di mana pun di Bumi** (UTC+14). `tier_used` bilangan
> bulat ≥ 0 yang wajib di dalam `adaptive_tiers` habit itu — di luarnya
> **selalu** `422 invalid_tier`, berapa pun angkanya (E-170: dulu `3` menjadi
> `422`, `7` menjadi `400`) — dan tidak boleh menyertai `skipped` (`400`).
>
> 🔧 **Arti `GET /habits/{id}/streak` (spec/07 2.4, 24 Sep 2026)** — semula
> hanya nama medan:
>
> | | |
> |---|---|
> | satuan | **periode** habit: hari · minggu ISO (Senin–Minggu) · bulan kalender. Periode **terpenuhi** bila tanggal `done`/`partial` di dalamnya ≥ `target_count` |
> | tanggal | **`for_date`** apa adanya — tidak pernah diturunkan dari `completed_at`, dan tidak digeser saat pengguna pindah zona |
> | hari ini | menurut `profiles.timezone` **saat ini**, dari jam basis data; periode yang belum berakhir tidak memutus rentetan; `for_date` sesudah hari ini (perangkat di zona lebih timur) tetap dihitung |
> | `skipped` | netral — tidak menambah, tidak memutus, tidak masuk penyebut. **Per kejadian**: tiap `skipped` memaafkan satu kali dari target periodenya — minggu bertarget 2 dengan satu `done` + satu `skipped` dimaafkan, bukan gagal (E-173) |
> | `schedule.weekdays` | hari di luarnya bukan hari habit itu — dilewati |
> | `current` · `longest` | periode terpenuhi berturut-turut — yang masih hidup · yang terpanjang |
> | `completion_rate_30d` | periode terpenuhi ÷ periode jatuh tempo yang bersinggungan dengan 30 hari terakhir — **`null`** bila belum ada satu pun yang jatuh tempo. **Awal habit** = tanggal lokal habit dibuat: periode yang dimulai sebelumnya hanya dihitung bila **terpenuhi** (catatan mundur dihargai; hari sebelum habit ada tidak menjadi "gagal" — E-173) |
> | `paused` | riwayat jeda tidak disimpan (spec/01 tidak punya kolomnya): masa jeda dihitung seperti hari biasa — batas yang diakui |
>
> ⚠️ Menyeberang garis tanggal ke timur melompati satu tanggal kalender;
> rentetan harian putus di sana kecuali tanggal itu dicatat mundur (`for_date`
> boleh tanggal lampau).

---

## Catatan harian

```
GET    /checkins             ?from=&to=
PUT    /checkins/{for_date}  { energy?, focus?, sleep_hours?, note? }   → upsert: 201 baru · 200 diganti
GET    /moods                ?from=&to=&limit=&cursor=     → { items, next_cursor }
POST   /moods                { id?, valence, label?, note?, occurred_at? }   → 201
GET    /journal              ?from=&to=&cursor=      → tanpa body, hanya ringkasan
GET    /journal/{id}                                 → dengan body
POST   /journal              { id?, title?, body, occurred_at? }
PATCH  /journal/{id}
DELETE /journal/{id}
GET    /activities           ?kind=&source=&from=&to=&cursor=
POST   /activities           { id?, kind, occurred_at, ended_at?, duration_seconds?, payload? }
```

> `GET /journal` **tidak** mengembalikan `body`. Daftar jurnal sering dimuat
> di layar ringkasan; mengirim seluruh isi tulisan pribadi ke sana adalah
> kebocoran yang tidak perlu.
>
> 🔧 **`PATCH` dan `DELETE /journal/{id}` menjangkau memorinya (spec/07 3.6).**
> Tiap jurnal melahirkan satu memori episodik (scope `journal_raw`). Menyunting
> jurnal mengganti isi memori itu, dan menghapusnya **mengosongkan** memori itu
> — keduanya di transaksi yang sama dengan jurnalnya; titik vektornya
> diselaraskan pekerja sesudah commit.
>
> 🔧 **`DELETE /journal/{id}` = hapus KERAS sejak 7 Okt 2026 — C-31 diputuskan (K-46,
> delegasi pemilik; ditulis di sini 8 Okt).** Versi pertama hapus-lunak (`deleted_at`):
> tulisan paling pribadi yang dihapus pemiliknya tetap tersimpan sampai akunnya dihapus,
> tanpa rute pemulihan apa pun (GDPR Art. 17 · UU PDP Pasal 8). Kini barisnya **dan**
> event `journal.created`-nya dihapus, dan memori turunannya dikosongkan (titiknya
> dibuang penyelaras), di satu transaksi — `204`, dan
> `DELETE` kedua → `404`. Jurnal yang sudah dihapus-lunak sebelumnya dibuang migrasi
> `0013`. Menghapus **semua** jurnal sekaligus: `DELETE /privacy/data/journal`.

> 🔧 **`/activities` (spec/07 3.8, 24 Sep 2026 — tinjauan kontrak Sprint 3, K5).**
> Klien **tidak** menyatakan sumber: badan dengan `source` → `400`, rute selalu
> mencatat `manual`, dan `inferred` hanya lewat jalur sistem (Behavior Engine).
> `?source=` memisahkan keduanya saat membaca — supaya mesin tidak belajar dari
> tebakannya sendiri (spec/01). `ended_at` (kolom spec/01) **dan**
> `duration_seconds` dua fakta tentang satu rentang: keduanya dikirim → wajib
> cocok (±1 dtk), rentang paling lama 7 hari → selain itu `400`; `ended_at` tidak
> boleh lebih dari 5 menit di depan jam basis data (`422 ended_at_in_future`),
> seperti `occurred_at` (`422 occurred_at_in_future`). `payload` paling besar
> 16 KB dan 32 tingkat bersarang (S5). `id` yang sudah dipakai → `409
> already_exists`. `from` inklusif / `to` eksklusif, keduanya berzona; kursor
> keyset `(occurred_at, id)`.
>
> 🔧 **`PUT /checkins/{for_date}` = GANTI, bukan tambal (spec/07 2.5, 24 Sep
> 2026).** Badan adalah check-in tanggal itu: medan yang tidak dikirim menjadi
> kosong — dua `PUT` yang sama selalu menghasilkan baris yang sama, apa pun
> isinya sebelumnya (idempoten dengan sendirinya; `Idempotency-Key` tidak
> dijanjikan untuk `PUT`) — termasuk `updated_at`: `PUT` yang identik dengan
> baris tersimpan tidak menulis apa pun (E-176). Satu pernyataan `INSERT … ON CONFLICT (user_id,
> for_date) DO UPDATE` — `PUT` serentak tidak bisa menyisipkan baris kedua.
> `sleep_hours` angka JSON dengan satu angka desimal (`numeric(3,1)`): `7.25`
> **ditolak** `400`, tidak dibulatkan diam-diam; `"7.5"` (string) juga `400`, dan
> jawabannya angka `7.5`, bukan string (E-170). `for_date` mengikuti aturan penyelesaian habit
> (`422 for_date_in_future` hanya bila belum terjadi di mana pun).
> `GET /checkins`: `from` dan `to` dikirim **bersama** (inklusif, paling lebar
> 366 tanggal, terbaru dulu); tanpa keduanya — 31 check-in terakhir.
>
> 🔧 **`GET /habits?for_date=` ditambahkan 24 Sep 2026 (E-169), saat 2.2 dan
> 2.7 ditulis.** 2.2 menuntut *“tier turun saat energi rendah”*, dan layar 2.7
> menandai habit selesai **hari ini** — tidak satu rute pun yang menjawab
> *“habit mana yang sudah selesai tanggal ini, dan tier mana yang disarankan”*
> tanpa N+1 permintaan. Dengan `for_date`, tiap habit membawa
> `day: { for_date, completion, energy, suggested_tier }` — `energy` ikut
> sebagai **alasan** tier yang disarankan (Explainable AI naskah 4 §29).
> Pemetaan energi → tier: **K-23** (naskah 4 §34).
>
> 🔧 **Mood (spec/07 2.6, 24 Sep 2026).** `occurred_at` **wajib berzona waktu**
> (`2026-09-24T06:30` tanpa zona adalah jam yang berbeda di tiap negara → `400`),
> boleh lampau, dan tidak boleh lebih dari 5 menit di depan jam basis data
> (`422 occurred_at_in_future`). `GET /moods`: `from` inklusif, `to`
> **eksklusif**, keduanya berzona; kursor keyset `(occurred_at, id)` — mood yang
> dicatat mundur masuk di tempatnya tanpa menggeser halaman berikutnya.

---

## AI

```
GET    /conversations                    ?cursor=
POST   /conversations                    { title? }
GET    /conversations/{id}/messages      ?cursor=
POST   /conversations/{id}/messages      { content }   → 202, balasan lewat stream
GET    /conversations/{id}/stream        → SSE: token, tool_call, done
POST   /conversations/{id}/confirmations { token, decision }   → 202  🔧 E-195
```

Balasan `POST /messages`:

```json
{
  "message_id": "…",
  "agent_run_id": "…",
  "status": "processing"
}
```

Peristiwa SSE `done`:

```json
{
  "content": "…",
  "confidence": 0.71,
  "rationale": ["Tidur 5j 40m tiga malam terakhir", "Workout terlewat 2x"],
  "agent_run_id": "…",
  "cost_usd": 0.0021
}
```

> `confidence` dan `rationale` ikut di **setiap** balasan AI, bukan hanya
> rekomendasi — itu penerapan Confidence Layer (§19) dan Explainable AI
> (naskah 4 §29) di lapisan API, bukan sekadar di basis data.

> 🔧 **Diterapkan Sprint 4 (tugas 4.8, 24 Sep 2026) — dan yang ditambahkan.**
>
> * **Giliran.** `POST …/messages` menjawab `202` sesudah run akarnya ditulis
>   (`agent_run_id` sah dirujuk). Perintah berbentuk tetap (*“catat mood 3”*, 4.1)
>   dijalankan saat itu juga, **tanpa agent dan tanpa model**: `agent_run_id: null`,
>   `status: "completed"`, `done.cost_usd: 0`. Satu giliran per percakapan —
>   pesan kedua saat yang pertama masih dijawab → `409 turn_in_progress`.
> * **`GET …/stream`** — seluruh peristiwa giliran terakhir **dari yang pertama**
>   (klien boleh menyambung sesudah `POST`), berakhir dengan `done` atau `error {code}`;
>   `204` bila tidak ada giliran yang sedang atau baru saja berjalan — di SSE, 204
>   berarti *jangan menyambung ulang* (balasan yang sudah selesai dibaca dari
>   `GET …/messages`). `tool_call` = `{tool, agent}` — tanpa masukannya. Aliran hidup di
>   proses api yang menjalankan gilirannya (**K-31**). `done` juga memuat `message_id`;
>   `cost_usd` = seluruh pohon run giliran itu.
> * 🔧 **E-194 — riwayat membawa alasannya.** `GET …/messages` (terbaru dulu, kursor
>   `(created_at, id)`) mengembalikan `confidence`, `rationale`, dan `cost_usd` tiap
>   balasan — `ai_messages` semula tanpa kedua kolom pertama (migrasi `0008`), jadi
>   balasan yang dibaca ulang kehilangan alasannya.
> * 🔧 **E-195 — konfirmasi punya rute.** spec/05 menulis *“`ask` → minta izin”* dan
>   spec/07 4.5 *“risk 2 minta izin sekali”*, tetapi tidak ada rute untuk MENJAWABNYA.
>   Giliran yang ditahan gerbang mengalirkan `confirmation_required`:
>
>   ```json
>   {
>     "token": "…", "kind": "permission", "agent": "habit-agent",
>     "tool": "habit.complete", "risk_level": 2, "scopes": ["habits"],
>     "remember_allowed": true, "expires_at": "2026-09-24T10:15:00+00:00"
>   }
>   ```
>
>   lalu `done` berisi pertanyaannya. `POST …/confirmations { token, decision }` —
>   `decision` ∈ `allow_always` (hanya bila `remember_allowed`: izin disimpan, tidak
>   ditanya lagi) · `allow_once` · `reject` — menjawab `202 { agent_run_id, status }`,
>   dan giliran yang sama diulang dari pesan penggunanya; hasilnya lewat `…/stream`.
>   `kind: "confirmation"` (R3) tidak bisa diingat. Token bertanda tangan, 15 menit,
>   milik satu pengguna dan satu percakapan, **sekali pakai**: jawaban kedua →
>   `409 confirmation_answered`; token rusak, kedaluwarsa, atau milik percakapan lain
>   → `422 invalid_confirmation` (tanpa membedakan ketiganya).
>
> 🔧 **Tinjauan tiga lensa sebelum PR (28 Sep 2026)** — yang ditambahkan:
>
> * **Satu giliran bisa ditanya lebih dari sekali** (E-199) — *“tanya aku”* untuk
>   bacaan, lalu tulisan R2. Token membawa pesan pengguna yang memulai giliran dan
>   persetujuan yang sudah dipegangnya; jawaban berikutnya mengulang giliran dengan
>   **semuanya**. Semua yang bisa menolak jawaban — token, `allow_always` untuk
>   `confirmation`, percakapannya, *sudah dijawab* — diperiksa **sebelum** giliran
>   baru dimulai: ketukan ganda saat giliran ulangan masih berjalan →
>   `409 confirmation_answered`, bukan `turn_in_progress` (E-202).
> * **Permintaan yang ditolak bukan giliran** (E-202): `409` · `422` pada
>   `…/messages` atau `…/confirmations` tidak menyentuh `GET …/stream` — aliran
>   tetap giliran terakhir yang sungguh terjadi.
> * **Id buatan klien** (tabel *Umum*): `POST /conversations` dan `POST …/messages`
>   dengan `id` yang sudah ada → `409 already_exists`, seperti modul lain — juga id
>   milik pengguna lain. Run yang terlanjur ditulis sebelum pesannya ditolak ditutup
>   `failed` (E-200).
> * **`error.code` SSE** (E-203) — kode API berbahasa Inggris, bukan kode internal:
>   `rate_limited` (batas laju tool) · `agent_error` (program agent memanggil tool atau
>   memutuskan secara salah — bukan salah klien) · `model_unavailable` · `cancelled`
>   · `internal_error` · kode layanan pemilik data yang menolak tulisan tool
>   (`not_found`, `invalid_tier`, `for_date_in_future`, …).
> * **`GET /conversations`** — terbaru **dibuat** dulu, kursor `(created_at, id)`:
>   urutan yang tidak bergeser saat percakapan lain menerima pesan (E-210).
> * **`status` giliran** di `202` dan saat diputar ulang (Idempotency-Key): `processing` ·
>   `completed` · 🆕 `failed` — giliran yang berakhir SSE `error` tidak menyimpan balasan,
>   dan dulu terbaca `processing` selamanya (E-212).
> * **Riwayat terurut `(created_at, id)`, dan cap waktunya monoton per percakapan**
>   (E-213): jam basis data yang melangkah mundur tidak lagi membuat balasan tampak lebih
>   tua dari pertanyaannya.

---

## Rekomendasi & Dashboard

```
GET    /dashboard                     → { as_of, dimensions:[{key,value,confidence,evidence_count,why}] }  🔧 6.1
GET    /reviews/weekly               ?week=YYYY-Www   → { week, start, end, complete, timezone, axes[], not_measured[], questions[], review_version }  🔧 6.2
GET    /recommendations              ?status=&domain=&limit=&cursor=   → { items, next_cursor }   🔧 K5
POST   /recommendations/{id}/feedback { action, reason?, outcome? }   → 201
POST   /recommendations/{id}/shown                                    → 204
```

> 🔧 **`GET /dashboard` ditambahkan 5 Okt 2026 (6.1).** naskah 4 §28 menolak satu
> angka Life Score dan meminta **beberapa dimensi, tiap skor ber-Why**. V0
> menampilkan hanya dimensi yang **diukur** — metrik `human_states` (energi, fokus)
> yang dilaporkan pengguna. Sumbu lain §28 (Finance/Social/Career/…) belum punya
> ukuran disepakati (**A-19**/**B-38**, [`../docs/99`](../docs/99-CATATAN-AUDIT.md)):
> menampilkannya sebagai angka = mengambil posisi dalam model yang belum diputuskan
> pemilik, jadi tidak ditampilkan sampai keputusan itu ada. `dimensions` kosong =
> cold start (belum ada check-in). `GET /recommendations` terbaru dulu;
> `?status=` divalidasi terhadap `recommendations.status` (`400 invalid_status`).
>
> 🔧 **`GET /recommendations` berkursor — 8 Okt 2026 (tinjauan kontrak Sprint 5–6, K5).**
> Versi pertama (dan kalimat di atas) menyebutnya *“daftar terbatas terbaru dulu (bukan
> berkursor)”*: 50 baris terbaru, sisanya **terpotong diam-diam** — yang dilarang aturan
> *Halaman* di atas, karena rekomendasi **tidak** dibatasi saat menulis (satu per habit per
> hari dilewati, 5.5, ditambah saran agent). Kini mengikuti aturan *Halaman*: `?limit=`
> (maks 100, bawaan 50) + `?cursor=` keyset `(created_at, id)` milik daftar ini;
> `next_cursor` `null` di halaman terakhir; kursor rusak → `400 invalid_cursor`.

> 🔧 **`GET /reviews/weekly` ditambahkan 8 Okt 2026 — dikodekan 7 Okt (6.2, K-45).**
> [`07`](07-BACKLOG-V0.md) 6.2: *menjawab 5 pertanyaan naskah 4 §31*. Dihitung **saat
> dibaca** dari habit, check-in, dan mood — tidak disimpan (menghapus sumbernya di Privacy
> Center juga menghapus tinjauannya).
>
> * `?week=` minggu ISO (`2026-W40`, Senin–Minggu) di **zona profil** (`UTC` bila
>   kosong); tanpa `week` = minggu yang sedang berjalan. Bukan pola `YYYY-Www` → `400`;
>   minggu yang tidak ada (`W53` di tahun 52 minggu) atau di luar rentang tanggal
>   lintas-endpoint (1900–2999) → `400 invalid_week`; minggu yang belum dimulai →
>   `422 week_in_future`. `complete: false` selama minggunya belum berakhir.
> * `axes[]` = `{ key, label, value, previous, unit, evidence_count, why }` — `habits`
>   (bagian periode terjadwal yang terpenuhi, `unit: "0-1"`), lalu rata-rata yang
>   dilaporkan sendiri: `energy` · `focus` · `mood` (`"1-5"`) · `sleep` (`"jam"`);
>   `previous` = minggu sebelumnya atau `null`. Sumbu tanpa data tidak muncul; sumbu §31
>   yang V0 tidak ukur ada di `not_measured[]` (`learning` · `finance` · `social` ·
>   `career` · `lifestyle` — sama dengan dashboard 6.1).
> * `questions[]` — selalu lima, berurutan `went_well` · `changed` · `failed` · `why` ·
>   `change_next_week`: `{ key, question, stance, items:[{text, evidence_count}], prompt }`.
>   Tanpa butir → `stance: "ask"` (Confidence Layer 5.4). **`why` selalu `ask`**: data
>   observasional tidak membuktikan sebab (naskah 4 §7) — butirnya hanya alasan yang
>   pengguna catat sendiri saat melewatkan habit dan hal yang terjadi **bersamaan**
>   (energi di hari terpenuhi vs terlewat), bukan klaim kausal.
> * Aturan periode = rentetan 2.4: `partial` memenuhi, `skipped` netral (tidak dihitung
>   gagal), hari di luar jadwal dan sebelum habit dibuat tidak dihitung, periode yang
>   belum berakhir belum gagal; habit bulanan tidak dinilai per minggu.
>   `review_version: "tinjauan-mingguan@v1"`.

---

## Privacy Center

```
GET    /privacy/summary      → 200 { categories[], not_collected[] }   — jumlah per kategori, bukan isi
GET    /privacy/permissions  → 200 { agents[] }                        — keputusan yang BERLAKU per agent
PUT    /privacy/permissions/{subject_type}/{subject_id}/{scope}  { action, decision, expires_at? }   → 200 izin yang berlaku
POST   /privacy/export       { password }   → 202 { export_id, status: "ready", expires_at, download_url }
GET    /privacy/export/{id}                 → 200 { export_id, status, expires_at, download_url }
GET    /privacy/export/{id}/download        → 200 berkas JSON, SEKALI pakai   (Content-Disposition: attachment)
DELETE /privacy/data/{category}  { password }   → 202 { category, deleted: { <tabel>: <baris> } }
```

> 🔧 **Diselaraskan 8 Okt 2026 dengan kode 6.4 (7 Okt; K-41 · K-42 · K-43 · K-46).**
> Bentuk lama di atas (`POST /privacy/export` → `202 { export_id }` *async*, tautan
> unduh di `download_url`) tidak pernah dikodekan apa adanya. Yang berubah, dan kenapa:
>
> * **Ekspor dan hapus meminta sandi lagi** (OWASP ASVS 4.0.3 V3.7.1) — token yang dicuri
>   tidak boleh cukup untuk menyalin atau memusnahkan seluruh data seseorang. Tebakannya
>   memakai jatah login gagal akun itu (**E-226**, lihat *Identity*): sandi salah →
>   `403 invalid_credentials`, jatah habis → `429`.
> * **Ekspor tidak dibangun di latar, dan tidak menginap.** `POST` hanya mencatat
>   permintaan (`ready`, berlaku **1 jam**; paling banyak **5 per pengguna per jam** →
>   `429 rate_limited`); isinya **dibangun saat diunduh** dari PostgreSQL, di bawah RLS,
>   dalam satu potret (`REPEATABLE READ`). Redis hanya memegang status, tidak pernah isi
>   (prinsip E-171).
> * **Tak ada rahasia di URL** (ASVS V8.3.1). `download_url` jalur
>   `/v1/privacy/export/{id}/download` — tanpa token; unduhan butuh **sesi pemiliknya**
>   dan catatan yang masih `ready`. Sekali pakai, atomik (satu skrip Lua): unduhan kedua
>   → `410 export_already_downloaded`; tak ada, kedaluwarsa, atau milik pengguna lain →
>   `404 export_not_found`. Pembangunan yang gagal mengembalikan catatannya ke `ready`.
>   `download_url` terisi selama `ready` — di jawaban `POST` maupun `GET /privacy/export/{id}`
>   (🔧 8 Okt 2026: versi pertama memberi `null` di jawaban `POST`); `null` sesudah diunduh.
> * **Isi ekspor:** `{ format: "humanverse-export", format_version: 1, exported_at,
>   user_id, categories: { <kategori>: { <tabel>: [baris…] } } }` — tiap tabel ber-`user_id`
>   [`01`](01-DATABASE-SCHEMA.md) tepat sekali (`tests/unit/test_cakupan_privasi.py`),
>   tanpa `password_hash`, memori hanya yang hidup. Header `Cache-Control: no-store` dan
>   `Content-Disposition: attachment; filename="humanverse-export-YYYYMMDD.json"`
>   (diekspos CORS). Jejak: `data.export_requested` · `data.exported` (+ jumlah baris).
>   `POST /privacy/export` **tanpa** `Idempotency-Key` (aturan *Tulis*).
> * **Hapus per kategori = hapus KERAS, sampai ke turunannya** (naskah 11 §7.25 —
>   *“tidak boleh hanya menghapus row di PostgreSQL”*), satu transaksi, jejak
>   `data.deleted` di transaksi yang sama. `deleted` menyebut baris per tabel,
>   termasuk turunannya. `202`, bukan `200`: titik vektor memori yang dilupakan dibuang
>   penyelaras sesudah commit — Qdrant tidak ikut transaksi ([`01`](01-DATABASE-SCHEMA.md) §12).
>   Idempoten dengan sendirinya: hapus kedua menghapus nol baris.
>
>   | `category` | Yang ikut terhapus |
>   |---|---|
>   | `goals` · `habits` · `checkins` · `moods` | barisnya (+ milestone · penyelesaian) · event domainnya (lewat `hapus_event_pengguna`, migrasi `0013` — `hvx_app` tetap tanpa `DELETE` atas `events`) · memori ber-scope sumbernya · rekomendasi yang mungkin diturunkan darinya (termasuk semua yang dibuat agent) · `checkins` juga `human_states` · 🔧 `habits` juga proyeksi perilakunya — `activities` `source='inferred'` `kind='habit'` (5.1; E-232, 8 Okt 2026) |
>   | `journal` | `journal_entries` · event `journal.*` · memori `journal_raw` |
>   | `activities` | `activities` |
>   | `memories` | seluruh memori — *“lupakan semua yang kamu ingat tentangku”*; sumbernya tetap |
>   | `conversations` | percakapan dan pesannya |
>   | `recommendations` | rekomendasi dan umpan baliknya |
>   | `history` | seluruh riwayat event (sisa teks bebas C-33) · memori pola perilaku (`kind='behavioral'`) · 🔧 seluruh proyeksi `activities` `source='inferred'` — tanpa riwayatnya, membangun ulang pun tak melahirkannya lagi (E-232) |
>
>   `account` · `profile` · `audit` **tidak** bisa dihapus di sini (`409
>   category_not_deletable`; ringkasan menyebut `why_not_deletable` dan jalannya — hapus
>   akun, atau ubah lewat Profil). Kategori tak dikenal → `404 unknown_category`. Keduanya
>   diperiksa **sebelum** sandi, jadi tidak memakai jatah tebakan.
> * **`GET /privacy/summary`** — `categories[]` = `{ key, label, count, derived_count,
>   tables: { <tabel>: <baris> }, deletable, retention, why_not_deletable }` untuk tiga belas
>   kategori, dari satu potret basis data: `count` = yang kamu catat, `derived_count` =
>   yang sistem turunkan darinya (mis. `human_states`, rekomendasi, jejak kerja agent);
>   baris yang diarsipkan (`deleted_at`) ikut dihitung — masih tersimpan, jadi masih
>   diketahui — kecuali memori yang sudah dilupakan (isinya sudah kosong, tinggal
>   menunggu penyelaras). `retention` = masa simpan dalam kalimat untuk pengguna (GDPR Art. 13(2)(a)).
>   `not_collected[]` = yang **tidak** dikumpulkan V0 (lokasi · kalender · keuangan ·
>   wearable) — jawaban *“apa yang kamu tahu tentang saya”* juga menyebut yang tidak.
> * **`GET /privacy/permissions`** — `agents[]` = `{ subject_type: "agent", subject_id,
>   purpose[], permissions[] }`, tiap izin `{ scope, action, decision, source, expires_at,
>   sensitive, confirm_each_time }` untuk tiap (scope, aksi) yang **sungguh** diminta tool
>   agent aktif. `source: "user"` = keputusan tersimpan yang belum kedaluwarsa;
>   `"default"` = bawaan gerbang risiko (R0·R1 `allow`, R2 ke atas `ask`, scope sensitif
>   selalu `ask` — termasuk **`mood` sejak C-32**, K-46; R3 ke atas `confirm_each_time`).
>   Scope sensitif di pemanggilan agent lain (delegasi) **tidak** ditampilkan: delegasi
>   tidak membaca apa pun, izin yang bermakna milik agent yang membaca (**E-227**).
> * **`PUT /privacy/permissions/…`** — `{ action: read|write|execute|share|delete,
>   decision: allow|deny|ask, expires_at? }` → `200` izin yang berlaku sesudahnya
>   (bentuk butir `permissions[]`). Hanya untuk (agent, scope, aksi) yang diminta —
>   selainnya `404 permission_not_requested`, bukan baris yang tak pernah ditanyakan;
>   `expires_at` wajib berzona dan di depan → selainnya `422 expires_at_in_past`.
>   Idempoten dengan sendirinya.

> 🔧 **`{subject_type}` ditambahkan 17 Sep 2026 (E-163), saat mesin izin 1.5
> ditulis.** Kunci unik `permissions` di [`01`](01-DATABASE-SCHEMA.md) adalah
> `(user_id, subject_type, subject_id, scope, action)`. Nama agent
> (`^[a-z][a-z0-9-]{2,39}$`, [`05`](05-AGENT-CONTRACTS.md)) dan id integrasi
> bisa sama — tanpa `subject_type`, `PUT` tidak bisa menunjuk satu baris.
> `decision: ask` = kembali bertanya. ✅ Rutenya dikodekan bersama layar 6.4 (7 Okt
> 2026): `{subject_type}` selain `agent` lolos bentuk jalur, tetapi V0 hanya punya izin
> agent — `404 permission_not_requested`.
>
> Ini menerjemahkan layar Privacy Center naskah 5 §26 menjadi endpoint.
> **`GET /privacy/summary` sengaja mengembalikan jumlah baris, bukan isinya** —
> layar itu untuk menjawab *"apa yang kamu tahu tentang saya"*, dan jawabannya
> harus bisa dibaca tanpa menumpahkan seluruh data ke layar.

| Rute | Galat yang dijanjikan |
|---|---|
| `POST /privacy/export` | `403 invalid_credentials` · `429` (5 per jam per pengguna, jatah login gagal akun habis — E-226, atau jatah per IP login habis — E-233) |
| `GET /privacy/export/{id}` | `404 export_not_found` — tidak ada, kedaluwarsa, atau milik pengguna lain (tanpa membedakannya) |
| `GET /privacy/export/{id}/download` | `404 export_not_found` · `410 export_already_downloaded` |
| `DELETE /privacy/data/{category}` | `404 unknown_category` · `409 category_not_deletable` — keduanya sebelum sandi · `403 invalid_credentials` · `429` (jatah login gagal akun — E-226, atau per IP — E-233) |
| `PUT /privacy/permissions/…` | `400` bentuk jalur/badan salah, `expires_at` tanpa zona · `404 permission_not_requested` · `422 expires_at_in_past` |
