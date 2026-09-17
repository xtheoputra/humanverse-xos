# AGENTS.md — untuk AI coding agent yang mengubah repo ini

> Dibaca **sebelum** mengubah satu baris pun (naskah 5 §4, naskah 4 §52).
> Manusia juga boleh membacanya; isinya aturan kerja, bukan visi.

---

## 1 · Tiga lapis dokumen, dan siapa yang menang

| Lapis | Isi | Boleh disunting? |
|---|---|---|
| [`docs/`](docs/) `01`–`275` | **kata pemilik apa adanya** — 24 naskah | 🛑 **tidak pernah**. Keraguan masuk [`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md) |
| [`arch/`](arch/README.md) | Master Architecture v2.0 — mengikat **NAMA & BATAS**, Phase 1–20 | ya, dengan catatan kenapa |
| [`spec/`](spec/README.md) | Engineering Spec V0 — mengikat **BENTUK** (kolom, payload, endpoint) | ya, dengan catatan kenapa |

> 🔑 **Untuk V0, `spec/` menang.** Kalau kode dan `spec/` tidak cocok, salah
> satunya salah — putuskan yang mana, lalu betulkan **keduanya dalam PR yang
> sama**. Kode yang diam-diam menyimpang dari spesifikasi adalah pola yang
> repo ini catat puluhan kali.
>
> 🔧 **Kesalahan `spec/`/`arch/` yang ketemu saat menulis kode: BETULKAN, jangan
> hanya dicatat** — pemilik, 17 Sep 2026: *“betulkan saja menurut anda benarnya
> dimana.”* Temuannya tetap ditulis di `docs/99-CATATAN-AUDIT.md`, lengkap
> dengan apa yang dibetulkan. Batas yang tidak berubah: `docs/01`–`275` tidak
> disunting, dan butir **C** tetap milik pemilik.

## 2 · Apa yang dikerjakan, dan urutannya

Satu-satunya daftar pekerjaan kode: [`spec/07-BACKLOG-V0.md`](spec/07-BACKLOG-V0.md)
— 51 tugas, 7 sprint. Urutan tahap sesudahnya: [`arch/10`](arch/10-URUTAN-IMPLEMENTASI.md).

- Satu tugas = satu kolom **“Selesai bila”**. Tugas belum selesai sampai
  kalimat itu bisa dibuktikan **mesin** (uji, pemeriksa, atau perintah).
- **Jangan menambah cakupan.** Bagian *“Yang TIDAK ada di backlog ini”*
  `spec/07` mengikat: Neo4j, Kafka, Kubernetes, marketplace, SDK, voice,
  vision — tidak satu pun masuk V0.
- **Gerbang lebih dulu daripada yang dijaganya** (arch/10 §1, diperiksa R-1).

## 3 · Governance — tidak bisa dilewati

```
Coding Agent → Implementation → Unit Test → Integration Test
→ Security Scan → AI Review → HUMAN REVIEW → Merge
```

- 🛑 **Tidak ada commit ke `master` tanpa HUMAN REVIEW.** Kerjakan di branch
  (`v0/sprint-N-…`), buka PR, pemilik yang menggabungkan.
- 🛑 **Keputusan yang salahnya ditanggung orang lain bukan milik agent**:
  hukum & privasi (seluruh butir **C**), uang, orang yang tidak punya akun,
  badan orang. Tulis sebagai temuan, jangan diputuskan.

## 4 · Peta kode V0

```
apps/api/src/hvx/
├── main.py            titik rakit — satu-satunya yang menyambung 12 modul
└── modules/           spec/06 — satu tabel dimiliki tepat satu modul
    ├── platform/      config · db · redis · log · /health (tanpa aturan domain)
    ├── identity/      users · consents · permissions · audit_logs
    ├── profile/ goals/ habits/ checkins/ journal/ activities/
    ├── events/  memory/  intelligence/
    └── agents/        tidak ada yang boleh mengimpornya
data/migrations/       Alembic; SQL di *.up.sql / *.down.sql
tests/unit/ · tests/integration/
tools/                 pemeriksa dokumen, uji mutasi, CI lokal
```

## 5 · Aturan yang DITEGAKKAN mesin — jangan dilawan, betulkan penyebabnya

| Aturan | Penegak | Kalau merah |
|---|---|---|
| modul hanya dimasuki lewat `__init__.py` | `import-linter` M-2 | ekspor nama di `__all__`, impor dari `hvx.modules.<modul>` |
| lapisan modul; domain tidak saling impor; tak ada yang mengimpor `agents` | `import-linter` M-1 · M-3 | komunikasi antar-domain **lewat event** |
| klien jaringan / SDK model hanya di `platform`; tanpa impor dinamis | `import-linter` B-2 + ruff banned-api | tambahkan di `platform`, ekspor fungsinya |
| modul baru wajib dicatat di kontrak | `import-linter` `exhaustive` + `test_penegak.py` | tambahkan ke lapisan `m1-m3-lapisan` **dan** kontrak `m2-<modul>` |
| citra & aksi CI dipatok digest/SHA | `test_rantai_pasok.py` | patok ke digest (`docker buildx imagetools inspect`) / SHA commit |
| tiap `CREATE TABLE` membawa `@retention` · `@who-can-set` · `@on-delete` + kolom `data_subject` | `periksa_dokumen.py` P-1 · P-2 | lihat [`arch/06`](arch/06-DATA-ARCHITECTURE.md) §5 §6 |
| migrasi == `spec/01` | `tests/integration/test_migrasi.py` | ubah `spec/01` dan migrasinya **bersama** |
| cakupan uji ≥ 70 % | `pytest --cov` | tulis ujinya, jangan turunkan ambangnya |
| **data tiap pengguna milik pribadinya** (H-27) — RLS di tiap tabel milik pengguna, FK `(induk_id, user_id)`, hak akses `hvx_app` sesempit spec/01 §10 | `tests/integration/test_kepemilikan_data.py` | tabel baru: `user_id` + `ENABLE ROW LEVEL SECURITY` + kebijakan §11 + `GRANT` §10 + FK komposit ke induk ber-`user_id` — di `spec/01` **dan** migrasinya |
| api tidak pernah tersambung sebagai superuser, pemilik tabel, atau `BYPASSRLS` (B-40) | `platform.pastikan_peran_aplikasi` + `test_aplikasi_hidup.py` | api memakai peran anggota `hvx_app`; migrasi memakai `HVX_MIGRATION_DATABASE_URL` |
| CI **tanpa tagihan** (H-26) — alur Actions hanya `workflow_dispatch` | `test_rantai_pasok.py` | jangan tambah pemicu otomatis; gerbangnya `ci_lokal.py --lapor-github` |

🔑 **Setiap penegak baru wajib dibuktikan sanggup gagal** — tambahkan
mutasinya di `tools/uji_mutasi.py` (dokumen) atau `tools/uji_mutasi_kode.py`
(kode). Pemeriksa yang tidak pernah merah tidak dihitung ada.

🔒 **Tiap kueri aplikasi berjalan di dalam `platform.transaksi_pengguna(engine,
user_id)`.** Tanpa itu RLS mengembalikan **nol baris** — gagal-tertutup, bukan
bocor. Yang butuh melihat lintas pengguna (mencari akun per email saat login,
sapuan hapus akun) memakai fungsi `SECURITY DEFINER` yang sempit, satu per
kebutuhan, di migrasi — **bukan** kebijakan RLS yang dilonggarkan.

## 6 · Perintah

```bash
python -m pip install uv          # sekali, kalau belum ada
uv sync                           # seluruh lingkungan dari uv.lock
uv run pytest -m "not integration"                  # putaran cepat
docker compose up -d --wait postgres redis          # layanan untuk uji integrasi
uv run --locked python tools/ci_lokal.py            # GERBANG PENUH sebelum PR
git push && uv run --locked python tools/ci_lokal.py --lapor-github   # + status di PR
```

Gerbang penuh wajib hijau sebelum PR dibuka. Sesudah `push`, jalankan dengan
`--lapor-github`: hasilnya menempel ke commit sebagai status **`ci-lokal`** di
PR — gratis, lewat API status commit. GitHub Actions **sengaja dimatikan**:
pemilik memutuskan CI tanpa tagihan (**H-26**, [#160](../../issues/160)).

## 7 · Gaya

- Pesan commit: `<area>: <ringkasan>` (area: `api` · `data` · `infra` · `ci` ·
  `tools` · `spec` · `arch` · `docs`), sebut nomor tugas `spec/07`.
- Nama di kode mengikuti kode di sekitarnya: istilah domain berbahasa
  Indonesia, istilah teknis apa adanya. Docstring menjelaskan **kenapa**,
  terutama kalau jawabannya pernah salah.
- `ikat_pengguna()` dan dependensi autentikasi: **`async def`**, selalu.
- Nama tabel `snake_case` jamak; nama event `domain.kata_kerja_lampau`
  (hanya dari tabel padanan [`spec/03`](spec/03-EVENT-CONTRACTS.md)); rute
  `/v1/…`.
