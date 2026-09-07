# 185 — §11.38–§11.41 Agent Runtime, State Machine, Task Graph & Long-Running Agents

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.38 — Agent Runtime

```
Agent Runtime
├── Agent Loader        ├── Permission Manager   ├── Watchdog
├── Agent Registry      ├── Policy Engine        ├── Budget Engine
├── Capability Manager  ├── Risk Engine          ├── Audit Logger
├── Context Manager     ├── Execution Engine     └── Feedback Engine
├── Memory Manager      ├── Verification Engine
├── Planner             │
├── Task Scheduler      │
└── Tool Manager        │
```

---

> ⚠️ **Enam belas komponen, dan lima di antaranya sudah punya rumah di pohon
> lain:** `Policy Engine` (`security/policy-engine/`), `Risk Engine`
> (`security/risk-engine/`), `Permission Manager` (`security/permissions/`),
> `Memory Manager` (`intelligence/memory-engine/`), `Planner`
> (`intelligence/planning/`).
>
> Bacaan yang masuk akal — dan yang sebaiknya ditulis — adalah bahwa runtime
> **memanggil**, tidak **memiliki**: `security/` punya mesinnya, `agents/`
> punya kliennya. Itu juga yang §11.51 (Agent Control Plane) isyaratkan, dan
> yang §8.42 wajibkan (*kode agent tidak boleh mengimpor `security/`* —
> pemanggilannya lewat gerbang). Lihat **E-97**.

> ⚠️ **`Supervisor` §11.23 tidak ada di daftar ini**, sementara `Watchdog` ada.
> Salah satu dari dua pengawas belum punya rumah — atau keduanya benda yang
> sama dengan dua nama.

---

## §11.39 — Agent State Machine

```
CREATED → INITIALIZING → READY → PLANNING → WAITING_POLICY
→ WAITING_PERMISSION → READY_TO_EXECUTE → EXECUTING → VERIFYING
→ COMPLETED → LEARNING
```

Kegagalan:

```
EXECUTING → FAILED → RECOVERING → REPLANNING
```

Kritis:

```
ANY STATE → ABORTED
```

---

> ⭐⭐ **`ANY STATE → ABORTED` adalah satu baris yang memberi Kill Switch
> §8.35 bentuk teknisnya di tingkat agent.** Tidak ada keadaan yang kebal
> dihentikan — termasuk `EXECUTING`. Itu yang membuat *"revocable"* di prinsip
> pembuka bisa dijalankan, bukan diniatkan.

> ⭐ **`WAITING_POLICY` dan `WAITING_PERMISSION` sebagai keadaan terpisah**
> menegaskan bahwa keduanya hal yang berbeda (§11.14 juga memisahkannya):
> policy bisa menolak selamanya, izin bisa datang belakangan dari pengguna.
> Sebuah agent yang menunggu izin **bukan** agent yang gagal.

> ⚠️ **Bandingkan dengan mesin keadaan kognitif §9.29** (`RECEIVED →
> UNDERSTANDING → CONTEXT_LOADING → RETRIEVING → REASONING → PLANNING →
> POLICY_CHECK → DECISION → ACTION → OBSERVATION → LEARNING`). Dua mesin
> keadaan untuk satu permintaan, dengan nama berbeda untuk langkah yang sama:
>
> | §9.29 kognitif | §11.39 agent |
> |---|---|
> | `POLICY_CHECK` | `WAITING_POLICY` + `WAITING_PERMISSION` |
> | `ACTION` | `EXECUTING` |
> | `OBSERVATION` | `VERIFYING` |
> | `REQUIRES_CONFIRMATION` | `WAITING_PERMISSION` |
>
> Keduanya bisa hidup bersama kalau dinyatakan bahwa **§9.29 adalah keadaan
> PERMINTAAN dan §11.39 adalah keadaan AGENT** — satu permintaan bisa
> melibatkan beberapa agent, masing-masing dengan keadaannya sendiri. Kalau
> tidak dinyatakan, dua mesin keadaan akan dibangun untuk hal yang sama.

> ⚠️ **`REPLANNING` kembali ke mana?** Alur kegagalan berakhir di `REPLANNING`
> tanpa panah balik. Kemungkinan besar ke `PLANNING`, dan itu berarti putaran
> — yang §11.24 pantau sebagai `Infinite loop` dan §11.25 batasi dengan
> *bounded retry*. Batas jumlah replan perlu ada di mesin keadaan ini, bukan
> hanya di penanganan kegagalan.

