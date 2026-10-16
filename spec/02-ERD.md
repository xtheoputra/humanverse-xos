# 02 — ERD & aturan kepemilikan data

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).

---

## Relasi

```
                              ┌───────────┐
                              │   users   │
                              └─────┬─────┘
                                    │ 1:1
                              ┌─────▼─────┐
                              │ profiles  │
                              └───────────┘
        ┌───────────────┬───────────────┬───────────────┬──────────────┐
        │ 1:N           │ 1:N           │ 1:N           │ 1:N          │
  ┌─────▼─────┐   ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐ ┌────▼─────┐
  │ consents  │   │permissions │  │   goals    │  │   habits   │ │  events  │
  └───────────┘   └────────────┘  └─────┬──────┘  └─────┬──────┘ └────┬─────┘
                                        │ 1:N           │ 1:N         │
                                 ┌──────▼───────┐ ┌─────▼──────────┐  │
                                 │goal_milestones│ │habit_completions│ │
                                 └──────────────┘ └────────────────┘  │
                                        ▲                             │
                                        │ goals.parent_id (self)      │
                                                                      │
        ┌───────────────┬───────────────┬───────────────┐             │
        │ 1:N           │ 1:N           │ 1:N           │ 1:N         │
  ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐      │
  │daily_checkins│ │mood_entries│  │journal_    │  │ activities │      │
  │            │  │            │  │  entries   │  │            │      │
  └────────────┘  └────────────┘  └────────────┘  └────────────┘      │
                                                                      │
                              ┌───────────┐                           │
                              │ memories  │◄──────────────────────────┘
                              └───────────┘   memories.source_event_id
                                    │
                                    │ embedding_id (bukan FK)
                                    ▼
                              [ Qdrant ]

  ┌──────────┐ 1:N  ┌─────────────┐ 1:N  ┌────────────┐
  │  agents  ├─────►│ agent_tools │      │agent_runs  │
  └────┬─────┘      └─────────────┘      └─────┬──────┘
       │ 1:N                                   │ self: parent_run_id
       └────────────────────────────────────►──┘
                                               │ 1:N
  ┌──────────────────┐ 1:N ┌────────────┐      │
  │ ai_conversations ├────►│ai_messages │◄─────┘  ai_messages.agent_run_id
  └──────────────────┘     └────────────┘

  ┌─────────────────┐ 1:N ┌──────────────────────────┐
  │ recommendations ├────►│ recommendation_feedback  │
  └────────┬────────┘     └──────────────────────────┘
           │ agent_id → agents · agent_run_id → agent_runs

  ┌──────────────┐        ┌────────────┐
  │ human_states │        │ audit_logs │  user_id TANPA FK (disengaja)
  └──────────────┘        └────────────┘
```

---

## Aturan kepemilikan data

| Aturan | Isi |
|---|---|
| **A. Satu pemilik** | Setiap baris berisi data pribadi punya `user_id`. Tidak ada pengecualian selain `agents`, `agent_tools`, dan `audit_logs`. |
| **B. Cascade dari `users`** | Semua tabel pribadi memakai `ON DELETE CASCADE` ke `users`. Satu `DELETE` menghapus seluruh jejak — kecuali audit dan Qdrant. |
| **C. Event tidak pernah diubah** | Baris `events` hanya ditulis sekali. Koreksi ditulis sebagai event baru, bukan `UPDATE`. **Ditegakkan basis data** sejak 17 Sep 2026: peran aplikasi tidak punya `UPDATE`/`DELETE` atas `events` ([`01`](01-DATABASE-SCHEMA.md) §10). |
| **D. Tabel domain adalah proyeksi** | `habit_completions` dll. boleh dibangun ulang dari `events`. Kalau keduanya berbeda, **event yang benar**. |
| **E. Agent tidak memiliki data** | Agent hanya menulis lewat `agent_runs`, `recommendations`, dan `memories`. Tidak ada agent yang menulis langsung ke `goals`, `habits`, atau `journal_entries`. |
| **F. Audit tidak menyimpan isi** | `audit_logs.metadata` boleh memuat id dan nama aksi, **tidak pernah** isi jurnal, isi pesan, atau isi memori. |
| **G. Baris hanya terlihat oleh pemiliknya** 🆕 | Peran aplikasi hanya membaca, mengubah, dan menulis baris pengguna yang sedang dilayani transaksi — RLS di 21 tabel ([`01`](01-DATABASE-SCHEMA.md) §11). Pemilik, 17 Sep 2026 (**H-27**): *“data masing-masing pengguna milik pribadi user.”* |
| **H. Anak dan induk satu pemilik** 🆕 | FK antara dua tabel milik pengguna selalu **pasangan** `(induk_id, user_id)` — baris anak milik B tidak bisa menunjuk induk milik A (**B-41**). RLS saja tidak cukup: pemeriksaan FK PostgreSQL tidak menerapkan RLS. |
| **I. Aplikasi bukan pemilik tabel** 🆕 | api tersambung sebagai anggota `hvx_app` — bukan superuser, bukan pemilik, tanpa `BYPASSRLS` — dan menolak mulai kalau tidak (**B-40**). Tanpa ini, G dan H hanya berlaku bagi yang mau mematuhinya. |

> Aturan **E** adalah pencegahan dini untuk **B-12** (ratusan agent menulis ke
> data yang sama). Selama agent hanya menulis ke tiga tabel miliknya sendiri,
> tidak ada dua agent yang bisa saling menimpa catatan pengguna.
>
> Aturan **G · H · I** dijaga `tests/integration/test_kepemilikan_data.py` —
> di katalog (tabel ke-24 tidak bisa lupa) **dan** di perilaku (pengguna A
> sungguh tidak bisa melihat atau menyentuh baris B).

---

## Yang sengaja tidak dijadikan foreign key

| Kolom | Alasan |
|---|---|
| `audit_logs.user_id` | FK akan membuat penghapusan akun mustahil atau menghapus buktinya. Lihat **C-9**. |
| `memories.embedding_id` | Menunjuk ke Qdrant, bukan PostgreSQL. Harus dibersihkan manual saat hapus akun. |
| `permissions.subject_id` | Bisa menunjuk agent, tool, atau integrasi — tiga tabel berbeda; dijaga di lapisan aplikasi. |
