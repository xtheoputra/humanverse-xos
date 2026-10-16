# 06 — Module Boundaries (modular monolith V0)

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menurunkan naskah 5 §1 (*Modular Monolith*) dan §4 (monorepo) menjadi aturan
> yang bisa ditegakkan alat, bukan sekadar niat.

---

## Kenapa modular monolith, bukan 12 service

V0 punya **satu** pengguna nyata: pemiliknya. Memecahnya jadi service berarti
membayar biaya jaringan, deploy, dan penelusuran sebelum ada yang memakainya.
Yang perlu dijaga sejak awal bukan **proses terpisah**, melainkan **batas yang
tidak boleh dilanggar** — supaya pemisahan nanti (V2) jadi pekerjaan sehari,
bukan penulisan ulang.

```
apps/api/                    ← satu proses, satu deploy (Python + FastAPI)
└── modules/
    ├── identity/
    ├── profile/
    ├── goals/
    ├── habits/
    ├── checkins/
    ├── journal/
    ├── activities/
    ├── events/
    ├── memory/
    ├── intelligence/
    ├── agents/
    └── platform/
```

Setiap modul berbentuk sama:

```
modules/habits/
├── __init__.py       ← SATU-SATUNYA pintu keluar (public API modul)
├── routes.py         ← HTTP; tidak boleh diimpor modul lain
├── service.py        ← aturan bisnis
├── repository.py     ← SQL; hanya menyentuh tabel milik modul ini
├── events.py         ← event yang diterbitkan & didengarkan
└── schemas.py
```

> 🔧 **Bahasa backend: Python + FastAPI (K-13, 10 Sep 2026).** Versi pertama
> berkas ini ditulis untuk TypeScript/Node **tanpa pernah menyatakannya**,
> sementara naskah 1 ([`../docs/05`](../docs/05-ARSITEKTUR.md)) menetapkan
> FastAPI di dua tempat dan ADR-004 mengunci LangGraph. Bukti lengkap dan cara
> membalikkannya di [`../arch/05`](../arch/05-TECHNOLOGY-STACK.md) §2.

---

## Kepemilikan tabel

**Satu tabel dimiliki tepat satu modul.** Modul lain tidak boleh menyentuhnya
dengan SQL — harus lewat `__init__.py` pemiliknya.

| Modul | Tabel |
|---|---|
| `identity` | `users`, `consents`, `permissions`, `audit_logs` |
| `profile` | `profiles`, `human_states` |
| `goals` | `goals`, `goal_milestones` |
| `habits` | `habits`, `habit_completions` |
| `checkins` | `daily_checkins`, `mood_entries` |
| `journal` | `journal_entries` |
| `activities` | `activities` |
| `events` | `events` |
| `memory` | `memories` |
| `intelligence` | `recommendations`, `recommendation_feedback` |
| `agents` | `agents`, `agent_tools`, `agent_runs`, `ai_conversations`, `ai_messages` |

---

## Aturan ketergantungan

```
        platform  ◄── boleh dipakai semua
            ▲
            │
   identity ◄── semua modul (untuk cek izin)
            ▲
            │
   ┌────────┴────────┬──────────┬─────────┐
 goals ◄─ habits   checkins   journal   activities
   ▲        ▲          ▲          ▲          ▲
   └────────┴──────────┴──────────┴──────────┘
                       │  (hanya lewat EVENT, bukan panggilan langsung)
                       ▼
                    events
                       ▼
                    memory
                       ▼
                  intelligence
                       ▼
                    agents
```

> 🔧 **Gambar di atas adalah arah DATA, bukan arah IMPOR** (K-17, 16 Sep 2026).
> Arah impor ditentukan aturan 6: modul domain yang wajib menerbitkan event
> harus bisa memanggil `events`, jadi `events` berada **di bawah** modul domain.
> `memory` di atas modul domain karena ekstraksi memori membaca isi jurnal
> (tugas 3.6) — dan isi jurnal sengaja **tidak pernah** masuk event
> ([`03`](03-EVENT-CONTRACTS.md)). `intelligence` di atasnya lagi: 5.3 menulis
> `human_states` milik `profile`, 5.5 membaca habit dan goal. Urutan lengkap:
> kontrak `m1-m3-lapisan` di `pyproject.toml`.

