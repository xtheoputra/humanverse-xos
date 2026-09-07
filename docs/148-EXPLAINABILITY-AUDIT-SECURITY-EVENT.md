# 148 — §8.24–§8.27 Explainability, Audit Trail, Security Event Pipeline & Abuse Prevention

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.24 — AI Explainability

User harus dapat bertanya:

> *"Kenapa kamu merekomendasikan ini?"*

Response dapat berupa:

```
Recommendation:
Workout ringan

Why:
• Tidur Anda lebih pendek dari rata-rata minggu ini
• Aktivitas kemarin cukup tinggi
• Anda memiliki target konsistensi olahraga

Confidence:
72%

Data used:
Sleep
Activity
Workout history
Goal
```

Bukan raw chain-of-thought. Kita memberikan:

> **Concise decision rationale** — bukan private reasoning trace.

---

> ⭐⭐ **`Data used` adalah bagian yang paling bernilai, dan belum pernah ada.**
> Naskah 4 §29 memberi *"Why"*; di sini pengguna juga melihat **data apa yang
> dipakai untuk sampai ke sana**. Itu membuat Privacy Center (§8.36) dan
> penjelasan menjadi satu benda: pengguna tidak hanya tahu siapa yang mengakses
> datanya, tapi **untuk apa akses itu dipakai**.

