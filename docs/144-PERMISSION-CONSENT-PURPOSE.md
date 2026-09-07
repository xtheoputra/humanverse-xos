# 144 — §8.7–§8.10 Permission Engine, Consent Engine & Purpose Limitation

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.7 — Permission Engine

> Kita sudah punya konsep permission dari fase sebelumnya.
> Sekarang kita jadikan **subsystem formal**.

Permission model:

```
Subject
   ↓
Resource
   ↓
Action
   ↓
Scope
   ↓
Condition
   ↓
Decision
```

Contoh:

```yaml
subject: habit-agent
resource: habit
action: read
scope: user-owned
condition:
  consent: true
decision: allow
```

---

> ⭐ **`condition` adalah field yang benar-benar baru dan langsung berguna.**
> Tabel `permissions` di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) hanya
> punya `decision` tetap plus `expires_at`; ia tidak bisa menyatakan
> *"boleh, **selama** persetujuan masih hidup"*. Dengan `condition.consent`,
> pencabutan persetujuan (§8.9) langsung mematikan izin **tanpa perlu
> mengubah baris izinnya** — dan itulah yang membuat tombol *Revoke* di
> Privacy Center benar-benar bekerja, bukan sekadar menandai.
>
> Perubahan yang dibutuhkan di spesifikasi: kolom `condition jsonb`, dan
> evaluasi izin yang membaca `consents` di jalur yang sama.

> ⚠️ **`scope: user-owned` hanya punya satu nilai di seluruh naskah.** Kalau
> itu satu-satunya nilai yang mungkin, ia bukan scope melainkan asumsi. Dan
> selama ia satu-satunya, model ini **tidak bisa menyatakan akses ke data
> orang lain** — yang persis dibutuhkan *Coaches* (**C-10**), *Family Mode*,
> dan *Company Wellness* (**C-12**). Tiga fitur yang sudah dijanjikan Phase 9
> tidak punya kata untuk izinnya.

---

## §8.8 — Granular Permission

Jangan hanya:

```
ALLOW AI
```

Tetapi:

```
ALLOW
 ├── read_profile
 ├── read_habits
 ├── read_sleep
 ├── write_recommendation
 └── notify_user

DENY
 ├── transfer_money
 ├── delete_account
 └── send_message
```

> Ini sangat penting ketika HumanVerse memiliki **ratusan agent**.

---

> ⭐ **Tiga larangan di daftar DENY memetakan tepat ke tiga tingkat risiko
> tertinggi §8.16**: `send_message` = R3, `transfer_money` = R4,
> `delete_account` = R4. Larangan dan tangga risiko akhirnya konsisten satu
> sama lain — sesuatu yang belum pernah terjadi di sebelas naskah sebelumnya.

---

## §8.9 — Consent Engine

Consent bukan sekadar checkbox:

```
☑ I agree
```

Kita buat **Consent Intelligence**. Consent memiliki:

```
Who
What
Why
When
Scope
Duration
Purpose
Revocation
Version
```

Contoh:

```yaml
consent:
  user: user_001
  purpose: fitness_recommendation
  data:
    - workout
    - sleep
    - activity
  duration: 30_days
  status: granted
```

User dapat mencabut:

```
Settings
   ↓
Privacy Center
   ↓
Permissions
   ↓
Fitness Agent
   ↓
Revoke Access
```

---

> ⭐⭐ **Ini bentuk consent terlengkap di dua belas naskah, dan ia menutup
> setengah dari beban hukum yang menggantung sejak naskah 1.** Bandingkan
> dengan tabel `consents` di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md),
> yang punya `kind`, `policy_version`, `granted`, `granted_at`, `revoked_at`:
>
> | Butir §8.9 | Ada di spesifikasi? |
> |---|---|
> | Who · When · Revocation · Version | ✅ `user_id` · `granted_at` · `revoked_at` · `policy_version` |
> | **What** (`data: [workout, sleep, activity]`) | ❌ tidak ada — `kind` hanya satu teks |
> | **Purpose** | ❌ tidak ada |
> | **Duration** | ❌ tidak ada |
> | Why | ❌ tidak ada |
>
> Tiga kolom yang perlu ditambahkan: `purpose text`, `data_scopes text[]`,
> `expires_at timestamptz`.

