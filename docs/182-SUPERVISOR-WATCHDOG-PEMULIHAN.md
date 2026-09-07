# 182 — §11.23–§11.27 Supervisor, Watchdog, Self-Healing, Transaksi & Reversibility

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.23 — Agent Supervisor

```
Supervisor → Agent → Task
```

Supervisor memeriksa:

```
Is task valid?          Is tool use allowed?
Is behavior within scope?  Is result expected?
Is output reasonable?
```

Jika abnormal: **PAUSE**

---

## §11.24 — Agent Watchdog

Monitoring:

```
Infinite loop          Permission violations
Repeated failures      High latency
Unexpected tool calls   Abnormal behavior
Excessive cost         Prompt injection
```

Jika terdeteksi:

```
Agent → Freeze → Revoke credentials → Notify → Audit
```

---

> ⭐⭐⭐ **Ini separuh dari *Human Override* yang G-8 / [#65](../../issues/65)
> catat tidak datang di Fase 8.**
>
> Butir itu mencatat tiga hal yang berbeda dan hanya dua yang ada: §8.17
> mencegah **sebelum** aksi, §8.35 Kill Switch menghentikan **semuanya**, dan
> tidak ada yang menghentikan **satu** agent yang sudah berjalan.
>
> `Freeze → Revoke credentials` mengisi tepat lubang itu — per agent, bukan
> per sistem. Dan §11.61 melengkapinya dengan enam kata kerja kendali:
> **Pause · Resume · Cancel · Revoke · Kill · Rollback**.
>
> ⚠️ Yang membedakannya dari *Human Override* sesungguhnya: ini **otomatis**,
> dipicu watchdog. Pembatalan **atas kehendak manusia** ada di §11.61 dan
> §11.28, jadi keduanya sekarang ada — tapi *Bias Detection*, butir kedua yang
> G-8 catat, masih **tidak muncul sekali pun** di lima belas naskah.

> ⭐ **`Prompt injection` sebagai gejala yang dipantau, bukan hanya sebagai
> serangan yang dicegah.** §8.20 menahan di jalur masuk; di sini ia dideteksi
> dari **perilaku agent** — agent yang tiba-tiba meminta tool di luar
> manifestnya adalah tanda injeksi yang lolos. Dua lapisan untuk satu ancaman,
> dan yang kedua menangkap kegagalan yang pertama.

> ⭐ **`Infinite loop` dan `Excessive cost`** adalah dua kegagalan yang paling
> mungkin terjadi lebih dulu daripada serangan mana pun — dan keduanya biasanya
> baru ditemukan lewat tagihan.

> ⚠️ **Supervisor dan Watchdog mengerjakan hal yang tumpang tindih** — keduanya
> memantau perilaku abnormal, satu berhenti di `PAUSE`, satu sampai `Revoke`.
> Bedanya mungkin cakupan (per tugas vs per agent), tapi itu tidak ditulis. Dan
> §11.38 mendaftarkan `Watchdog` sebagai komponen runtime sementara `Supervisor`
> **tidak ada di daftar itu** — jadi salah satunya belum punya rumah.

> ⚠️ **"Is output reasonable?" dan "Is result expected?" tidak bisa diperiksa
> tanpa acuan.** Ini masalah **B-10** yang sama (*akurat terhadap apa*).
> Jawaban yang tersedia dan tidak butuh penilai: `Prediction Calibration`
> §9.34 dan **kontrak tool** — keluaran yang tidak sesuai skema tool
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) bisa ditolak tanpa menilai
> isinya. Selebihnya menuntut manusia.

---

## §11.25 — Self-Healing Agent Execution

```
Action → Failure → Classify Failure
```

| Jenis | Tindakan |
|---|---|
| Transient | Retry |
| Invalid Input | Replan |
| Permission | Ask User |
| External Failure | Alternative Tool |
| Unknown | **Stop + Report** |

> Jangan membuat agent *"retry forever"*. Gunakan **bounded retry**.

---

> ⭐⭐ **Klasifikasi sebelum penanganan adalah yang membedakan pemulihan dari
> pengulangan buta** — dan `Unknown → Stop + Report` adalah baris yang paling
> penting: bawaan untuk kegagalan yang tidak dikenali adalah **berhenti**,
> bukan mencoba lagi.
>
> `Permission → Ask User` juga tepat: kegagalan izin **bukan kegagalan
> teknis**, dan mencoba ulang tidak akan pernah menolongnya.

