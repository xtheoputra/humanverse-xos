# 04 — Dependency Graph & Batas Keras

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“dependency graph”* naskah 24. Memberi bentuk kanonik bagi
> [#93](../../issues/93) · [#106](../../issues/106) · [#111](../../issues/111) ·
> [#125](../../issues/125) · [#140](../../issues/140) — enam belas catatan
> *“rantai tanpa gerbang”* yang selama ini tidak punya rantai pembanding.

---

## §1 Graf ketergantungan antar-konteks

Panah berarti **“boleh mengimpor”**. Tidak ada panah = **tidak boleh**.
Graf ini **asiklik**; siklus adalah kegagalan CI, bukan perdebatan.

```
                    ┌──────────────────────────────────────────┐
   MELINTANG        │  security ◄── governance                 │
                    │      ▲            ▲                      │
                    │      │  (hanya lewat gateway & policy)    │
                    └──────┼────────────┼──────────────────────┘
                           │            │
   L0  platform  ─────────►┴────────────┘        ◄── boleh dipakai SEMUA
        ▲
        │
   L1  services/identity ◄──────────── semua konteks (cek subjek izin)
        ▲
        │
   L1  services/* (human-core, domain vertikal)
        │   └──── hanya lewat EVENT antar-sesamanya
        ▼
   L2  events ──► memory ──► context
                                │
                                ▼
   L3  knowledge ◄── intelligence ◄── world-model ◄── simulation
                          │                 ▲              ▲
                          └─────────────────┴──────────────┘
                                │
                                ▼
   L4  agents ──► tools ──► platform/gateway
                                │
                                ▼
   L5  perception ──► spatial ──► embodiment
                                     │
                                     ▼
                              embodiment/safety-kernel   (di TEPI)
```

### Aturan yang menghasilkan arah panahnya

| # | Aturan | Asal | Kenapa arahnya begitu |
|---|---|---|---|
| 1 | modul hanya boleh mengimpor **pintu keluar** modul lain, tidak pernah berkas dalamnya | [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) aturan 1 | batas yang tidak ditegakkan alat dilanggar dalam dua minggu |
| 2 | konteks domain **tidak boleh** saling mengimpor — komunikasinya lewat **event** | `spec/06` aturan 3 | kalau `habits` boleh memanggil `checkins` langsung, keduanya menyatu sebulan dan pemisahan jadi mustahil |
| 3 | **`agents` boleh membaca; tidak ada yang mengimpor `agents`** | `spec/06` aturan 4 | agent adalah **konsumen** arsitektur, bukan bagiannya. Kalau `intelligence` mengimpor `agents`, kesimpulan mulai bergantung pada siapa yang memanggilnya |
| 4 | **`agents` tidak mengambil data sendiri** — semua lewat `context` | **H-19** ([#62](../../issues/62)) | izin dibaca **satu kali di satu tempat**. Dua tempat = dua tafsir |
| 5 | `simulation` boleh **membaca** `world-model`, tidak pernah **menulis** | [K-2](../docs/KEPUTUSAN-DIDELEGASIKAN.md) | `world-model` menyimpan, `simulation` menjalankan |
| 6 | `embodiment` **memakai** `spatial`, tidak menyalinnya | [`03`](03-MONOREPO-FINAL.md) §4 | *“robot tidak bisa bergerak dengan aman tanpa SpatialOS”* — §19 penutup |
| 7 | `platform` **tidak boleh** memuat aturan domain | [`02`](02-BOUNDED-CONTEXT.md) | kalau `platform` tahu apa itu *habit*, ia bukan platform |
| 8 | **tak satu pun** konteks mengimpor `security/` — ia dipanggil lewat **gateway** dan **policy engine** | §8.42 | lihat §2 B-1 |

---

## §2 Enam batas keras

> 🔑 **Batas keras** = aturan yang kalau dilanggar, seluruh lapisan di atasnya
> berhenti berarti. Keenamnya **wajib punya pemeriksaan CI**; yang tidak punya
> penegak tidak dihitung ada. Penegaknya di [`11`](11-PENEGAKAN.md).

| | Batas | Asal | Kalau dilanggar |
|---|---|---|---|
| **B-1** | **Kode agent tidak boleh mengimpor `security/`** | §8.42 | agent bisa membaca — dan akhirnya memanggil — mesin yang menilai dirinya. Control Plane dan Data Plane menyatu |
| **B-2** | **Agent tidak boleh melewati Action Gateway** | §11.14 | seluruh rantai gerbang di §4 menjadi opsional; jalur pintas selalu ditemukan |
| **B-3** | **Simulasi tidak boleh mengubah data dunia nyata** | §12.16 | *“bagaimana kalau…”* menjadi *“sudah terjadi”* |
| **B-4** | **`Code → Simulation → Safety Test → Hardware`** — urutan wajib | §16.26 | kode yang belum pernah disimulasikan menggerakkan benda di dekat orang |
| **B-5** | **Kebijakan lokal boleh MEMPERKETAT, tidak pernah MELONGGARKAN** | Konstitusi §20.16 ⁽¹⁾ | Konstitusi berhenti menjadi lapisan tertinggi, dan sembilan pasal lain kehilangan penegakannya |
| **B-6** | **Tepat SATU pohon `security/`** | [K-9](../docs/KEPUTUSAN-DIDELEGASIKAN.md) keputusan 3 | B-1 tidak bisa **dinyatakan** — tidak ada satu `security/` untuk dirujuk |

⁽¹⁾ 🔧 **B-5 adalah keputusan saya.** §20.16 menyatakan Konstitusi sebagai
*“governance layer tertinggi”* tetapi **tidak menyatakan apakah `local policy`
§20.11 bisa melonggarkannya** — itu salah satu dari tiga hal yang audit catat
belum ada. Saya memilih arah yang **jatuh ke sisi aman kalau seseorang lupa
mengisinya**: kebijakan yang tidak menyebut apa-apa mewarisi Konstitusi apa
adanya, dan yang menyebut sesuatu hanya bisa menambah pembatas.
**Cara membalikkan:** satu baris yang menyatakan pengecualian, lengkap dengan
siapa yang boleh memberikannya.

> 💡 **Pertanyaan yang menghasilkan B-5 sama dengan yang menghasilkan
> [K-12](../docs/KEPUTUSAN-DIDELEGASIKAN.md) dan [K-10](../docs/KEPUTUSAN-DIDELEGASIKAN.md):**
> *kalau seseorang LUPA mengisinya, ke sisi mana ia jatuh?*

### 🛑 B-4 punya satu konsekuensi yang belum pernah ditulis

§12.16 dirumuskan untuk **menjaga data**: *simulasi tidak boleh mengubah dunia
nyata*. §16.26 dirumuskan untuk **menjaga orang**: *simulasi tidak boleh
dilewati*. **Keduanya menyebut simulasi, tetapi arahnya berlawanan** — yang satu
membatasi apa yang boleh keluar dari simulasi, yang lain mewajibkan sesuatu
masuk ke dalamnya.

⇒ Keduanya harus ditegakkan **terpisah**. Sebuah pemeriksaan yang hanya
memastikan simulasi terisolasi akan **meloloskan** kode robot yang tidak pernah
disimulasikan sama sekali.

---

## §3 Rantai tindakan kanonik — satu bentuk untuk seluruh repo

Empat rantai keselamatan ditulis dengan jumlah gerbang berbeda: **9** (§11.14) ·
**11** (§14.20, tapi kehilangan tiga) · **5** (§15.22) · **5** (§16.18). Tidak
ada satu pun yang bisa dipakai untuk memeriksa yang lain, sebab tak ada yang
kanonik.

⭐ **§20.35 memberi bentuk yang lebih baik daripada semua usul sebelumnya:
bukan menambah gerbang ke satu rantai, melainkan MEMECAH rantainya jadi dua
cabang** — sehingga analisis tetap murah, dan tindakan tidak punya jalan pintas.

```
                   ┌──► ANALYSIS ─────────────────────────────────► jawaban
                   │      (CONTEXT + AUDIT saja)                       │
 INTENT ──► CONTEXT┤                                                   │
                   │                                                   │
                   └──► ACTION                                         │
                          │                                            │
        POLICY ─► CONSENT ─► RISK ─► IMPACT ─► DELIBERATE ─►           │
        CONFIRMATION ─► RATE LIMIT ─► GATEWAY ─► EXECUTE               │
                                          │                            │
                                      OVERRIDE  (berlaku SELAMA aksi)  │
                                          │                            │
                                          ▼                            ▼
                                        AUDIT ◄───── menampung KEDUA cabang
```

| # | Gerbang | Menjawab | Asal |
|---|---|---|---|
| 1 | `CONTEXT` | data apa yang boleh dilihat — **izin baca diperiksa di sini, sekali** | **H-19** §9.31 |
| 2 | `POLICY` | apakah tindakan ini diizinkan aturan | **H-18** §9.29 |
| 3 | `CONSENT` | apakah pengguna pernah memberi izin untuk **tujuan** ini | §11.14 · **B-22** ([#59](../../issues/59)) |
| 4 | `RISK` | berapa **R**-nya — **gerbang, bukan suku penjumlahan** | §8.17 · **B-29** ([#96](../../issues/96)) |
| 5 | `IMPACT` | **siapa yang terkena selain penggunanya** | §20.35 · §20.17 |
| 6 | `DELIBERATE` | pertimbangan sebelum keputusan, untuk yang kolektif | §20.38 |
| 7 | `CONFIRMATION` | manusia menekan setuju — **wajib mulai R3** | **H-15** ([#5](../../issues/5)) |
| 8 | `RATE LIMIT` | berapa kali dalam jendela apa — **diikat `trace_id`, bukan agent** | §11.14 · §14.57 |
| 9 | `GATEWAY` | satu-satunya pintu keluar (**B-2**) | §11.14 |
| 10 | `EXECUTE` | — | — |
| 11 | `OVERRIDE` | Pause · Resume · Cancel · Revoke · Kill · **Rollback** — berlaku **selama** aksi | §11.61 · Pasal 10 |
| 12 | `AUDIT` | jejak untuk **kedua** cabang | Pasal 4 · §20.35 |

> 🔑 **Butir 8 memakai `trace_id`, dan itu bukan detail.** §14.25 menunjukkan
> `10 agents × 5 notif = 50 interruptions` — pagu **per-agent** berhenti berarti
> apa-apa begitu ada banyak agent. Hal yang sama berlaku bagi uang (§14.40:
> A bayar B, B bayar C, tiap transaksi di bawah pagu, **tak ada yang melihat
> totalnya**). Anggaran yang benar diikat pada **jejak**, bukan pada pelaku.

> ⭐ **Butir 11 lebih kuat daripada butir 7, dan itu perlu dinyatakan.**
> Konfirmasi berlaku **sebelum** aksi; override berlaku **selama** aksi. Sebuah
> sistem yang punya konfirmasi tetapi tidak punya override tidak bisa
> menghentikan apa pun yang sudah berjalan — dan `Rollback` sudah pernah
> **hilang** dari Safety Kernel §13.34 sesudah §11.61 memberikannya
> ([#91](../../issues/91)).

### Gerbang mana menyala pada tingkat R berapa

| Gerbang | R0 | R1 | R2 | R3 | R4 |
|---|---|---|---|---|---|
| `CONTEXT` · `POLICY` · `RISK` · `GATEWAY` · `OVERRIDE` · `AUDIT` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `CONSENT` | — | ✅ | ✅ | ✅ | ✅ |
| `RATE LIMIT` | — | ✅ | ✅ | ✅ | ✅ |
| `IMPACT` | — | — | ✅ | ✅ | ✅ |
| `DELIBERATE` | — | — | — | ✅ | ✅ |
| **`CONFIRMATION`** | — | — | — | ✅ **wajib** | — |
| **hasil** | jalan | jalan | jalan | **tunggu manusia** | 🛑 **DENY** |

- **R4 = `DENY` bawaan**, didefinisikan ***irreversible*** — **H-21**
  ([#67](../../issues/67)). Tidak ada baris `CONFIRMATION` untuk R4 sebab tidak
  ada yang dieksekusi. *“Ask Every Time”* **bukan** pengganti penolakan
  ([#90](../../issues/90)).
- **Kapabilitas yang menyentuh pihak ketiga = minimum R3** —
  [K-1](../docs/KEPUTUSAN-DIDELEGASIKAN.md). ⇒ tiap tindakan yang akibatnya
  sampai kepada orang lain **selalu** melewati `CONFIRMATION`. Itu mekanisme
  yang membuat K-1 nyata, bukan kalimat.
- **`R` dan `L` adalah dua tangga.** `risk_level: R2` + `autonomy.max_level: L2`
  hidup berdampingan di satu manifest (**H-21**). Properti agent adalah
  **`max_risk`**, bukan `risk` ([#97](../../issues/97)) — satu angka tak bisa
  menjadi keduanya.

### 🛑 Dua rantai yang masih tanpa gerbang — dan sengaja tidak saya isi

Sensus rantai menemukan **20 dari 36** rantai tindakan sudah punya gerbang; tiga
yang belum menggerakkan benda fisik. Satu sudah ditutup
([K-7](../docs/KEPUTUSAN-DIDELEGASIKAN.md) memberi `Permission` pada §15.15).

| Rantai | Keadaan |
|---|---|
| **§16.5** `Human Goal → World Model → Motion Planner → Joint Controller → Execution` | 🛑 **milik pemilik** — humanoid, benda yang bisa melukai orang |
| **§16.7** `Target → Obstacle Map → Trajectory → Collision Check → Optimization → Execution` | 🛑 **milik pemilik** — dan `Optimization` **sesudah** `Collision Check` berarti lintasan yang sudah diperiksa **berubah lagi** sesudahnya |

⚠️ Yang bisa dinyatakan tanpa memutuskannya: **keduanya harus melewati §3
sebelum `Execution`**, dan §16.7 harus menukar urutan dua simpul terakhirnya.
Gerbang mana yang tepat untuk gerak sendi — dan berapa angkanya
([#112](../../issues/112): jarak henti · latensi reaksi · batas gaya · personal
space · kecepatan per zona) — bukan keputusan gaya, dan bukan milik saya.

---

## §4 Policy berbasis KEMAMPUAN, bukan berbasis PERANGKAT

**Mekanisme untuk [#104](../../issues/104) (C-23) — tanpa memutuskan butir C-nya.**

§15.23 memberi `bedroom: {camera: false, audio: false}`. Itu daftar
**PERANGKAT**. WiFi sensing (§15.4) tidak butuh kamera maupun mikrofon, menembus
dinding, dan mendeteksi napas — ⇒ sakelar itu mematikan sensor yang salah, dan
**setiap sensor baru otomatis diizinkan sampai ada yang ingat menambahkannya.**

🔧 **Bentuk yang menutupnya secara struktural** — memakai mekanisme yang sudah
ada di repo ini (`deny` eksplisit §14.21 + default deny §14.37):

```yaml
room: bedroom
allow:                      # yang TIDAK disebut, DITOLAK
  - presence.count          # berapa orang, tanpa identitas
deny:                       # eksplisit, mengalahkan allow di mana pun
  - vitals.*                # termasuk breathing, heart-rate
  - identity.*
  - imaging.*
```

| Aturan | Kenapa |
|---|---|
| policy menyebut **kemampuan**, bukan perangkat | sensor baru **tidak** otomatis diizinkan |
| yang tidak disebut → **ditolak** | kelalaian jatuh ke sisi aman |
| `deny` mengalahkan `allow` **di mana pun** | ruangan yang menolak sebuah kemampuan menolaknya **juga dari luar ruangan itu** — kalau tidak, sensor tembus dinding di koridor membatalkan seluruh policy kamar |

🛑 **Yang TETAP milik pemilik:** apakah `through-wall sensing` dan `breathing
detection` **dibangun sama sekali** ([#102](../../issues/102)) — itu menyentuh
orang di properti tetangga, yang tidak pernah menyetujui apa pun dan tidak bisa
tahu. Berkas ini hanya memastikan bahwa apa pun keputusannya, **sakelarnya
mengikat**.

---

## §5 Rute API — satu segmen pertama, satu konteks

Butir yang **tidak** disebut naskah 24, dan celahnya sudah tercatat
([`../docs/PETA-FASE.md`](../docs/PETA-FASE.md)).

| Aturan | Isi |
|---|---|
| awalan | **`/v1`** — [K-8](../docs/KEPUTUSAN-DIDELEGASIKAN.md); 111 rute naskah lawan nol memakai `/api/v1` |
| segmen pertama | **wajib** nama bounded context, atau domain yang dimiliki satu konteks |
| kepemilikan | satu rute dimiliki **tepat satu** konteks — sama seperti tabel |
| tindakan | rute yang menyebabkan tindakan **wajib** melewati §3; tidak ada rute yang menulis langsung ke perangkat |

⚠️ **Pengecualian yang harus dinyatakan:** `POST /v1/robot/emergency-stop`
(§16.29) berjalan lewat HTTP, dan HTTP **hilang saat jaringan putus** — yaitu
pemicu darurat nomor empat §16.20. ⇒ rute itu **kenyamanan, bukan pengaman**.
Pengamannya ada di `embodiment/safety-kernel/` di tepi
([`03`](03-MONOREPO-FINAL.md) §5).

---

## §6 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Graf §1 asiklik | ✅ — diperiksa `madge --circular` di CI |
| Batas keras | **6**, dan **6 punya penegak** di [`11`](11-PENEGAKAN.md) |
| Gerbang di rantai kanonik | **12** — memuat seluruh gerbang dari keempat rantai naskah |
| Gerbang yang hilang dari §14.20 (`Consent`·`Rate Limit`·`Confirmation`) | ✅ **ketiganya ada** |
| Cabang ANALYSIS membebani gerbang | **NIHIL** kecuali `CONTEXT` + `AUDIT` |
| Rantai tindakan tanpa gerbang | **2** — §16.5 · §16.7, keduanya ditandai milik pemilik |
| Rute tanpa konteks pemilik | **NIHIL** — aturan §5 |