> ⭐⭐ **`purpose` di sini menutup lingkaran yang dibuka naskah 11.** §7.24
> menempelkan `purpose` pada **datanya**; §8.9 menempelkan `purpose` pada
> **persetujuannya**; §8.10 melarang pemakaian di luar tujuan. Ketiganya
> bersama membentuk satu penegakan yang bisa dijalankan mesin:
>
> ```
> data.purpose  ⊆  consent.purpose   →  boleh
> data.purpose  ⊄  consent.purpose   →  tolak
> ```
>
> Tidak ada satu pun naskah yang menuliskan perbandingan itu, tetapi itulah
> mekanismenya. Selama ini pembatasan tujuan selalu berupa kalimat; sekarang
> ia adalah **satu operasi himpunan antara dua kolom**.

> ⚠️ **`duration: 30_days` berlaku untuk consent, sementara
> `permissions.expires_at` berlaku untuk izin.** Keduanya bisa hidup bersama —
> tapi harus ditulis mana yang menang bila berbeda. Usul: consent adalah
> atapnya; izin tidak boleh hidup lebih lama dari persetujuan yang
> mendasarinya.

---

## §8.10 — Purpose Limitation

> Ini prinsip yang **sangat penting**.

Misalnya user memberikan **sleep data** untuk **sleep recommendation**.
Agent **tidak otomatis boleh** menggunakan data itu untuk:

```
advertising
insurance scoring
employment scoring
```

Jadi:

> **Data boleh digunakan untuk tujuan yang diizinkan, bukan semua tujuan yang
> secara teknis memungkinkan.**

---

> ⭐⭐ **Kalimat penutup itu adalah jawaban paling langsung untuk C-11 dan
> sebagian besar C-12 — dan ia datang dari pemilik sendiri, bukan dari catatan
> audit.**
>
> - **C-11** (melatih model di atas data pengguna ≠ memakainya): data
>   ber-`purpose: fitness_recommendation` tidak bisa melatih Behavior
>   Foundation Model tanpa tujuan baru.
> - **C-12** (*Company Wellness*): **`employment scoring` disebut sebagai
>   larangan eksplisit**. Kekhawatiran terbesarnya — pemberi kerja memakai
>   data kesehatan pekerja untuk menilai pekerjanya — kini dilarang oleh
>   pemilik sendiri, dalam kata pemilik sendiri.
>
> Yang **belum** ditutup dari C-12: apakah *Enterprise Admin* boleh melihat
> data **per orang** atau hanya agregat. Larangan penilaian tidak sama dengan
> larangan melihat.

> 🛑 **Dan justru karena §8.10 benar, ia menimbulkan penghambat baru untuk
> Phase 5.** Kalau data V0 dikumpulkan dengan `purpose: [personalization]`,
> maka **seluruh data V0–V2 tidak bisa dipakai melatih model apa pun di Phase
> 5** — R1 *Behavior Foundation Model*, R2 *Preference*, R6 *Federated
> Personal AI* — tanpa persetujuan baru yang ditanyakan ulang kepada setiap
> pengguna, mundur ke belakang.
>
> Butir **B-21** sudah mencatat bahwa Research Lab tidak bisa mulai sebelum V0
> mengumpulkan datanya. Sekarang ada syarat kedua yang lebih tajam: **data itu
> hanya berguna kalau tujuannya sudah ditanyakan sejak awal**. Ini keputusan
> yang harus diambil **di V0**, bukan di Phase 5 — dan biayanya sekarang hampir
> nol, nanti hampir mustahil.
>
> Yang dibutuhkan: `consents.kind = 'model_training'` sebagai persetujuan
> tersendiri sejak Sprint 1, ditambah aturan bahwa **menolaknya tidak
> mengurangi layanan**. Lihat **B-22** / [#59](../../issues/59).
