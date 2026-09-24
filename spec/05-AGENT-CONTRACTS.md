# 05 — Agent Contracts

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menurunkan manifest naskah 5 §14 menjadi skema yang bisa divalidasi.

---

## Skema manifest

```yaml
# agents/<name>/manifest.yaml
name:        coach-agent          # ^[a-z][a-z0-9-]{2,39}$
version:     1.0.0                # semver, wajib
kind:        core                 # core | domain | third_party
status:      active               # draft | active | deprecated | disabled

purpose:                          # 1-5 baris, untuk manusia
  - daily coaching conversation
  - weekly review

capabilities:                     # kontrak mesin; nama snake_case
  - daily_coaching
  - weekly_review

tools:                            # harus ada di tool registry
  - habit.list
  - habit.streak
  - memory.search
  - checkin.get

memory:
  read:  [ habits, goals, checkins, mood ]
  write: [ coaching_notes ]

model:
  class:    reasoning             # simple | reasoning | vision | embedding
  fallback: simple

max_risk:   R1                    # 🔧 pagu RISIKO AKSI yang boleh dilakukan agent ini
autonomy:
  max_level: L2                   # 🔧 tangga OTONOMI, terpisah dari R (H-21)
  kill_condition: []              # 🔧 syarat berhenti tanpa menunggu manusia
deploy:     cloud                 # 🔧 edge | cloud | both

evaluation:
  suite: coach-agent-v1
  gates:
    safety:          0.99         # turun di bawah ini = tidak boleh production
    user_satisfaction: 0.70
  budget:
    p95_latency_ms:  4000
    cost_usd_per_run: 0.02
```

Aturan validasi yang ditegakkan saat registrasi:

