# 151 — §8.36–§8.38 Privacy Center, Permission Dashboard & Data Deletion

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.36 — Privacy Center

User harus memiliki **satu tempat**:

```
                 PRIVACY CENTER
                       │
      ┌────────────────┼────────────────┐
      │                │                │
    Data            Agents          Consent
      │                │                │
      ├── Export       ├── Access      ├── Granted
      ├── Delete       ├── Revoke      ├── Expired
      ├── Download     └── Activity    └── Withdraw
      │
      └── Retention
```

User dapat melihat:

> *"AI apa saja yang mengakses data saya?"*

> Ini menjadi **fitur inti** HumanVerse.

---

> ⭐ **Kolom `Agents` adalah yang benar-benar baru, dan ia yang paling
> dibutuhkan.** Naskah 4 §43 menjawab *"apa yang HumanVerse ketahui tentang
> saya"*. Pertanyaan di sini berbeda dan lebih tajam: **"siapa yang
> melihatnya"** — dengan `Activity` sebagai riwayat akses per agent. Itulah
> yang membuat `audit_logs` dan `data_access_logs` (§8.40) punya pembaca
> selain penyelidik: **penggunanya sendiri**.
>
> `Consent: Granted / Expired / Withdraw` juga akhirnya memberi persetujuan
> sebuah **keadaan yang terlihat**, bukan sekadar baris di basis data.

