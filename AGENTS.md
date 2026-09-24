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
├── pekerja.py         proses kedua: relay event → Redis Streams, konsumen, penyelaras memories → Qdrant
└── modules/           spec/06 — satu tabel dimiliki tepat satu modul
    ├── platform/      config · db · redis · log · galat · batas laju · /health (tanpa aturan domain)
    ├── identity/      users · consents · permissions · audit_logs — sesi · sandi · izin · audit
    ├── profile/ goals/ habits/ checkins/ journal/ activities/
    ├── events/  memory/  intelligence/
    └── agents/        tidak ada yang boleh mengimpornya
apps/mobile/           Flutter — layar V0 (spec/07 2.7); klien = `lib/api/klien.dart`
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
| SQL sebuah modul hanya menyebut tabel miliknya (`spec/06` aturan 5) — di berkas `.py` mana pun | `tests/unit/test_batas_tabel.py` | baca lewat pintu keluar modul pemilik (mis. `identity.ambil_pengguna`) di transaksi yang sama |
| fungsi `SECURITY DEFINER` hanya dari daftar izin, `search_path` terpatok, tidak untuk `PUBLIC` | `test_kepemilikan_data.py` | tambahkan ke `DEFINER_DIIZINKAN` **dengan alasannya** + `REVOKE ALL … FROM PUBLIC` + `GRANT EXECUTE … TO hvx_app` |
| IP klien dan email tidak pernah disimpan mentah — di audit maupun kunci Redis | `test_sidik_ip.py` · `test_auth.py` | pakai `platform.sidik_ip(request)` / `platform.sidik(settings, label, nilai)` — HMAC berkunci |
| batas laju: `/v1/*` per IP, rute bersesi per pengguna, `429` + `Retry-After` | `test_batas_laju.py` | rute baru di bawah `/v1` sudah terbatasi; rute yang butuh pengguna memakai `identity.PenggunaDiperlukan`; `429` hanya lewat `platform.galat_terlalu_sering` |
| jatah batas laju **dipakai**, tidak ditanya dulu lalu dihitung nanti | `test_batas_laju.py` (tebakan serentak) | `PembatasLaju.ambil` selalu memakai satu jatah; yang perlu dikembalikan sesudah berhasil memakai `lupakan()` |
| operasi sesi yang membaca lalu menulis catatan sesi = **satu skrip Lua** | `test_sesi.py` (menyela tiap celah antarperintah) | jangan pecah menjadi `GET`/`HGETALL` lalu `MULTI` — keluar dan pencabutan kalah balapan |
| perubahan basis data dan jejak auditnya satu transaksi | `test_izin.py` · `test_persetujuan.py` · `test_auth.py` | panggil `audit(conn, …)` dengan `conn` perubahannya; jangan `commit()` di antaranya |
| galat basis data dicatat **tanpa pesan** (pesan PostgreSQL membawa isi baris) | `test_galat_basis_data.py` | jangan konfigurasi ulang log tanpa `_galat_basis_data_tanpa_isi`; baca SQLSTATE dan nama constraint, bukan pesannya |
| teks bebas dari klien tidak memuat NUL; `jsonb` dari klien paling dalam 32 tingkat (S5) | `test_auth.py` · `test_profil.py` · `test_aktivitas.py` | medan `str` yang disimpan: `platform.TeksTanpaNul`; `jsonb`: `platform.tanpa_nul_bersarang` (NUL **dan** kedalaman) |
| angka · boolean · tanggal · waktu dari klien **ketat** — pydantic mode python mengoersi `true`→1, detik Unix→tanggal UTC (E-170) | `test_masukan_ketat_semua_rute.py` (skema inti tiap rute) | medan badan: `platform.Bulat` · `Benar` · `Tanggal` · `WaktuBerzona` · `AngkaJson`; kueri/jalur bertanggal: `platform.Tanggal` · `WaktuBerzona` — jangan `int`/`bool`/`date`/`datetime` polos |
| rute tulis domain **menyatakan dan memanggil** `Idempotency-Key` | `test_idempotensi_terpasang.py` | `idem: platform.Idempoten` + `return await idem.jalankan(user_id, kerja, baca_ulang)`; `kerja` mengembalikan `platform.Jawaban(status, isi, id)` — Redis hanya menyimpan rujukan (E-171) |
| bacaan/pendengar lintas modul domain lewat titik rakit, bukan impor (K-23) | `test_main.py` | fungsi pintu keluar modul dipasang `hvx.main` di `app.state`; rute mengambilnya dan **menolak berjalan** tanpanya |
| tulisan yang menaut baris lain (goal) mengunci barisnya hidup | `test_batas_dan_balapan.py` (serentak) | `goals.kunci_goal_hidup(conn, id)` — `FOR SHARE` — **sebelum** menulis anak, milestone, atau tautan |
| daftar yang dibaca utuh dibatasi **saat menulis** (K-24) | `test_batas_dan_balapan.py` | hitung di bawah `pg_advisory_xact_lock` per pemilik → `422 *_limit_reached`; jangan memotong saat membaca |
| kursor halaman terikat daftar asalnya | `test_halaman.py` | `platform.kursor_waktu("<daftar>", …)` · `baca_kursor_waktu("<daftar>", …)` |
| tulisan **fakta perilaku** menerbitkan eventnya di transaksi yang sama (`spec/06` aturan 6); kunci per **kejadian** (`spec/03` aturan 1) | `test_penerbitan_event.py` | `events.terbitkan(conn, …)` dengan `conn` tulisannya; baris peta baru di `spec/06` **dan** ujinya |
| stream Redis membawa **rujukan**, bukan isi; konsumen membaca event di bawah RLS pemiliknya dan ACK **sesudah** commit (K-25) | `test_relay.py` | penangan `(conn, EventMasuk)` yang **idempoten**; jangan menaruh payload di stream |
| Qdrant tidak punya RLS: tiap pencarian vektor bersaring `user_id`, payload titik **tanpa isi**, hasilnya dibaca ulang di PostgreSQL | `test_vektor.py` · `test_memori.py` | cari lewat `memory.PencariMemori`; tulis ke Qdrant hanya lewat `memory.PenyelarasVektor` — tidak pernah dari jalan permintaan |
| scope hanya dari **daftar resmi** `spec/05`; scope sensitif tidak pernah `allow` karena bawaan (E-180) | `test_izin_masukan.py` · `test_izin.py` · `test_memori.py` | scope baru: `spec/05` *Daftar scope resmi* **dan** `identity.SCOPE_RESMI`, di PR yang sama |
| turunan data pribadi mengikuti sumbernya — jurnal disunting/dihapus → memorinya, di transaksi yang sama (K-27) | `test_memori.py` | pendengar lewat titik rakit (`pendengar_jurnal_berubah`); vektornya menyusul lewat penyelaras |
| penyemat memori **berkunci, per pengguna** — vektor tidak bisa dibalik jadi kata, dan vektor dua pengguna tidak sebanding (K-26, S1) | `test_sematan.py` · `test_config.py` · `test_memori.py` | `platform.penyemat_dari(settings)` lalu `.untuk(user_id)`; penyemat proses sendiri tidak menyemat |
| fungsi lintas-RLS milik proses pekerja hanya untuk `hvx_pekerja`; api **menolak mulai** sebagai anggotanya, pekerja menolak mulai **tanpa** peran itu (S4) | `test_kepemilikan_data.py` · `test_aplikasi_hidup.py` | `GRANT EXECUTE … TO hvx_pekerja` (bukan `hvx_app`) di `spec/01` §12 **dan** migrasi; login pekerja `HVX_PEKERJA_DB_USER` |
| Qdrant tidak pernah dipanggil sambil memegang kunci baris, dan penyematan tidak berjalan di event loop pekerja (K3, S2) | `test_memori.py` | baca → semat (thread) → kirim → tandai hanya bila sidik isinya masih sama |
| model bahasa hanya lewat `platform.GerbangModel` — kelas → model → token & biaya tiap panggilan; model tanpa harga ditolak saat mulai; perintah berbentuk tetap (*“catat mood 3”*) **tanpa model sama sekali** (K-28) | `test_niat.py` · `test_gerbang_model.py` · `test_rute_model.py` | penyedia baru di `platform/model.py` + harganya di `HVX_MODEL_HARGA`; perintah baru di `agents/niat.py` — `deterministic` hanya untuk perintah yang diawali kata perintahnya |
| manifest agent & tool registry lulus **9 aturan spec/05 + A-1 + K-14** sebelum api bisa dibuat; katalog `agents` dikelola **migrasi** dan api menolak mulai bila berbeda (K-29) | `test_registri_agent.py` (satu kasus per aturan) · `test_katalog_agent.py` | manifest/tool baru di `agents/manifest/` · `agents/alat/`, versi baru + migrasi katalog baru; jangan pernah beri `hvx_app` hak tulis katalog |
| agent menyentuh data **hanya lewat tool**, dan tiap tool lewat satu jalan: registry → manifest pemanggil → masukan **ketat** → batas laju per pengguna → gerbang → keluaran = skema `output` persis — termasuk pemanggilan agent lain (K-14); tool coach **tanpa catatan bebas** pengguna (C-32) | `test_pelaksana_alat.py` · `test_alat_v0.py` | tool baru = YAML `agents/alat/` **dan** entri `agents.IMPLEMENTASI` (dicek satu lawan satu saat dirakit); implementasi memanggil pintu keluar modul pemilik datanya, tidak pernah SQL, dan mencatat scope yang **benar-benar** disentuhnya |
| aplikasi Flutter bersih dan teruji | `ci_lokal.py`: `dart format` · `flutter analyze --fatal-infos` · `flutter test` · layar diketuk lawan api hidup (smoke) | `flutter`/`dart` di PATH, atau `HVX_FLUTTER`/`HVX_DART` |

