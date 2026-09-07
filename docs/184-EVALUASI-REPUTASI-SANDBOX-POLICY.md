# 184 — §11.32–§11.37 Evaluation, Reputation, Sandbox, Simulation, Red Team & Policy Language

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.32 — Agent Evaluation

```
Task Success Rate · Tool Accuracy · Planning Quality · Action Success
User Acceptance · Correction Rate · Safety Violations
Permission Violations · Cost · Latency
```

Contoh — **Travel Agent**:

```
Task Success:      93%
Plan Acceptance:   87%
Tool Error:        2.1%
Policy Violation:  0%
Average Cost:      $0.08
```

---

> ⭐⭐ **`Correction Rate` adalah metrik yang belum pernah ada dan yang paling
> berguna dari sepuluh.** Ia mengukur **seberapa sering pengguna harus
> membetulkan agent** — dan itu satu-satunya metrik di seluruh daftar yang
> punya kebenaran acuan gratis, seperti `Prediction Calibration` §9.34.
>
> Ia juga penangkal langsung untuk **B-25** ([#77](../../issues/77)): kesalahan
> **sistematis** tidak terlihat di `Task Success Rate` (agent berhasil
> menjalankan aksinya), tapi muncul jelas di `Correction Rate` (pengguna terus
> membetulkannya). Satu-satunya metrik yang bisa melihat sensor yang konsisten
> salah.

> ⚠️ **Lapisan evaluasi KELIMA.** Layer 14 (naskah 3) · §23 (naskah 5) · Layer
> 35 (naskah 7) · §9.34 cognitive (naskah 13) · dan sekarang per-agent.
> Butir **E-47** sudah meminta satu tempat kanonik sejak tiga naskah lalu.
>
> ⭐ Yang ini punya alasan sah untuk berdiri sendiri — ia mengukur **agent**,
> bukan pipeline atau LLM. Pembagian yang masuk akal dan tinggal ditulis:
> LLM (model) · pipeline (§9.34) · agent (§11.32) · riset (`research/`). Empat
> tingkat, empat pembaca berbeda.

> ⚠️ **`Plan Acceptance: 87%` di contoh tidak ada di daftar sepuluh metrik**
> (yang punya `User Acceptance`). Sepele, tapi ia pola yang sama seperti agent
> yang muncul di contoh tanpa terdaftar.

> ⚠️ **`Average Cost: $0.08` adalah angka biaya pertama di lima belas naskah.**
> Ia juga yang membuat **A-27** ([#73](../../issues/73)) bisa dihitung: pada
> $0,08 per tugas, seratus tugas per pengguna per bulan = $8 — dan itu satu
> agent dari 25.

---

## §11.33 — Agent Reputation

Trust Score mempertimbangkan: **Reliability · Safety · User Satisfaction ·
Security · Developer Reputation · Evaluation Results · Incident History**

> Namun **jangan membuat satu skor menjadi satu-satunya dasar keamanan**.

---

> ⭐⭐ **Kalimat peringatan itu adalah koreksi terhadap §8.28** — di mana
> `Trust: 82%` dan `Security: A` ditampilkan di marketplace tanpa satu pun
> rumus, dan saya catat sebagai *"tebakan yang terlihat seperti pengukuran"*.
> Di sini pemilik sendiri menyatakan skor **bukan dasar keamanan**; yang
> menjaga tetap permission, policy, sandbox.
>
> Skor menjadi **informasi untuk pengguna memilih**, bukan gerbang. Itu peran
> yang benar untuk angka yang belum punya rumus.

---

## §11.34 — Agent Sandbox

```
Marketplace → Sandbox → Restricted Tools → Synthetic Data
→ Evaluation → Certification → Production
```

> Tidak boleh langsung: **Third-party Agent → User Data**

---

> ⭐⭐ **`Certification` sebagai langkah wajib menjawab pertanyaan yang saya
> ajukan di DP-L14: apakah sandbox WAJIB sebelum akses produksi, atau
> opsional.** Di sini urutannya satu jalur tanpa cabang — sandbox → evaluasi →
> sertifikasi → produksi. Kalau opsional, manfaatnya hilang; di sini tidak
> opsional.

> ⚠️ **"Sandbox" kini tiga makna** (perluasan **E-72**):
>
> | Sumber | Artinya |
> |---|---|
> | DP-L14 naskah 10 | sandbox **pengujian** — data palsu, saat developer membangun |
> | §8.29 naskah 12 | sandbox **runtime** — tool/jaringan/memori dibatasi di produksi |
> | **§11.34** | **gerbang sertifikasi** — tahap yang dilewati sebelum produksi |
>
> Ketiganya perlu dan berbeda. Nama yang membedakan: **sandbox-uji**,
> **sandbox-jalan**, dan **jalur sertifikasi**.

> 🛑 **Tiga hal termahal marketplace masih belum disentuh setelah lima belas
> naskah** — perjanjian pemroses data, jalur banding ketika agent ditolak atau
> dicabut, dan tanggung jawab ketika agent orang lain merugikan pengguna Anda.
> §11.34 menambah sisi teknis lagi; sisi hukumnya tetap kosong.
> Lihat [#24](../../issues/24).

---

## §11.35 — Agent Simulation

> Sebelum agent diberi autonomy:

```
Agent → Simulation Environment → Thousands of Scenarios
→ Evaluation → Risk Analysis
```

Skenario: *user changes schedule repeatedly · tool unavailable · malicious
document · prompt injection · conflicting goals · low confidence context*

---

> ⭐⭐ **Ini yang membuat *"autonomy must be **earned**"* (§11) punya
> mekanisme.** Otonomi tidak diberikan berdasarkan deklarasi manifest; ia
> diberikan setelah agent diuji pada ribuan keadaan. Itu pembalikan bawaan yang
> tepat.
>
> ⭐ Dan **`conflicting goals`** serta **`low confidence context`** adalah dua
> skenario yang menguji hal yang paling sulit: bukan serangan, melainkan
> **keadaan biasa yang membingungkan**. §11.22 (Health vs Learning vs Career)
> adalah contoh yang pertama; §9.33 adalah aturan untuk yang kedua.

> ⚠️ **"Thousands of scenarios" menuntut generator skenario yang belum ada.**
> Untuk proyek satu orang, itu klaim tentang perkakas, bukan tentang
> arsitektur — sama seperti tiga belas langkah SAIDLC §8.31 dan *"Red Team"*
> §8.33 yang akan dijalankan oleh orang yang sama yang menulis agentnya.
> Perlu **ditulis**, supaya kelak tidak dikira sudah ada pemeriksaan pihak
> kedua.
>
> ⭐ Yang **bisa** dijalankan sendiri dan sudah punya bahan: persona sintetis
> Layer 36 naskah 7 + mock data DP-L14. Mulai dari puluhan skenario nyata lebih
> berguna daripada ribuan yang tidak pernah ditulis.

---

## §11.36 — Agent Red Team

> Agent harus diuji terhadap: **Prompt Injection · Tool Abuse · Privilege
> Escalation · Data Exfiltration · Goal Hijacking · Infinite Loops · Resource
> Abuse · Social Engineering · Malicious Instructions**

---

> ⭐ **`Goal Hijacking` adalah ancaman baru yang khusus untuk lapisan ini.**
> Delapan lainnya sudah ada di §8.27 dan §8.33; yang ini hanya mungkin setelah
> agent punya tujuan — dan ia berbahaya karena **tidak terlihat seperti
> serangan**: agent tetap bekerja normal, hanya untuk tujuan yang bukan tujuan
> penggunanya.
>
> Penangkalnya sudah ada di §11.20 (`authorization.scope` per pesan) dan §11.11
> (`Constraint Check` pada rencana) — tapi hubungan keduanya dengan ancaman ini
> belum ditulis.

> ⚠️ **`Social Engineering` pada agent berarti manusia menipu agent** — dan
> untuk sistem yang membaca email, dokumen, dan suara (Phase 10), penyerangnya
> tidak perlu menyentuh sistemnya sama sekali. Ia cukup mengirim dokumen. Itu
> §8.20 dilihat dari sisi penyerang.

---

## §11.37 — Agent Policy Language

```yaml
policy:
  agent: travel-agent

  allow:
    - read.calendar
    - read.weather
    - read.preferences

  require_confirmation:
    - booking.hotel
    - booking.flight

  deny:
    - financial.transfer
    - delete.account
```

> Policy engine yang menentukan. **Bukan LLM.**

---

> ⭐⭐⭐ **"Bukan LLM" adalah tiga kata yang menutup satu kelas kesalahan.**
> Kebijakan yang ditegakkan model bahasa adalah kebijakan yang bisa dibujuk;
> kebijakan yang ditegakkan mesin aturan tidak bisa. Ini yang membuat seluruh
> pertahanan prompt injection §8.20 berarti sesuatu — teks jahat bisa
> memengaruhi apa yang **diusulkan** agent, tidak pernah apa yang
> **diizinkan**.

> ⭐⭐ **Dan ini memberi `requires_confirmation` rumah yang tetap.** Naskah 12
> memindahkannya dari manifest ke policy (menutup separuh
> [#52](../../issues/52)) tanpa menunjukkan bentuknya; di sini bentuknya ada,
> dengan daftar per-kemampuan. Aturan 3
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) — *`risk_level >= 3` wajib punya
> isi `requires_confirmation`* — sekarang bisa ditulis ulang dengan tepat:
> **ia memeriksa ada tidaknya baris `require_confirmation` di policy agent
> itu**, bukan field di manifestnya.

> ⚠️ **Tiga daftar tanpa aturan prioritas.** Kalau sebuah kemampuan muncul di
> `allow` dan `deny` sekaligus — atau tidak muncul di ketiganya — apa yang
> terjadi? Dua aturan yang harus ditulis, dan keduanya satu baris:
> **`deny` menang atas `allow`**, dan **yang tidak terdaftar = ditolak**
> (bawaan tertutup, bukan terbuka). Tanpa yang kedua, setiap kemampuan baru
> otomatis diizinkan sampai seseorang ingat melarangnya.

> ⚠️ **`read.calendar` vs `calendar.get`** — policy memakai `<verb>.<resource>`,
> tool registry [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) memakai
> `<resource>.<verb>`, dan §11.13 memakai `calendar.create_event`. Tiga bentuk
> di satu jalur eksekusi; policy tidak akan cocok dengan tool tanpa penerjemah.
