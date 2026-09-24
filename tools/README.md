# `tools/` — perkakas pemeriksa & gerbang

> ⚠️ **Ini bukan kode produksi.** Kode produksi ada di [`../apps/api`](../apps/api/README.md)
> (Sprint 0 & 1, branch `v0/sprint-0-foundation` · `v0/sprint-1-identity`, menunggu HUMAN REVIEW). Berkas di
> sini **memeriksa** dokumen, DDL, pohon direktori, dan kode — dan memulangkan
> kode keluar `1` kalau ada aturan yang dilanggar.

| Berkas | Tugasnya | Dependensi |
|---|---|---|
| [`periksa_dokumen.py`](periksa_dokumen.py) | **15** pemeriksaan [`../arch/11`](../arch/11-PENEGAKAN.md) yang membaca dokumen, DDL, dan pohon repo | nol — Python 3.10+ |
| [`uji_mutasi.py`](uji_mutasi.py) | membuktikan pemeriksaan di atas **sanggup gagal** — 25 mutasi, tiap mutasi wajib melahirkan temuan **baru** | nol |
| [`uji_mutasi_kode.py`](uji_mutasi_kode.py) | membuktikan kontrak `import-linter` (satu mutasi per id kontrak), larangan ruff, peta penegak, rantai pasok, uji migrasi, dan pemindai rahasia, penjaga Sprint 1 (sandi · sesi · persetujuan · izin · batas laju · galat basis data di log), penjaga Sprint 2 (goals · habits · rentetan · check-in · mood · Idempotency-Key · masukan ketat · balapan & batas · aplikasi Flutter), dan penjaga Sprint 3 (event & penerbitannya · relay & grup konsumen · peran pekerja · journal · Qdrant & penyemat berkunci per pengguna · ekstraksi, penyelaras & pencarian memori · daftar scope resmi · activities), serta batas waktu alat ini sendiri **sanggup gagal** — 342 mutasi, tiap mutasi wajib gagal dengan **alasan yang dimaksud**, dan untuk pytest alasan itu hanya dibaca dari **baris galat** (`E …`) — sumber uji yang ikut tercetak tidak dihitung | lingkungan `uv` (+ basis data, Redis & Qdrant untuk 234 mutasi — `HVX_TEST_DATABASE_URL` · `HVX_TEST_REDIS_URL` · `HVX_TEST_QDRANT_URL` —, Flutter untuk 17 — dengan `TZ=WIB-7` —, Docker untuk 1 mutasi pemindai) |
| [`ci_lokal.py`](ci_lokal.py) | **gerbang penuh** `lint → typecheck → test → build → scan` — satu sumber untuk mesin lokal dan [`ci.yml`](../.github/workflows/ci.yml) | `uv`, Docker |

---

## `periksa_dokumen.py`

