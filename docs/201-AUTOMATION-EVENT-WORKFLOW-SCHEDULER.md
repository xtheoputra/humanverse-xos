# 201 — Automation, Event Bus, Workflow & Scheduler (naskah ketujuhbelas)

> Merekam **§13.11–§13.16**.

---

## §13.11 — Personal Automation Engine

Contoh: *"Kalau saya selesai olahraga, ingatkan saya minum dan review jadwal."*

```
WorkoutCompleted
       ↓
Check Context
       ↓
Check State
       ↓
Trigger Rule
       ↓
Notification
```

Lebih advanced:

```
WorkoutCompleted
       ↓
Energy > 0.7
       ↓
No urgent meeting
       ↓
Suggest learning session
```

> ⚠️ **`Energy > 0.7` — angka pengguna KEENAM, dan skalanya bertabrakan dengan
> §13.15.** Di sini energi berskala **0–1**; di §13.15 ia berskala **0–100**
> (anggaran harian 100). Di §13.29 Control Center ia ditampilkan sebagai
> **72%**. Tiga penulisan untuk satu besaran di satu naskah.
>
> **E-37** sudah mencatat *tiga sistem skoring dengan skala berbeda* sebagai
> salah satu dari empat butir yang **mengunci Engineering Spec**. Ini
> menambahnya, dan kali ini tabrakannya **di dalam satu naskah**, bukan
> antar-naskah — jadi ia bisa diselesaikan tanpa menunggu keputusan pemilik yang
> besar: cukup pilih satu skala.

> ⭐ **Automasi berhenti di `Suggest`, bukan `Schedule`.** Tingkat otonominya
> L1 (Recommend), bukan L4. Itu bawaan yang benar untuk aturan yang dibuat
> pengguna sendiri.

---

## §13.12 — Event-Driven HumanOS

```
                 EVENT BUS
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Habit        Calendar      Health
     Agent         Agent        Agent
       │            │            │
       └────────────┼────────────┘
                    ▼
              Cognitive Core
```

Events:

```
GoalCreated        GoalChanged        TaskCompleted
HabitCompleted     WorkoutCompleted   SleepStarted
SleepEnded         MeetingStarted     MeetingEnded
MoodChanged        LocationChanged    EnergyChanged
DeadlineApproaching
RecommendationAccepted
RecommendationRejected
```

> ⭐⭐ **`RecommendationAccepted` / `RecommendationRejected` adalah dua event
> paling berharga di daftar ini.** Keduanya menutup gelang umpan balik: tanpa
> mereka, sistem tidak pernah tahu sarannya berguna atau tidak. **B-19**
> (agency diuji dengan apa) dan seluruh *learning loop* Phase 12 bergantung pada
> sinyal semacam ini.

