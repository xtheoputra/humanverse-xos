# Gerbang Skema — tidak ada yang mengunci Engineering Spec

> ⚠️ **Bukan kata pemilik.** Berkas ini merekonsiliasi dua dokumen di repo ini
> yang **saling bertentangan** tentang apakah pekerjaan terhalang.
>
> 🔴 **Versi pertama berkas ini (7 Sep 2026, commit `58d026c`) SALAH** dan sudah
> diganti seluruhnya. Lihat [bagian terakhir](#koreksi-atas-versi-pertama-berkas-ini).

---

## Dua dokumen, dua jawaban yang berlawanan

| Dokumen | Klaimnya |
|---|---|
| **`README.md`** (akar) | *"Yang **masih mengunci Engineering Spec** — karena keempatnya menentukan skema basis data: A-19 · E-16..E-18 · E-39 · E-37."* |
| **`spec/README.md`** | *"**Artinya V0 bisa dimulai sekarang.** Yang tersisa sebagai penghambat nyata hanyalah **#3** dan **#20** — keduanya bukan soal skema."* |

Yang benar adalah **`spec/README.md`**. Ia bahkan punya bagian tersendiri —
*"Empat keputusan yang mengunci skema — dan cara saya menanganinya"* — yang
menyelesaikan keempatnya satu per satu, dan alasannya bisa diperiksa langsung di
DDL.

Yang dibaca orang lebih dulu adalah yang salah.

---

## Bukti di DDL, bukan di prosa

### #32 / E-37 — skala skoring: **sudah dipilih**

`spec/01-DATABASE-SCHEMA.md`:

```sql
score            numeric(4,3) CHECK (score BETWEEN 0 AND 1),
score_breakdown  jsonb NOT NULL DEFAULT '{}'::jsonb,
confidence       numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
scoring_version  text NOT NULL DEFAULT 'v1',
```

**`0–1`, ditegakkan `CHECK`, dengan `confidence` bersanding dan `scoring_version`
supaya rumusnya boleh berubah tanpa migrasi.** Alasan yang ditulis
`spec/README.md` tepat: skala 100-poin dan persen **lossless** dikonversi ke
0–1; sebaliknya tidak.

Yang **masih** terbuka dari E-37 bukan soal penyimpanan, melainkan **rumusnya**:
§11 menyebut 7 komponen sementara contohnya memakai 5, dan belum ada bobot. Itu
tidak menghalangi satu baris DDL pun — `score_breakdown jsonb` menampung bentuk
apa pun.

### #2 / A-19 — model angka pengguna: **sengaja tidak diputuskan**

```sql
CREATE TABLE human_states (
  ...
  metrics       jsonb NOT NULL DEFAULT '{}'::jsonb,
  model_version text NOT NULL,
  UNIQUE (user_id, for_date, model_version)
);
```

Bukan tujuh kolom tetap. Tiap metrik menyimpan
`{value, confidence, evidence_count, model_version}` sesuai Confidence Layer.
`UNIQUE` yang menyertakan `model_version` berarti **enam model boleh hidup
berdampingan** — termasuk *Energy Budget* §13.15 yang baru datang di naskah 17.

Model mana pun yang akhirnya dipilih **tidak butuh migrasi**. Itu bukan
penundaan; itu keputusan bahwa pertanyaannya belum matang dan skemanya tidak
boleh menyandera jawabannya.

### #7 / E-16..E-18 — model graf: **tidak menyentuh V0**

`spec/01` punya **nol tabel graf** — dan itu disengaja. V0 adalah *modular
monolith* PostgreSQL + Redis; **Neo4j baru masuk V2**.

Butir ini memblokir **V2**, bukan spesifikasi ini.

### #33 / E-39 — memory: **ditutup**

Issue **#33 sudah CLOSED**, dan jawabannya dua kolom karena keduanya menjawab
hal berbeda: `kind` = *bagaimana* memori disimpan & diambil; `scope` = *siapa*
boleh membacanya. Naskah 13 §9.7 menambahkan sumbu ketiga `tier` → **H-16**.

---

## Penghambat V0 yang sebenarnya

Keduanya **bukan soal skema**, dan keduanya butuh tangan pemilik:

| Issue | Isi | Kenapa hanya pemilik |
|---|---|---|
| **[#3](../../issues/3)** — A-17 | Siapa yang mengerjakan V0 dalam 4–6 minggu, sesudah cakupannya naik jadi 12 fitur | Soal waktu dan orang, bukan teknis |
| **[#20](../../issues/20)** — C-5 | Cek ketersediaan merek, domain, dan nama paket `HumanVerse XOS` | Butuh pencarian merek dan pembelian |

---

## Diperiksa ulang 9 September 2026: delapan sensus baru, **nol penghambat skema baru**

Sesi 25 menerbitkan delapan pengukuran lintas naskah
([`SENSUS-MODUL`](SENSUS-MODUL.md) · [`PETA-FASE`](PETA-FASE.md) ·
[`SENSUS-EVENT`](SENSUS-EVENT.md) · [`SENSUS-AGENT`](SENSUS-AGENT.md) ·
[`SENSUS-TABEL`](SENSUS-TABEL.md) · [`SENSUS-TANGGA`](SENSUS-TANGGA.md) ·
[`SENSUS-RANTAI`](SENSUS-RANTAI.md)), dengan angka-angka besar: 247 nama tabel,
128 nama event, 59 agent. **Tak satu pun menambah penghambat bagi V0**, dan
itu perlu dinyatakan supaya tidak terbaca sebaliknya.

| Temuan | Menyentuh V0? |
|---|---|
| **247 nama tabel** ([#151](../../issues/151)) | ❌ `spec/01` tetap **23 tabel**. 139 nama baru lahir di Phase 14–20; **nol dibutuhkan V0**. ⭐ Sensus itu justru **memverifikasi ulang provenans `spec/01`** — tepat 19 nama dari naskah 5, dan tepat tiga (`events`·`agent_tools`·`human_states`) yang memang bukan dari naskah |
| **128 nama event PascalCase** ([#149](../../issues/149)) | ❌ `spec/03` tetap 22 event dua segmen. Yang 128 itu milik Phase 10–20 |
| **59 nama agent** ([#150](../../issues/150)) | ❌ V0 memakai 4 agent; 44 dari 59 nama hanya pernah disebut sekali |
| **B-39 pesan di R2** ([#152](../../issues/152)) | ❌ untuk V0 — [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) menyatakan **V0 tidak punya satu pun tool level 3 atau 4**, jadi tidak ada pengiriman pesan ke pihak ketiga. ⚠️ **Mendesak untuk Phase 11 ke atas**, dan berdiri sendiri dari [#139](../../issues/139) |
| **Tiga rantai tanpa gerbang** ([#153](../../issues/153)) | ❌ §15.15 · §16.5 · §16.7 — Phase 15 dan 16 |
| **Awalan API** ([#38](../../issues/38)) | ✅ **diperbaiki** — [`../spec/04`](../spec/04-API-CONTRACTS.md) kini `/v1`, sejalan standar pemilik dan 111 rute naskah. Endpoint ditulis tanpa awalan, jadi perubahannya satu baris |

⇒ **Penghambat V0 tetap dua, dan tetap bukan soal skema:
[#3](../../issues/3) dan [#20](../../issues/20).**

> 💡 Ini penerapan aturan di bagian bawah berkas ini kepada diri sendiri:
> **sebelum menyatakan sesuatu terhalang, buka berkas yang paling berkepentingan
> membantahnya.** Delapan pengukuran dengan angka besar mudah terbaca sebagai
> delapan penghambat baru; diperiksa satu per satu terhadap `spec/`, tak satu
> pun menyentuh V0.

---

## Koreksi atas versi pertama berkas ini

Versi pertama menyimpulkan **"TIGA pertanyaan tersisa, bukan empat"** dan
menyusun usul untuk ketiganya. Kesimpulan itu **terlalu tinggi**, dan usulnya
menjawab pertanyaan yang **sudah dijawab**.

Sebabnya bisa disebut persis: saya memeriksa `99-CATATAN-AUDIT.md` dan
`README.md`, **tetapi tidak memeriksa `spec/README.md`** — berkas yang seluruh
tugasnya justru menjawab pertanyaan itu. Dua dari tiga usul saya
(`0–1` untuk skor, dan menampung banyak model tanpa migrasi) ternyata **sudah
ada di DDL**, ditulis lebih dulu dan dengan alasan yang lebih baik.

Ini kesalahan yang bentuknya sama persis dengan yang saya temukan di
`README.md`: **percaya pada daftar ringkasan alih-alih memeriksa sumbernya.**
Saya menemukannya di dokumen orang lain lalu mengulanginya di dokumen sendiri,
dalam sesi yang sama.

Aturan yang layak dipegang sesudah ini: **sebelum menyatakan sesuatu terhalang,
buka berkas yang paling berkepentingan membantahnya.** Di repo ini, untuk
apa pun yang menyangkut skema, berkas itu adalah `spec/`.
