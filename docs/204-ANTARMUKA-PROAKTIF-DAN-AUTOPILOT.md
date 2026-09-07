# 204 — Control Center, Chat, Voice, Proaktif & Life Autopilot (naskah ketujuhbelas)

> Merekam **§13.29–§13.33**.

---

## §13.29 — HumanOS Control Center

```
┌─────────────────────────────────────┐
│           HUMANVERSE                │
│                                     │
│  Good morning.                      │
│                                     │
│  Energy       72%                   │
│  Focus        81%                   │
│  Goal         64%                   │
│                                     │
│  TODAY                              │
│  ───────────────────────────────    │
│  09:00 Work                         │
│  13:00 Meeting                      │
│  17:30 Gym                          │
│  20:00 AI Learning                  │
│                                     │
│  AI INSIGHTS                        │
│  ───────────────────────────────    │
│  Your workload is higher today.     │
│                                     │
│  [View Plan] [Simulate]             │
└─────────────────────────────────────┘
```

> 🛑 **Tiga angka di layar utama, nol keyakinan, nol produsen.** `Energy 72%`,
> `Focus 81%`, `Goal 64%` adalah hal PERTAMA yang dilihat pengguna setiap pagi.
> **A-19** mencatat lima model angka pengguna tanpa satu pun berumus; ini
> menaikkannya jadi enam **dan** menempatkannya di posisi paling dipercaya di
> seluruh produk.
>
> **B-15/B-1 — Confidence Layer sudah ditutup sebagai keputusan**: angka
> taksiran harus membawa keyakinannya. Layar ini melanggarnya secara langsung.
> Ironisnya §13.3 memberi objek `intent` medan `confidence` sejak awal — jadi
> mekanismenya ada; ia hanya tidak dipakai di tempat ia paling dibutuhkan.
>
> ⚠️ Ditambah: `72%` di sini vs `Energy > 0.7` di §13.11 vs `Daily Energy = 100`
> di §13.15 — **tiga skala untuk satu besaran, di dalam satu naskah** (lihat
> [`201`](201-AUTOMATION-EVENT-WORKFLOW-SCHEDULER.md)).

> ⭐ **`[Simulate]` sebagai tombol setara `[View Plan]`.** Phase 12 menjadi
> sesuatu yang bisa disentuh pengguna, bukan mesin latar. Itu keputusan produk
> yang bagus dan konsisten dengan posisi Phase 13 sebagai lapisan operasi.

---

## §13.30 — Personal AI Chat

Chat bukan lagi *"Tanya AI"*, tetapi **command center untuk HumanOS**.

User: *"Apa yang harus saya lakukan hari ini?"*

HumanOS mengambil: Calendar + Goals + Tasks + Energy + Context + Deadlines +
Behavior + Weather + Digital Twin → lalu menghasilkan plan.

> ⚠️ **Sembilan sumber ditarik untuk satu pertanyaan.** §13.5 sendiri menuntut
> *"context harus scoped"*. Sebuah pertanyaan sepele seperti *"apa yang harus
> saya lakukan hari ini?"* yang menarik `Behavior` dan `Digital Twin` sekaligus
> adalah bentuk yang paling mungkin melanggar scoping — dan justru bentuk yang
> paling sering dipakai.

---

## §13.31 — Voice HumanOS

User dapat berbicara:

- *"Besok jadwalkan belajar AI dua jam."*
- *"Saya terlalu banyak kerja minggu ini."*
- *"Tolong siapkan rencana untuk menyelesaikan project ini."*

```
Voice → Intent → Cognitive Runtime → Plan → Policy → Action
```

> ⭐ **`Policy` tetap berada sebelum `Action`,** dan kali ini urutannya benar —
> berbeda dari rantai §13.10 yang menaruh `Risk` sesudah `Policy`.

> ⚠️ **Suara melewatkan satu gerbang yang ada di jalur lain: `Confirmation`.**
> §13.4 (teks) berakhir `Ask Confirmation → Execute`; §13.31 (suara) berakhir
> `Policy → Action`. Suara adalah kanal yang **paling mudah disalahdengar** dan
> paling mungkin dipicu orang lain di ruangan yang sama — ia butuh konfirmasi
> lebih banyak, bukan lebih sedikit.

---

## §13.32 — Proactive HumanOS

> Ini bagian yang membuat sistem terasa seperti personal AI, bukan chatbot.

HumanVerse mendeteksi:

```
Deadline approaching
+
Current workload high
+
Energy decreasing
+
Historical pattern = procrastination
```

Kemudian:

> *"Deadline project Anda tinggal 3 hari. Berdasarkan workload saat ini, ada
> risiko terlambat. Saya menemukan dua jadwal alternatif. Mau saya tampilkan?"*

> **Bukan langsung melakukan sesuatu.**

> ⭐⭐⭐ **Kalimat penutupnya adalah pengaman terbaik di seluruh naskah, dan ia
> ditulis pemilik.** Proaktivitas adalah tempat paling mudah sebuah sistem
> berubah dari membantu menjadi mengatur; menetapkan bahwa keluarannya adalah
> **tawaran**, bukan tindakan, menahannya di **L1 (Recommend)**.
>
> ⚠️ Satu hal yang perlu ditulis: *"Historical pattern = procrastination"*
> adalah **penilaian tentang karakter pengguna** yang disimpan dan dipakai
> sistem. Itu berbeda kelas dari mencatat jam tidur. Ia butuh `sensitivity` yang
> tinggi (§13.6 menyediakan medannya), dan pengguna sebaiknya bisa melihat serta
> membantahnya — kalau tidak, sistem membentuk pendapat tentang orang yang tidak
> pernah bisa dikoreksi orang itu.

---

## §13.33 — Life Autopilot

```
USER GOAL → HUMANOS → UNDERSTAND → SIMULATE → PLAN
          → EXECUTE → MONITOR → ADAPT
```

Namun autonomy tetap:

```
L0 Observe
L1 Recommend
L2 Prepare
L3 Confirm
L4 Bounded Autonomy
```

sesuai **Phase 11**.

> ⭐⭐⭐ **Tabrakan penomoran PALING BERBAHAYA tidak kambuh.** **E-77 /
> [#67](../../issues/67)** — dua tangga 0–4 dengan arti terbalik di ujung atas —
> ditutup di naskah 15. Naskah ini **memanggil tangga L dan menyebut sumbernya**
> alih-alih mendefinisikan ulang. Setelah lima naskah yang menggerus keputusan
> tertutup, satu yang mengutip dengan benar layak dicatat.

> ⚠️ **Tetapi dua anak tangga berganti nama.** §11.16 menulis **L3 — Ask
> Confirmation** dan **L4 — Execute within Boundaries**; di sini keduanya jadi
> **L3 Confirm** dan **L4 Bounded Autonomy**. Artinya sama dan urutannya sama,
> jadi ini bukan penggerusan — tapi repo ini sudah punya enam sumbu penomoran
> yang bertabrakan, dan mengganti nama anak tangga yang baru saja distabilkan
> menambah gesekan tanpa menambah kejelasan. Pakai nama §11.16.

> 🛑 **`EXECUTE` berdiri tanpa gerbang di rantai utamanya.** Rantai
> `PLAN → EXECUTE → MONITOR` tidak memuat `POLICY_CHECK` maupun
> `WAITING_CONFIRMATION`, padahal state machine §13.36 memuat keduanya di antara
> `PLANNING` dan `EXECUTING`. Tangga L disebut **di bawah** diagram, bukan
> **di dalam**-nya. Diagram inilah yang akan disalin orang; ia sebaiknya memuat
> gerbangnya sendiri.
