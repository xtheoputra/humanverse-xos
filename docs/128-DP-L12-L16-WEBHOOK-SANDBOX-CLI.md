# 128 — DP-L12–L16: Webhook, Subscription, Sandbox, CLI & Packaging

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L12 — Webhook Platform

```
habit.completed · goal.completed · outfit.selected · journal.created
```

```
HumanVerse → Webhook → Developer Server
```

Tambahkan: **retries · signature verification · idempotency**.

> ⭐⭐ **Ini menjawab issue #38 (format nama event).**
>
> Keempat event di atas memakai **dua segmen**, dan yang paling menentukan:
> naskah 7 Layer 22 menulis event yang **sama persis** sebagai
> `fashion.outfit.selected` (tiga segmen), sedangkan naskah ini menulisnya
> **`outfit.selected`**.
>
> Sekarang **dua naskah memakai dua segmen** (naskah 5 dengan 21 event, naskah
> 10 dengan 7 event) melawan **satu naskah tiga segmen**. Format dua segmen
> juga yang sudah dipakai di
> [`../spec/03`](../spec/03-EVENT-CONTRACTS.md).
>
> ⭐ **`retries`, `signature verification`, dan `idempotency`** disebut
> bersamaan — ketiganya memang harus datang bersama, dan `idempotency` sudah
> punya bentuknya di `events.idempotency_key`.
>
> 🛑 **`journal.created` dikirim ke server developer pihak ketiga.** Meski
> muatannya hanya `word_count` (aturan [`../spec/03`](../spec/03-EVENT-CONTRACTS.md)),
> keberadaan event itu sendiri memberi tahu pihak ketiga **kapan seseorang
> menulis jurnal** — pola waktu yang cukup mengungkap. Lihat **C-14**.

---

## DP-L13 — Event Subscription

```yaml
subscriptions:
  - habit.completed
  - goal.completed
  - workout.completed
```

> **Tidak semua event dikirim.**

> ⭐ Langganan eksplisit (bukan kirim-semua) adalah bentuk minimalisasi data
> yang benar, dan membuat izin bisa diperiksa per event.

---

## DP-L14 — Testing Sandbox

Mock data: **fake user · fake wardrobe · fake habits · fake goals**.
Sehingga testing **aman**.

> ⭐⭐ **Ini butir yang paling menjawab A-15/C-7** (beban hukum marketplace).
> Sandbox berarti developer bisa membangun dan menguji **tanpa pernah menyentuh
> data orang sungguhan**. Dipadukan dengan persona sintetis Pillar 36 naskah 7,
> ini jalur yang benar.
>
> ⚠️ Yang perlu ditegaskan: apakah sandbox **wajib** sebelum akses produksi
> diberikan, atau opsional. Kalau opsional, manfaatnya hilang.

---

## DP-L15 — Local Development CLI

```
hv init · hv login · hv run · hv test · hv publish
```

```
hv init fashion-agent
→ fashion-agent/
    README · manifest · agent.py · tests
```

> ⭐ `tests` ikut dibuat oleh `hv init` — pengujian jadi bawaan, bukan tambahan.

---

## DP-L16 — Agent Packaging

```
fashion-agent.hvap
```

Isi: **manifest · code · prompts · assets · tests**

> Marketplace membaca package ini.

> ⚠️ Format paket belum menyebut **tanda tangan** dan **checksum**. Untuk
> berkas yang berisi kode dan prompt yang akan berjalan di atas data pribadi,
> keduanya wajib — kalau tidak, tidak ada cara membuktikan paket yang dipasang
> sama dengan yang direview (**DP-L18**).
