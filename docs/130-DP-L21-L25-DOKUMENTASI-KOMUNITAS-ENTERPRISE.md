# 130 — DP-L21–L25: Dokumentasi, Contoh, Sertifikasi, Komunitas & Enterprise

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L21 — Documentation Platform

```
docs/
  guides/  tutorials/  api/  sdk/
  agents/  plugins/    examples/
```

> **Semua memiliki contoh kode.**

> ℹ️ Ini pohon `docs/` **ketiga**: naskah 5 §4 (`architecture api agents domain
> security decisions`), naskah 7 Layer 41 (+ `prompts design playbooks`,
> − `domain`), dan yang ini (`guides tutorials sdk plugins examples`). Ketiganya
> untuk pembaca berbeda — dua yang pertama untuk tim & AI coding agent, yang
> ini untuk developer luar. Bukan tabrakan, tapi perlu dinyatakan bahwa ini
> **dokumentasi publik**, terpisah dari dokumentasi internal.

---

## DP-L22 — Example Library

```
Habit Agent · Fashion Agent · Calendar Plugin
Travel Plugin · Notification Plugin
```

> Developer belajar dari contoh.

---

## DP-L23 — Certification Program

```
Verified Agent · Trusted Plugin · Enterprise Ready
```

> Ini meningkatkan kepercayaan.

> ⚠️ Badge kepercayaan hanya bernilai kalau **syaratnya tertulis dan
> diperiksa**. *Verified* yang diberikan tanpa kriteria publik justru
> memindahkan risiko ke pengguna: mereka akan lebih percaya, padahal
> pemeriksaannya belum tentu lebih dalam.

---

## DP-L24 — Developer Community

```
Forum · Discord · Hackathon · Documentation · Templates
```

---

## DP-L25 — Enterprise Integration

Perusahaan bisa menghubungkan:

```
HR System · Calendar · Wellness Platform · Learning Platform
```

> ## Tetap melalui consent pengguna.

> ⭐ Kalimat penutup itu penting dan benar. Tapi ia perlu bentuk teknis, karena
> **HR System** adalah persis kasus **C-12**: persetujuan yang diberikan kepada
> pemberi kerja tidak pernah sepenuhnya bebas.
>
> Yang perlu ditetapkan sebelum satu integrasi HR pun dibangun:
> pemberi kerja melihat **agregat saja, tidak pernah per orang**; ambang minimum
> agregasi; jurnal dan mood **tidak pernah** masuk agregat; dan apa yang terjadi
> pada data pekerja saat ia keluar dari perusahaan.
