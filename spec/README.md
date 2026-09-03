# Engineering Specification v1.0 — HumanVerse XOS

> ⚠️ **Berkas di folder ini BUKAN kata pemilik.** Ini hasil kerja engineering
> yang diturunkan dari enam naskah di [`../docs/`](../docs/). Berkas naskah
> `01`–`98` tetap murni; setiap keputusan teknis di sini bisa ditelusuri ke
> naskah asalnya, dan setiap hal yang **saya putuskan sendiri** ditandai
> **🔧 usulan** — pemilik boleh membatalkannya.

Lapisan **04. Engineering Specification** dari peta 14 lapisan
([`../docs/98`](../docs/98-PETA-14-LAPISAN-ENGINEERING.md)).

**Cakupan: V0 saja.** V0 adalah satu-satunya lingkup tertutup yang pernah
ditetapkan pemilik (naskah 5 §29–§32). Tabel untuk V1+ **tidak** ditulis di
sini kecuali dibutuhkan V0 — menulisnya sekarang berarti menebak.

---

## Isi

| Berkas | Isi |
|---|---|
| [`01-DATABASE-SCHEMA.md`](01-DATABASE-SCHEMA.md) | DDL PostgreSQL lengkap — **23 tabel**, tipe, PK, FK, index, constraint |
| [`02-ERD.md`](02-ERD.md) | Relasi antar tabel + aturan kepemilikan data |
| [`03-EVENT-CONTRACTS.md`](03-EVENT-CONTRACTS.md) | Envelope, versi skema, idempotensi, 21 event + payload |
| [`04-API-CONTRACTS.md`](04-API-CONTRACTS.md) | Endpoint REST V0, request/response, kode galat |
| [`05-AGENT-CONTRACTS.md`](05-AGENT-CONTRACTS.md) | Manifest schema, tool registry, permission & risk |
| [`06-MODULE-BOUNDARIES.md`](06-MODULE-BOUNDARIES.md) | Batas modul di dalam modular monolith + aturan ketergantungan |
| [`07-BACKLOG-V0.md`](07-BACKLOG-V0.md) | Backlog 7 sprint, satu tugas per baris untuk AI coding agent |

---

## Empat keputusan yang mengunci skema — dan cara saya menanganinya

Empat issue terbuka (#2, #7, #32, #33) seharusnya memblokir spesifikasi ini.
**Tiga di antaranya ternyata tidak perlu diputuskan sekarang** — skemanya bisa
dirancang supaya menampung kedua kemungkinan tanpa biaya. Satu lagi ternyata
tidak menyentuh V0 sama sekali.

| Issue | Kelihatannya memblokir | Kenyataannya |
|---|---|---|
| **#33** memory: 6 jenis atau nama scope? | kolom tabel `memories` | 🔧 **Keduanya, karena keduanya menjawab hal berbeda.** `kind` = *bagaimana* memori disimpan & diambil. `scope` = *siapa* boleh membacanya (dipakai permission engine). Dua kolom, konflik bubar. |
| **#32** tiga skala skor | kolom `recommendations.score` | 🔧 **Simpan 0–1 `numeric(4,3)` + `scoring_version` + `score_breakdown jsonb`.** Skala 100-poin dan persen keduanya lossless dikonversi ke 0–1; sebaliknya tidak. Rumus boleh berubah tanpa migrasi. |
| **#2** lima model angka pengguna | kolom `human_states` | 🔧 **`metrics jsonb`, bukan 7 kolom tetap.** Tiap metrik menyimpan `{value, confidence, evidence_count, model_version}` sesuai Confidence Layer (naskah 5 §19). Model mana pun yang akhirnya dipilih tidak butuh migrasi. |
| **#7** model graf | isi Neo4j | ✅ **Tidak menyentuh V0.** V0 adalah *modular monolith* dengan PostgreSQL + Redis (naskah 5 §1, §32 Sprint 0). Neo4j baru masuk V2. Butir ini memblokir **V2**, bukan spesifikasi ini. |

> **Artinya V0 bisa dimulai sekarang.** Yang tersisa sebagai penghambat nyata
> hanyalah **#3** (12 fitur & 7 sprint dalam 4–6 minggu) dan **#20** (cek
> merek) — keduanya bukan soal skema.

---

## Prinsip yang dipegang di seluruh spesifikasi

| # | Prinsip | Asal |
|---|---|---|
| 1 | **Semua waktu `timestamptz`, disimpan UTC.** Zona waktu pengguna ada di `profiles.timezone`. | wajib untuk pola harian (naskah 5 §7) |
| 2 | **Kunci utama `uuid`**, bukan serial — supaya klien bisa membuat id luring. | rencana offline (bagian D audit) |
| 3 | **Event adalah sumber kebenaran perilaku**; tabel domain adalah proyeksi yang boleh dibangun ulang. | naskah 5 §7–§8 |
| 4 | **Setiap taksiran membawa `confidence` + `evidence_count`.** | Confidence Layer §19 |
| 5 | **Hak hapus nyata**: `deleted_at` untuk pembatalan cepat, dan prosedur hard-delete tertulis. Jejak audit menyimpan *metadata*, bukan isi. | §26 & §24, butir C-9 |
| 6 | **Tidak ada tabel tanpa `user_id`** kecuali katalog sistem — menyiapkan Row-Level Security. | §25 Data Access Policy |
| 7 | **Nol tabel untuk fitur yang tidak ada di V0.** | §29 *"Itu saja."* |

---

## Yang sengaja TIDAK ada di sini

`wardrobe_items` · `outfits` · `sleep_records` · `workouts` · `skills` ·
`projects` · `notifications` — semuanya disebut di naskah 5 §5 sebagai isi
PostgreSQL, tetapi **tidak satu pun ada di V0** (§29, §31). Menulis skemanya
sekarang berarti mengunci tebakan. Ditulis nanti di Engineering Spec V2.
