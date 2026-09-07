# 143 — §8.4–§8.6 Identity, Authentication & Authorization

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.4 — Layer 1: Identity Security

Setiap:

```
User
Agent
Service
Device
Developer
Application
Integration
```

harus mempunyai **identity**.

Contoh:

```yaml
identity:
  id: agent-habit-001
  type: agent
  owner: humanverse-core
  environment: production
  status: active
```

Tidak boleh ada:

```
anonymous agent
anonymous service
untracked automation
```

---

> ⭐ **`owner` dan `environment` adalah dua field yang belum pernah ada.**
> `owner` menjawab pertanyaan yang selalu muncul begitu marketplace hidup —
> *siapa yang bertanggung jawab kalau agent ini berbuat salah* — dan
> `environment: production` mencegah agent uji coba menyentuh data sungguhan.
> Keduanya melengkapi manifest [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> yang punya `status` tapi tidak punya keduanya.

> 🛑 **Tujuh jenis identity, dan *Coach* bukan salah satunya.** Layer 49
> naskah 7 menambahkan **Coaches** sebagai peserta ekosistem: **manusia yang
> melihat data manusia lain**. Di daftar ini ia tidak ada — dan ia juga tidak
> muat ke mana pun. Ia bukan `User` (data yang dilihat bukan miliknya), bukan
> `Agent`, bukan `Service`.
>
> Masalahnya berlanjut ke §8.7: `scope: user-owned` **secara struktur tidak
> bisa menyatakan "data orang lain"**. Sama seperti
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) yang membatasi
> `permissions.subject_type` ke `('agent','tool','integration')` — tak satu
> pun mengenal manusia sebagai subjek izin.
>
> Sebelas naskah membangun model izin untuk **agent**. Aktor yang paling
> berisiko justru **manusia**, dan sesudah naskah yang khusus membahas
> keamanan pun ia masih belum punya tempat. Lihat **C-10** / [#40](../../issues/40).

> ⚠️ **"Layer 1" adalah kali ketiga penomoran Layer dimulai ulang** — Layer
> 6–20 (naskah 3), Layer 21–50 (naskah 7), Layer 1–25 (naskah 10, ditulis
> `DP-L`), sekarang Layer 1–2 lagi. Dan ia berhenti di Layer 2: empat puluh
> bagian sesudah §8.6 tidak memakai nomor Layer sama sekali. Lihat **G-7**.

---

## §8.5 — Authentication

```
User
 ├── Password
 ├── Passkey
 ├── MFA
 ├── OAuth
 └── Device authentication

Service
 ├── Service identity
 ├── mTLS
 └── short-lived credentials

Agent
 ├── Agent identity
 ├── signed manifest
 └── scoped token
```

Prinsip:

> **Credential harus short-lived dan memiliki scope sekecil mungkin.**

---

> ⭐ **`signed manifest` menutup lubang yang tidak pernah dinyatakan.**
> Sepanjang sebelas naskah, manifest agent adalah berkas YAML biasa —
> tidak ada yang mencegah isinya diubah setelah lolos review. Tanda tangan
> membuat manifest yang sudah direview **tidak bisa diganti diam-diam**, dan
> itulah yang membuat proses review DP-L18 (naskah 10) berarti sesuatu.
> Sejalan dengan `Code signing` dan `Artifact signing` di §8.30.

> ⚠️ **`Password` masih ada di daftar bersama `Passkey`.** Untuk V0 satu
> pengguna, kelima mekanisme User tidak mungkin dibangun semua. Yang perlu
> diputuskan: mana yang masuk V0. Lihat **A-25** / [#58](../../issues/58).

---

## §8.6 — Layer 2: Authorization

Authentication menjawab:

> *"Siapa kamu?"*

Authorization menjawab:

> *"Apa yang boleh kamu lakukan?"*

Contoh — **Habit Agent**:

```
READ:
✓ habits
✓ habit_completions
✓ goals

WRITE:
✓ habit_recommendations

DENY:
✗ financial_accounts
✗ private_messages
✗ medical_records
```

---

> ⭐ **Nama-nama ini persis nama tabel di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md)** — `habits`,
> `habit_completions`, `goals` ada semua. Ini pertama kalinya contoh izin
> dari pemilik memakai nama yang benar-benar bisa dieksekusi, bukan nama
> karangan. `habit_recommendations` yang belum ada tetap konsisten: di
> spesifikasi ia adalah `recommendations` dengan `subject_type = 'habit'`.

> 🛑 **§8.6 dan §8.11 memakai dua model akses yang berbeda, di dalam naskah
> yang sama.** Di sini agent diberi **READ tingkat tabel**. Di §8.11 Personal
> Data Vault dinyatakan sebaliknya:
>
> > *"Data tidak diberikan langsung ke agent."* Agent bertanya
> > *"I need user's sleep average for the last 14 days"*, dan vault
> > mengembalikan `{ "sleep_average": 6.8 }` — **bukan seluruh database
> > sleep**.
>
> Kedua model tidak bisa berlaku bersamaan tanpa aturan yang menyatakan kapan
> masing-masing dipakai. Dan ini bukan dua bagian yang kebetulan berbeda gaya:
> **§8.15 (capability isolation) dan §8.37 (permission dashboard) keduanya
> memakai model §8.6**, sehingga §8.11 berdiri sendirian melawan tiga bagian
> lain di naskahnya sendiri.
>
> Konsekuensinya nyata: `permissions(user, subject, scope, action)` di
> spesifikasi adalah model §8.6. Model §8.11 menuntut permukaan yang sama
> sekali lain — **katalog pertanyaan yang boleh diajukan**, masing-masing
> dengan bentuk jawabannya — dan katalog itu belum pernah ada di dua belas
> naskah. Ini pola yang sama dengan **E-25** (naskah 4 bertabrakan dengan
> dirinya sendiri). Lihat **E-71** / [#62](../../issues/62).

> ⚠️ **`journal` tidak ada di daftar DENY.** Yang ditolak: `financial_accounts`,
> `private_messages`, `medical_records`. Naskah 5 §15 menempatkan *private
> journal* di daftar DENY **bahkan untuk agent internal**, dan
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) melarang agent `third_party`
> meminta scope `journal`. Di naskah yang khusus membahas keamanan, jurnal
> tidak disebut satu kali pun — lihat **G-9**.
