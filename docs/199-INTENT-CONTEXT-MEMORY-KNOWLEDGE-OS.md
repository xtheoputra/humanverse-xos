# 199 — Intent, Context, Memory & Knowledge OS (naskah ketujuhbelas)

> Merekam **§13.3–§13.7**.

---

## §13.3 — Human Intent Engine

> Ini salah satu komponen terpenting.

User tidak harus memberikan instruksi teknis. Misalnya:
*"Aku ingin hidup lebih teratur."*

HumanOS harus mengubahnya menjadi:

```
Intent
 ↓
Goal
 ↓
Objectives
 ↓
Constraints
 ↓
Metrics
 ↓
Plan
 ↓
Actions
```

Intent object:

```yaml
intent:
  id:
  user_id:
  type:
  description:
  desired_outcome:
  constraints:
  preferences:
  urgency:
  confidence:
```

> ⭐ **`confidence` ada sejak medan pertama.** Itu sejalan dengan **Confidence
> Layer** (**B-15**/**B-1**) yang sudah ditutup: setiap angka taksiran harus
> membawa keyakinannya. Intent adalah tempat paling awal keyakinan bisa hilang,
> dan naskah ini menaruhnya di sana.

> ⚠️ **Tidak ada `purpose` dan tidak ada `scope`.** Intent adalah objek yang
> memicu seluruh rantai — Goal → Plan → Actions → tool. §8 menuntut setiap
> pengambilan data punya `purpose` yang dinyatakan; kalau intent tidak
> membawanya, `purpose` harus disintesis di suatu tempat di hilir, dan tempat
> itu tidak ditunjuk.

---

## §13.4 — Natural Language → Life Command

HumanOS menyediakan semacam **Life Command Interface**.

Contoh: *"Atur minggu depan supaya saya punya waktu belajar AI 10 jam."*

```
Parse Intent
      ↓
Calendar Analysis
      ↓
Goal Analysis
      ↓
Energy Analysis
      ↓
Constraint Analysis
      ↓
Simulation
      ↓
Generate Schedule
      ↓
Ask Confirmation
      ↓
Execute
```

> ⭐⭐ **Rantainya berakhir di `Ask Confirmation → Execute`, bukan langsung
> `Execute`.** Itu konsisten dengan tangga L (§11.16) dan dengan state machine
> §13.36 yang memuat `WAITING_CONFIRMATION`. Pengaman terpasang di contoh, bukan
> cuma di bab keamanan — itu tanda yang bagus.

---

## §13.5 — Personal Context OS

HumanOS harus selalu mengetahui context yang relevan:

Time · Location · Calendar · Activity · Weather · Energy · Mood · Focus ·
Goals · Deadlines · Relationships · Environment · Device · Current Task ·
Historical Pattern

> Tetapi: **context harus scoped**, bukan berarti AI bebas membaca semua data.
> Ini mengikuti architecture Phase 8.

> ⭐⭐⭐ **Pengaman Phase 8 dipanggil ulang dengan tegas, dan oleh pemilik
> sendiri.** Kalimat *"context harus scoped"* menutup jalan pembacaan bahwa
> daftar lima belas item di atas adalah izin baca menyeluruh. Ini kebalikan dari
> pola yang sudah empat kali terjadi (naskah baru menghapus pengaman diam-diam)
> — di sini naskah baru **menguatkan** pengaman naskah lama.

> ⚠️ **`Weather` muncul lagi sebagai bagian context.** **H-11** / [#78](../../issues/78)
> menutup *"Weather & Calendar = TOOL"*, dan **E-94** mencatat H-11 sudah
> tergerus keputusan keempat. Di sini keduanya tampil sebagai *sumber context*,
> bukan tool — konstruksi yang sama yang menggerus H-11 sebelumnya. Perlu
> ditegaskan: context **diambil melalui** tool, atau context adalah lapisan
> tersendiri yang boleh punya sumbernya sendiri.

---

## §13.6 — Personal Memory OS

Memory sekarang menjadi **OS-level service**:

Working Memory · Short-Term · Episodic · Semantic · Procedural · Behavioral ·
Preference · Goal Memory · Decision Memory · Relationship Memory ·
Project Memory

Setiap memory memiliki:

```
owner
scope
purpose
confidence
sensitivity
retention
source
timestamp
```

> ⭐⭐⭐ **`purpose` ADA di sini, dan bersanding dengan `scope`, `sensitivity`,
> dan `retention`.** Delapan medan ini adalah bentuk terkuat yang pernah ditulis
> untuk objek memory di tujuh belas naskah. **E-73** mengeluhkan §10.3 hanya
> punya `classification` dan `retention`; ini menjawabnya melampaui yang diminta.

> 🛑 **Sebelas jenis memory — sebelumnya EMPAT PENYIMPANAN, bukan enam.**
> **A-10** ditutup dengan *"empat penyimpanan bukan enam"*. Daftar ini memberi
> sebelas **jenis**. Jenis dan penyimpanan tidak harus satu lawan satu, dan
> **E-39** persis menanyakan itu: *memory dibedakan sebagai jenis atau sebagai
> nama scope?* Naskah ini menambah tujuh nama baru tanpa menjawab pertanyaan
> yang sudah dua kali diajukan, dan **E-39 adalah salah satu dari empat butir
> yang masih mengunci Engineering Spec** karena ia menentukan skema basis data.

---

## §13.7 — Personal Knowledge OS

HumanOS memiliki knowledge layer yang menggabungkan:

```
Personal Knowledge
+
General Knowledge
+
Domain Knowledge
+
Situational Knowledge
+
World Knowledge
```

Contoh:

```
User wants AI career
       ↓
Personal Skill Graph
       ↓
AI Knowledge Graph
       ↓
Current Industry Knowledge
       ↓
Career Simulation
```

> ⚠️ **Lapisan pengetahuan keenam yang tidak punya pemilik.** *World Knowledge*
> dan *Current Industry Knowledge* datang dari luar pengguna, tetapi naskah ini
> tidak menyebut dari mana, seberapa segar, atau dengan lisensi apa. **C-**
> (risiko hukum) sudah memuat butir tentang penerbitan ulang sumber luar; sebuah
> *knowledge layer* yang mencampur pengetahuan pribadi dengan pengetahuan dunia
> akan mewarisi seluruh pertanyaan itu, dan di sini ia belum disebut sama sekali.
