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
| **C. Event tidak pernah diubah** | Baris `events` hanya ditulis sekali. Koreksi ditulis sebagai event baru, bukan `UPDATE`. |
| **D. Tabel domain adalah proyeksi** | `habit_completions` dll. boleh dibangun ulang dari `events`. Kalau keduanya berbeda, **event yang benar**. |
| **E. Agent tidak memiliki data** | Agent hanya menulis lewat `agent_runs`, `recommendations`, dan `memories`. Tidak ada agent yang menulis langsung ke `goals`, `habits`, atau `journal_entries`. |
| **F. Audit tidak menyimpan isi** | `audit_logs.metadata` boleh memuat id dan nama aksi, **tidak pernah** isi jurnal, isi pesan, atau isi memori. |

> Aturan **E** adalah pencegahan dini untuk **B-12** (ratusan agent menulis ke
> data yang sama). Selama agent hanya menulis ke tiga tabel miliknya sendiri,
> tidak ada dua agent yang bisa saling menimpa catatan pengguna.

---

## Yang sengaja tidak dijadikan foreign key

| Kolom | Alasan |
|---|---|
| `audit_logs.user_id` | FK akan membuat penghapusan akun mustahil atau menghapus buktinya. Lihat **C-9**. |
| `memories.embedding_id` | Menunjuk ke Qdrant, bukan PostgreSQL. Harus dibersihkan manual saat hapus akun. |
| `permissions.subject_id` | Bisa menunjuk agent, tool, atau integrasi — tiga tabel berbeda; dijaga di lapisan aplikasi. |
