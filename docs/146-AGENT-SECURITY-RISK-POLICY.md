# 146 — §8.14–§8.18 Agent Security, Risk Engine, Human Confirmation & Policy Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.14 — Agent Security

> Karena HumanVerse akan memiliki banyak agent, agent harus diperlakukan
> seperti **software principal**.

Setiap agent memiliki:

```yaml
agent:
  id:
  version:
  owner:
  capabilities:
  tools:
  permissions:
  memory_scope:
  risk_level:
  security_policy:
```

---

> ⭐ **`risk_level` kembali — dan itu menutup separuh butir E-60 /
> [#52](../../issues/52).** Manifest DP-L8 naskah 10, yang ditetapkan sebagai
> *standar marketplace*, membuang `risk_level` dan `requires_confirmation`.
> Yang pertama kembali di sini, untuk **setiap** agent.

> ⭐ **`requires_confirmation` tidak kembali ke manifest — ia pindah ke Policy
> Engine (§8.18), dan itu lebih kuat.** Selama ia berada di manifest, **penulis
> agent** yang menentukan kapan penggunanya dimintai izin; agent pihak ketiga
> tinggal menuliskan daftar kosong. Setelah pindah ke policy, yang menentukan
> adalah **platform**. Untuk marketplace, ini perbaikan nyata, bukan
> kehilangan.
>
> Konsekuensinya: **aturan 3 di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)**
> (*`risk_level >= 3` wajib punya isi `requires_confirmation`*) harus ditulis
> ulang — ia sekarang memeriksa manifest, dan seharusnya memeriksa **ada
> tidaknya baris policy** untuk agent itu.

