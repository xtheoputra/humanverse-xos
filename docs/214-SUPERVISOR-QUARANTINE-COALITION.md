# 214 — §14.27–§14.32 Supervisor, Watchdog, Quarantine, Simulation Lab, Collective Red Team & Coalition Security

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.27–§14.28 — Agent Supervisor & Watchdog

Supervisor mendeteksi: **infinite loop · tool abuse · privilege escalation ·
abnormal behavior**, dan memonitor **cost · latency · policy violations**;
dapat **menghentikan agent · revoke credential · quarantine**.

```
Agent → Watchdog → Behavior Monitoring → Anomaly Detection
→ Policy Monitoring → Action
```

Tindakan: **ALLOW · WARN · PAUSE · THROTTLE · REVOKE · QUARANTINE · KILL**

---

> ⭐⭐ **Tujuh tindakan — dan `WARN` serta `THROTTLE` adalah dua yang belum ada
> di §11.24** (yang langsung dari deteksi ke `Freeze → Revoke → Notify →
> Audit`).
>
> Keduanya mengisi jarak yang selama ini kosong: sebuah agent yang **agak**
> tidak normal tidak harus dibekukan. `THROTTLE` khususnya tepat untuk
> `Excessive cost` dan `High latency` — dua gejala yang biasanya bukan serangan
> melainkan kesalahan, dan yang jawabannya memperlambat, bukan menghentikan.
>
> Tangga tujuh langkah ini juga sejajar dengan tangga risiko: **tindakan
> pengawas sebanding dengan seberapa yakin ia bahwa ada yang salah.**

> ⚠️ **`Supervisor` dan `Watchdog` masih dua benda dengan tugas yang hampir
> sama** — keberatan yang sama seperti §11.23/§11.24, dan masih belum
> dijelaskan bedanya. §11.38 mendaftarkan `Watchdog` sebagai komponen runtime
> dan **tidak** mendaftarkan `Supervisor`; §14.51 tidak mendaftarkan keduanya
> secara terpisah. Salah satunya belum punya rumah.

---

## §14.29 — Agent Quarantine

```
PRODUCTION → SUSPICIOUS → QUARANTINE → FORENSICS → EVALUATION
→ RESTORE / RETIRE
```

> Agent **tidak langsung dihapus**. Ini penting untuk audit.

---

> ⭐⭐⭐ **"Tidak langsung dihapus" adalah aturan yang menyelamatkan
> penyelidikan — dan ia melengkapi §8.34 `Preserve evidence`.**
>
> Menghapus agent yang berbuat salah adalah refleks yang wajar dan salah:
> bersamanya hilang manifest, riwayat pesan, jejak delegasi, dan bukti
> bagaimana ia sampai ke sana. `QUARANTINE → FORENSICS` menahan semuanya.
>
> ⭐ Dan `RESTORE` sebagai keluaran yang setara dengan `RETIRE` mengakui sesuatu
> yang jarang ditulis: **sebagian besar perilaku mencurigakan ternyata bukan
> serangan.** Sistem yang hanya bisa mematikan akan mematikan terlalu banyak.

> ⚠️ **Karantina agent federasi tidak bisa dijalankan seperti agent internal.**
> Agent yang berjalan di mesin orang lain tidak bisa "dibekukan" — yang bisa
> dicabut hanyalah **aksesnya**. Bedanya perlu ditulis, karena `QUARANTINE`
> untuk agent eksternal berarti *"putus koneksi dan tahan buktinya"*, bukan
> *"tahan prosesnya"*.

---

## §14.30–§14.31 — Simulation Lab & Collective Red Team

```
Agent → Sandbox → Synthetic Environment → Scenario Simulation
→ Adversarial Testing → Red Team → Evaluation → Certification
```

> **Bukan hanya menguji satu agent.** Kita menguji rantai `Agent A → B → C →
> Tool → External Service`, karena **vulnerability dapat muncul dari kombinasi
> agent, bukan satu agent**.