| # | Aturan | Ditegakkan oleh |
|---|---|---|
| 1 | Modul hanya boleh mengimpor `__init__.py` modul lain, tidak pernah berkas dalamnya | `import-linter` kontrak `protected`, satu per modul (`m2-*`) |
| 2 | Tidak ada impor melingkar | `import-linter` kontrak `layers` (`m1-m3-lapisan`, antarmodul) + `acyclic_siblings` (`m1-siklus-dalam`, di dalam modul) |
| 3 | Modul domain (`goals`…`activities`, `profile`) **tidak boleh** saling mengimpor — komunikasinya lewat event, atau lewat **pembaca/pendengar yang disambung titik rakit** `hvx.main` di transaksi pemanggil (K-17, **K-23** — lihat catatan di bawah) | `import-linter` lapisan independen di `m1-m3-lapisan` · sambungannya: `tests/unit/test_main.py` |
| 4 | `agents` boleh membaca modul lain; **tidak ada** modul yang mengimpor `agents` | `import-linter` — `agents` lapisan teratas `m1-m3-lapisan`, `exhaustive = true` |
| 5 | `repository.py` hanya boleh menyebut tabel milik modulnya | `tests/unit/test_batas_tabel.py` — tabel kepemilikan dibaca **dari berkas ini**; SQL **tiap berkas `.py`** modul dipindai, bukan hanya `repository.py` · mutasi `06.5` |
| 6 | Setiap tulisan ke tabel domain yang mengubah **fakta perilaku** **wajib** menerbitkan event padanannya di [`03`](03-EVENT-CONTRACTS.md), **di transaksi yang sama** — peta lengkapnya di bawah | `tests/integration/test_penerbitan_event.py` — tiap baris peta, lewat HTTP; kirim ulang tidak menerbitkan apa pun · mutasi `3.2` |

