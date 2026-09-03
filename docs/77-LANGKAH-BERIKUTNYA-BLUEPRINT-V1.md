# 77 — Langkah berikutnya: Blueprint Engineering v1.0

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Kata pemilik

> Langkah berikutnya yang paling tepat **bukan menambah fitur lagi**. Kita
> sudah memiliki cukup banyak visi.
>
> Sekarang kita harus mengubah visi ini menjadi **Blueprint Engineering v1.0**.

Isinya:

```
struktur repository final
100+ service/module
seluruh database schema
event schema
agent registry
MCP tools
API contract
AI agent specification
permission model
folder architecture
development phases
urutan task yang dapat langsung diberikan kepada AI coding agents
```

> Itu akan menjadi **master technical blueprint** yang benar-benar bisa dipakai
> untuk mulai membangun.

---

## ✅ Sudah ditulis — 3 September 2026

Pemilik menulis sendiri **Blueprint Engineering v1.0** pada hari yang sama,
sebagai **naskah kelima**. Isinya ada di berkas
[`80`](80-BLUEPRINT-IKHTISAR.md)–[`96`](96-SESUDAH-V0-DAN-TARGET-AKHIR.md).

Yang ia tutup: struktur repo final (**H-10**), Weather/Calendar sebagai tool
(**H-11**), empat penyimpanan bukan enam (**H-12**), V0–V6 sebagai rencana
kanonik (**H-13**), dan **Confidence Layer** sebagai jawaban angka-yang-tampak-
seperti-fakta (**H-14**).

Yang ia **belum** tutup, dan justru menjadi lebih mendesak karena Engineering
Spec akan mengunci skema: **A-19** (kini lima model angka pengguna),
**E-16..E-18** (model graf), **E-39** (memory: jenis atau nama scope), dan
**E-37** (tiga sistem skoring).

Langkah berikutnya menurut pemilik:
[`97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md`](97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md).

---

## Status

| Hal | Keadaan |
|---|---|
| Blueprint Engineering v1.0 | ✅ **selesai** — naskah 5, berkas `80`–`96` |
| Kode | **masih nol** |
| Keputusan pemblokir | lihat [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) |

> ⚠️ Naskah keempat sudah menjawab **A-2 (MVP = V0, 4–6 minggu)** dan
> **A-7 (nama = HumanVerse XOS)**. Tetapi sebelum blueprint ditulis, dua hal
> masih menentukan isinya:
>
> - **A-18** — Phase 1/2/3 atau V0–V6 yang jadi rencana kanonik?
> - **A-19** — empat model angka pengguna yang berbeda harus disatukan dulu,
>   karena blueprint akan mengunci skema basis datanya.