> ⚠️ **`Confidence: 72%` adalah skala keempat, dan ia memperburuk E-37.**
> Sekarang berjalan bersamaan: bobot **persen** (naskah 2) · Outfit Score
> **100 poin** (naskah 3) · Recommendation Score **0–1** (naskah 5) ·
> confidence **persen** di sini · **Trust Score persen** dan **Security Score
> huruf A** (§8.28) · dan **R0–R4** (§8.16). Spesifikasi menyimpan 0–1 karena
> persen dan 100-poin bisa diturunkan darinya tanpa kehilangan apa pun.
> Yang **ditampilkan** boleh persen; yang **disimpan** sebaiknya tetap satu.
> Lihat [#32](../../issues/32).
>
> Dan butir **H-14** masih menunggu hal yang sama seperti empat naskah lalu:
> ambang **High / Medium / Low** dan cara menghitung `confidence` itu sendiri.
> `72%` adalah angka pertama yang pernah muncul — tapi contoh bukan ambang.
> Lihat [#34](../../issues/34).

---

## §8.25 — AI Audit Trail

Setiap keputusan penting dicatat:

```
Request
Agent
Model
Version
Tools
Data categories accessed
Policy result
Risk score
Recommendation
User confirmation
Action
Outcome
```

Contoh:

```json
{
  "agent": "habit-agent",
  "model": "model-x",
  "risk": "R1",
  "data_accessed": [
    "habits",
    "sleep"
  ],
  "decision": "recommend_low_intensity",
  "policy": "ALLOW",
  "user_action": "accepted"
}
```

---

> ⭐ **Enam field baru yang berguna**: `Model`, `Version`, `Policy result`,
> `Risk score`, `Action`, `Outcome`. `Model` + `Version` menjawab pertanyaan
> yang tidak bisa dijawab sebelumnya — *"rekomendasi buruk itu keluar dari
> model yang mana"* — dan itu prasyarat *Automatic Rollback* (**B-10**).
> `Outcome` melengkapi `User action`: sistem akhirnya mencatat **apa yang
> terjadi setelahnya**, bukan hanya apa yang diputuskan.

> 🛑 **Tetapi *alasan ringkas* hilang, dan H-7 ditutup atas dasar itu.**
> Naskah 4 §45 menulis dua hal sekaligus: *"tidak perlu menyimpan
> chain-of-thought privat"* **dan** *"yang disimpan adalah audit metadata
> **dan alasan ringkas yang dapat diverifikasi**"*. Daftar dua belas field di
> atas memuat metadata-nya, tetapi **tidak satu pun alasan**.
>
> §8.24 memang memberi alasan — kepada **pengguna**, saat itu juga. Yang
> hilang adalah alasan yang **tersimpan**. Bedanya menentukan: tanpa alasan
> tersimpan, jejak audit bisa menjawab *data apa yang disentuh* dan *apa yang
> diputuskan*, tapi **tidak pernah bisa menjawab kenapa** — dan pertanyaan
> "kenapa" adalah satu-satunya alasan jejak audit ada.
>
> Butir **B-13** (*self-improving agent sulit diaudit*) ditutup sebagai
> **H-7** justru karena §45 menyimpan alasan ringkas. Penutupan itu perlu
> ditinjau ulang. Lihat **E-75** / [#64](../../issues/64).

> ⚠️ **`data_accessed: ["habits","sleep"]` mendukung model §8.6, bukan model
> §8.11.** Yang dicatat adalah **kategori data**, bukan pertanyaan yang
> diajukan. Ini bukti keempat bahwa Personal Data Vault berdiri sendirian —
> lihat **E-71** / [#62](../../issues/62).

---

## §8.26 — Security Event Pipeline

Semua security event masuk **event bus**:

```
Authentication Failed
Permission Denied
Consent Revoked
Suspicious Agent
Prompt Injection
Data Access
Policy Violation
Tool Abuse
```

kemudian:

```
Event Bus
    ↓
Security Analytics
    ↓
Detection
    ↓
Alert
    ↓
Incident Response
```

---

> 🛑 **Delapan nama ini tidak mengikuti format nama event yang baru saja
> ditutup.** Butir **E-43** ditutup sebagai [#38](../../issues/38) dua naskah
> lalu: **dua segmen, `<domain>.<past_tense_verb>`, huruf kecil, dan sekali
> dipakai tidak pernah diganti** ([`../spec/03`](../spec/03-EVENT-CONTRACTS.md)).
>
> | Naskah 12 | Bentuk dua segmen |
> |---|---|
> | Authentication Failed | `auth.failed` |
> | Permission Denied | `permission.denied` |
> | Consent Revoked | `consent.revoked` |
> | Policy Violation | `policy.violated` |
> | Tool Abuse | `tool.abused` ? |
> | **Suspicious Agent** | — bukan frasa kerja |
> | **Prompt Injection** | — bukan frasa kerja |
> | **Data Access** | — bukan frasa kerja |
>
> Tiga terakhir bukan *kejadian* melainkan *kategori*, jadi ia tidak bisa
> diterjemahkan tanpa ditulis ulang (`agent.flagged`, `injection.detected`,
> `data.accessed`). Nama event **tidak boleh diganti setelah dipakai** —
> jadi ini harus diselesaikan sebelum baris pertama, bukan sesudahnya.
> Lihat **E-70** / [#63](../../issues/63).

> ⚠️ **`Data Access` sebagai event akan menjadi yang terbanyak di seluruh
> sistem.** Setiap pembacaan data oleh setiap agent, dicatat — di V0 dengan
> empat agent itu wajar; dengan 22 agent dan ratusan pemanggilan per hari per
> pengguna, `data_access_logs` (§8.40) akan tumbuh lebih cepat daripada data
> penggunanya sendiri. Ia butuh retensi sendiri sejak awal (§7.26), dan ia
> masuk hitungan **C-9**: log akses adalah data pribadi juga.

---

## §8.27 — Abuse Prevention

HumanVerse harus mampu mendeteksi:

```
Account takeover
Credential abuse
Agent abuse
API abuse
Prompt injection
Data exfiltration
Rate abuse
Automated scraping
Privilege escalation
Malicious plugin
```

---

> ⚠️ **Sepuluh jenis penyalahgunaan, dan sembilan di antaranya baru relevan
> setelah ada pengguna kedua.** Untuk V0 dengan satu pengguna, yang benar-benar
> perlu ada sejak awal hanya **rate limit** (sudah ada di tool registry
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md): `60/min/user`) dan
> **prompt injection** — yang justru satu-satunya yang tidak butuh pengguna
> kedua, karena penyerangnya adalah teks, bukan orang.
>
> Daftar ini adalah contoh baik dari apa yang perlu dipilah sebelum V0:
> semuanya benar, hampir semuanya belum waktunya. Lihat **A-25** /
> [#58](../../issues/58).