Contoh: A punya izin **baca**, B punya izin **tulis**.

```
A → data
A → B
B → external system
```

> Maka diperlukan **Cross-Agent Security Policy**.

---

> ⭐⭐⭐ **Contoh tiga baris itu adalah kelas kerentanan yang belum pernah
> disebut di delapan belas naskah — dan tidak satu pun gerbang yang ada bisa
> melihatnya.**
>
> Setiap gerbang memeriksa **satu agent pada satu waktu**: risk gate
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md), Action Gateway §11.14, Security
> Mesh §14.20. Semuanya akan meluluskan A (hanya membaca) dan meluluskan B
> (hanya menulis, dengan data yang diberikan padanya). **Gabungan keduanya
> adalah eksfiltrasi**, dan tidak ada pemeriksa yang melihat gabungan.
>
> Ini juga alasan teknis di balik prinsip §14.64: **collective risk > individual
> risk**. Di sini ia bukan slogan melainkan contoh yang bisa diperagakan.

---

## §14.32 — Agent Coalition Security

> HumanVerse harus bisa mendeteksi: *"Apakah beberapa agent sedang membentuk
> jalur privilege escalation?"*

```
Agent A → Agent B → Agent C → Sensitive Database
```

> **Graph-based policy engine** dapat mendeteksi jalur tersebut.

---

> ⭐⭐⭐ **Ini menjawab persis catatan yang saya tulis di berkas
> [`181`](181-MULTI-AGENT.md) tentang §11.20:**
>
> > Aturan yang belum ditulis, dan ia satu kalimat: *lingkup pesan tidak boleh
> > lebih luas daripada lingkup pengirimnya.* Tanpa itu, agent berlingkup
> > sempit bisa meminta agent lain melakukan hal yang ia sendiri tidak boleh —
> > **privilege escalation lewat delegasi**, yang §8.27 daftarkan sebagai
> > penyalahgunaan tapi belum punya penangkalnya di jalur ini.
>
> Naskah ini memberi **dua** penangkal, bukan satu:
>
> | Pendekatan | Bagian |
> |---|---|
> | **Aturan** — delegasi tidak boleh melampaui kewenangan pendelegasi | §14.42 · §14.43 |
> | **Deteksi** — graf kapabilitas mencari jalur eskalasi | §14.32 · §14.33 |
>
> Yang pertama mencegah; yang kedua menangkap yang lolos. Keduanya dibutuhkan,
> dan bersama-sama mereka menutup celah yang saya catat.

> 🛑 **Tetapi deteksi berbasis graf buta persis di tempat risikonya paling
> tinggi: batas federasi.**
>
> Graf kapabilitas hanya bisa memuat agent yang kapabilitasnya **diketahui**.
> Untuk agent internal, itu manifest yang tervalidasi registry. Untuk agent
> **federasi** (§14.4), kapabilitas **dideklarasikan sendiri** oleh agent yang
> berjalan di mesin orang lain — dan §14.5 bahkan menaruh `trust_level` di
> dalam deklarasi itu.
>
> Artinya: `A → B → C → Sensitive Database` bisa dideteksi selama A, B, dan C
> internal. Begitu salah satunya eksternal, jalurnya **hilang dari graf** —
> bukan karena tidak ada, melainkan karena satu simpulnya tidak melaporkan apa
> yang benar-benar bisa ia lakukan.
>
> Tiga hal yang perlu ditulis dan masing-masing satu baris: **kapabilitas agent
> federasi diverifikasi di gerbang, bukan dipercaya** (§14.19 sudah punya
> langkahnya) · **jalur yang memuat simpul eksternal diperlakukan sebagai
> jalur berisiko lebih tinggi**, bukan setara · dan **agent eksternal tidak
> boleh menjadi perantara** antara dua agent internal. Lihat **B-28** /
> [#94](../../issues/94).
