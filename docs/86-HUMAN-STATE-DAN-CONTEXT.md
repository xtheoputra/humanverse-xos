# 86 — §9–§10 Human State Engine & Context Engine

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9 — Human State Engine

```json
{
  "energy": 0.62,
  "focus": 0.48,
  "motivation": 0.71,
  "stress": 0.34,
  "social_energy": 0.55,
  "physical_readiness": 0.76,
  "cognitive_load": 0.63
}
```

> Nilai tersebut **bukan diagnosis medis**. Itu adalah **internal probabilistic
> estimates** berdasarkan data yang tersedia.

Contohnya:

```
Sleep ↓
     ↓
Energy ↓
     ↓
Focus ↓
     ↓
Workout probability ↓
     ↓
Recommendation adjusted
```

> ⚠️ **`mood` hilang** dari HumanState dibanding naskah 4 (8 field → **7
> field**). Ini kemungkinan besar disengaja dan benar: *mood* punya event
> sendiri (`mood.logged`) dan tabel sendiri (`mood_entries`) — ia **dilaporkan
> pengguna**, bukan **ditaksir sistem**. Perlu konfirmasi. Lihat butir **E-34**.

---

## §10 — Context Engine

> AI **tidak boleh** menjawab berdasarkan profile saja.

```
User + Time + Location + Weather + Calendar
+ Recent Behavior + Goals + Current State
+ Preferences + History
```

Contoh:

```
07:00
+ Rain
+ Office day
+ Meeting 09:00
+ User prefers minimal style
+ Laundry unavailable
```

AI kemudian menghasilkan **outfit recommendation** — bukan sekadar menjawab
*"Hari ini tren fashion apa?"*
