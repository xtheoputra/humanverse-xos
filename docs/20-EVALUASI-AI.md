# 20 — AI Evaluation System

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Setiap agent memiliki evaluator.**

---

## Contoh — Fashion Agent

Evaluator bertanya:

- apakah outfit cocok?
- apakah warna sesuai?
- apakah cuaca cocok?

**Evaluator memberi skor.**

---

## Bentuk kasar

```
   Agent  ──▶  keluaran  ──▶  Evaluator  ──▶  skor
                                  │
                                  └──▶ Feedback Learning
                                       (tahap 8 AI Pipeline)
```