| Kode | Memeriksa | Populasi |
|---|---|---|
| **B-6** | tepat satu pohon `security/`; **tidak ada pohon keamanan kedua** | pohon [`../arch/03`](../arch/03-MONOREPO-FINAL.md) **+ repo nyata** (tingkat atas, akar paket, modul) |
| **M-4** 🆕 | tak ada direktori bernama kata [kamus tabrakan](../arch/02-BOUNDED-CONTEXT.md) §4 di luar pemilik sahnya | repo nyata; letak V0 dinormalkan lewat [`../arch/03`](../arch/03-MONOREPO-FINAL.md) §8 |
| **P-1** | tiap `CREATE TABLE` menyatakan retensi · who-can-set · on-delete | [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) **+ tiap `data/migrations/versions/*.up.sql`** |
| **P-2** | tiap tabel punya kolom `data_subject` | idem |
| **P-3** | tidak ada `user_id` nullable tanpa penjaga — **komentar SQL tidak dihitung penjaga** | idem |
| **E-1** | segmen pertama `event_type` ada di registry domain | [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2 |
| **E-2** | `event_type` dua segmen, huruf kecil, **kata kerja lampau** | [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) |
| **E-3** 🆕 | `events.source` tidak menerima `sensor` | `CHECK` di DDL `spec/01` + migrasi |
| **E-4** | kata kerja pengubah keadaan punya kembaran kegagalan | [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §6 |
| **E-5** | tiap nama event di naskah punya baris di tabel padanan | seluruh `docs/` |
| **A-1** 🆕 | satu angka tidak dipakai untuk `R` **dan** `L` | skema manifest [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) + DDL `agents` |
| **A-2** | tiap tool di `tools:` punya `risk_level <= max_risk` | [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) |
| **A-3** | agent yang dipanggil agent lain punya entri `kind: agent` | **K-14** |
| **G-1** | tiap pasal Konstitusi §20.16 punya ≥ 1 penegak | [`../arch/08`](../arch/08-AGENT-CONTRACTS.md) §4 |
| **R-1** | `index(gerbang) < index(yang dijaganya)` | [`../arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md) §2.1 |

```bash
python tools/periksa_dokumen.py                # semua (15)
python tools/periksa_dokumen.py --senarai      # + tiap nama/berkas yang dipanen
python tools/periksa_dokumen.py P-1 M-4        # sebagian
python tools/uji_mutasi.py                     # buktikan merahnya bisa terjadi
```

Pemeriksaan yang membaca **impor kode** tidak ada di sini — itu kontrak
`import-linter` di [`../pyproject.toml`](../pyproject.toml) (M-1 · M-2 · M-3 ·
B-2). Peta lengkap 26 pemeriksaan, mana yang jalan dan mana yang menunggu
pemicu apa: blok ` ```penegak ` [`../arch/11`](../arch/11-PENEGAKAN.md) §6,
dijaga `tests/unit/test_penegak.py`.

---

## `ci_lokal.py` — gerbang yang sungguh berjalan

```bash
uv run python tools/ci_lokal.py                  # kelima tahap
uv run python tools/ci_lokal.py --daftar         # cetak langkahnya saja
uv run python tools/ci_lokal.py --lapor-github   # kelima tahap + status `ci-lokal` di commit
```

> 🔑 **CI tanpa tagihan — keputusan pemilik H-26** (17 Sep 2026, menjawab
> [#160](../../issues/160)): *“gunakan alternatif versi gratis, jangan ada
> tagihan.”* Alur Actions hanya `workflow_dispatch` (dijaga
> `test_rantai_pasok.py`); gerbangnya berjalan di mesin pengembang, dan
> `--lapor-github` menempelkan hasilnya ke commit HEAD sebagai status
> **`ci-lokal`** lewat API status commit — fitur dasar repo, bukan Actions.
>
> 🛑 Status itu hanya menempel pada pohon yang **benar-benar diuji**: laporan
> ditolak untuk gerbang sebagian, pohon kerja kotor, dan commit yang belum
> menjadi ujung cabang di `origin` — dan keadaan repo diperiksa **ulang** sesudah
> gerbang selesai, sebab uji mutasi merusak lalu memulihkan berkas di tempat.

---

## Tiga aturan yang dipegang berkas-berkas ini

**1 · Registry dibaca DARI dokumennya, tidak ditulis ulang di dalam kode.**
Domain dari `arch/07` §2, pasal dari `arch/08` §4, pasangan gerbang dari blok
` ```r1 ` `arch/10`, kamus tabrakan dari `arch/02` §4, peta penegak dari blok
` ```penegak ` `arch/11`. **Kalau dokumennya hilang, pemeriksa GAGAL dengan
galat — bukan lulus karena tidak menemukan apa pun.**

**2 · Populasi yang diperiksa dinyatakan, bukan ditebak.** `--senarai` mencetak
tiap nama beserta asalnya; daftar pengecualian menyertakan **alasan per baris**.

**3 · Tiap pemeriksaan terbukti sanggup gagal — dengan alasan yang dimaksud.**
Kode keluar `1` saja tidak cukup: uji yang gagal karena galat lingkungan juga
keluar `1`.

---

## 🔴 Alat ini salah enam kali sebelum benar — dan itu bagian laporannya

| | Yang keliru | Kalau tidak ketahuan |
|---|---|---|
| 1 | panen butir roadmap ikut membaca **catatan audit** ⇒ milestone yang hanya **diusulkan** terhitung **ada** | Phase 18 tampak punya gerbang keselamatan |
| 2 | panen nama event **hanya membaca token di dalam backtick** | seluruh keluarga `security.*` lolos E-1 dan E-2 |
| 3 | `uji_mutasi.py` membaca/menulis lewat `read_text`/`write_text` ⇒ di Windows berkas ber-LF **dikembalikan sebagai CRLF** | "dikembalikan apa adanya" yang diam-diam mengubah berkas |
| 4 | P-3 mencari penjaga sebagai *baris yang menyebut `CHECK`, `data_subject`, `user_id`* ⇒ **komentar SQL** yang menyebut ketiganya lolos | migrasi 0001 punya komentar persis begitu, tepat di atas CHECK-nya |
| 5 | `uji_mutasi_kode.py` mencari `harus_memuat` di **seluruh** keluaran pytest ⇒ pytest mencetak sumber uji sampai baris yang gagal, jadi pesan `assert` yang **lulus** ikut tercetak | galat lingkungan sesudahnya — Redis mati, sandi peran diganti proses lain — terhitung *“berbunyi dengan alasan yang dimaksud”* (tinjauan Sprint 1) |
| 6 🆕 | `uji_mutasi_kode.py` menunggu tiap mutasi **tanpa batas** ⇒ mutasi yang membuat ujinya menggantung (pekerja yang tidak menolak peran yang salah berjalan terus) menahan seluruh putaran — dan menghentikan proses langsungnya saja tidak cukup: di Windows `python.exe` venv menjalankan interpreter sebagai **proses anak** yang memegang pipa keluaran | gerbang yang tidak pernah selesai, tanpa satu baris pun di keluarannya (tinjauan Sprint 3 — kini 600 dtk, lalu seluruh pohon prosesnya dihentikan) |

> 💡💡 **Pertanyaannya tetap satu, dan ia berbuah lagi: *apa yang alat ukur ini
> TIDAK PERNAH lihat?*** Untuk nomor 3 dan 4 jawabannya: alat ukur itu sendiri.

## Yang alat-alat ini **tidak** bisa periksa

| Tidak terjaga | Kenapa |
|---|---|
| apakah sebuah nama event **bermakna** | penilaian, bukan pola |
| apakah sebuah roadmap **urutannya masuk akal** selain soal gerbang | R-1 hanya memeriksa pasangan yang **dideklarasikan** |
| B-1 · B-3 · B-4 · B-5 · P-4 · P-5 · P-6 | subjeknya belum ada — pemicu tiap baris di blok `penegak` `arch/11` §6 |
