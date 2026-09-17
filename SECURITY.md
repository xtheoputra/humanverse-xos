# SECURITY.md

## Melaporkan kerentanan

Repo ini privat dan belum punya pengguna selain pemiliknya. Laporkan lewat
**GitHub Security Advisory privat** di repo ini (*Security → Report a
vulnerability*), atau langsung kepada pemilik repo. **Jangan** membuka issue
publik untuk kerentanan, dan jangan menyertakan data pengguna nyata di laporan.

## Versi yang didukung

Belum ada rilis. `master` adalah satu-satunya garis yang dipelihara.

---

## Yang dijaga sejak Sprint 0 — dan penegaknya

Setiap baris di bawah punya penegak yang **terbukti sanggup gagal**
(`tools/uji_mutasi.py` · `tools/uji_mutasi_kode.py`). Baris yang penegaknya
hanya sebagian ditulis dengan batasnya.

| Hal | Bentuk | Penegak |
|---|---|---|
| tidak ada DSN / lingkungan bawaan | `Settings` gagal mulai tanpa `HVX_DATABASE_URL`, `HVX_REDIS_URL`, **`HVX_ENV`** | `tests/unit/test_config.py` |
| rahasia tidak masuk berkas repo | pemindai rahasia `trivy fs` atas pohon repo (tanpa `.venv`, `.git`, cache) | `ci_lokal.py scan` · mutasi *token tertanam* |
| kredensial lokal | bernilai `*-dev-only`, port hanya di `127.0.0.1` | `docker-compose.yml` — ⚠️ tanpa uji |
| proses api | pengguna non-root `hvx` (uid 10001) | `api.Dockerfile` — ⚠️ tanpa uji |
| jalur keluar jaringan | klien jaringan (HTTP · `urllib` · `socket` · `ssl` · SMTP/FTP/IMAP/POP · xmlrpc · websockets) & SDK model hanya boleh diimpor `platform` — **seluruh paket `hvx`**, termasuk modul dan berkas baru | `import-linter` **B-2** + ruff banned-api (`http.client`, `asyncio.open_connection`, **`importlib.import_module`**) |
| `/health` tidak membocorkan infrastruktur | galat ketergantungan tidak pernah masuk jawaban HTTP | `test_health.py` |
| 500 tidak membocorkan galat | amplop `{error: {code, message}}` tanpa rincian; rincian hanya ke log | `test_log.py` |
| log tidak bisa disuntik lewat `X-Request-ID` | nilai klien yang bukan id diganti | `test_log.py` |
| dokumentasi API interaktif | terbuka hanya di `local` · `test` · `ci` (daftar izin); `/docs` · `/redoc` · `/openapi.json` → 404 di produksi | `tests/unit/test_main.py` (lewat HTTP) |
| dependensi produksi | `pip-audit --strict` atas `uv.lock` — **penanda platform dibuang dulu**, supaya paket yang hanya ada di citra Linux ikut diaudit di mesin Windows | `ci_lokal.py scan` |
| kunci dependensi | `uv lock --check` · `UV_LOCKED` di Actions · `uv sync --locked` di citra | `ci_lokal.py lint` · mutasi *dependensi tanpa kunci ulang* |
| kode | `bandit` + aturan `S` ruff | `ci_lokal.py lint` · `scan` |
| citra | `trivy image` — HIGH/CRITICAL yang sudah ada perbaikannya = gagal; citra diberikan sebagai **tar hanya-baca**, pemindai **tidak** mendapat soket Docker | `ci_lokal.py scan` |
| citra luar dipatok **digest** | `python`, `uv`, `postgres`, `redis`, `trivy` — tag bisa dipindahkan (trivy sendiri pernah: GHSA-69fq-xp46-6x23) | `tests/unit/test_rantai_pasok.py` |
| aksi CI dipatok **SHA commit** | + `persist-credentials: false` + `permissions: contents: read` | `tests/unit/test_rantai_pasok.py` |

## 🛑 Yang BELUM dijaga — dan diketahui

| Celah | Akibat | Ditutup di |
|---|---|---|
| **api tersambung ke PostgreSQL sebagai superuser pemilik tabel** (D0) | `REVOKE UPDATE, DELETE ON audit_logs FROM PUBLIC` di `spec/01` **tidak menghalangi apa pun** bagi role itu — diverifikasi: `UPDATE` & `DELETE` lolos. Superuser juga **melewati RLS**. | Sprint 1 — **B-40**: role aplikasi terpisah, bukan superuser dan bukan pemilik, sebelum 1.5–1.6 |
| **`user_id` baris anak tidak diikat ke `user_id` induknya** (`goal_milestones.goal_id`, `ai_messages.conversation_id`, … 11 FK satu kolom) | seorang pengguna bisa menempelkan baris ke goal atau percakapan pengguna lain — dan saat pemilik induk menghapusnya, baris orang lain itu **ikut terhapus** (`CASCADE`). FK tidak melihat RLS | **B-41** — sebelum tugas 2.1 (tulisan baris anak pertama): FK komposit `(induk_id, user_id)` atau aturan repository yang dijaga uji |
| **PR merah tidak terhalang digabung** | Actions terhalang tagihan ([#160](../../issues/160)); perlindungan branch & ruleset tidak tersedia untuk repo privat pada paket akun ini (HTTP 403) | pemilik — tagihan/paket akun. Sampai itu: gerbangnya HUMAN REVIEW (H-25) + `ci_lokal.py` manual |
| belum ada autentikasi, izin, batas laju | semua rute selain `/health` belum ada | Sprint 1 (1.1–1.7) |
| B-1 *kode agent tidak mengimpor `security/`* | belum bisa dinyatakan: V0 belum punya `security/` | tugas 4.5 |
| eskalasi krisis untuk jurnal | `journal_entries.safety_flag` ada, jalurnya tidak | [#21](../../issues/21) — pemilik |
| pembangunan citra tidak sepenuhnya reprodusibel | `apt-get upgrade` saat membangun menarik tambalan Debian hari itu | dipilih sadar: citra dasar yang dipatok digest tidak pernah menerima tambalan sendiri |

Seluruh risiko hukum & privasi (butir **C** di
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md)) adalah keputusan
pemilik dan tidak diputuskan di kode.
