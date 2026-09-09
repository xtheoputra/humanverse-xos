# Sensus daftar agent lintas naskah

> ⚠️ **Bukan kata pemilik.** Pengukuran. Ia **tidak memilih** daftar agent mana
> yang kanonik — itu tetap [#35](../../issues/35) · [#79](../../issues/79) ·
> [#89](../../issues/89).

---

## Kenapa berkas ini ada

Daftar agent dicatat sebagai deret: *“berubah keempat kalinya”*, *“versi
kelima”*. Dan jumlahnya ditaksir dengan **penjumlahan**:

| Sumber | Jumlah | dari [#89](../../issues/89) |
|---|---|---|
| Hierarki §11.4 | 25 | |
| Muncul di contoh tanpa terdaftar (**E-95**) | +7 | |
| §12.29 | +12 | |
| | **> 40** | |

Penjumlahan itu mengabaikan dua daftar yang lebih tua **dan** menganggap tidak
ada nama yang berulang. Berkas ini menghitung **himpunannya**.

---

## Lima daftar, diambil apa adanya dari naskah

| | Daftar | Sumber | Jumlah |
|---|---|---|---|
| **L1** | Agent Registry | [`56`](56-AGENT-FACTORY.md) §12 · naskah 4 | 14 |
| **L2** | Initial production + Domain agents | [`88`](88-ARSITEKTUR-AGEN.md) §12 · naskah 5 | 22 |
| **L3** | Agent Hierarchy | [`177`](177-HIERARKI-REGISTRY-IDENTITAS.md) §11.4 · naskah 15 | 25 |
| **L4** | Agent yang diperlukan | [`196`](196-REPO-API-DB-AGENT.md) §12.29 · naskah 16 | 12 |
| **L5** | hidup di contoh, tak terdaftar | **E-95** / [#79](../../issues/79) | 7 |

Nama dinormalkan: akhiran `Agent` dibuang, `CamelCase` dipecah — jadi
`FashionAgent`, `Fashion Agent`, dan `Fashion` dihitung **satu**.

---

## 🔴🔴 Hasil

| | |
|---|---|
| baris kalau dijumlah mentah | **80** |
| **nama unik** | **59** |
| muncul di **4 atau 5** daftar | **NIHIL** |
| muncul di **3** daftar | **6** |
| muncul di **2** daftar | 9 |
| muncul di **1** daftar saja | **44** — 75 % |

🛑 **Tidak ada satu pun nama agent yang muncul di semua daftar.**

L4 memang wajar tidak beririsan — ia agent simulasi Phase 12, ranah yang lain.
Maka pembandingan yang adil adalah **ketiga registry umum L1 · L2 · L3**, dan
hasilnya:

```
Career · Fashion · Habit · Learning · Social · Travel
```

**Enam nama.** Itu seluruh irisan dari daftar yang masing-masing berisi 14, 22,
dan 25 agent.

> ⭐ **Inti yang stabil selama sebelas naskah berjumlah enam, dan keenamnya
> agent DOMAIN.** Tidak satu pun agent inti/sistem (`Orchestrator`, `Memory`,
> `Safety`, `Evaluation`) bertahan di ketiganya — bukan karena dibuang,
> melainkan karena **L1 belum punya lapisan itu** dan L2 lawan L3 menamainya
> berbeda.

---

## Tiga pasang nyaris-kembar yang membuat irisannya tampak lebih kecil

| L2 | L3 | Kemungkinan |
|---|---|---|
| `Orchestrator` | `Supreme Orchestrator` | benda yang sama, satu tingkat lebih tinggi |
| `Planner` | `Planning` | hampir pasti sama |
| — (`Finance` di L1) | `Finance Behavior` | L1 `Finance` → L2/L3 `Finance Behavior` = penggantian nama |

Kalau ketiganya dianggap identik, inti stabilnya menjadi **tujuh**, bukan enam.
⚠️ Angka itu **tidak** dipakai sebagai hasil utama: menyamakan `Orchestrator`
dengan `Supreme Orchestrator` adalah **keputusan**, bukan pengukuran — dan itu
milik [#35](../../issues/35).

---

## Yang hilang lalu kembali

| Nama | Ada | Tidak ada |
|---|---|---|
| `Health` | L1, L3 | **L2** |

`Health` satu-satunya yang hilang di satu daftar lalu muncul lagi. `Grooming`,
`Productivity`, `Entertainment`, dan `Research` hilang sesudah L1 dan **tidak
pernah kembali** ke registry mana pun — `Productivity` hanya muncul lagi di L5,
yaitu di contoh, tanpa terdaftar.

---

## Apa artinya untuk [#89](../../issues/89) dan [#139](../../issues/139)

[#89](../../issues/89) menanyakan **kriteria mana yang agent dan mana yang
service**. Sensus ini tidak menjawabnya, tetapi memberi ukuran soalnya:
**59 nama, dan 44 di antaranya hanya pernah disebut sekali.** Sebuah nama yang
muncul di satu daftar dan tidak pernah lagi adalah kandidat terkuat untuk
*bukan agent* — dan itu tiga perempat daftarnya.

Untuk [#139](../../issues/139), butir *agent contracts*: kontrak ditulis untuk
himpunan, bukan untuk penjumlahan. Himpunannya **59**, bukan *“> 40”*.

---

## Yang sensus ini **tidak** putuskan

Tidak memilih daftar kanonik, tidak menggabungkan nama kembar, dan tidak
memutuskan mana yang jadi service. Ia hanya mengganti *“versi kelima”* dan
*“lebih dari empat puluh”* dengan **59 nama, nol di semua daftar, enam di
ketiga registry umum.**

Terbit sebagai **[#150](../../issues/150)** (**E-154**).
