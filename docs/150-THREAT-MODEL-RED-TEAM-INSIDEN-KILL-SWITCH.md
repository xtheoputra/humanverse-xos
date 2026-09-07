# 150 — §8.32–§8.35 Threat Modeling, AI Red Team, Incident Response & Kill Switch

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.32 — Threat Modeling

Setiap fitur baru harus menjawab:

```
What can go wrong?
Who can attack it?
What data can leak?
What privilege can be abused?
What happens if AI is wrong?
What happens if agent is compromised?
What happens if external data is malicious?
```

> Framework seperti **STRIDE** dapat digunakan untuk software security,
> ditambah **AI-specific threat modeling**.

---

> ⭐ **Tiga pertanyaan terakhir adalah yang membedakan daftar ini dari
> checklist keamanan biasa.** STRIDE tidak punya kotak untuk *"bagaimana kalau
> AI-nya benar tapi salah"*. Pertanyaan **"What happens if AI is wrong?"**
> adalah satu-satunya tempat di dua belas naskah di mana **kesalahan yang
> jujur** — bukan serangan, bukan bug — diperlakukan sebagai risiko yang harus
> dirancang jalan keluarnya.
>
> Itu langsung menyentuh butir yang menggantung: **B-17** (satu salah hitung
> di Wardrobe Graph meracuni semua rekomendasi sesudahnya), **C-13**
> (*Identity Memory* permanen yang menguatkan dirinya sendiri), dan **B-14**
> (Context Engine gagal senyap). Ketiganya adalah *"AI is wrong"*, bukan
> *"AI is attacked"* — dan jawabannya sama: **jalur koreksi manusia**. Yang
> justru hilang dari §8.36; lihat **E-74**.

---

## §8.33 — AI Red Team

Sebelum agent production:

```
Normal tests
+
Adversarial tests
+
Prompt injection tests
+
Data leakage tests
+
Privilege escalation tests
+
Tool abuse tests
+
Hallucination tests
+
Safety tests
```

> Agent harus **"diserang" secara terkontrol** sebelum diberi akses nyata.

---

> ⭐ **Ini melengkapi `evaluation.gates` di
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) dari sisi yang berlawanan.**
> Gerbang evaluasi mengukur agent pada masukan **normal** (`safety >= 0.95`,
> `user_satisfaction >= 0.70`). Delapan uji di atas mengukurnya pada masukan
> yang **sengaja dibuat jahat**. Agent bisa lolos gerbang pertama dan runtuh
> di gerbang kedua — dan hanya gerbang kedua yang mewakili dunia nyata setelah
> marketplace dibuka.
>
> Yang perlu ditambahkan ke skema manifest: gerbang kedua ini juga harus punya
> ambang, sejajar `evaluation.gates`, supaya *"sudah di-red-team"* bisa
> diperiksa mesin dan bukan diakui sendiri.

---

## §8.34 — Incident Response

Jika terjadi **Data leak · Agent compromise · Security breach · Model abuse ·
Unauthorized action**, maka:

```
Detection
 ↓
Containment
 ↓
Revoke credentials
 ↓
Disable agent
 ↓
Block tools
 ↓
Preserve evidence
 ↓
Investigate
 ↓
Remediate
 ↓
Recovery
 ↓
Postmortem
```

---

> ⭐ **`Preserve evidence` menempatkan diri di urutan yang benar** — setelah
> penahanan, sebelum penyelidikan. Itu yang membuat `audit_logs` dan
> `security_events` (§8.40) berguna: keduanya harus **tidak ikut terhapus**
> saat agent dinonaktifkan.
>
> ⚠️ Dan di situlah ia bertabrakan dengan **C-9**: bukti yang harus
> dipertahankan adalah data pribadi juga. Rantai hapus §8.38 tidak menyebut
> satu pun dari tiga tabel log. Dua kewajiban yang sah, saling berlawanan,
> dan tidak ada yang menuliskan mana yang menang.

---

## §8.35 — Kill Switch

HumanVerse membutuhkan **Global AI Kill Switch**.

```
                HUMANVERSE
                    │
              AI CONTROL
                    │
              🚨 KILL SWITCH
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
   Stop Agents   Stop Tools   Stop Actions
```

> **Bahkan orchestrator tidak boleh dapat menonaktifkan mekanisme ini
> sendiri.**

---

> ⭐⭐ **Kalimat terakhir itu adalah kalimat keamanan terbaik di dua belas
> naskah.** Ia menyatakan bahwa ada satu bagian sistem yang **tidak boleh
> dikendalikan oleh bagian AI mana pun**, termasuk yang paling berkuasa. Itu
> membuat Kill Switch bukan sekadar tombol, melainkan **batas arsitektur** —
> dan ia yang membuat pemisahan Control Plane / Data Plane §8.42 punya alasan
> yang bisa dijelaskan dalam satu kalimat.

> ⚠️ **Tiga hal yang belum ditulis, dan tanpa ketiganya tombolnya tidak bisa
> dipakai:**
>
> | Pertanyaan | Kenapa perlu |
> |---|---|
> | **Siapa yang boleh menekan?** | Kalau hanya pemilik, maka tombolnya mati selama ia tidur. Perlu juga pemicu otomatis — mis. lonjakan `policy.violated` — yang boleh menekan sendiri. |
> | **Apa yang terjadi pada aksi R3/R4 yang sedang berjalan?** | *Stop Actions* di tengah transaksi finansial bisa lebih merugikan daripada membiarkannya selesai. Perlu aturan: batalkan, tuntaskan, atau tahan. |
> | **Bagaimana sistem kembali hidup?** | Tidak ada langkah *unkill*. Dan kalau menghidupkannya kembali semudah mematikannya, jaminan "orchestrator tidak bisa mematikan" jadi tidak berarti — ia tinggal menghidupkannya lagi. |
>
> Yang paling menentukan adalah yang ketiga: **jaminannya bukan pada tombol
> mati, melainkan pada tombol hidup.** Lihat **B-23**.

> ⚠️ **Kill switch dan jalur krisis tarik-menarik.** Kalau seluruh agent
> berhenti, apa yang terjadi pada pengguna yang saat itu sedang menulis
> sesuatu yang menandakan krisis (**C-3**)? Sistem yang berhenti total juga
> berhenti menolong. Jalur eskalasi ke manusia semestinya **bukan agent**,
> justru supaya ia selamat dari kill switch — tapi jalur itu belum ada sama
> sekali. Lihat **G-9** dan [#21](../../issues/21).