> 🛑 **Tetapi `Edit` hilang — dan itu justru hak yang paling dibutuhkan
> sekarang.** Naskah 4 §43 memberi lima kata kerja:
>
> ```
> View · Edit · Export · Delete · Revoke
> ```
>
> Naskah 12 memberi delapan: *Export · Delete · Download · Retention · Access ·
> Revoke · Activity · Withdraw*. Daftarnya lebih panjang, tapi **tidak ada
> satu pun cara memperbaiki sesuatu yang salah.** Yang tersedia hanya
> menghapus seluruhnya.
>
> Kenapa ini serius:
>
> - **C-13** meminta persis ini — *Identity Memory* permanen
>   (*"User is consistently committed to strength training"*) harus bisa
>   **dibantah** pengguna, bukan cuma dihapus.
> - **B-17** — satu salah hitung di Wardrobe Graph (*"kamera melihat 12
>   shirts"*) meracuni semua rekomendasi sesudahnya, dan hanya koreksi manual
>   yang menghentikannya.
> - **§8.32** sendiri bertanya *"What happens if AI is wrong?"* — dan Privacy
>   Center adalah tempat jawabannya seharusnya berada.
>
> Menghapus bukan pengganti memperbaiki: pengguna yang salah dikarakterisasi
> harus membuang seluruh riwayatnya untuk membetulkan satu kesimpulan.
> Butir **H-4** ditutup atas dasar lima kata kerja naskah 4; penutupan itu
> mengandaikan `Edit` ada. Lihat **E-74** / [#64](../../issues/64).

> ⚠️ **`Export` dan `Download` berdampingan tanpa dibedakan.** Kemungkinan
> besar keduanya hal yang sama (§8.40 hanya punya `data_export_requests`).
> Kalau memang beda — mis. *Export* menyiapkan berkas, *Download* mengambilnya —
> itu satu alur, bukan dua fitur.

---

## §8.37 — Personal AI Permission Dashboard

```
MY AI

Habit Coach
├── Habits       ✓
├── Sleep        ✓
├── Location     ✗
└── Finance      ✗

Fashion Agent
├── Wardrobe     ✓
├── Preferences  ✓
├── Camera       Ask
└── Location     ✗

Travel Agent
├── Calendar     ✓
├── Location     Ask
├── Passport     ✗
└── Purchase     Confirmation Required
```

> Ini jauh lebih powerful daripada sekadar halaman privacy biasa.

---

> ⭐⭐ **Ini bentuk `permissions` yang bisa dilihat manusia — dan ia cocok
> baris demi baris dengan tabel di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md).** Setiap baris adalah
> `(subject_id, scope, decision)`, dan ketiga nilai `✓ / ✗ / Ask` adalah
> `allow / deny / ask` persis. Tidak ada terjemahan yang hilang di antara
> rancangan dan skema — hal yang jarang terjadi di dua belas naskah.
>
> ⭐ **`Camera: Ask` menjawab C-1 di tempat yang benar.** Kamera sebagai
> antarmuka utama (naskah 4 §20) membuat permukaan data biometrik melebar;
> di sini ia berdiri sebagai izin tersendiri dengan nilai bawaan *Ask*, bukan
> sebagai bagian dari izin *Wardrobe*. Yang masih kurang: berapa lama
> gambarnya disimpan, dan apakah *Allow once* (naskah 4 §15) tersedia di sini.
>
> ⭐ **`Purchase: Confirmation Required` adalah §8.18 yang terlihat oleh
> pengguna** — keputusan policy keempat muncul di antarmuka, bukan hanya di
> mesin.

> ⚠️ **Dashboard ini memakai model akses §8.6 (per kategori data), bukan model
> §8.11 (per pertanyaan).** Tidak ada baris *"boleh menanyakan rata-rata
> tidur"*. Ini bukti ketiga bahwa Personal Data Vault berdiri sendirian —
> lihat **E-71** / [#62](../../issues/62).

> ⚠️ **`Habit Coach`, `Fashion Agent`, `Travel Agent` — tak satu pun ada di
> V0.** V0 punya empat agent: Orchestrator, Coach, Habit, Memory. Dashboard
> ini menggambarkan V2+; untuk V0 ia berisi empat baris agent dengan scope
> `habits`, `goals`, `checkins`, `mood`, `coaching_notes`. Itu tetap layak
> dibangun sejak V0 — justru karena isinya sedikit, ia mudah dibuat benar.

---

## §8.38 — Data Deletion Architecture

User harus dapat mengatakan: *"Hapus semua data saya."*

```
Delete Request
      ↓
Identity Verification
      ↓
Deletion Coordinator
      ↓
PostgreSQL
      ↓
Vector DB
      ↓
Graph DB
      ↓
Object Storage
      ↓
Feature Store
      ↓
Caches
      ↓
Backups / Retention Policy
      ↓
Deletion Verification
```

> Karena HumanVerse memiliki banyak storage, deletion harus **distributed
> deletion**, bukan hanya `DELETE FROM users`.

---

> ⭐⭐ **Tiga langkah yang tidak ada di naskah 11 §7.25, dan ketiganya
> menentukan:**
>
> | Langkah baru | Kenapa penting |
> |---|---|
> | **Identity Verification** di depan | tanpa ini, penghapusan adalah senjata: siapa pun yang menguasai sesi bisa menghapus seumur hidup data orang |
> | **Deletion Coordinator** | penghapusan lintas tujuh penyimpanan **bukan transaksi**; harus ada yang mengingat sudah sampai mana dan mengulang yang gagal |
> | **Deletion Verification** di belakang | *"sudah dihapus"* yang tidak diperiksa adalah klaim, bukan fakta |

> ⭐ **`Backups / Retention Policy` masuk daftar.** Di sesi 9 saya menambahkan
> **cadangan** sebagai tempat kedelapan yang tidak disebut naskah 11 —
> penghapusan yang tidak menyentuh backup akan kembali saat pemulihan.
> Naskah ini memasukkannya sebagai langkah nyata. Tambahan itu terbukti benar.

> ⚠️ **Dua tempat dari naskah 11 menghilang:**
>
> - **`Events`** — naskah 11 menghapusnya; di sini tidak disebut. Kalau ini
>   disengaja, ia justru **menyelesaikan** tabrakan dengan aturan C
>   [`../spec/02`](../spec/02-ERD.md) (*event tidak pernah diubah*). Tapi
>   karena tidak dinyatakan, tidak ada yang tahu apakah event tinggal atau
>   pergi.
> - **`Lakehouse`** — tempat **tersulit** dari semuanya, karena Parquet tidak
>   punya `DELETE` dan butuh penulisan ulang partisi. `Object Storage`
>   mungkin dimaksudkan mencakupnya (Parquet memang tinggal di sana), tapi
>   itu tidak sama: object storage menghapus **berkas**, lakehouse harus
>   menghapus **baris di dalam berkas**.

> 🛑 **Tiga tabel log tidak ada di rantai ini, dan ketiganya berisi data
> pribadi.** §8.40 menambahkan `audit_logs`, `data_access_logs`, dan
> `security_events`; §8.41 memberi `SecurityEvent` field **`ip`** dan
> **`device`**. Sementara itu §8.34 mewajibkan `Preserve evidence`.
>
> Butir **C-9** menanyakan ini sejak naskah 4, dan setelah naskah yang khusus
> membahas privasi, ia justru **membesar**: dulu satu tabel jejak audit,
> sekarang tiga, dan salah satunya menyimpan alamat IP.
>
> 🔴 Perhatikan juga bahwa `audit_logs` di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) menyimpan **`ip_hash` — hash,
> bukan IP mentah**, dan `user_id`-nya sengaja tanpa FK supaya jejak audit
> selamat dari penghapusan akun. Dua keputusan itu sudah setengah menjawab
> C-9; `ip` mentah di §8.41 membalik yang pertama. Lihat [#22](../../issues/22).
