# 57 — §13–§14 Komunikasi Antar-Agent & Memory Policy

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §13 — Agent-to-Agent Communication

> **Agent tidak boleh saling berbicara secara liar.** Gunakan protocol.

```
FashionAgent
      │
      │ request
      ▼
WeatherAgent
      │
      │ result
      ▼
FashionAgent
```

Pesan:

```json
{
  "from": "FashionAgent",
  "to": "WeatherAgent",
  "type": "weather_request",
  "context_id": "ctx_123",
  "payload": {
    "date": "tomorrow"
  }
}
```

Semua communication:

- authenticated
- logged
- traceable
- permission-controlled

---

## §14 — Agent Memory Policy

> **Tidak semua agent boleh membaca semua memory.**

### Fashion Agent

| | Isi |
|---|---|
| **Boleh** | fashion preferences · wardrobe · style history |
| **Tidak boleh otomatis** | private journal · financial account · medical records |

### Finance Agent

| | Isi |
|---|---|
| **Boleh** | budget · transactions · financial goals |
| **Tidak boleh** | private conversations |

> **Ini sangat penting.**
