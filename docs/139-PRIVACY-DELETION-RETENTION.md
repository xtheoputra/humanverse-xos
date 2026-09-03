# 139 — §7.24–§7.26 Privacy Architecture, Deletion Engine & Retention

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.24 — Data Privacy Architecture

> Data pipeline harus **membawa metadata privacy**.

```json
{
  "data_class": "sensitive",
  "purpose": [ "personalization" ],
  "retention": "90d",
  "consent_required": true
}
```

> Jadi data tidak sekadar `data = data`, tetapi:
>
> ## data + purpose + permission + retention + provenance

---

> ⭐⭐ **Ini bagian terkuat di seluruh naskah kesebelas.** `purpose` yang
> menempel pada datanya sendiri adalah **pembatasan tujuan** yang bisa
> ditegakkan mesin, bukan janji di halaman kebijakan.
>
> Konsekuensinya langsung menjawab butir yang menggantung: data yang
> `purpose: [personalization]` **tidak bisa** dipakai melatih model tanpa
> `purpose` baru dan persetujuan baru — persis yang diminta **C-11**.
>
> Ini juga melengkapi checklist Research Governance (Pillar 15 naskah 9) yang
> mewajibkan `Consent` per riset: yang satu memaksa pertanyaannya ditanyakan,
> yang ini membuat jawabannya **ikut menempel pada datanya**.
>
> Yang perlu ditambahkan supaya lengkap: `consents.kind = 'model_training'`
> sebagai izin tersendiri di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md), dan
> aturan bahwa **menolaknya tidak mengurangi layanan**.

---

## §7.25 — Data Deletion Engine

> Ketika user meminta *"Hapus data saya"*, kita membutuhkan **cascade
> deletion**.

```
User
 ↓ Operational DB
 ↓ Events
 ↓ Lakehouse
 ↓ Features
 ↓ Vector Memory
 ↓ Graph
 ↓ Caches
```

> ## Tidak boleh hanya menghapus row di PostgreSQL.

> ⭐⭐ **Ini memperluas prosedur hapus akun di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) dengan empat tempat yang belum
> saya cakup.** Spesifikasi V0 hanya menangani PostgreSQL (cascade) dan Qdrant
> (manual, lewat `memories.embedding_id`). Naskah ini menambahkan:
>
> | Tempat | Kenapa mudah terlewat |
> |---|---|
> | **Lakehouse** | berkas Parquet tidak punya `DELETE`; butuh penulisan ulang partisi atau *delete vector* |
> | **Features** | nilai turunan tetap membawa jejak perilaku meski event aslinya hilang |
> | **Graph** | simpul yatim tetap menyimpan hubungan (*"pernah bekerja di X"*) |
> | **Caches** | Redis tidak ikut transaksi; data bisa hidup sampai TTL habis |
>
> Ditambah satu yang belum disebut siapa pun: **cadangan (backup)**. Penghapusan
> yang tidak menyentuh backup akan kembali saat pemulihan. Ini yang membuat
> janji *Delete* mahal — dan justru karena itu harus diputuskan sekarang,
> bersama **C-9**.
>
> ⚠️ Perhatikan `Events` ikut dihapus. Itu bertabrakan dengan aturan **C** di
> [`../spec/02`](../spec/02-ERD.md) (*event tidak pernah diubah*) dan dengan
> gagasan event sebagai sumber kebenaran. Keduanya bisa hidup bersama hanya
> bila dinyatakan: event **boleh dihapus atas permintaan pemiliknya**, tidak
> boleh diubah oleh sistem.

---

## §7.26 — Data Retention

```
Created → Active → Archived → Deleted
```

Policy per domain berbeda:

```
Raw telemetry            → short retention
Aggregated analytics     → longer retention
User-controlled memories → explicit policy
```

> ⭐ **Ini yang hilang dari Compression Policy Pillar 4 naskah 9** (**B-20**),
> di mana Raw, Episode, dan Summary sama-sama disimpan *"penuh"* tanpa jendela
> waktu. Di sini prinsipnya benar: *raw pendek, agregat panjang*.
>
> Yang masih perlu: **angkanya**. `"retention": "90d"` di §7.24 adalah satu-
> satunya angka konkret di seluruh naskah — jadikan itu titik awal daftar
> retensi per domain.
