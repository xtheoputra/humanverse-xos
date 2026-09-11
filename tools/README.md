# `tools/` — perkakas pemeriksa dokumen

> ⚠️ **Ini bukan kode produksi, dan repo ini tetap nol baris kode produksi.**
> Berkas di sini **membaca dokumen** dan memulangkan kode keluar `1` kalau ada
> aturan yang dilanggar. Kode produksi V0 belum boleh dimulai — ia menunggu
> [#3](../../issues/3). Pemisahan itu sengaja dan disebut di
> [`../README.md`](../README.md).

---

## `periksa_dokumen.py`

Menjalankan **dua belas** dari **dua puluh enam** pemeriksaan
[`../arch/11`](../arch/11-PENEGAKAN.md) — kedua belas yang tidak membutuhkan
satu baris kode produksi pun, sebab yang diperiksanya **sudah ada sebagai
dokumen**: DDL di `spec/01`, manifest di `spec/05`, pohon monorepo di
`arch/03`.

| Kode | Memeriksa | Sumber aturannya |
|---|---|---|
| **B-6** | tepat satu pohon `security/` di tingkat atas | [`../arch/03`](../arch/03-MONOREPO-FINAL.md) |
| **P-1** | tiap `CREATE TABLE` menyatakan retensi · who-can-set · on-delete | [`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §5 |
| **P-2** | tiap tabel punya kolom `data_subject` | [`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §6 |
| **P-3** | tidak ada `user_id` nullable tanpa penjaga | [`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §6 |
| **E-1** | segmen pertama `event_type` ada di registry domain | [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2 |
| **E-2** | `event_type` dua segmen, huruf kecil, **kata kerja lampau** | [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) |
| **E-4** | kata kerja pengubah keadaan punya kembaran kegagalan | [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §6 |
| **E-5** | tiap nama event di naskah punya baris di tabel padanan | [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) · [`../docs/SENSUS-EVENT.md`](../docs/SENSUS-EVENT.md) |
| **A-2** | tiap tool di `tools:` punya `risk_level <= max_risk` | [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) |
| **A-3** | agent yang dipanggil agent lain punya entri `kind: agent` | **K-14** |
| **G-1** | tiap pasal Konstitusi §20.16 punya ≥ 1 penegak | [`../arch/08`](../arch/08-AGENT-CONTRACTS.md) §4 |
| **R-1** | `index(gerbang) < index(yang dijaganya)` | [`../arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md) §2.1 |

```bash
python tools/periksa_dokumen.py                # semua (12)
python tools/uji_mutasi.py                     # buktikan merahnya bisa terjadi
python tools/periksa_dokumen.py --senarai      # + tiap nama yang dipanen
python tools/periksa_dokumen.py E-1 E-2        # sebagian
python tools/periksa_dokumen.py --json         # untuk CI
```

Nol dependensi. Python 3.10+. Keluar **1** kalau ada yang gagal.

> 🛑 **Jalankan MANUAL sebelum tiap commit.**
> `.github/workflows/periksa-dokumen.yml` sudah terpasang, tetapi **belum
> pernah berjalan sekali pun**: GitHub Actions terhalang di tingkat akun
> (*“recent account payments have failed or your spending limit needs to be
> increased”*), dan repo ini privat sehingga menitnya ditagih.
> ⇒ **skripnya hijau, gerbangnya mati** — [#160](../../issues/160), dan ia
> hanya bisa dibuka pemilik sebab ia soal tagihan.

---

## Tiga aturan yang dipegang berkas ini

**1 · Registry dibaca DARI dokumennya, tidak ditulis ulang di dalam kode.**
Daftar 46 domain diambil dari `arch/07` §2; sepuluh pasal Konstitusi dari
`arch/08` §4; pasangan gerbang dari blok ` ```r1 ` di `arch/10` §2.1.
Kalau dokumennya berubah, pemeriksa ikut. **Kalau dokumennya hilang, pemeriksa
GAGAL dengan galat — bukan lulus karena tidak menemukan apa pun.**

**2 · Populasi yang diperiksa dinyatakan, bukan ditebak.** `--senarai`
mencetak tiap nama beserta baris asalnya. Daftar pengecualian
(`BUKAN_EVENT`, `PRA_KEPUTUSAN`, `DILUAR_TABEL`) menyertakan **alasan per
baris**, supaya ia tidak menjadi tempat menyembunyikan temuan.

**3 · Angka di prosa diperiksa terhadap tabel di atasnya.** Itu yang menangkap
*“39 domain”* di `arch/07` §2 sementara tabelnya memuat **45**.

---

## 🔴 Alat ini sendiri salah dua kali sebelum benar — dan itu bagian laporannya

| | Yang keliru | Kalau tidak ketahuan |
|---|---|---|
| 1 | panen butir roadmap ikut membaca **catatan audit saya sendiri** ⇒ `G18.11 Safety, Privacy & Governance`, milestone yang hanya **diusulkan**, terhitung **ada** | Phase 18 tampak punya gerbang keselamatan. Alat yang mencari kegagalan justru **menutupinya** |
| 2 | panen nama event **hanya membaca token di dalam backtick** ⇒ kedelapan nama `security.*` (K-10) tidak pernah diperiksa | seluruh keluarga event **keamanan** lolos E-1 dan E-2 |

Pembeda untuk keliru 1 tidak dikarang: `docs/SENSUS-EVENT.md` sudah mengujinya —
percobaan *“semua baris `>` itu catatan saya”* **salah** (naskah juga mengutip
pemilik dengan `>`); yang lulus validasi silang adalah menilai blok dari **baris
pertamanya**. Aturan itu dipakai ulang apa adanya (`buang_catatan_audit`).

> 💡💡 **Satu pertanyaan menemukan keduanya, dan ia layak diulang setiap kali
> sesuatu berubah menjadi hijau: *apa yang alat ukur ini TIDAK PERNAH lihat?***
> Bukan *“apakah hasilnya benar”* — hasilnya benar untuk populasi yang
> dilihatnya. Yang salah **populasinya**.

✅ **Bukti pembetulannya sah:** sesudahnya kedelapan roadmap memulangkan jumlah
butir yang sama dengan angka yang dokumennya sendiri sebutkan — A14 10 ·
R16 10 · H17 12 · G18 10 · S19 10 · C20 12 · `spec/07` **51 tugas** ·
`arch/10` **13 tahap**.

---

## Yang alat ini **tidak** bisa periksa

| Tidak terjaga | Kenapa |
|---|---|
| apakah sebuah nama event **bermakna** | penilaian, bukan pola |
| apakah sebuah roadmap **urutannya masuk akal** selain soal gerbang | R-1 hanya memeriksa pasangan yang **dideklarasikan** di `arch/10` §2.1 |
| empat belas pemeriksaan lain (`B-1`…`B-5` · `M` · `P-4`…`P-6` · `E-3` · `A-1`) | semuanya butuh kode **produksi**; dipasang Sprint 0 tugas **0.4 · 0.7 · 0.8** |

⚠️ **R-1 tidak menebak pasangan gerbangnya sendiri.** Roadmap baru yang belum
punya baris di blok ` ```r1 ` **tidak diperiksa** — dan itu disengaja: gerbang
yang ditebak mesin akan salah menuduh, lalu diabaikan orang. Menambah roadmap
berarti menambah barisnya di `arch/10` §2.1.
