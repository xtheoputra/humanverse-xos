# 167 — §10.8–§10.11 Audio, Voice, Video & Temporal Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.8 — Audio Intelligence

```
Audio
├── Speech Detection            ├── Sound Event Detection
├── Voice Activity Detection    ├── Acoustic Scene Classification
├── ASR                         ├── Audio Embedding
├── Speaker Diarization         └── Temporal Audio Analysis
└── Language Detection
```

```
Microphone → Voice Activity → Speech → ASR → Intent → Cognitive Runtime
```

User: *"Besok saya ada meeting jam sembilan."*

```
Speech → Text → Intent Extraction → Calendar Entity → Temporal Entity → Event
```

Kemudian: `MeetingCreated`

---

> ⭐ **Contoh ini menunjukkan jalur terpendek dari suara ke event domain** —
> dan `Temporal Entity` adalah langkah yang membuatnya benar: *"besok jam
> sembilan"* harus jadi timestamp mutlak sebelum masuk kalender, dan itu
> bergantung pada zona waktu pengguna (**A-3** / [#9](../../issues/9), pasar &
> bahasa awal, masih terbuka).

> 🛑 **`Speaker Diarization` berarti mikrofon memisahkan siapa berbicara — dan
> orang lain di ruangan ikut terekam.** Ini permukaan yang sama dengan §10.6
> tapi lewat telinga: percakapan di dalam rumah memuat suara pasangan, anak,
> tamu — orang yang tidak pernah menyetujui apa pun.
>
> Diarization justru **membuat masalahnya lebih tajam, bukan lebih ringan**:
> memisahkan pembicara berarti sistem punya representasi per orang, termasuk
> untuk orang yang bukan penggunanya. Model izin tidak punya kata untuk itu
> (**C-10** / [#40](../../issues/40)). Lihat **C-17** / [#75](../../issues/75).

> ⚠️ **`Acoustic Scene Classification`** menyimpulkan *di mana* seseorang
> berada dari suara latar — restoran, mobil, kantor. Itu penentuan lokasi
> tanpa izin lokasi. Kalau `Location` punya izin sendiri di §10.27, jalur ini
> semestinya tunduk pada izin yang sama.

---

## §10.9 — Voice Intelligence

> Voice menjadi **interface utama**.

```
Voice → VAD → Noise Reduction → ASR → Language Understanding → Intent
→ Cognitive Runtime → Response Generation → TTS → Voice Output
```

Tambahkan **Voice Session Memory** agar percakapan panjang tetap memiliki
context.

---

> ⭐ **`Voice Session Memory` mengisi tepat satu lubang di enam jenis memory
> H-16**: *Working Memory* adalah satu-satunya yang belum pernah punya contoh
> konkret di empat belas naskah. Sesi suara adalah contohnya — hidup selama
> percakapan, hilang sesudahnya.
>
> ⚠️ Yang perlu ditetapkan: **kapan ia berhenti**. Working memory yang tidak
> pernah kedaluwarsa berubah jadi episodic memory tanpa ada yang memutuskan
> begitu, dan ia memuat isi percakapan mentah — data paling sensitif yang
> disimpan paling longgar.

> ⚠️ **"Voice menjadi interface utama" adalah kenaikan lingkup yang tidak kecil
> untuk V0.** Dua belas fitur V0 tidak memuat suara sama sekali, dan
> [`../spec/04`](../spec/04-API-CONTRACTS.md) tidak punya satu pun endpoint
> audio. Ini Phase 10, jadi wajar — tapi kalimat *"interface utama"* sebaiknya
> tidak dibaca sebagai keputusan yang mendahului V0.

---

## §10.10 — Video Intelligence

> Video berbeda dengan image. Image: *"What is there?"* Video: *"What
> happened?"*

```
Video → Frame Sampling → Object Detection → Tracking → Pose
→ Temporal Modeling → Action Recognition → Event Detection
→ Sequence Understanding
```

Contoh:

```
Frame 1  Person sitting
Frame 2  Person stands
Frame 3  Person walks
Frame 4  Person picks object
Frame 5  Person leaves
```

Video engine menghasilkan:

```
Event: Person picked up object
```

---

> ⭐⭐ **Lima bingkai menjadi satu event — dan di situlah jawaban untuk masalah
> volume yang §10.30 tinggalkan terbuka.** Rantai ini melakukan **agregasi
> temporal**: yang keluar dari mesin video bukan lima `ObjectDetected`
> melainkan satu `Person picked up object`.
>
> Itu persis yang dibutuhkan supaya event persepsi bisa masuk ke bus yang sama
> dengan `habit.completed` — dan naskah tidak menyambungkan keduanya. Lihat
> **E-89** / [#74](../../issues/74).

> ⚠️ **`Frame Sampling` adalah keputusan biaya yang belum punya angka.** Satu
> per detik, satu per lima detik, atau hanya saat ada gerakan — pilihan itu
> menentukan biaya, energi, dan berapa banyak yang terlewat. Untuk *"person
> picks object"* satu per detik mungkin terlalu jarang; untuk *"person has been
> sitting 90 minutes"* (§10.11) satu per menit sudah cukup. **Dua kebutuhan
> yang berlawanan di satu aliran** — dan itu argumen untuk sampling adaptif,
> bukan satu angka.

---

## §10.11 — Temporal Intelligence

> HumanVerse harus memahami: **State + Change + Duration + Sequence**

```
10:00 sitting
10:30 sitting
11:00 sitting
11:30 walking
```

Bukan hanya *"Person detected"*, tetapi:

> *"Person has been detected in a relatively stable seated state for
> approximately 90 minutes."*

Data temporal kemudian bisa masuk ke **Behavior Engine**.

---

> ⭐⭐ **Kalimat itu adalah bentuk keluaran yang benar, dan ia menyelesaikan dua
> hal sekaligus.**
>
> 1. **Bahasa.** *"relatively stable"* dan *"approximately"* — ketidakpastian
>    ada di kalimatnya, bukan hanya di angka `confidence` di sebelahnya. Persis
>    aturan **may** §9.15.
> 2. **Volume.** Satu kalimat menggantikan 5.400 pembacaan (90 menit pada 1 Hz).
>    Ini agregasi yang sama seperti §10.10, dan lagi-lagi tidak disambungkan ke
>    §10.30.
>
> ⭐ Ia juga melengkapi **`change points`** §9.16: `11:30 walking` adalah titik
> perubahan, dan itu satu-satunya baris di deret itu yang benar-benar perlu
> disimpan sebagai event.

> 🛑 **Tetapi "90 menit" hanya bisa diketahui kalau kamera menyala 90 menit.**
> Dan §10.22 menuntut pola *"repeated over 30 days"*. Digabung dengan opsi izin
> **`Always`** yang baru muncul di §10.27, ini adalah **pemantauan
> berkelanjutan di dalam rumah** — bukan analisis atas foto yang dikirim
> pengguna.
>
> Bedanya bukan derajat, melainkan jenis. **C-1** menyangkut kategori data
> khusus dalam gambar; ini menyangkut **kehadiran seseorang yang terus
> dicatat**. Empat belas naskah belum pernah membahasnya. Lihat **C-17** /
> [#75](../../issues/75).

> ⚠️ **`Behavior Engine` menerima data temporal ini — dan B-14 berlaku penuh.**
> Kalau kamera mati dua jam, apakah itu *"tidak duduk"* atau *"tidak
> terobservasi"*? Deret waktu dari sensor punya lubang, dan lubang yang
> diperlakukan sebagai nilai akan menghasilkan pola palsu. Aturan yang sama
> seperti [#26](../../issues/26): **ketiadaan sinyal harus menurunkan
> `confidence`, bukan menjadi datum.**
