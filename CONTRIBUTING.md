# CONTRIBUTING.md

> Untuk manusia **dan** AI coding agent. Agent juga wajib membaca
> [`AGENTS.md`](AGENTS.md).

---

## 1 · Menyiapkan mesin

| Butuh | Versi |
|---|---|
| Python | 3.12 |
| [uv](https://docs.astral.sh/uv/) | 0.12 (`python -m pip install uv`) |
| Docker + Compose | Compose v2 |

```bash
uv sync --locked                          # lingkungan penuh dari uv.lock
cp .env.example .env                      # isi kata sandi lokal; ganti port kalau bentrok
docker compose up -d --wait               # postgres · redis · migrate · api
curl http://127.0.0.1:8000/health         # {"status":"ok",...}
```

Port bawaan 8000 · 5432 · 6379 sering sudah dipakai proyek lain. Ganti lewat
`HVX_API_PORT` · `HVX_POSTGRES_PORT` · `HVX_REDIS_PORT` di `.env` — compose
hanya membuka port di `127.0.0.1`.

## 2 · Alur satu tugas

```
spec/07 tugas N.M
  → branch  v0/sprint-N-<ringkas>
  → kode + uji + (kalau ada aturan baru) penegak + mutasinya
  → uv run --locked python tools/ci_lokal.py   ← WAJIB hijau
  → PR: tempel ringkasan ci_lokal + centang "Selesai bila"
  → HUMAN REVIEW oleh pemilik → merge
```

- **Satu commit per tugas**, pesan `<area>: <ringkasan> (spec/07 N.M)`.
  Deskripsi commit menjelaskan **kenapa**, terutama keputusan yang bisa
  dibalik.
- **Satu PR per sprint** boleh, selama tiap tugas punya commit sendiri supaya
  bisa ditinjau satu per satu (**K-18**). Hanya commit terakhir yang dijamin
  lulus gerbang penuh — katakan itu di deskripsi PR.
- `--locked` di perintah gerbang bukan hiasan: `uv run` biasa menulis ulang
  `uv.lock` yang basi sebelum gerbang sempat memeriksanya.
- GitHub Actions belum berjalan ([#160](../../issues/160)): `ci_lokal.py`
  adalah gerbangnya. Menempelkan hasilnya di PR bukan formalitas — itu
  satu-satunya bukti bahwa gerbang dijalankan.

## 3 · Menjalankan uji

```bash
uv run pytest -m "not integration"        # cepat, tanpa layanan

export HVX_TEST_DATABASE_URL=postgresql://hvx:<sandi>@127.0.0.1:5432/hvx
export HVX_TEST_REDIS_URL=redis://127.0.0.1:6379/0
uv run pytest --cov                       # penuh + gerbang cakupan 70 %
```

Uji integrasi **gagal** — tidak dilewati — kalau dua variabel di atas kosong.
Ia membuat basis data sekali pakai (`hvx_uji_*`) dan menghapusnya lagi, jadi
role-nya butuh hak `CREATE DATABASE`.

## 4 · Mengubah skema

1. Ubah [`spec/01`](spec/01-DATABASE-SCHEMA.md) **lebih dulu** — ia sumber
   bentuk.
2. Tambah revisi di `data/migrations/versions/`: `NNNN_<slug>.py` +
   `NNNN_<slug>.up.sql` + `NNNN_<slug>.down.sql`.
3. Tiap `CREATE TABLE` baru membawa `data_subject` dan tiga anotasi
   (`@retention` · `@who-can-set` · `@on-delete`) — P-1/P-2 menolak yang lupa.
4. `uv run pytest tests/integration/test_migrasi.py` — migrasi harus sama
   persis dengan `spec/01`, dan turun harus bersih.

## 5 · Menambah aturan

Aturan baru di `arch/` atau `spec/` **tidak dihitung selesai** sampai:

1. ada penegaknya (kontrak `import-linter`, pemeriksaan di
   `tools/periksa_dokumen.py`, atau uji);
2. penegak itu **terbukti sanggup gagal** — mutasinya di `tools/uji_mutasi.py`
   atau `tools/uji_mutasi_kode.py`;
3. barisnya ada di blok ` ```penegak ` [`arch/11`](arch/11-PENEGAKAN.md) §6.

## 6 · Dokumen

- `docs/01`–`275` merekam kata pemilik — **jangan disunting**.
- Temuan, keraguan, koreksi → [`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md).
- Keputusan engineering yang diambil sendiri →
  [`docs/KEPUTUSAN-DIDELEGASIKAN.md`](docs/KEPUTUSAN-DIDELEGASIKAN.md), selalu
  dengan **bacaan yang ditolak** dan **cara membalikkan**.
- Tutup sesi kerja dengan entri di [`docs/SESSION-LOG.md`](docs/SESSION-LOG.md).