> 🔧 **Aturan 6 semula: *“setiap tulisan ke tabel domain”* — dan `profile` modul
> domain (aturan 3).** Sprint 1 menulis `profiles` (pendaftaran · `PATCH
> /me/profile`) tanpa event, sebab ke-22 event V0 di [`03`](03-EVENT-CONTRACTS.md)
> tidak memuat satu pun `profile.*`: domainnya **terdaftar** di
> [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2 dan sengaja **belum dipakai**.
> Kalimat lama dilanggar sejak tulisan pertama tanpa ada yang tahu — dan
> penegaknya masih menulis *“belum ada tulisan domain”* (**E-166**, tinjauan
> Sprint 1). Event profil yang dibutuhkan kelak masuk lewat `03` dulu, baru
> aturan ini mengikatnya.

> 🔧 **Aturan 3 dan bacaan yang harus satu transaksi (K-17, K-23).** Event
> menjawab *“beri tahu yang lain bahwa sesuatu terjadi”*, bukan *“baca keadaan
> modul lain di transaksi ini”*. Sprint 1–2 butuh yang kedua: profil awal dibuat
> di transaksi pendaftaran; rentetan habit butuh zona waktu profil; tier habit
> butuh energi check-in; habit hanya boleh menaut goal yang hidup; goal yang
> dihapus melepas habit yang menautnya. Tidak satu modul pun mengimpor yang
> lain untuk itu — **titik rakit `hvx.main`** memasang fungsi pintu keluar satu
> modul di `app.state`, dan modul lain memanggilnya dengan koneksinya sendiri
> (RLS dan transaksinya sama). Yang terpasang: `pendengar_pendaftaran`
> (identity → profile) · `pembaca_zona_waktu` (habits ← profile) ·
> `pembaca_energi` (habits ← checkins) · `pembaca_goal_hidup` (habits ← goals) ·
> `pendengar_goal_dihapus` (goals → habits) · `pendengar_jurnal_berubah`
> (journal → memory, 3.6 — `memory` di ATAS `journal` dan boleh mengimpornya,
> tetapi `journal` tidak boleh mengimpor `memory`). Rute yang butuh sambungan
> MENOLAK berjalan tanpanya (`RuntimeError`), bukan jatuh ke bawaan diam-diam,
> dan `tests/unit/test_main.py` memeriksa keenamnya terpasang.
>
> ✅ **Aturan 6 dan Sprint 2 (E-176) — ditutup 3.2.** Sprint 2 menulis
> `goals` · `goal_milestones` · `habits` · `habit_completions` ·
> `daily_checkins` · `mood_entries` sebelum tabel `events` ada (3.1). Sejak 3.2
> tiap tulisan di peta di bawah menerbitkan eventnya di transaksi yang sama.
> Tidak ada *backfill*: tidak ada data produksi sebelum 3.2 (V0 belum dipasang
> di mana pun — D0 lokal), dan basis data pengembang dibuat ulang.

### Peta aturan 6 — tulisan mana menerbitkan apa (tugas 3.2)

| Tulisan ([`04`](04-API-CONTRACTS.md)) | Event | Kunci ([`03`](03-EVENT-CONTRACTS.md) aturan 1) |
|---|---|---|
| `POST /goals` | `goal.created` | `goal:<id>:created` |
| `PATCH /goals/{id}` yang **mengubah** status menjadi `achieved` | `goal.completed` | `goal:<id>:completed:<achieved_at>` |
| `POST /habits` | `habit.created` | `habit:<id>:created` |
| `POST …/completions` yang **melahirkan baris** `done`/`partial` · `skipped` | `habit.completed` · `habit.skipped` | `habit-completion:<completion_id>` |
| `DELETE …/completions/{for_date}` yang **menghapus baris** | `habit.completion_retracted` | `habit-completion:<completion_id>:retracted` |
| `PUT /checkins/{for_date}` yang **mengubah** isi check-in (atau membuatnya) | `checkin.logged` | `checkin:<for_date>:<updated_at>` |
| `POST /moods` | `mood.logged` | `mood:<mood_id>` |
| `POST /journal` (3.4) | `journal.created` | `journal:<journal_id>` |

**Tanpa event V0 — dan kenapa:** `PATCH /goals` selain perubahan menjadi
`achieved`, hapus-lunak goal & habit, milestone, `PATCH /habits`, profil. Semuanya
**konfigurasi**, bukan fakta perilaku: tabelnya sendiri sumber kebenarannya, dan
aturan **D** [`02`](02-ERD.md) (*tabel domain adalah proyeksi event*) berlaku bagi
fakta perilaku — yang dibaca Behavior Engine. ⚠️ Satu yang diakui: goal
`achieved` yang dibuka lagi tidak menerbitkan apa pun, jadi `goal.completed`-nya
tetap di riwayat. Event konfigurasi (mis. `goal.changed` di tabel padanan) bisa
mulai diterbitkan kapan saja tanpa kehilangan apa pun — tabelnya menyimpan
keadaannya.

🔧 **Tiga tulisan yang semula tidak disebut di peta maupun di sini** (tinjauan
kontrak Sprint 3, K6):

| Tulisan | Kenapa tanpa event V0 |
|---|---|
| `POST /activities` (3.8) | ⚠️ **Fakta perilaku — dan diakui sebagai pengecualian.** Event padanannya (`workout.completed`, `meal.logged`, `learning.completed`, `meeting.completed`) ada di [`03`](03-EVENT-CONTRACTS.md) tetapi **belum ✅ V0**, dan bentuk payload-nya tidak memetakan kosakata `activities.kind` yang masih terbuka. Tabel `activities` menyimpan faktanya, jadi event bisa diterbitkan belakangan dengan `source='backfill'` tanpa kehilangan apa pun. Sampai itu aturan **D** tidak berlaku untuk `activities` — dinyatakan di sini, bukan diam-diam |
| `PATCH /journal/{id}` | menyunting tulisan tidak melahirkan fakta perilaku baru: *menulis jurnal* terjadi pada `occurred_at`-nya, dan isinya tidak pernah masuk event |
| `DELETE /journal/{id}` | hapus-lunak (`deleted_at`); `journal.created` (hanya `word_count`) tetap di riwayat. Apakah fakta *pernah menulis jurnal* ikut dicabut bersama tulisannya — bentuk E-178 untuk jurnal — terikat **C-31**, milik pemilik |

> 🔧 **Aturan 6 dipersempit 24 Sep 2026 (E-179), saat 3.2 ditulis.** Kalimat
> sebelumnya (*“setiap tulisan ke tabel yang punya event padanan”*) menuntut
> event untuk tiap `PATCH` judul goal — padahal 23 event `03` tidak punya satu
> pun jenis untuknya, dan menambah sepuluh event konfigurasi ke V0 gagal uji
> [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §7. Yang dijaga kini persis yang
> membuat aturan **D** benar: **tidak ada fakta perilaku yang lolos tanpa event** —
> dengan satu pengecualian yang dinyatakan: `activities` V0 (tabel di atas).

> Tiap kontrak di atas **terbukti sanggup gagal** — `tools/uji_mutasi_kode.py`
> memiliki satu mutasi per id kontrak, dan `tests/unit/test_penegak.py`
> menolak kontrak tanpa mutasi maupun modul di disk yang tidak tercatat di
> kontrak.

> Aturan **3** yang paling sering dilanggar dan paling mahal dibatalkan. Kalau
> `habits` boleh memanggil `checkins` langsung, keduanya menyatu dalam sebulan
> dan pemisahan V2 jadi mustahil. Kalau lewat event, keduanya tetap bisa
> dipisah kapan saja.
>
> Aturan **6** membuat aturan **D** di [`02-ERD.md`](02-ERD.md) benar: tabel
> domain boleh dibangun ulang dari event **hanya jika** tidak ada tulisan yang
> lolos tanpa event.

---

## Jalan keluar ke V2

Ketika satu modul perlu dipisah jadi service:

1. `__init__.py`-nya sudah jadi kontrak — ganti isinya dengan klien HTTP/gRPC.
2. Tabelnya sudah tidak disentuh modul lain — pindahkan basis datanya.
3. Event-nya sudah mengalir lewat antrean — tidak ada yang berubah bagi
   consumer.

Kalau ketiga hal itu tidak benar sejak V0, pemisahan berarti penulisan ulang.
Itulah seluruh alasan aturan di atas ada.
