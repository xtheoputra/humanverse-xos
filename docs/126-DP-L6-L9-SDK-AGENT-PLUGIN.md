# 126 — DP-L6–L9: SDK, Agent SDK, Manifest Standard & Plugin SDK

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L6 — HumanVerse SDK

```
sdk/
├── typescript/   ├── kotlin/   ├── go/
├── python/       ├── swift/    └── rust/
├── flutter/
```

```typescript
const client = new HumanVerseClient({ apiKey: process.env.HV_KEY })
const habits = await client.habits.list()
```

```python
client = HumanVerse()
client.habits.list()
```

> Developer tidak perlu memanggil HTTP manual.

> ⚠️ **SDK naik dari 5 bahasa jadi 7** — `go` dan `rust` baru. Butir **B-11**
> (setiap perubahan kontrak agen harus dirilis ke semua bahasa sekaligus)
> menjadi ×7. Dan naskah 5 §58 menempatkan Developer SDK di **V6**, jadi ini
> beban yang jauh dari sekarang — tapi jumlahnya sebaiknya diputuskan saat
> memilih, bukan bertambah tiap naskah.

---

## DP-L7 — Agent SDK

> Ini **berbeda** dari API SDK. Tujuannya: **membuat AI Agent**.

```
agent-sdk/
├── runtime/   ├── manifest/   ├── evaluation/
├── memory/    ├── testing/    └── packaging/
├── tools/
```

```python
class FashionAgent(HumanAgent):
    def run(self, context):
        return Recommendation(...)
```

SDK mengurus: **memory · tool · logging · evaluation**.

> ⭐ Memasukkan `evaluation/` dan `testing/` ke dalam SDK **membuat benchmark
> jadi bagian dari membuat agent**, bukan pekerjaan terpisah yang mudah
> dilewati. Sejalan dengan Pillar 13 naskah 9.

---

## DP-L8 — Agent Manifest Standard

```yaml
name: fashion-agent
version: 1.0

capabilities:
  - recommend_outfit

tools:
  - weather
  - wardrobe

memory:
  read:
    - wardrobe

permissions:
  - wardrobe.read
```

> **Ini menjadi standar marketplace.**

---

> 🛑 **Manifest versi keempat — dan justru dua pengaman terpentingnya hilang.**
>
> | Field | naskah 4 §11 | naskah 5 §14 | naskah 10 DP-L8 |
> |---|---|---|---|
> | `purpose` | ✅ | ✅ | ❌ |
> | `risk_level` | ✅ (`low`) | ✅ (angka 0–4) | ❌ **hilang** |
> | `requires_confirmation` | — | ✅ | ❌ **hilang** |
> | `memory.write` | ✅ | ✅ | ❌ |
> | `permissions` | — | — | ✅ baru |
>
> `risk_level` dan `requires_confirmation` adalah dua field yang membuat aksi
> agent bisa dikendalikan — dan keduanya menghilang **tepat di manifest yang
> ditetapkan sebagai standar marketplace**, yaitu tempat agent **pihak ketiga**
> masuk. Di situlah keduanya paling dibutuhkan, bukan paling tidak.
>
> `permissions: [wardrobe.read]` juga menduplikasi `memory.read: [wardrobe]` —
> dua tempat menyatakan hal yang sama akan berbeda cepat atau lambat.
>
> Lihat butir **E-60**. Skema validasi di
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) mempertahankan keduanya.

---

## DP-L9 — Plugin SDK

> Tidak semua developer ingin membuat agent. Ada yang hanya membuat **plugin**.

```
Spotify · Google Calendar · Notion · Strava
```

```yaml
plugin:
  name: spotify
permissions:
  - music.read
```

> ℹ️ `music.read` menyambung dengan domain **Music** yang muncul di Pillar 2
> naskah 9 — sampai sekarang masih tanpa modul, agent, maupun tabel.
>
> ⚠️ Keempat contoh plugin adalah **integrasi keluar** ke layanan pihak ketiga.
> Arah datanya (masuk saja, atau dua arah) belum ditetapkan — dan itu
> menentukan apakah plugin bisa **mengirim** data pengguna ke Spotify/Notion,
> bukan hanya membaca darinya.