| # | Aturan |
|---|---|
| 1 | Setiap nama di `tools` **harus ada** di tool registry. Manifest dengan tool tak dikenal ditolak. |
| 2 | Setiap scope di `memory.read`/`write` **harus ada** di daftar scope resmi. |
| 3 🔧 | **Setiap tool di `tools:` wajib punya `risk_level <= max_risk`.** Manifest yang mendaftarkan tool lebih berisiko daripada pagunya **ditolak**. (Menggantikan aturan lama *“`risk_level >= 3` wajib punya `requires_confirmation`”* — [#52](../../issues/52) sudah memindahkan `requires_confirmation` ke Policy Engine.) |
| 4 | `evaluation.gates.safety` **wajib** ada dan `>= 0.95`. |
| 5 | Satu `name` hanya boleh punya **satu** baris `status: active`. |
| 6 | `kind: third_party` **tidak boleh** meminta scope `journal`, `journal_raw` 🔧, `finance`, atau `health`. |
| 7 🔧 | Tool yang akibatnya sampai kepada **orang selain pemegang akun** (`reaches_third_party: true`) **wajib** `risk_level >= 3`. Manifest yang menurunkannya **ditolak**. |
| 8 🔧 | Tool **tanpa** `risk_level` **ditolak** saat registrasi. **Tidak ada bawaan** — kelalaian berhenti di validator, bukan di produksi. |
| 9 🔧 | Perluasan aturan 6: `kind: third_party` juga **tidak boleh** meminta scope `spatial`, `location`, `people`, atau `csi`. |

## 🔧 Daftar scope resmi V0 (aturan 2 · E-180)

> Ditambahkan 24 September 2026, saat tugas 3.7 ditulis. Aturan 2 merujuk
> *“daftar scope resmi”* sejak versi pertama berkas ini — tetapi daftarnya
> **tidak pernah ditulis di mana pun**, jadi tidak satu penegak pun bisa
> memeriksanya, dan pencarian memori 3.7 (*“agent tanpa izin scope tidak
> menerima barisnya”*) tidak punya pembanding.

| Scope | Isi | Sensitif ⁽¹⁾ | Dibaca manifest V0 |
|---|---|---|---|
| `habits` | habit dan penyelesaiannya | — | coach · habit · memory |
| `goals` | goal dan milestone | — | coach · memory |
| `checkins` | check-in harian: energi, fokus, jam tidur | — | coach · memory |
| `mood` | mood yang dilaporkan, dan memori episodiknya (3.6) | — | coach · memory |
| `coaching_notes` | catatan yang ditulis `coach-agent` | — | coach · memory |
| `journal_raw` | isi jurnal apa adanya, dan memori episodiknya (3.6) | ✅ | **tidak satu pun** |

⁽¹⁾ **Sensitif = tidak pernah `allow` karena bawaan.** Hanya keputusan `allow`
yang disimpan pengguna sendiri (`PUT /privacy/permissions/…`, 6.x) yang
membukanya — bukan bawaan risk 0·1 gerbang risiko. Naskah 5 §15: *private
journal* ada di daftar **tidak boleh otomatis**, bahkan bagi agent yang bekerja
di atasnya. Ditegakkan di satu tempat: mesin izin (`identity.MesinIzin.cek`).

Daftar ini **mengikat tiga penegak**: mesin izin menolak keputusan atas scope di
luar daftar (1.5); pencarian memori menolak manifest yang memintanya (3.7);
registry agent menolak manifest-nya (4.2, aturan 2). Sumber kodenya satu:
`identity.SCOPE_RESMI` — scope baru masuk **di sini dulu**, lalu di sana, di PR
yang sama.

> 🔧 **Dua koreksi yang ikut (E-180).** **(a)** Aturan 6 melarang pihak ketiga
> meminta `journal` — tetapi scope yang benar-benar ada di V0 adalah
> `journal_raw`, yang **lebih** sensitif; tanpa menyebutnya, larangan itu
> dilewati dengan meminta scope mentahnya. **(b)** Kolom *Memory write*
> `memory-agent` di bawah berisi `memories` — nama **tabel**, bukan scope, dan
> aturan 2 menolak manifest yang menuliskannya. Diganti dengan cakupan yang
> setara dengan kolom baca-nya.

> Aturan 6 adalah penegakan **C-7/A-15** di lapisan yang paling murah:
> selama marketplace belum punya proses review, sandbox, dan perjanjian
> pemroses data, agent pihak ketiga tidak bisa meminta data paling sensitif —
> ditolak oleh validator, bukan oleh kebijakan tertulis.

> 🔧 **Aturan 7 (ditambahkan 9 Sep 2026, keputusan didelegasikan K-1).**
> §11.15 menaruh `send low-risk message` di **R2** — di bawah ambang
> konfirmasi yang **H-15** ([#5](../../issues/5)) tetapkan di R3 — sementara
> tiga tangga risiko sebelumnya menaruh pengiriman pesan di **3/R3**, dan kata
> *“low-risk”* tidak pernah didefinisikan di mana pun. Tetangganya di baris yang
> sama, `purchase low-value item`, punya penyelamat berupa angka
> (`amount_limit: 0`); pesan tidak punya padanannya.
>
> **Yang menanggung risikonya adalah penerima**, yang tidak pernah menyetujui
> apa pun (**C-19**). Karena penilai dan penanggung risiko bukan pihak yang
> sama, bawaannya diambil ke sisi yang lebih aman sampai ada definisi yang bisa
> diuji mesin.
>
> ⚠️ **Untuk V0 aturan ini tidak mengubah apa pun** — V0 tidak punya satu pun
> tool level 3 atau 4. Ia berlaku begitu Phase 11 mulai dikodekan.
> Cara membalikkannya ada di
> [`../docs/KEPUTUSAN-DIDELEGASIKAN.md`](../docs/KEPUTUSAN-DIDELEGASIKAN.md) K-1.

> 🔧 **Aturan 3 ditulis ulang (10 Sep 2026, K-14).** Dua alasan, keduanya sudah
> tercatat: [#52](../../issues/52) memindahkan `requires_confirmation` ke Policy
> Engine — jadi aturan lama memeriksa medan yang seharusnya tidak lagi ada di
> manifest; dan **E-119** ([#97](../../issues/97)) menunjukkan `risk_level`
> sebagai properti **agent** membalik pemisahan R/L yang **H-21** selesaikan.
> Satu agent bisa membaca kalender (R0) **dan** memesan hotel (R3) — satu angka
> tidak bisa menjadi keduanya, tetapi sebuah **pagu** bisa.
>
> ⭐ Aturan baru membuat manifest **tidak bisa berbohong**: `max_risk: R1` sambil
> mendaftarkan tool R3 ditolak **saat registrasi**, bukan ditemukan saat ia
> memesan hotel. Konfirmasi tidak lagi dinyatakan di manifest sama sekali — ia
> turunan dari `R` lewat tabel gerbang
> [`../arch/04`](../arch/04-DEPENDENCY-GRAPH.md) §3.

> 🔧 **Aturan 8 dan 9 (K-12).** **G-11** mencatat 13 tool persepsi §10.26 tanpa
> satu pun `risk_level`, dan §15.24 mengulanginya untuk lima panggilan SDK
> spasial yang mengembalikan **denah rumah** dan **posisi pengguna**. Medan
> `risk_level` memang sudah ada di skema — tetapi **medan yang ada di skema
> bukan medan yang ditegakkan**.
>
> Bawaan `risk_level: 0` sengaja **tidak** dipakai: bawaan nol berarti tool yang
> lupa diberi tingkat risiko otomatis menjadi **yang paling tidak dijaga**.
>
> Aturan 9 memperluas larangan scope aturan 6 ke data spasial, sesuai usul yang
> sudah dicatat di [`../docs/226`](../docs/226-SDK-REPO-API-DATA-EVENT-DEPLOYMENT.md).

---

## 🔧 Kapan sesuatu adalah agent, dan kapan ia service (K-5)

> Ditambahkan 9 September 2026 — **keputusan didelegasikan K-5**, menutup
> **G-13** / [#89](../../issues/89).

Sebuah komponen masuk registry agent **hanya bila ketiganya benar**:

| # | Uji | Kalau tidak |
|---|---|---|
| a | merencanakan **lebih dari satu langkah** | urutan tetap ⇒ service |
| b | **memilih** di antara beberapa tool saat berjalan | pemanggilan tetap ⇒ service |
| c | bisa **dihentikan di tengah** dan meninggalkan jejak yang bisa dilanjutkan (`agent_runs`) | sekali jalan ⇒ service |

⭐ **Ketiganya juga persis yang membuat risk gate bermakna**: sesuatu yang tidak
memilih tool tidak butuh gerbang tool. Uji (b) sendirian meloloskan pipeline
bercabang; uji (c) sendirian meloloskan job antrean biasa.

Dasarnya kata pemilik sendiri, §12.29: *“jangan membuat semuanya sebagai
autonomous agent sejak awal — sebagian lebih baik sebagai deterministic/model
services.”* Itu satu-satunya peringatan semacam itu dalam 24 naskah, dan
sensus menemukan **44 dari 59 nama agent hanya pernah disebut sekali**
([`../docs/SENSUS-AGENT.md`](../docs/SENSUS-AGENT.md)).

⚠️ **Diperiksa, bukan dinyatakan (10 Sep 2026).** `coach-agent` dan
`habit-agent` lulus ketiganya. `orchestrator-agent` **gagal uji (b)** — ia punya
`tools: —`; yang dipilihnya **agent lain**. Itu bukan perkara istilah:
selama memanggil agent bukan pemanggilan tool, **sisi-sisi pohon eksekusi
(`parent_run_id`) tidak pernah melewati risk gate**. ⇒ **K-14**: memanggil agent
lain adalah pemanggilan tool, terdaftar dengan `kind: agent` dan
`risk_level = max_risk` agent yang dipanggil. `memory-agent` **perbatasan** —
diputuskan saat Sprint 3–4 ditulis. Rinciannya di
[`../arch/08`](../arch/08-AGENT-CONTRACTS.md) §2.

---

## Tool registry

```yaml
# tools/<name>.yaml
name:        habit.streak
version:     1.0.0
kind:        read                  # read | write | external
description: Hitung rentetan dan tingkat penyelesaian sebuah habit
scopes:      [ habits ]            # scope memory/data yang disentuh
risk_level:  0
input:
  habit_id:  { type: uuid, required: true }
output:                            # 🔧 = GET /habits/{id}/streak (04, E-176)
  current:              integer
  longest:              integer
  completion_rate_30d:  number | null   # null = belum ada periode jatuh tempo
side_effects: none                 # none | writes_user_data | external_call
reaches_third_party: false         # 🔧 K-1: true bila akibatnya sampai ke orang
                                   #     selain pemegang akun. true ⇒ risk_level >= 3
rate_limit:   60/min/user
```

> 🔧 **`reaches_third_party` (K-1).** Medan ini yang ditegakkan aturan 7. Ia
> sengaja **bukan** turunan dari `side_effects`: `external_call` bisa berarti
> memanggil API cuaca (tak menyentuh siapa pun) **atau** mengirim pesan kepada
> orang lain — dua hal yang risikonya berbeda jauh, dan satu medan tidak bisa
> memisahkannya. Seluruh tool V0 bernilai `false`.

Tool V0 — **9 tool + 3 entri `kind: agent`**:

| Tool | Kind | Risk | Dipakai |
|---|---|---|---|
| `habit.list` | read | 0 | Coach, Habit |
| `habit.streak` | read | 0 | Coach, Habit |
| `habit.complete` | write | 2 | Habit |
| `goal.list` | read | 0 | Coach |
| `checkin.get` | read | 0 | Coach |
| `mood.recent` | read | 0 | Coach |
| `memory.search` | read | 0 | Coach, Memory |
| `memory.write` | write | 2 | Memory |
| `recommendation.create` | write | 1 | Coach |
| `agent.coach` | **agent** | 1 | Orchestrator |
| `agent.habit` | **agent** | 2 | Orchestrator |
| `agent.memory` | **agent** | 2 | Orchestrator |

> 🔧 **Tiga baris terakhir ditambahkan 11 September 2026 — menerapkan
> [K-14](../docs/KEPUTUSAN-DIDELEGASIKAN.md), yang sudah diputuskan
> 10 September.** K-14 berbunyi *“setiap agent yang bisa dipanggil agent
> lain **wajib terdaftar di tool registry** dengan `kind: agent`”*, dan
> [`07`](07-BACKLOG-V0.md) 4.3 sudah **menghitungnya** (*“9 tool V0 + 3
> entri `kind: agent`”*) — tetapi **registry-nya sendiri tetap 9 baris.**
> `risk_level` tiap entri = `max_risk` agent yang dipanggil (K-14).
>
> 🛑 **Akibatnya bukan kerapian: selama ketiganya tidak punya baris,
> aturan validasi 3 (*tiap tool wajib `risk_level <= max_risk`*) TIDAK
> BISA DIJALANKAN untuk `orchestrator-agent`** — tool yang dipakainya
> tidak punya `risk_level` untuk dibandingkan. Gerbangnya ada,
> angkanya tidak.
>
> 💡 **Ini kali KEEMPAT bentuk yang sama tercatat** (#52 · H-21/#67 ·
> B-22/#59, ketiganya di Sesi 26) — sebuah keputusan diambil, ditutup,
> **lalu tidak pernah diterapkan pada berkas yang paling
> berkepentingan**. Kali ini yang terlewat adalah keputusan yang dibuat
> **sehari sebelumnya**, oleh orang yang menulis catatannya sendiri.
> Ditemukan [`../tools/periksa_dokumen.py`](../tools/README.md) **A-3**,
> bukan dengan membaca ulang.

> **`weather.get` dan `calendar.get` tidak ada di V0** — keduanya tool
> (butir **H-11**), tapi Fashion dan Context baru masuk V2. Ditulis di
> registry V2.

---

## Empat agent V0

| Agent | `max_risk` | Tools | Memory read | Memory write |
|---|---|---|---|---|
| `orchestrator-agent` | **R2** ⁽¹⁾ | `agent.coach` · `agent.habit` · `agent.memory` (**`kind: agent`**, K-14) | — | — |
| `coach-agent` | R1 | habit.list, habit.streak, goal.list, checkin.get, mood.recent, memory.search, recommendation.create | habits, goals, checkins, mood, coaching_notes | coaching_notes |
| `habit-agent` | R2 | habit.list, habit.streak, habit.complete | habits | — |
| `memory-agent` | R2 | memory.search, memory.write | semua scope **kecuali** `journal_raw` | semua scope **kecuali** `journal_raw` 🔧 |

⁽¹⁾ 🔧 **`orchestrator-agent` naik dari `risk_level: 0` ke `max_risk: R2`**, dan
itu konsekuensi langsung aturan 3 yang baru: ia memanggil `agent.habit`
(`risk_level` = `max_risk` `habit-agent` = **R2**), jadi pagu R0 akan
**ditolak validator**. Angka lama tampak benar hanya selama pemanggilan agent
tidak dihitung sebagai tool.

> **`memory-agent` boleh membaca hampir semua scope tetapi tidak `journal_raw`.**
> Ia mengekstrak memori **dari** jurnal lewat pipeline tertutup, bukan dengan
> membaca sesuka hati. Itu penerapan naskah 5 §15: *private journal* ada di
> daftar DENY bahkan untuk agent yang bekerja di atasnya.
>
> 🔧 **Pipeline tertutup itu, di V0 (spec/07 3.6):** konsumen stream `memori`
> di proses pekerja — **service**, bukan agent: ia selalu menulis keluaran
> ekstraksinya dan tidak memilih tool (uji K-5 (a)(b) gagal). Itu menjawab
> separuh pertanyaan [`../arch/08`](../arch/08-AGENT-CONTRACTS.md) §2.2 untuk
> jalur ekstraksi; `memory-agent` di percakapan (4.7) diputuskan saat ditulis.
> Tanpa model bahasa, yang diekstrak V0 hanya memori **episodik** — apa yang
> dilaporkan atau ditulis pengguna, kapan (K-27).

---

## Risk gate

Alur wajib sebelum aksi dijalankan:

```
capability diminta
      ↓
risk_level TOOL  (bukan agent — agent hanya punya PAGU `max_risk`)
      ↓
R >= 3 ?  → ya → konfirmasi manusia WAJIB  (H-15 / #5)
      ↓
permissions(user, agent, scope, action) → 'deny' → tolak & catat
                                        → 'ask'  → minta izin
                                        → 'allow'→ lanjut
      ↓
jalankan · catat agent_runs · catat audit_logs
```

**Default V0** 🔧 — menjawab issue #5 dengan pilihan paling aman:

| Risk | Default V0 |
|---|---|
| 0 · informasi | `allow` |
| 1 · rekomendasi | `allow` |
| 2 · aksi reversibel | **`ask`** sekali per jenis aksi, lalu boleh diingat |
| 3 · aksi berdampak | **`ask` setiap kali** |
| 4 · high-impact | **tidak ada di V0** — tidak ada tool yang bisa mencapainya |

> 🔧 **“Default” di tabel ini = bawaan untuk yang BELUM diputuskan pengguna**
> (E-167, tinjauan Sprint 1). Mesin izin 1.5 semula menjawab `ask` untuk *tanpa
> baris* dan untuk *`ask` yang disetel pengguna* — gerbang tidak bisa menerapkan
> risk 0 · 1 → `allow` tanpa menimpa pilihan *“tanya aku”*. Mesin izin kini
> menerima `MesinIzin.cek(…, bawaan=…)`; gerbang risiko (tugas 4.5, **belum
> ada**) memanggilnya dengan bawaan per risk. Keputusan tersimpan yang **belum
> kedaluwarsa** — termasuk `ask` — menang atas bawaan itu. **R ≥ 3 tidak
> terpengaruh**: konfirmasi manusia diminta sebelum mesin izin ditanya, jadi
> `allow` yang tersimpan tidak pernah melewatinya.

> V0 tidak punya satu pun tool level 3 atau 4. Itu disengaja: janji *"Act
> selalu di bawah kontrol pengguna"* paling mudah ditepati dengan tidak
> memberi agent kemampuan yang belum perlu.

> 🔧 **Gerbang di atas adalah bentuk V0 dari rantai kanonik 12 gerbang**
> [`../arch/04`](../arch/04-DEPENDENCY-GRAPH.md) §3. Yang belum ada di V0 —
> `IMPACT`, `DELIBERATE`, `OVERRIDE` — memang belum punya hal untuk dijaga:
> tidak ada tool V0 yang menyentuh orang lain (`reaches_third_party: false`
> pada kesembilannya) dan tidak ada aksi yang berjalan cukup lama untuk
> di-override. Keduanya masuk bersama Phase 11.
