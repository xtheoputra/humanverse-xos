# 202 — Agent Runtime, AI Kernel, Model Router & Edge (naskah ketujuhbelas)

> Merekam **§13.17–§13.22**.

---

## §13.17 — Personal Agent Runtime

Phase 11 memiliki Agent Runtime. Phase 13 membungkusnya menjadi **Personal
Agent Runtime**.

```
HumanOS
   ↓
Agent Runtime
   ↓
Agent Pool
   ├── Coach
   ├── Planner
   ├── Career
   ├── Learning
   ├── Finance Behavior
   ├── Health
   ├── Travel
   └── Lifestyle
```

Tetapi semuanya tetap melalui:

```
Policy · Permission · Risk · Budget · Audit · Verification
```

> ⭐⭐⭐ **Enam gerbang disebut ulang secara utuh, dan `Budget` termasuk di
> dalamnya.** Ini pemanggilan ulang pengaman Phase 11 yang paling lengkap di
> naskah ini. Bahwa `Budget` ikut disebut penting: **H-6** mengakui biaya
> inferensi berlipat, dan Budget adalah satu-satunya gerbang yang menahannya.

> ⚠️ **Delapan agent, dan `Finance Behavior` ada di antaranya.** Naskah 12
> menempatkan `travel-agent purchase` di R4. `Travel` dan `Finance Behavior`
> sebagai agent tetap di kolam yang sama menuntut kejelasan: apakah keduanya
> punya `autonomy.max_level` yang lebih rendah daripada `Coach`? Manifest §11.5
> menyediakan medannya; naskah ini tidak mengisinya untuk satu agent pun.

---

## §13.18 — Personal AI Kernel

```
                    PERSONAL AI
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Context           Memory          Digital Twin
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                     Reasoning
                         ↓
                     Planning
                         ↓
                    Simulation
                         ↓
                     Decision
                         ↓
                      Agency
```

> ⭐ **Rantainya berakhir di `Agency`, bukan `Action`.** Agency adalah nama
> Phase 11, jadi diagram ini menyerahkan langkah terakhir ke lapisan yang sudah
> punya gerbangnya sendiri, alih-alih membuat jalur eksekusi baru.

---

## §13.19 — Model Router

HumanOS tidak boleh menggunakan model terbesar untuk semuanya.

```
Task → Complexity → Risk → Latency → Cost → Model Selection
```

| Tugas | Model |
|---|---|
| Simple classification | small model |
| OCR | vision model |
| Speech | ASR model |
| Reasoning | strong reasoning model |
| **High-risk decision** | **multi-model verification** |

> ⭐⭐⭐ **`Risk` adalah masukan kedua bagi pemilih model, dan keputusan
> berisiko tinggi diverifikasi lebih dari satu model.** Ini menjawab **H-6**
> (biaya inferensi) dan keselamatan dengan satu mekanisme: yang murah untuk yang
> ringan, yang mahal hanya untuk yang berbahaya. Model Router memang sudah
> dijadwalkan; di sini ia mendapat aturan pemilihannya.

---

## §13.20 — Personal AI Model Layer

> Jangan langsung berpikir: *"Kita harus melatih LLM sendiri."*

Lebih baik:

```
Foundation Models
        +
Personal Context + Personal Memory + Digital Twin
        +
Behavior Model + Preference Model + World Model
        +
User Feedback
        ↓
Personal Intelligence
```

Model menjadi **interchangeable**.

> ⭐⭐ **Penolakan eksplisit untuk melatih model sendiri, dari pemilik.** Ini
> keputusan berbiaya besar yang diambil ke arah yang murah, dan ia menjaga pagu
> **B-2**. Layak dinaikkan menjadi butir keputusan (**H**) alih-alih dibiarkan
> sebagai kalimat di tengah naskah — karena ini persis jenis keputusan yang
> tergerus diam-diam oleh naskah berikutnya.

---

## §13.21 — Local AI / Edge HumanOS

Sebisa mungkin data sensitif diproses **locally**.

```
                 HUMAN DEVICE
                     │
             ┌───────┴───────┐
             ↓               ↓
          Edge AI          Cloud AI
             │               │
       Sensitive/basic     Advanced
       processing          reasoning
```

| Di perangkat | Di cloud |
|---|---|
| Wake word | Large reasoning |
| VAD | |
| Basic vision | |
| Privacy filtering | |

> ⭐⭐ **`Privacy filtering → device` adalah penempatan yang benar dan sering
> salah.** Menyaring data sensitif **sebelum** ia meninggalkan perangkat berarti
> cloud tidak pernah memegangnya. Ini menguatkan Phase 8 dan **C-18** (RF/Wi-Fi
> sensing menangkap orang yang tidak memakai HumanVerse).

> ⚠️ **"Sebisa mungkin" bukan aturan.** Kalimat pembukanya menyerahkan
> keputusan ke pelaksana. Yang perlu ditulis: kelas data mana yang **tidak
> pernah** boleh meninggalkan perangkat — bukan mana yang sebaiknya tidak.

---

## §13.22 — Device Abstraction Layer

```
HumanOS
   ↓
Device Abstraction
   ├── Smartphone   ├── Laptop     ├── Desktop
   ├── Smartwatch   ├── Earbuds    ├── Camera
   ├── IoT          ├── Smart Home └── Sensors
```

> Agent tidak perlu tahu detail hardware.

> ⭐ **Abstraksi perangkat sebagai lapisan tersendiri menjaga agent tetap tidak
> tahu apa-apa soal hardware** — itu juga yang membuat izin bisa ditegakkan di
> satu tempat, bukan di setiap agent.

> 🛑 **`Camera`, `Smart Home`, dan `Sensors` membawa seluruh isi C-18 ke dalam
> Phase 13.** Butir itu mencatat bahwa penginderaan RF **menangkap orang yang
> tidak memakai HumanVerse dan tidak bisa menyadarinya** — tamu, anak, pasangan,
> tetangga di balik dinding. Daftar perangkat di sini menyebutnya sebagai baris
> biasa, sejajar dengan `Laptop`.
>
> Yang minimum harus ditulis sebelum satu baris kode, sesuai C-18: penginderaan
> semacam ini hanya menghasilkan **hitungan/kehadiran anonim**, tidak pernah
> identitas, dan datanya tidak masuk graf siapa pun selain penggunanya.
