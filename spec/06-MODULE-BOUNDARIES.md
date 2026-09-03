# 06 — Module Boundaries (modular monolith V0)

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menurunkan naskah 5 §1 (*Modular Monolith*) dan §4 (monorepo) menjadi aturan
> yang bisa ditegakkan alat, bukan sekadar niat.

---

## Kenapa modular monolith, bukan 12 service

V0 punya **satu** pengguna nyata: pemiliknya. Memecahnya jadi service berarti
membayar biaya jaringan, deploy, dan penelusuran sebelum ada yang memakainya.
Yang perlu dijaga sejak awal bukan **proses terpisah**, melainkan **batas yang
tidak boleh dilanggar** — supaya pemisahan nanti (V2) jadi pekerjaan sehari,
bukan penulisan ulang.

```
apps/api/                    ← satu proses, satu deploy
└── src/modules/
    ├── identity/
    ├── profile/
    ├── goals/
    ├── habits/
    ├── checkins/
    ├── journal/
    ├── activities/
    ├── events/
    ├── memory/
    ├── intelligence/
    ├── agents/
    └── platform/
```

Setiap modul berbentuk sama:

```
modules/habits/
├── index.ts          ← SATU-SATUNYA pintu keluar (public API modul)
├── routes.ts         ← HTTP; tidak boleh diimpor modul lain
├── service.ts        ← aturan bisnis
├── repository.ts     ← SQL; hanya menyentuh tabel milik modul ini
├── events.ts         ← event yang diterbitkan & didengarkan
└── types.ts
```

---

## Kepemilikan tabel

**Satu tabel dimiliki tepat satu modul.** Modul lain tidak boleh menyentuhnya
dengan SQL — harus lewat `index.ts` pemiliknya.

| Modul | Tabel |
|---|---|
| `identity` | `users`, `consents`, `permissions`, `audit_logs` |
| `profile` | `profiles`, `human_states` |
| `goals` | `goals`, `goal_milestones` |
| `habits` | `habits`, `habit_completions` |
| `checkins` | `daily_checkins`, `mood_entries` |
| `journal` | `journal_entries` |
| `activities` | `activities` |
| `events` | `events` |
| `memory` | `memories` |
| `intelligence` | `recommendations`, `recommendation_feedback` |
| `agents` | `agents`, `agent_tools`, `agent_runs`, `ai_conversations`, `ai_messages` |

---

## Aturan ketergantungan

```
        platform  ◄── boleh dipakai semua
            ▲
            │
   identity ◄── semua modul (untuk cek izin)
            ▲
            │
   ┌────────┴────────┬──────────┬─────────┐
 goals ◄─ habits   checkins   journal   activities
   ▲        ▲          ▲          ▲          ▲
   └────────┴──────────┴──────────┴──────────┘
                       │  (hanya lewat EVENT, bukan panggilan langsung)
                       ▼
                    events
                       ▼
                    memory
                       ▼
                  intelligence
                       ▼
                    agents
```

| # | Aturan | Ditegakkan oleh |
|---|---|---|
| 1 | Modul hanya boleh mengimpor `index.ts` modul lain, tidak pernah berkas dalamnya | lint rule `no-restricted-imports` |
| 2 | Tidak ada impor melingkar | `madge --circular` di CI |
| 3 | Modul domain (`goals`…`activities`) **tidak boleh** saling mengimpor — komunikasinya lewat event | lint + review |
| 4 | `agents` boleh membaca modul lain; **tidak ada** modul yang mengimpor `agents` | lint rule |
| 5 | `repository.ts` hanya boleh menyebut tabel milik modulnya | uji: grep nama tabel per modul |
| 6 | Setiap tulisan ke tabel domain **wajib** menerbitkan event | uji integrasi per modul |

> Aturan **3** yang paling sering dilanggar dan paling mahal dibatalkan. Kalau
> `habits` boleh memanggil `checkins` langsung, keduanya menyatu dalam sebulan
> dan pemisahan V2 jadi mustahil. Kalau lewat event, keduanya tetap bisa
> dipisah kapan saja.
>
> Aturan **6** membuat aturan **D** di [`02-ERD.md`](02-ERD.md) benar: tabel
> domain boleh dibangun ulang dari event **hanya jika** tidak ada tulisan yang
> lolos tanpa event.

---

## Jalan keluar ke V2

Ketika satu modul perlu dipisah jadi service:

1. `index.ts`-nya sudah jadi kontrak — ganti isinya dengan klien HTTP/gRPC.
2. Tabelnya sudah tidak disentuh modul lain — pindahkan basis datanya.
3. Event-nya sudah mengalir lewat antrean — tidak ada yang berubah bagi
   consumer.

Kalau ketiga hal itu tidak benar sejak V0, pemisahan berarti penulisan ulang.
Itulah seluruh alasan aturan di atas ada.
