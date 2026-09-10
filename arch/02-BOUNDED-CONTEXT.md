# 02 — Bounded Context Final

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“bounded context final”* naskah 24. Menutup
> [#130](../../issues/130) (*World Model lawan Global Twin*) dan
> [#147](../../issues/147) (**G-20**); memberi bentuk bagi
> [#55](../../issues/55) dan [#84](../../issues/84).

---

## §1 Definisi yang dipakai — dan kenapa definisi ini yang dipilih

> 🔑 **Sebuah bounded context memiliki satu KOSAKATA. Di dalamnya, sebuah kata
> berarti tepat satu hal. Di luar batasnya, kata yang sama boleh berarti hal
> lain — dan itu SAH, asalkan batasnya dinyatakan.**

Definisi ini dipilih karena ia satu-satunya yang **menjelaskan pengukuran repo
ini**. Sensus menemukan `simulation/` di **13 pohon**
([`../docs/SENSUS-MODUL.md`](../docs/SENSUS-MODUL.md)); pemeriksaan tangan
menemukan itu **lima mesin berbeda**. Dua bacaan mungkin:

| Bacaan | Akibat |
|---|---|
| *“tiga belas duplikat, gabungkan”* | satu modul raksasa yang tak seorang pun bisa memiliki |
| **konteks** — *“lima kosakata, masing-masing sah”* | lima modul, masing-masing punya pemilik, dan **namanya dibedakan** |

Bacaan kedua yang dipakai. Itu juga
[K-9](../docs/KEPUTUSAN-DIDELEGASIKAN.md) hasil ketiga (**diganti nama**, bukan
digabung, bukan dibiarkan).

### Uji empat pertanyaan — sebuah modul adalah konteks hanya bila keempatnya terjawab

| | Pertanyaan | Kalau tak terjawab |
|---|---|---|
| 1 | **Tabel apa yang HANYA dia tulis?** | ia bukan konteks — ia pembaca |
| 2 | **Awalan event apa yang HANYA dia terbitkan?** | ia tidak punya suara; ia perpustakaan |
| 3 | **Kata apa yang artinya LOKAL di dalamnya?** | batasnya tidak diperlukan — gabungkan ke induknya |
| 4 | **Apa yang ia TIDAK BOLEH lakukan?** | batasnya tidak bisa ditegakkan, dan akan hilang dalam dua bulan |

⚠️ **Pertanyaan 4 yang paling sering dilewati, dan yang paling mahal.** Repo ini
sudah membuktikannya sepuluh kali: *aturan yang dinyatakan tetapi tidak dijaga*.
Kolom **TIDAK BOLEH** di §3 adalah satu-satunya kolom yang langsung menjadi
pemeriksaan CI di [`11`](11-PENEGAKAN.md).

---

## §2 Tujuh belas konteks, lima lapisan

```
 MELINTANG ─── security ····· governance ····· platform
                  │               │               │
                  ▼               ▼               ▼
  L1 MANUSIA      identity ── human-core
                       │           │
  L2 INGATAN           └──► events ──► memory ──► context
                                                    │
  L3 KESIMPULAN        knowledge ◄── intelligence ◄──┘
                            ▲            │
                       world-model ──► simulation
                                         │
  L4 TINDAKAN                     agents ──► tools
                                         │
  L5 DUNIA FISIK    perception ──► spatial ──► embodiment
```

⚠️ **Panah = arah ketergantungan yang DIIZINKAN**, bukan aliran data. Grafnya
lengkap beserta larangannya di [`04`](04-DEPENDENCY-GRAPH.md).

---

## §3 Tiap konteks, empat jawaban

### L1 · Manusia

| | **`identity`** |
|---|---|
| menjawab | **siapa orang ini, dan apa yang ia izinkan** |
| memiliki tabel | `users` · `consents` · `permissions` · `audit_logs` · `sessions` |
| menerbitkan | `identity.*` · `consent.*` · `permission.*` |
| kata lokal | **`session`** = sesi login (di `platform` ia sesi runtime agent) |
| 🛑 **TIDAK BOLEH** | menyimpan apa pun tentang **perilaku**. Begitu `identity` tahu kebiasaan seseorang, tabel izin dan tabel perilaku hidup di satu modul dan hak hapus ([#22](../../issues/22)) jadi mustahil dipisahkan dari jejak audit |

| | **`human-core`** |
|---|---|
| menjawab | **apa yang orang ini lakukan dan inginkan** — direkam, bukan disimpulkan |
| memiliki tabel | `profiles` · `goals` · `goal_milestones` · `habits` · `habit_completions` · `daily_checkins` · `mood_entries` · `journal_entries` · `activities` |
| menerbitkan | `goal.*` · `habit.*` · `journal.*` · `mood.*` · `meal.*` · `sleep.*` · `workout.*` · `travel.*` · `learning.*` · `meeting.*` · `outfit.*` · `purchase.*` |
| kata lokal | **`state`** = keadaan manusia (`human_states`) |
| 🛑 **TIDAK BOLEH** | **menyimpulkan apa pun.** Ia merekam. Setiap angka di sini punya asal yang bisa ditunjuk pengguna. Taksiran hidup di `intelligence`, dan tiap taksiran wajib membawa `confidence` |

> 🔑 **Batas ini yang membuat §10.5 bisa ditegakkan** (*Perception ≠
> Interpretation ≠ Inference*): `steps: 8420` dan `energy: 0.62` tidak boleh
> duduk di tabel yang sama, sebab yang pertama terukur dan yang kedua
> disimpulkan — dan **B-15** ([#15](../../issues/15)) lahir justru karena
> keduanya tampak sama presisinya.

### L2 · Ingatan & konteks

| | **`events`** |
|---|---|
| menjawab | **apa yang terjadi, terurut, tepat sekali** |
| memiliki tabel | `events` |
| menerbitkan | — (ia **bus**-nya, bukan penerbitnya) |
| kata lokal | **`registry`** = schema registry event |
| 🛑 **TIDAK BOLEH** | menafsirkan, dan **tidak boleh menerima aliran mentah**. Uji admisinya di [`07`](07-EVENT-CONTRACTS.md) §3 — ia yang menutup **E-89** ([#74](../../issues/74)) |

| | **`memory`** |
|---|---|
| menjawab | **apa yang sistem ingat tentang orang ini** |
| memiliki tabel | `memories` |
| menerbitkan | `memory.*` |
| kata lokal | **`memory`** = ingatan tentang seseorang (di `embodiment` ia *procedural/skill memory* — keterampilan robot, bukan ingatan orang) |
| 🛑 **TIDAK BOLEH** | mengambil keputusan, dan **tidak boleh dibaca tanpa scope**. Lima sumbunya (`kind` · `scope` · `tier` · `modality` · `level`) tegak lurus — **H-16** ([#33](../../issues/33)) |

| | **`context`** |
|---|---|
| menjawab | **apa yang relevan SEKARANG** |
| memiliki tabel | **nihil** — ia satu-satunya konteks tanpa tabel, dan itu disengaja |
| menerbitkan | — |
| kata lokal | **`package`** = *context package* (`filtered · scoped · ranked · sanitized`) |
| 🛑 **TIDAK BOLEH** | menyimpan hasilnya. Dan sebaliknya: **tidak ada konteks lain yang boleh memeriksa izin baca** — pemeriksaannya **satu kali, di sini** (**H-19**, [#62](../../issues/62)) |

> ⚠️ **`context` lulus uji 4 pertanyaan meski tanpa tabel**, dan itu justru
> letak nilainya: sebuah konteks yang **memiliki satu-satunya jalan masuk** ke
> data orang tidak perlu memiliki data. Kalau ia punya tabel, ia akan menjadi
> cache — dan cache izin adalah cara izin basi sampai ke agent.

### L3 · Kesimpulan

| | **`intelligence`** |
|---|---|
| menjawab | **apa yang disimpulkan tentang orang ini** |
| memiliki tabel | `human_states` · `recommendations` · `recommendation_feedback` · `patterns` · `predictions` |
| menerbitkan | `insight.*` · `recommendation.*` · `prediction.*` |
| kata lokal | **`simulation`** = simulasi **perilaku** · **`planning`** = perencanaan **tugas** · **`registry`** = model registry |
| 🛑 **TIDAK BOLEH** | bertindak. Ia mengeluarkan **usul berangka**; yang mengeksekusi `agents`, lewat gerbang |

| | **`knowledge`** |
|---|---|
| menjawab | **apa yang benar, dan dari mana** |
| memiliki tabel | graf (Neo4j, V2+) · `ontology` · `provenance` · `evidence` |
| menerbitkan | `knowledge.*` |
| kata lokal | **`graph`** = graf pengetahuan **kausal** (di `spatial` ia *scene graph* **geometris**; di `agents` ia *agent graph* **struktural**) |
| 🛑 **TIDAK BOLEH** | menyimpan apa pun **tentang satu orang** — itu `memory`. Dan setiap klaim wajib membawa rantai provenans yang lengkap: `Transformation` dan `Policy` termasuk ([#135](../../issues/135)) |

| | **`world-model`** |
|---|---|
| menjawab | **keadaan dunia di luar orang ini** — dan ia **MENYIMPAN** |
| memiliki tabel | `world_entities` · `world_states` · `world_relationships` · `world_events` · `transitions` |
| menerbitkan | `world.*` |
| kata lokal | **`state`** = keadaan dunia · **`transition`** = model transisi kausal |
| 🛑 **TIDAK BOLEH** | menjalankan skenario, dan **tidak boleh memiliki `scenario/` maupun `counterfactual/`** — [K-2](../docs/KEPUTUSAN-DIDELEGASIKAN.md), menutup [#147](../../issues/147) |

| | **`simulation`** |
|---|---|
| menjawab | **apa yang terjadi kalau…** — dan ia **MENJALANKAN**, tidak menyimpan |
| memiliki tabel | **nihil yang durable.** Keluarannya selalu bisa dibangun ulang dari `world-model` + parameter + `seed` |
| menerbitkan | `simulation.*` |
| kata lokal | **`scenario`** · **`counterfactual`** · **`assumption`** — ketiganya **hanya** di sini |
| 🛑 **TIDAK BOLEH** | **mengubah data dunia nyata** (§12.16) — batas keras, ditegakkan CI, [`11`](11-PENEGAKAN.md) B-3 |

> 🔑 **`world-model` menyimpan, `simulation` menjalankan.** Itu
> [K-2](../docs/KEPUTUSAN-DIDELEGASIKAN.md), dan ia sekaligus memberi **B-24**
> ([#70](../../issues/70)) alamat yang selama ini hilang: sumber model transisi
> adalah `world-model/transition/`, bukan tempat lain.

### L4 · Tindakan

| | **`agents`** |
|---|---|
| menjawab | **siapa yang bertindak, atas kewenangan siapa** |
| memiliki tabel | `agents` · `agent_versions` · `agent_runs` · `agent_capabilities` · `agent_trust_scores` · `agent_messages` · `approvals` |
| menerbitkan | `agent.*` |
| kata lokal | **`simulation`** = 🛑 **dilarang di sini** — lihat §4 · **`registry`** = daftar agent · **`sandbox`** = isolasi runtime |
| 🛑 **TIDAK BOLEH** | (a) mengimpor `security/` (§8.42) · (b) melewati Action Gateway (§11.14) · (c) mengambil data sendiri — semua lewat `context` (**H-19**) |

| | **`tools`** |
|---|---|
| menjawab | **apa yang bisa dipanggil, dan berapa risikonya** |
| memiliki tabel | `agent_tools` (registry tool) |
| menerbitkan | `tool.*` |
| kata lokal | **`registry`** = daftar tool · **`sandbox`** = lingkungan uji tool |
| 🛑 **TIDAK BOLEH** | mendaftarkan tool **tanpa `risk_level`** — [K-12](../docs/KEPUTUSAN-DIDELEGASIKAN.md) aturan 8, ditolak validator, bukan oleh kebijakan tertulis |

### L5 · Dunia fisik

| | **`perception`** |
|---|---|
| menjawab | **apa yang tertangkap sensor** |
| memiliki tabel | **nihil di PostgreSQL.** Aliran mentah (CSI · point cloud · bingkai · audio) hidup di kelas penyimpanan lain — [`06`](06-DATA-ARCHITECTURE.md) §2 |
| menerbitkan | `perception.*` — **hanya sesudah diringkas** |
| kata lokal | **`state`** = `perception-state`, keadaan sensor (bukan keadaan manusia) |
| 🛑 **TIDAK BOLEH** | (a) menyimpulkan **niat** · (b) mengirim data mentah keluar perangkat (§15.29) · (c) menulis satu baris pun ke `events` sebelum lulus uji admisi |

| | **`spatial`** |
|---|---|
| menjawab | **di mana benda dan orang berada** |
| memiliki tabel | `spatial_maps` · `anchors` · `scene_graph` · `navigation_paths` · `people_tracks` |
| menerbitkan | `spatial.*` |
| kata lokal | **`navigation`** = mencari jalur di peta · **`graph`** = scene graph **geometris** |
| 🛑 **TIDAK BOLEH** | memperlakukan `Person` sebagai jenis objek yang sama dengan `Sofa` (§16.10 memberi `human` prioritas tertinggi), dan **tidak boleh menyimpan `MOVING_TO` sebagai pengukuran** — ia prediksi, wajib membawa `confidence` |

| | **`embodiment`** |
|---|---|
| menjawab | **apa yang menggerakkan benda fisik** |
| memiliki tabel | `robots` · `joints` · `missions` · `trajectories` · `emergency_events` |
| menerbitkan | `robot.*` · `mission.*` · `emergency.*` |
| kata lokal | **`planning`** = **motion** planning · **`simulation`** = **fisika** · **`memory`** = keterampilan (*procedural*) |
| 🛑 **TIDAK BOLEH** | mencapai perangkat keras tanpa melewati `Code → Simulation → Safety Test → Hardware` (§16.26) — batas keras, [`11`](11-PENEGAKAN.md) B-4 |

### L0 · Melintang — dan sengaja BUKAN lapisan

| | **`security`** |
|---|---|
| menjawab | **apa yang boleh** |
| memiliki | `safety` · `privacy` · `consent` · `audit` · `permissions` · `policies` · `trust` · `compliance` · `ethics` sebagai **submodul** — [K-9](../docs/KEPUTUSAN-DIDELEGASIKAN.md) keputusan 3 |
| kata lokal | **`kill`** = kill switch (manusia mematikan sistem) · **`sandbox`** = karantina |
| 🛑 **TIDAK BOLEH** | ada lebih dari satu pohon. **Selama ada 19 pohon keamanan, aturan §8.42 tidak bisa DINYATAKAN** — tidak ada satu `security/` untuk dirujuk |

| | **`governance`** |
|---|---|
| menjawab | **siapa yang memutuskan** |
| memiliki | Konstitusi §20.16 · Autonomy Contract · Risk Agent (punya **veto**, §14.13) |
| kata lokal | **`kill`** = `kill condition` sebuah kontrak |
| 🛑 **TIDAK BOLEH** | hidup **di dalam** pohon fase. Sudah terbukti **tiga kali** bahwa `governance/` di dalam pohon fase **tidak diwarisi** fase berikutnya ([#138](../../issues/138)) |

| | **`platform`** |
|---|---|
| menjawab | **apa yang membuat semuanya berjalan** |
| memiliki | runtime · observability · model-router · billing · job/queue · migrasi |
| kata lokal | **`session`** = sesi runtime · **`state`** = keadaan proses |
| 🛑 **TIDAK BOLEH** | memuat aturan domain. Kalau `platform` tahu apa itu *habit*, ia bukan platform |

> 🔑 **`security` menjawab APA YANG BOLEH; `governance` menjawab SIAPA YANG
> MEMUTUSKAN.** Itu sebabnya keduanya **tidak** digabung meski keduanya naik ke
> tingkat atas. Menggabungkannya berarti mesin yang menegakkan aturan dan badan
> yang menetapkan aturan hidup di satu modul — dan pemisahan itu justru seluruh
> isi Pasal 1 dan Pasal 10 Konstitusi.

---

## §4 Kamus tabrakan — kata yang artinya berbeda di konteks berbeda

**Ini tabel yang membuat [`03`](03-MONOREPO-FINAL.md) bisa memvonis 54 nama.**
Semuanya **sah**; yang tidak sah adalah memakai **nama direktori yang sama**
untuk keduanya.

| Kata | Konteks | Artinya | Nama direktori final |
|---|---|---|---|
| **simulation** | `intelligence` | perilaku manusia | `sim-behavior/` |
| | `embodiment` | fisika & tabrakan | `sim-physics/` |
| | *health* (P17) | fisiologi | `sim-physiology/` |
| | *civilization* (P20) · *global* (P18) | masyarakat & ekonomi | `sim-society/` |
| | `agents` | 🛑 **bukan simulasi sama sekali** — gladi bersih agent sebelum sertifikasi (`RED TEAM → SIMULATION → CERTIFICATION → SANDBOX`) | `evaluation/scenario-runs/` |
| **state** | `human-core` | keadaan manusia | `human-state/` |
| | `world-model` | keadaan dunia | `world-state/` |
| | `platform` | keadaan proses | `session-state/` |
| | `perception` | keadaan sensor | `perception-state/` ⁽¹⁾ |
| **planning** | `intelligence` · `agents` | perencanaan **tugas** | `planning/` |
| | `embodiment` | perencanaan **lintasan** | `motion-planning/` |
| **registry** | `agents` | daftar agent | `agents/registry/` |
| | `tools` | daftar tool | `tools/registry/` |
| | `events` | schema registry | `events/schema-registry/` |
| | `intelligence` | model registry | `model-registry/` ⁽¹⁾ |
| **graph** | `knowledge` | **kausal** | `knowledge/graph/` |
| | `spatial` | **geometris** | `spatial/scene-graph/` |
| | `agents` | **struktural** | `agents/agent-graph/` |
| **memory** | `memory` | ingatan tentang orang | `memory/` |
| | `embodiment` | keterampilan robot | `embodiment/skills/` |
| **sandbox** | `agents` | isolasi runtime | `agents/sandbox/` |
| | `tools` | uji tool | `tools/test-harness/` |
| | `security` | karantina | `security/quarantine/` |
| **kill** | `security` | mematikan **sistem** | `security/kill-switch/` |
| | `agents` | watchdog menghentikan **satu agent** | `agents/watchdog/` |
| | `governance` | syarat berakhirnya **kontrak** | `governance/contracts/` |
| **research** | *research* (P5) | **mencari cara** | `research/` |
| | `intelligence` | **menjalankan di produksi** | 🛑 tidak punya `research/` |
| **navigation** | `spatial` | jalur di peta | `spatial/navigation/` |
| | `embodiment` | 🛑 **tidak punya sendiri** — ia MEMAKAI `spatial` | — |

⁽¹⁾ dua nama itu **sudah** dipakai naskah dalam bentuk berkualifikasi
(`perception-state/`, `model-registry/`, `experiment-registry/`) — jadi
konvensinya bukan usul baru, melainkan yang sudah dipraktikkan sebagian.

> ⭐ **Baris `agents` di bawah *simulation* adalah temuan berkas ini, dan yang
> paling berakibat dari kesembilan baris.** §11.50 menaruh `simulation/`
> **bersebelahan dengan `risk/`, `approvals/`, dan `sandbox/`** — yaitu di jalur
> eksekusi tindakan. Ia bukan simulator dunia; ia **satu tahap dalam pipa
> sertifikasi** (§11 red-team). Selama namanya `simulation/`, ada dua
> kemungkinan yang keduanya buruk: seseorang menyambungkannya ke mesin simulasi
> Phase 12, atau seseorang mengira jalur tindakan sudah punya simulator padahal
> yang ada cuma harness uji.
> 💡 **Cara menemukannya bukan membaca namanya, melainkan membaca TETANGGANYA
> di pohon yang sama.**

---

## §5 Yang diperiksa dan ternyata BUKAN tabrakan

⚠️ Ditulis di sini supaya pembaca berikutnya tidak “memperbaikinya”. Enam dari
sepuluh temuan pemindai duplikasi sebelumnya adalah positif palsu jenis ini
([`../docs/SENSUS-MODUL.md`](../docs/SENSUS-MODUL.md) Tabel C).

> 🔑 **Aturan: nama di bawah induk yang JENISNYA BERBEDA bukan duplikat.**

| Nama | Muncul di | Vonis |
|---|---|---|
| `health/` | `tools/` · `prompts/` · `events/` · modul domain | ✅ **sah** — empat **faset** satu domain, bukan empat salinan |
| `fashion/` · `lifestyle/` | idem | ✅ sah |
| `agents/` | `agents/` (kode) · `prompts/agents/` · `docs/agents/` | ✅ sah |
| `security/` | `platform/security/` · `tests/security/` · `docs/security/` | ✅ sah |
| `memory/` | `benchmarks/memory/` · `agent-sdk/memory/` | ✅ sah — *tolok ukur untuk* memory, dan *permukaan SDK untuk* memory |
| `docs/` · `api/` | beberapa pohon | ✅ sah — faset |

⇒ Dari **128** nama yang dipakai >1 pohon, yang benar-benar bertabrakan sebagai
**konsep** adalah yang ada di §4. Sisanya diselesaikan mekanis oleh uji
naik-turun di [`03`](03-MONOREPO-FINAL.md).

---

## §6 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Jumlah konteks | **17** — 11 domain + 3 dunia fisik + 3 melintang |
| Konteks yang menjawab keempat pertanyaan §1 | **17 dari 17** |
| Konteks tanpa tabel | **3** — `context`, `simulation`, `perception`; ketiganya disengaja dan alasannya ditulis |
| Tabel dimiliki >1 konteks | **NIHIL** — diperiksa terhadap [`06`](06-DATA-ARCHITECTURE.md) |
| Awalan event dimiliki >1 konteks | **NIHIL** — diperiksa terhadap [`07`](07-EVENT-CONTRACTS.md) |
| Kata di kamus §4 tanpa nama direktori final | **NIHIL** |
| Pohon keamanan | **1** (+ `governance/` berdiri sendiri) — turun dari **19** |
