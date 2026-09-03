# 92 — §22–§24 Model Router, Evaluation & Audit Trail

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §22 — AI Model Router

> **Tidak semua request membutuhkan model paling mahal.**

```
Request
   ↓
Classifier
   ↓
┌───────────────┬──────────────┬───────────────┐
│ Simple        │ Reasoning    │ Multimodal    │
│               │              │               │
│ Small model   │ Large model  │ Vision model  │
└───────────────┴──────────────┴───────────────┘
```

| Permintaan | Rute |
|---|---|
| *"Catat mood saya"* | cheap model / **deterministic** |
| *"Analisis pola kebiasaan saya"* | reasoning model |
| *"Analisis foto outfit"* | vision model |
| *"Search semantic memory"* | embedding model |

Tujuannya: **Quality + Latency + Cost + Privacy**.

> ⭐ Kata **`deterministic`** untuk "catat mood" itu penting: bukan semua hal
> harus lewat model. Mencatat mood adalah `INSERT`, bukan inferensi.

---

## §23 — AI Evaluation

```
Agent Evaluation
│
├── Accuracy
├── Relevance
├── Personalization
├── Consistency
├── Safety
├── Latency
├── Cost
└── User Satisfaction
```

Contoh:

```
FashionAgent v1.4

Accuracy         91%
Relevance        88%
Personalization  94%
Safety           99%
Latency          1.8s
Cost             $0.00x
```

Jika versi baru **v1.5** menurunkan Personalization dan Safety:

```
Evaluation
    ↓
  Fail
    ↓
 Rollback
```

> **Jangan langsung production.**

---

## §24 — AI Audit Trail

Untuk setiap AI execution:

```
Request → Agent → Tools → Memory accessed
        → Decision → Action → Outcome
```

Disimpan sebagai **metadata audit** — bukan menyimpan *hidden chain-of-thought*
mentah.

```json
{
  "agent": "fashion-agent",
  "action": "recommend_outfit",
  "tools_used": [
    "weather.get",
    "wardrobe.search"
  ],
  "memory_scopes": [
    "fashion_preferences",
    "wardrobe"
  ],
  "decision": "outfit_342",
  "confidence": 0.91
}
```

> ⭐ Perhatikan `confidence` ikut tercatat di audit trail — Confidence Layer
> (§19) tersambung sampai ke jejak audit.