> ⚠️ **`External Failure → Alternative Tool` adalah satu-satunya baris yang
> bisa berbahaya.** Berpindah tool berarti agent memakai kemampuan yang
> **tidak dipilih untuk permintaan ini** — dan tool pengganti bisa punya
> `risk_level` berbeda. Aturannya harus: **tool pengganti melewati Action
> Gateway dari awal**, bukan mewarisi izin dari yang gagal.

> ⚠️ **`Replan` bisa berputar.** `Invalid Input → Replan → Invalid Input →
> Replan` adalah infinite loop yang berpakaian pemulihan, dan §11.24 memantau
> `Infinite loop` — tapi *bounded retry* hanya disebut untuk retry, bukan untuk
> replan. Batas jumlah replan per tugas perlu ada di tempat yang sama.

---

## §11.26 — Transactional Agent Actions

```
Prepare → Validate → Commit
```

atau:

```
Prepare → Confirmation → Execute → Verify
```

Untuk action yang dapat dibatalkan:

```
Execute → Undo capability
```

Contoh: `create calendar event` dapat **create · update · delete**.

---

> ⭐ **`Prepare` sebagai langkah tersendiri memberi L2 (§11.16) bentuk
> teknisnya.** *"Saya sudah menyiapkan reminder"* bukan basa-basi — ia keadaan
> nyata: aksi sudah tersusun, tervalidasi, dan menunggu. Itu yang membuat
> `autonomy.max_level: L2` bisa dijalankan tanpa mengeksekusi apa pun.

---

## §11.27 — Reversibility Engine

Setiap action memiliki `reversible: true/false`.

| Aksi | Sifat |
|---|---|
| Create reminder | reversible |
| Send email | **partially reversible** |
| Delete data | potentially irreversible |
| Financial transaction | potentially irreversible |

> Semakin sulit dibalik: **semakin tinggi risk requirement**.

---

> ⭐⭐⭐ **Ini sumbu ketiga, dan ia yang paling menjelaskan.**
>
> ```
> risk_level    (R0–R4)  → seberapa besar AKIBATNYA
> autonomy      (L0–L4)  → seberapa jauh AGENT boleh bertindak sendiri
> reversible             → seberapa sulit DIBATALKAN
> ```
>
> Yang ketiga menjelaskan yang pertama: **R4 = `DENY` (§11.15) karena R4
> didefinisikan sebagai *irreversible***. Jadi ketiga sumbu itu tidak sejajar —
> reversibility adalah **sebab**, risiko adalah **akibatnya**.
>
> Dan itu memberi aturan turunan yang bisa langsung dipakai:
> **aksi yang tidak reversibel tidak pernah boleh berjalan pada L4**, apa pun
> `risk_level`-nya. Satu baris validasi di
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md).

> ⭐⭐ **`Send email` = *partially reversible* adalah jujur, dan jarang
> ditulis.** Email bisa ditarik dari kotak masuk, tapi **tidak dari kepala
> orang yang sudah membacanya**. Kategori ketiga itu penting justru karena ia
> tidak bisa diperlakukan seperti keduanya: tidak aman dianggap bisa
> dibatalkan, dan tidak adil dianggap permanen.
>
> Ini juga permukaan **C-19**: yang tidak bisa ditarik dari email bukan
> datanya, melainkan **akibatnya pada orang ketiga**.

> ⚠️ **`reversible` belum ada di Action Object §11.13 maupun di tool registry
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)**, yang punya `side_effects:
> none | writes_user_data | external_call`. Ketiga nilai itu **hampir**
> memetakan ke reversibility — `none` selalu reversible, `external_call` hampir
> tidak pernah — tapi keduanya menjawab pertanyaan berbeda dan sebaiknya jadi
> dua kolom.

> ⚠️ **Reversibility punya jendela waktu.** Menghapus calendar event bisa
> dibatalkan hari ini, tidak setelah rapatnya lewat. Pembayaran bisa
> dibatalkan sebelum diproses. Jadi field ini sebenarnya
> `reversible_until` — dan tanpa itu, agent akan menganggap aksi lama masih
> bisa ditarik.