> 🛑 **Manifest agent kelima — dan `memory` runtuh dari dua field jadi satu.**
>
> | Field | n4 §11 | n5 §14 | n10 DP-L8 | **n12 §8.14** |
> |---|---|---|---|---|
> | `purpose` | ✅ | ✅ | ❌ | ❌ masih hilang |
> | `risk_level` | ✅ | ✅ | ❌ | ✅ **kembali** |
> | `requires_confirmation` | — | ✅ | ❌ | ➡️ pindah ke policy |
> | `memory.read` / `memory.write` | ✅ dua field | ✅ dua field | ⚠️ hanya read | 🛑 **`memory_scope` satu field** |
> | `permissions` | — | — | ✅ | ✅ |
> | `model` · `evaluation` | — | ✅ | ❌ | ❌ |
> | `owner` | — | — | — | ✅ **baru** |
> | `security_policy` | — | — | — | ✅ **baru** |
>
> `memory_scope` tunggal berarti **agent yang boleh membaca sebuah scope
> otomatis boleh menulisinya**. Itu membatalkan aturan paling halus di
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md): `coach-agent` membaca lima
> scope tetapi hanya menulis `coaching_notes`, dan `memory-agent` membaca
> hampir semua scope **kecuali** `journal_raw`. Tanpa pemisahan read/write,
> kedua batas itu tidak bisa dinyatakan. Lihat **E-68** /
> [#61](../../issues/61).

---

## §8.15 — Agent Capability Isolation

**Fashion Agent**

```
✓ wardrobe
✓ fashion trends
✓ preferences

✗ bank account
✗ private chat
✗ medical records
```

**Finance Behavior Agent**

```
✓ spending patterns
✓ budgeting behavior

✗ execute transaction
✗ transfer money
✗ access unrelated health data
```

Dengan demikian:

> **Agent capability ≠ unlimited system access.**

---

> ⭐ **Finance Behavior Agent yang dilarang `execute transaction` adalah
> penegakan C-4 di lapisan izin, bukan di lapisan kalimat.** Naskah 4 §17
> berkata *"jangan menjanjikan return investasi"* — sebuah aturan bahasa.
> Di sini agent keuangan **tidak diberi kemampuannya sama sekali**. Aturan
> yang tidak bisa dilanggar lebih baik daripada aturan yang harus dipatuhi.

> ⚠️ **`access unrelated health data` adalah satu-satunya larangan bersyarat
> di seluruh naskah** — semua larangan lain absolut. Siapa yang memutuskan
> *"unrelated"*, dan berdasarkan apa? Kalau jawabannya `purpose` (§8.10), itu
> jawaban yang baik dan sebaiknya ditulis. Kalau tidak, larangan ini tidak
> bisa ditegakkan mesin.

---

## §8.16 — Risk Engine

```
R0 — Informational
R1 — Low impact
R2 — Moderate
R3 — High impact
R4 — Critical
```

Contoh:

| Action | Risk |
|---|---|
| Menjelaskan konsep | R0 |
| Memberi rekomendasi outfit | R0 |
| Mengubah habit | R1 |
| Mengirim reminder | R1 |
| Membuat keputusan karier otomatis | R2 |
| Mengirim pesan atas nama user | R3 |
| Transaksi finansial | R4 |
| Menghapus data penting | R4 |

---

> 🛑 **Tangganya tetap lima tingkat, tetapi kalibrasinya turun satu takik —
> dan buktinya adalah contoh yang sama persis.**
>
> | Contoh pemilik | naskah 4 §16 | naskah 12 §8.16 |
> |---|---|---|
> | **rekomendasi outfit** | **Level 1** (*"Kamu bisa memakai outfit ini"*) | **R0** |
> | menulis ke data pengguna | Level 2 (*"Tambahkan workout ke task list"*) | **R1** (*"Mengubah habit"*) |
> | booking / pembelian | Level 3 (*"Booking hotel"*) | **R4** (§8.18: `travel-agent purchase` = R4) |
> | kirim pesan atas nama user | Level 3 | R3 ✅ **sama** |
>
> Ini bukan tafsir: *rekomendasi outfit* adalah contoh yang **identik** di dua
> naskah, dan ia pindah dari Level 1 ke R0. Ujung bawah tangga turun, ujung
> atas naik — tangganya **meregang**.
>
> **Akibatnya nyata di V0.** [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> memberi `habit.complete` dan `memory.write` **risk 2**, dan default V0
> meminta `ask` di level 2. Kalau *"mengubah habit"* adalah R1, dan §8.17
> hanya meminta konfirmasi di R3/R4, maka **setiap tulisan ke data pengguna di
> V0 berjalan tanpa satu pun konfirmasi**.
>
> Yang perlu diputuskan: apakah default `ask` di level 2 tetap berlaku sebagai
> pengetatan sengaja untuk V0, atau ditinggalkan. Diamkan, dan spesifikasi
> serta naskah akan menegakkan dua aturan berbeda. Lihat **E-67** /
> [#60](../../issues/60).

> ⚠️ **R2 diisi contoh yang tidak reversibel.** *"Membuat keputusan karier
> otomatis"* duduk di tingkat yang **tidak butuh konfirmasi**, di atas
> *"mengirim reminder"* dan di bawah *"mengirim pesan"*. Di naskah 4, Level 2
> berarti **action reversibel** — dan keputusan karier bukan itu. Sebuah agent
> yang mengubah arah karier seseorang tanpa bertanya adalah persis yang
> dilarang kalimat penutup naskah ini sendiri (§8.46).

---

## §8.17 — Human Confirmation

Untuk **R3/R4**:

```
AI
 ↓
Action Proposal
 ↓
Risk Engine
 ↓
Human Confirmation
 ↓
Execution
```

Contoh:

> *"Saya menemukan tiket penerbangan Rp3.200.000. Apakah Anda ingin saya
> membelinya?"*

AI **tidak boleh** langsung membeli hanya karena sebelumnya user berkata:

> *"Kalau murah, belikan."*

> Untuk action berisiko tinggi tetap diperlukan **policy yang eksplisit**.

---

> ⭐⭐ **Ini menutup A-22 / [#5](../../issues/5) — dan aturan
> "kalau murah, belikan" adalah bagian terkuatnya.** Butir A-22 menanyakan
> sampai tingkat mana agent boleh bertindak sendiri; jawabannya: **otomatis
> sampai R2, konfirmasi mulai R3**. Naskah 4 hanya mewajibkannya di Level 4.
>
> Yang lebih penting daripada tingkatnya: pemilik menyatakan bahwa **izin yang
> diberikan di muka bukan konfirmasi**. Itu memisahkan dua hal yang selama ini
> tercampur:
>
> ```
> Consent      → mengizinkan AKSES ke data,        berjangka waktu (§8.9)
> Confirmation → mengizinkan satu AKSI tertentu,   sekali pakai   (§8.17)
> ```
>
> Persetujuan 30 hari untuk membaca data penerbangan **tidak** memberi hak
> membeli tiket. Pemisahan ini belum pernah ditulis di sebelas naskah dan ia
> menyelesaikan kekaburan yang sudah lama ada di **B-19** (*Email Automation*
> Phase 10). Dicatat sebagai **H-15**.

---

## §8.18 — Policy Engine

> Policy Engine adalah **hakim**.

```
Request
  ↓
Identity
  ↓
Permission
  ↓
Consent
  ↓
Risk
  ↓
Policy Engine
  ↓
ALLOW
DENY
REQUIRE_CONFIRMATION
REDACT
```

Contoh:

```yaml
policy:
  agent: travel-agent
  action: purchase
  risk: R4
  require_confirmation: true
```

---

> ⭐ **Rantai ini yang benar, bukan rantai §8.2.** Di sini `Risk` dihitung
> **sebelum** Policy Engine memutuskan — sesuai dengan naskah 4 §17 dan dengan
> risk gate [`../spec/05`](../spec/05-AGENT-CONTRACTS.md). Di §8.2, Policy
> mendahului Risk. Dua diagram di naskah yang sama; yang dipakai sebaiknya
> yang ini. `Consent` juga muncul di rantai ini tetapi **tidak ada** di lima
> komponen Security Fabric §8.3.

> ⭐ **REDACT adalah keputusan keempat, dan ia benar-benar baru.**
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) hanya mengenal
> `decision IN ('allow','deny','ask')`. REDACT adalah yang dilakukan Privacy
> Filter §8.22 — dan ia mengisi celah nyata: sampai sekarang, permintaan yang
> menyentuh sedikit data sensitif hanya punya dua pilihan, ditolak seluruhnya
> atau diluluskan seluruhnya.
>
> ⚠️ Tapi REDACT **tidak menahan permintaan, ia mengubah jawaban** — titik
> penegakannya ada di keluaran, bukan di gerbang masuk. Kalau ia ditaruh di
> kolom yang sama dengan `allow/deny/ask`, mesin izin akan mengira ia bisa
> memutuskan di depan padahal ia baru bisa bekerja di belakang. Skema perlu
> membedakan **keputusan gerbang** (`allow`/`deny`/`ask`) dari **transformasi
> hasil** (`redact` + daftar field). Lihat **E-76**, digabung ke
> [#60](../../issues/60).

> ⚠️ **`REQUIRE_CONFIRMATION` adalah nama ketiga untuk hal yang sama.**
> Naskah 5 §14 menyebutnya `requires_confirmation`;
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) menyebutnya `ask`; sekarang
> `REQUIRE_CONFIRMATION`. Satu nilai enum, tiga ejaan — pilih satu sebelum ia
> masuk basis data.
