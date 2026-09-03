# 58 — §15–§17 Permission Engine, Risk Engine & Human Safety Layer

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15 — Permission Engine

```
User
 │
 ▼
Consent
 │
 ▼
Permission Engine
 │
 ├── Read
 ├── Write
 ├── Execute
 ├── Share
 └── Delete
```

Contoh: **Fashion Agent meminta akses kamera.** User menjawab:

- *Allow once*
- *Allow while using Fashion*
- *Deny*

---

## §16 — Agent Risk Engine

> **Tidak semua action sama risikonya.**

| Level | Jenis | Contoh dari pemilik |
|---|---|---|
| **0** | Informasi | *"Cuaca besok 30°C."* |
| **1** | Rekomendasi | *"Kamu bisa memakai outfit ini."* |
| **2** | Action reversibel | *"Tambahkan workout ke task list."* |
| **3** | Action berdampak | *"Booking hotel."* |
| **4** | High-impact | tindakan yang menyangkut keputusan medis, keuangan besar, atau tindakan hukum |

> Level 4 **harus ada Explicit Confirmation.**

---

## §17 — Human Safety Layer

```
User Request
      ↓
Agent
      ↓
Safety Classifier
      ↓
Risk Engine
      ↓
Policy Engine
      ↓
Action
```

### Batas untuk health

> AI boleh membantu **tracking** dan memberikan **edukasi umum**.
> Tetapi **tidak boleh berpura-pura menjadi dokter** atau membuat diagnosis
> definitif.

### Batas untuk finance

> AI boleh membantu **analisis perilaku finansial**.
> Tetapi **jangan menjanjikan return investasi**.
