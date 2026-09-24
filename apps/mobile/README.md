# `apps/mobile` — aplikasi HumanVerse XOS V0 (Flutter)

Satu basis kode untuk seluler **dan** web ([`arch/05`](../../arch/05-TECHNOLOGY-STACK.md)
§4, ADR-001). Layar pertama: **daftar habit + tandai selesai** —
[`spec/07`](../../spec/07-BACKLOG-V0.md) tugas 2.7.

| Layar | Isi |
|---|---|
| Masuk / Daftar | email + sandi (daftar: nama, zona waktu IANA, persetujuan syarat & privasi **wajib**, pelatihan model **opsional**, bawaannya tidak) |
| Habit hari ini | tanggal **lokal perangkat** · energi check-in 1–5 · tiap habit: tandai selesai / batalkan, pilih tier (tier yang disarankan dari energi, beserta alasannya — naskah 4 §34) · habit yang **dilewati** (`skipped`, dari perangkat lain) tampil lain dan bisa dibatalkan · tambah habit |

Klien (`lib/api/klien.dart`) — tiga hal yang dulu salah (tinjauan Sprint 2, E-175):

* **Satu penyegaran token untuk semua.** Permintaan serentak yang sama-sama
  menerima `401` menunggu penyegaran yang sama; yang sudah disegarkan
  permintaan lain langsung diulang dengan token baru. Dua penyegaran dengan
  token segar yang sama dibaca server sebagai pencurian — sesinya dicabut.
* **Satu tindakan, satu id.** Habit baru membawa id buatan klien (`idBaru()`),
  yang juga `Idempotency-Key`-nya; "Simpan" yang diketuk lagi dengan isian yang
  sama sesudah jaringan putus mengirim id yang **sama** — diputar ulang server,
  bukan habit kedua. `409 already_exists` = percobaan sebelumnya sudah sampai.
* **Penyelesaian tanpa kunci**: `(habit, tanggal)` unik di server, dan kirim
  ulang tanggal yang sama menjawab `200` dengan baris lama.

## Menjalankan

```bash
# api + PostgreSQL + Redis (akar repo), dengan asal aplikasi web diizinkan CORS
HVX_CORS_ORIGINS=http://localhost:5000 docker compose up -d --wait

cd apps/mobile
flutter run -d chrome --web-port 5000 --dart-define=HVX_API=http://127.0.0.1:8000
# emulator Android: --dart-define=HVX_API=http://10.0.2.2:8000 (debug saja — teks-polos)
```

## Uji

```bash
flutter analyze --fatal-infos     # gerbang lint
flutter test                      # uji klien (MockClient) + uji widget (layanan palsu)
dart run tool/ujung_ke_ujung.dart http://127.0.0.1:8000   # klien asli lawan api hidup
flutter test test/ujung --dart-define=HVX_API_UJI=http://127.0.0.1:8000   # LAYAR diketuk lawan api hidup
```

Semuanya dijalankan gerbang [`tools/ci_lokal.py`](../../tools/ci_lokal.py) —
analyze & format di tahap `lint`, `flutter test` di tahap `test`, dan kedua uji
lawan api hidup di tahap `build` terhadap tumpukan compose dari citra CI. Tanpa
`HVX_API_UJI`, `test/ujung/` **dilewati** (bukan lulus diam-diam): `flutter
test` biasa melaporkannya sebagai `~1`.

## Yang sengaja belum

| | Kenapa | Kapan |
|---|---|---|
| token disimpan di perangkat | token segar di penyimpanan web terbaca skrip mana pun di asal yang sama; halaman yang dimuat ulang meminta masuk lagi | bersama mode luring — `spec/07` 6.6 |
| teks syarat & kebijakan privasi | milik pemilik (#59 butir 2, C-11) — persetujuan dicatat untuk `draf-v0` | pemilik |
| mode luring | antrean lokal + sinkron tanpa duplikat | `spec/07` 6.6 |
