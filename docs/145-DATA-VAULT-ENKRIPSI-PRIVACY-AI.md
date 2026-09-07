# 145 — §8.11–§8.13 Personal Data Vault, Encryption & Privacy-Preserving AI

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.11 — Personal Data Vault

```
                PERSONAL DATA VAULT
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Identity         Health           Finance
        │                │                │
     Career           Social          Lifestyle
        │                │                │
        └────────────────┼────────────────┘
                         │
                    Encryption
```

> Data **tidak diberikan langsung** ke agent.

Agent meminta:

```
"I need user's sleep average
for the last 14 days."
```

Vault memberikan:

```json
{
  "sleep_average": 6.8
}
```

bukan seluruh database sleep. Ini disebut:

> ## Minimum Necessary Data

---

> ⭐⭐ **Naskah 4 §44 menyatakan prinsipnya; naskah ini memberi
> mekanismenya.** *"Agent hanya mendapat data yang dibutuhkan"* adalah kalimat
> yang tidak bisa diperiksa. `{ "sleep_average": 6.8 }` bisa: entah agent
> menerima satu angka, atau tidak. Domainnya juga bertambah dari tiga
> (Identity · Health · Finance) menjadi **enam** — Career, Social, dan
> Lifestyle masuk, sejajar dengan tujuh dimensi *Personal Representation
> Layer* (**E-56**).

> 🛑 **Tetapi model ini bertabrakan dengan §8.6, §8.15, dan §8.37 di naskah
> yang sama.** Ketiganya memberi izin **per scope/tabel** (`✓ habits`,
> `✓ wardrobe`, `✓ Sleep`); hanya §8.11 yang memberi **jawaban atas
> pertanyaan**. Keduanya sah, tetapi menuntut permukaan teknis yang sama
> sekali berbeda:
>
> | | Model §8.6/§8.15/§8.37 | Model §8.11 |
> |---|---|---|
> | Yang diizinkan | scope (`habits`, `sleep`) | pertanyaan (`sleep_average(14d)`) |
> | Yang disimpan | baris `permissions` | katalog pertanyaan + bentuk jawaban |
> | Agent menerima | baris data | satu nilai turunan |
> | Sudah ada di spesifikasi | ✅ `permissions` | ❌ belum pernah ada |
>
> Katalog pertanyaan itu **belum pernah ditulis di dua belas naskah**, dan ia
> bukan pekerjaan kecil: setiap pertanyaan yang boleh diajukan harus
> didaftarkan, diberi bentuk jawaban, dan diberi tingkat risiko sendiri —
> pada dasarnya sebuah *tool registry* kedua. Lihat **E-71** /
> [#62](../../issues/62).
>
> ⚠️ Perhatikan juga: diagram naskah 4 §44 punya **Permission Layer** antara
> vault dan agent. Di sini yang tersisa di bawah vault hanya `Encryption`.
> Izin tidak hilang (§8.7 punya sendiri), tapi diagramnya tidak lagi
> menunjukkan di mana ia berdiri.

---

## §8.12 — Data Encryption

```
At Rest
   ↓
Database encryption

In Transit
   ↓
TLS / mTLS

Application
   ↓
Field-level encryption

Secrets
   ↓
Secrets Manager / KMS
```

Untuk data tertentu:

```
PII
Health
Financial
Location
Private communications
```

gunakan **proteksi yang lebih kuat**.

---

> ⚠️ **Daftar lima ini hampir persis Level 3 klasifikasi naskah 11 §7.2**
> (*journal · location history · financial behavior · health-related
> tracking*), ditambah *PII* dan *Private communications*. Karena itu ia
> **tidak bisa** dibaca sebagai isi Level 4 yang masih kosong — dua level akan
> punya daftar yang sama. **G-6 tetap terbuka**, dan sekarang lebih menonjol:
> satu naskah penuh tentang keamanan lewat tanpa mengisi tingkat sensitivitas
> tertingginya sendiri. Lihat [#57](../../issues/57).

> 🛑 **Field-level encryption bertabrakan dengan seluruh Phase 7.** Kalau
> health dan financial dienkripsi di lapisan aplikasi, maka:
>
> - **Feature Store** (§7.13) tidak bisa menghitung fitur turunannya;
> - **Lakehouse** (§7.10) menyimpan Parquet yang tidak bisa diagregasi;
> - **Vector/Qdrant** (§7.16) tetap menyimpan *embedding* yang diturunkan dari
>   teks aslinya — dan embedding **tidak ikut terenkripsi**, padahal ia
>   membawa isi;
> - **Behavior Foundation Model** (R1) tidak punya bahan.
>
> Ini bukan alasan untuk tidak mengenkripsi; ini alasan untuk menuliskan
> **field mana** yang dienkripsi di lapisan aplikasi dan mana yang cukup
> *at rest*. Yang biasanya benar: enkripsi di lapisan aplikasi hanya untuk
> yang **tidak pernah dihitung** — isi jurnal, nomor rekening, foto — dan
> *at rest* untuk sisanya. Keputusan itu belum ada.

---

## §8.13 — Privacy-Preserving AI

> Ini akan menjadi salah satu **differentiator** HumanVerse.

**Data minimization** — model hanya menerima data yang diperlukan.

**Pseudonymization**

```
user_id = user_8f91...
```

bukan identitas langsung.

**Differential Privacy** — untuk agregasi dan analytics tertentu:

```
Real data
   ↓
Noise mechanism
   ↓
Aggregate insight
```

**Federated Learning** — untuk beberapa use case:

```
Device A ─┐
Device B ─┼── local training
Device C ─┘
      │
      ↓
Model Updates
      ↓
Central Model
```

> Data mentah **tidak selalu perlu keluar dari perangkat**.

---

> 🛑 **Kata "differentiator" adalah janji ke luar, dan janji ini belum punya
> tempat di tangga versi.** Naskah 4 §41/§42 menempatkan *On-device AI* dan
> *Federated ML* di **V5**. Butir **A-14** sudah mencatat konsekuensinya:
> **V0 sampai V4 tetap diproses di cloud**. Menyebut privacy-preserving AI
> sebagai pembeda tanpa menyebut versinya berarti calon pengguna akan
> mendengar janji yang baru ditepati bertahun-tahun kemudian.
>
> Ini bukan keberatan teknis melainkan keberatan tentang **apa yang boleh
> dikatakan kapan**. Tiga dari empat teknik di atas justru **sudah bisa
> dipakai di V0** dan sebaiknya diklaim sekarang:
>
> | Teknik | Bisa di V0? |
> |---|---|
> | Data minimization | ✅ ya — itu §8.11, dan tidak butuh apa pun yang baru |
> | Pseudonymization | ✅ ya — `users.id` sudah uuid, bukan email |
> | Differential Privacy | ⚠️ hanya bila ada analytics agregat; V0 belum punya |
> | Federated Learning | ❌ butuh aplikasi di perangkat — V5 |
>
> Lihat **C-15**, dan [#6](../../issues/6) yang menanyakan kapan janji privasi
> ditepati.

> ⚠️ **Federated Learning dan §8.10 tarik-menarik.** Pembelajaran terfederasi
> mengirim *model update*, bukan data mentah — tapi update itu **tetap
> diturunkan dari data pengguna**, jadi ia tetap membutuhkan
> `purpose: model_training`. Privasi teknis tidak menggantikan dasar izin.
> Lihat **B-22** / [#59](../../issues/59).
