# 104 — Layer 27–29: UX Intelligence, Interaction Model & Conversation Framework

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 27 — UX Intelligence

> **AI membantu UX.**
>
> Misalnya: user selalu membuka dashboard. AI bisa **memindahkan shortcut**
> yang sering digunakan.
>
> Tetapi:
> - perubahan harus **transparan**,
> - **bisa dibatalkan**,
> - **tidak membingungkan**.

> ⭐ Tiga syarat itu penting justru karena antarmuka yang berubah sendiri
> adalah salah satu cara termudah membuat orang merasa kehilangan kendali —
> lawan langsung dari *"Manusia tetap menjadi pusat sistem"*.

---

## Layer 28 — Human Interaction Model

| Mode | Isi |
|---|---|
| **Chat Mode** | Percakapan alami dengan AI |
| **Voice Mode** | Asisten suara real-time |
| **Vision Mode** | Kamera untuk outfit, makanan, atau objek |
| **Dashboard Mode** | Insight visual dan laporan |

> **Semua memakai context yang sama.**

> ⚠️ Voice dan Vision ada di **V5** (naskah 5 §33). V0 hanya punya Chat dan
> Dashboard.

---

## Layer 29 — AI Conversation Framework

> Setiap percakapan memiliki **struktur**.

```
User Input
    ↓
Intent Detection
    ↓
Context Retrieval
    ↓
Memory Retrieval
    ↓
Planning
    ↓
Agent Execution
    ↓
Response
    ↓
Feedback
    ↓
Memory Update
```

> Ini membuat chat tetap **konsisten**.

> ⭐ Sembilan langkah ini adalah versi paling lengkap dari alur yang sebelumnya
> muncul terpisah-pisah (naskah 2 workflow, naskah 4 §13 orchestrator,
> naskah 5 §13). **Intent Detection** dan **Memory Update** belum pernah
> disebut sebelumnya — keduanya menutup lingkaran belajar.
>
> ⚠️ Tidak ada langkah **Safety/Risk** di rantai ini, padahal naskah 4 §17
> menempatkan *Safety Classifier → Risk Engine → Policy Engine* tepat sebelum
> aksi, dan naskah 5 §12 punya SafetyAgent. Lihat butir **E-45**.