---

## §11.40 — Agent Task Graph

> Jangan selalu memakai linear workflow. Gunakan **DAG**:

```
                Goal
          ┌──────┼──────┐
       Task A  Task B  Task C
          └──┬───┴──┬───┘
             ↓      ↓
            Task D
              ↓
            Result
```

> Ini memungkinkan **parallel execution**.

---

> ⭐ **DAG menjelaskan kenapa `Plan Verification` §11.11 dibutuhkan.** Dalam
> alur linear, memeriksa tiap aksi satu per satu hampir cukup. Dalam DAG, tiga
> tugas berjalan **bersamaan** — dan tiga aksi R1 yang paralel bisa melanggar
> anggaran yang tidak dilanggar satu pun di antaranya. Gerbang per-aksi tidak
> bisa melihat itu; `Budget Check` §11.14 harus **atomik** terhadap eksekusi
> paralel, atau anggaran akan terlampaui oleh balapan.

> ⚠️ **Eksekusi paralel dan Action Gateway belum dinyatakan hubungannya.**
> Kalau Task A, B, C masing-masing memicu konfirmasi manusia, pengguna akan
> mendapat tiga pertanyaan sekaligus — dan §11.28 Action Center perlu tahu
> bahwa ketiganya milik satu rencana. Tanpa itu, persetujuan terasa seperti
> hujan pemberitahuan, yang persis dilawan §11.43.

---

## §11.41 — Long-Running Agents

> Agent bisa mempunyai task panjang. Contoh goal: *Improve learning
> consistency* — bukan selesai dalam satu request.

Agent memiliki **Persistent Task** dengan: `schedule · state · checkpoint ·
memory · deadline · success criteria`

```
Monday:    Plan
Tuesday:   Observe
Wednesday: Adapt
Thursday:  Evaluate
Sunday:    Review
```

---

> ⭐⭐ **`success criteria` sebagai field wajib adalah yang paling menentukan di
> daftar itu** — dan ia yang membuat `Plan Verification` §11.11 punya sesuatu
> untuk diverifikasi. Sebuah tugas panjang tanpa kriteria sukses tidak bisa
> selesai; ia hanya bisa berhenti.
>
> ⚠️ Tapi bentuknya tidak pernah didefinisikan di lima belas naskah. Untuk
> *"improve learning consistency"*, kriterianya bisa berupa: jumlah sesi per
> minggu, rentetan hari, atau rasio rencana-vs-terlaksana. Ketiganya mengukur
> hal yang berbeda, dan agent akan mengoptimalkan yang mana pun dipilih.

> ⭐ **`checkpoint` menjawab pertanyaan yang belum diajukan:** apa yang terjadi
> pada tugas tujuh hari kalau sistem mati di hari ketiga. Bersama `resumable`
> §11.10, ini satu-satunya tempat di lima belas naskah yang menangani
> **pemulihan setelah gagal total**, bukan hanya gagal per aksi.

> 🛑 **Agent yang berjalan seminggu membuat B-14 menjadi struktural.**
> Butir itu mencatat: Context Engine menyentuh cuaca, kalender, lokasi, dan
> wearable terus-menerus, dan kegagalannya akan **senyap** — rekomendasi tetap
> keluar, hanya jadi salah.
>
> Untuk permintaan sekali jalan, kesalahan itu terlihat segera. Untuk tugas
> Senin-sampai-Minggu, sinyal yang mati hari Rabu menghasilkan **`Review` hari
> Minggu yang dibangun dari dua hari data** — dan tidak ada apa pun di §11.41
> yang mewajibkan agent menyadarinya.
>
> Aturan yang dibutuhkan sama dengan yang saya usulkan di
> [#26](../../issues/26), kini pada tugas: **`Evaluate` wajib melaporkan berapa
> bagian jendela waktunya benar-benar terobservasi**, dan `confidence` review
> turun sebanding. Lihat **B-26** / [#83](../../issues/83).

> 🛑 **Dan ini komponen pertama yang berjalan tanpa diminta.** Empat belas
> naskah menggambarkan sistem yang menjawab; `schedule` di sini berarti sistem
> yang **bekerja sendiri sepanjang minggu**. Konsekuensinya nyata dan belum
> dibahas: biaya berjalan terus (dijawab sebagian oleh Budget Engine §11.18),
> dan pengamatan berjalan terus — yang menyentuh **C-17** dari sisi yang
> berbeda. Lihat **A-28** / [#80](../../issues/80).