> 🛑 **`Calendar Agent` dan `Health Agent` — H-11 tergerus untuk keputusan
> KEENAM.** **H-11** / [#78](../../issues/78) menutup *"Weather & Calendar =
> TOOL, bukan agent"*. **E-94** mencatat naskah 15 menggerusnya dengan mengirim
> `{"to": "weather-agent"}`. Diagram ini menaruh **`Calendar Agent`** sejajar
> dengan `Habit Agent` di event bus — konstruksi yang sama, sekali lagi.
>
> Enam naskah berturut-turut memperlakukan kalender sebagai agent. Pada titik
> ini H-11 bukan tergerus, melainkan **tidak pernah dipakai**. Yang perlu
> diputuskan bukan lagi *"tool atau agent"* melainkan *"apakah keputusan H-11
> dicabut"*.

---

## §13.13 — Personal Workflow Engine

HumanOS bukan hanya menjalankan single action. Ia menjalankan **workflow**.

```
Goal → Workflow → Tasks → Agents → Tools → Verification → Outcome
```

Contoh: *"Plan a vacation"*

```
Travel Intent
 ↓
Destination Research
 ↓
Budget Analysis
 ↓
Weather
 ↓
Calendar
 ↓
Flight Search
 ↓
Hotel Search
 ↓
Simulation
 ↓
Compare
 ↓
Recommendation
 ↓
Confirmation
 ↓
Booking
```

> ⭐⭐ **`Verification` berdiri sebagai kotak tersendiri sebelum `Outcome`.**
> Itu sejalan dengan state machine §13.36 (`EXECUTING → VERIFYING → COMPLETED`)
> dan dengan tuntutan Phase 11 bahwa hasil tindakan harus diperiksa, bukan
> diasumsikan.

> 🛑 **`Booking` adalah eksekusi finansial yang tidak bisa ditarik, dan
> rantainya hanya dijaga satu kotak `Confirmation`.** Menurut §11.15 ini R3
> (*financial transaction*) atau R4 (*irreversible*). Kalau R4, ia **`DENY`** —
> dan alur ini tidak boleh berakhir di `Booking` sama sekali tanpa tindakan
> pengangkatan tingkat yang terpisah. Ini contoh konkret dari penggerusan yang
> dicatat di [§13.10](200-LIFE-GRAPH-CAPABILITY-DAN-PERMISSION.md).

---

## §13.14 — Personal Scheduler

Traditional scheduler: *time availability*. HumanOS scheduler:

```
Time + Energy + Focus + Cognitive Load + Priority + Goal
+ Deadline + Context + Preference + Recovery
```

Contoh:

| Jenis tugas | Ditaruh di |
|---|---|
| High-focus task | morning |
| Administrative task | low-energy period |
| Exercise | recovery-compatible period |

> ⚠️ **"High-focus task → morning" adalah asumsi kronotipe yang ditulis sebagai
> aturan.** Tidak semua orang berpuncak di pagi hari. Sistem yang mengaku
> memodelkan energi individu sebaiknya **menurunkan** jam puncak dari data
> orangnya, bukan menetapkannya. Ini kecil sekarang, tapi ia akan menjadi bawaan
> yang sulit dicabut begitu penjadwal dibangun di atasnya.

---

## §13.15 — Energy-Aware Operating System

HumanOS dapat membuat **Energy Budget**:

```
Daily Energy = 100

Work             -35
Study            -20
Gym              -15
Social           -10
Travel           -10
Buffer            10
```

> Kemudian sistem tidak menjadwalkan manusia seperti komputer tanpa batas.

> ⭐⭐⭐ **Ini prinsip terbaik di seluruh naskah ketujuh belas.** Sebuah
> penjadwal yang punya **anggaran** tidak bisa mengisi kalender sampai penuh —
> batasnya struktural, bukan imbauan. Kalimat penutupnya layak naik menjadi
> prinsip produk.

> 🛑 **Tetapi angka-angkanya tidak punya produsen.** 100, −35, −20, −15, −10,
> −10, +10: dari mana? Diukur, disetel pengguna, atau ditaksir model? **A-19**
> mencatat lima model angka pengguna tanpa satu pun rumus; ini yang keenam.
> Anggaran energi lebih berbahaya daripada skor lain karena ia **menolak
> pekerjaan** — kalau angkanya salah, sistem akan menolak sesuatu yang
> sebenarnya sanggup dikerjakan, dan pengguna akan mematikan fiturnya.
>
> Yang minimum harus ditulis: apakah 100 itu tetap untuk semua orang, dan apakah
> biaya per aktivitas dipelajari atau dipatok.

---

## §13.16 — Attention OS

Notifications · Messages · Tasks · Meetings · Recommendations · Alerts

diprioritaskan berdasarkan:

```
importance · urgency · goal relevance · risk
context · attention cost · notification fatigue
```

Output:

```
NOW · LATER · DIGEST · SILENT · ASK
```

> ⭐⭐ **`notification fatigue` sebagai masukan, bukan sebagai keluhan.** Sistem
> yang menghitung kelelahan perhatian sebagai biaya adalah kebalikan dari
> aplikasi yang mengejar keterlibatan. Ini sejalan dengan prinsip proyek, dan
> pantas dijaga saat monetisasi akhirnya dibahas (**A-27**: proyek ini punya
> model biaya yang diakui dan **nol fase pendapatan**).

> ⚠️ **`ASK` di daftar keluaran attention bertabrakan makna dengan `ask` di
> tangga risiko.** Di sini ia berarti *"tanya pengguna kapan ini sebaiknya
> ditampilkan"*; di `spec/05` `ask` berarti *"minta konfirmasi sebelum
> bertindak"*. Satu kata, dua gerbang berbeda — dan keduanya akan muncul di
> kode yang sama.
