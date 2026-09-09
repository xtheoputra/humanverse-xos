# Sensus tangga risiko & otonomi

> ⚠️ **Bukan kata pemilik.** Pengukuran. Ia tidak memilih tangga mana yang
> berlaku — itu tetap [#60](../../issues/60) · [#97](../../issues/97) ·
> [#152](../../issues/152).

---

## Kenapa berkas ini ada

Tangga risiko ditulis **empat kali** dalam dua puluh empat naskah, dan
selisihnya dicatat satu per satu (*“turun satu takik”*, **E-67**). Berkas ini
menaruh keempatnya berdampingan, lalu melacak **satu tindakan yang sama**
melintasi semuanya — teknik yang di repo ini paling sering berbuah.

---

## Empat tangga risiko, semuanya lima anak tangga

| | naskah 4 · [`58`](58-PERMISSION-RISK-SAFETY.md) §16 | naskah 5 · [`88`](88-ARSITEKTUR-AGEN.md) §16 | Phase 8 · [`146`](146-AGENT-SECURITY-RISK-POLICY.md) §8.16 | Phase 11 · [`180`](180-RISIKO-OTONOMI-BUDGET.md) §11.15 |
|---|---|---|---|---|
| **0** | Informasi | Information | R0 Informational | R0 Informational — *read public information* |
| **1** | **Rekomendasi** | **Recommendation** | R1 **Low impact** | R1 Low impact — *note · habit · reminder* |
| **2** | Action reversibel | Low-impact action | R2 **Moderate** | R2 Moderate — *low-risk message · schedule · low-value purchase* |
| **3** | Action berdampak | Meaningful external action | R3 High impact | R3 High impact — *financial · important communication · account* |
| **4** | High-impact | High-impact action | R4 Critical | R4 Critical — *irreversible* → **DENY** |

⭐ **Jumlah anak tangganya stabil — lima, empat kali berturut-turut.** Itu
kestabilan yang jarang di repo ini (bandingkan daftar agent: 14 → 22 → 25).

🛑 **Yang bergeser isinya.** Di naskah 4 dan 5, anak tangga **1 adalah
*Rekomendasi*** — memberi saran. Sejak Phase 8, **1 adalah *tindakan berdampak
rendah***. *Rekomendasi* keluar dari tangga sama sekali, dan **setiap tindakan
turun satu takik**. Itulah **E-67** / [#60](../../issues/60).

---

## 🔴🔴 Melacak satu tindakan: “kirim pesan kepada orang lain”

| Naskah | Tingkat |
|---|---|
| naskah 4 §16 | 3 |
| naskah 5 §16 | **3** — *“Kirim pesan kepada seseorang.”* |
| Phase 8 §8.16 | **R3** — *“Mengirim pesan atas nama user”*; audit di berkas itu mencatat *“Level 3 ǀ R3 ✅ sama”* |
| **Phase 11 §11.15** | 🛑 **R2** — *“send low-risk message”* |

**Ambang konfirmasi sudah ditutup sebagai H-15 / [#5](../../issues/5): otomatis
sampai R2, konfirmasi manusia wajib mulai R3.**

⇒ Pemindahan itu **melewati ambangnya**. Tindakan yang di tiga naskah pertama
menuntut manusia menekan setuju, di Phase 11 boleh berjalan sendiri.

### Dan §11.15 menaruh pesan di DUA tingkat sekaligus

```
R2 Moderate     · send low-risk message · modify schedule · purchase low-value item
R3 High impact  · financial transaction · important communication · account changes
```

Yang memisahkannya bukan mekanisme melainkan **dua kata sifat yang tidak pernah
didefinisikan**: *low-risk* dan *important*. Pencarian seluruh `docs/`:
`low-risk` muncul **dua kali** — di baris R2 ini, dan sekali dalam konteks tak
berhubungan. **Tidak ada satu kalimat pun yang menyatakan apa yang membuat
sebuah pesan berisiko rendah.**

### ⭐ Tetangganya di baris yang sama diselamatkan; pesan tidak

`purchase low-value item` punya cacat yang sama, **dan catatan audit sudah
menandainya**. Ia punya penyelamat: §11.17 memberi `purchases: { amount_limit: 0 }`
— nol sampai pengguna menaikkannya sendiri.

🛑 §11.17 memberi bawaan untuk `calendar.create_event` (20/hari),
`notification.send` (10/hari), dan `purchases.amount_limit` (0) — **tidak ada
entri untuk pesan kepada pihak ketiga**. (`notification.send` adalah
pemberitahuan kepada **penggunanya sendiri**.) §11.18 mendaftar `Messages`
sebagai kategori budget, tetapi §11.17 tidak pernah memberinya nilai.

⇒ **Dari tiga kategori di baris R2, yang tidak mendapat definisi maupun angka
bawaan justru satu-satunya yang punya ORANG LAIN di ujung penerimanya.**
→ **B-39** / [#152](../../issues/152).

---

## Tangga kedua: otonomi (L0–L4), dan kenapa ia menyelamatkan sesuatu

§11.16 memberi tangga **kedua** yang sering tertukar dengan tangga risiko:

```
L0 Observe · L1 Recommend · L2 Prepare · L3 Ask Confirmation · L4 Execute within Boundaries
```

⭐ **Pemisahan ini benar dan sudah ditutup sebagai H-21**: `R` mengukur
**risiko tindakan**, `L` mengukur **sejauh mana agent boleh bertindak sendiri**.
Dua sumbu, bukan satu.

⭐⭐ Dan ia menjawab **E-67** dari arah yang lebih baik daripada usul saya
sendiri: alih-alih menaikkan angka risiko `update habit`, manifest §11.5
memberi `habit-coach` **`autonomy.max_level: L2`** — *Prepare*, bukan
*Execute*. Risikonya tetap R1; **otonominya yang membatasi**.

⚠️ Konsekuensinya harus ditulis: **gerbang risiko
[`../spec/05`](../spec/05-AGENT-CONTRACTS.md) sekarang perlu memeriksa
`autonomy.max_level`, bukan hanya `risk_level`.** Tanpa itu ia melihat separuh
dari yang menentukan. Dan `L1 Recommend` di tangga otonomi adalah tempat
*Rekomendasi* yang hilang dari tangga risiko sejak Phase 8 — dua tangga itu
saling menutupi lubang masing-masing, tetapi hanya kalau keduanya diperiksa.

---

## Yang sensus ini **tidak** putuskan

Tidak memilih tangga yang berlaku, tidak mendefinisikan *low-risk*, dan tidak
mengubah ambang H-15. Ia hanya menaruh keempat tangga berdampingan dan
menunjukkan bahwa **satu tindakan berpindah melewati ambang konfirmasi tanpa
pernah dinyatakan**.