🔑 **Setiap penegak baru wajib dibuktikan sanggup gagal** — tambahkan
mutasinya di `tools/uji_mutasi.py` (dokumen) atau `tools/uji_mutasi_kode.py`
(kode). Pemeriksa yang tidak pernah merah tidak dihitung ada.

🔒 **Tiap kueri aplikasi berjalan di dalam `platform.transaksi_pengguna(engine,
user_id)`** — atau `platform.transaksi_sistem(engine)` untuk baris sistem
(`user_id` NULL), yang sengaja berbentuk sama supaya jalur *“akun ada”* dan
*“akun tidak ada”* tidak berbeda waktu. Tanpa itu RLS mengembalikan **nol
baris** — gagal-tertutup, bukan bocor. Yang butuh melihat lintas pengguna (mencari akun per email saat login,
sapuan hapus akun) memakai fungsi `SECURITY DEFINER` yang sempit, satu per
kebutuhan, di migrasi — **bukan** kebijakan RLS yang dilonggarkan.

## 6 · Perintah

```bash
python -m pip install uv          # sekali, kalau belum ada
uv sync                           # seluruh lingkungan dari uv.lock
uv run pytest -m "not integration"                  # putaran cepat
docker compose up -d --wait postgres redis qdrant   # layanan untuk uji integrasi
(cd apps/mobile && flutter test)                    # aplikasi — tanpa server
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
- Galat ke klien: `platform.GalatApi(status, kode, pesan)` — `kode` `snake_case`
  berbahasa Inggris (`email_taken`), pesan **tidak pernah mengutip masukan**.
  Pesan galat yang hanya ke log pun tidak mengutip nilai milik pengguna: galat
  basis data disaring `platform`, galat kode sendiri **tidak** (`SECURITY.md`).
- Perubahan yang harus berjejak: `identity.audit(conn, …)` di **transaksi yang
  sama** dengan perubahannya — metadata hanya skalar pendek, bukan isi.
- Nama tabel `snake_case` jamak; nama event `domain.kata_kerja_lampau`
  (hanya dari tabel padanan [`spec/03`](spec/03-EVENT-CONTRACTS.md)); rute
  `/v1/…`.
