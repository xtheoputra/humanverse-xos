# 179 — §11.12–§11.14 Execution Engine, Action Object & Action Gateway

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.12 — Agent Execution Engine

```
Plan → Task Queue → Task Scheduler → Permission → Policy
→ Tool Executor → External System → Result
```

Contoh — *"Tambahkan meeting ke calendar"* — **bukan**:

```
LLM → calendar
```

tetapi:

```
LLM → Structured Action → Validator → Permission → Risk → Calendar Tool
```

---

> ⭐⭐ **`LLM → Structured Action` adalah batas yang menentukan seluruh
> arsitektur ini.** Model tidak memanggil apa pun; ia **menghasilkan objek**
> yang kemudian diperiksa. Itu perbedaan antara sistem yang bisa diaudit dan
> sistem yang tidak — dan ia juga yang membuat §8.20 (prompt injection) bisa
> ditahan: teks jahat paling jauh hanya bisa menghasilkan *usulan aksi*, dan
> usulan itu tetap harus lolos empat gerbang.

> ⚠️ **`Calendar Tool` di sini, `Calendar Agent` di §11.4.** Dua bentuk untuk
> satu benda di naskah yang sama — lihat **E-94**.

---

## §11.13 — Action Object

```json
{
  "action_id": "act_001",
  "agent_id":  "calendar-agent",
  "tool":      "calendar.create_event",

  "input": {
    "title":    "AI Study",
    "start":    "2026-09-07T19:30:00",
    "duration": 120
  },

  "risk_level": "R1",
  "requires_confirmation": false
}
```

---

> ⭐ **Bentuk `<domain>.<verb>` pada `tool` cocok persis dengan tool registry
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)** (`habit.streak`,
> `memory.search`). Salah satu dari sedikit penamaan yang tidak bergeser.

> ⚠️ **`agent_id: "calendar-agent"` sementara `tool: "calendar.create_event"`**
> — agent dan tool memakai nama yang sama untuk hal yang berbeda. Kalau
> Calendar Agent adalah agent tipis yang memiliki `calendar.*`, itu masuk akal;
> tapi dua benda bernama sama akan tertukar di log.

> 🛑 **`requires_confirmation` kini ada di TIGA tempat, dan tak satu pun
> menyatakan mana yang otoritatif:**
>
> | Tempat | Bentuk |
> |---|---|
> | manifest naskah 5 §14 | `requires_confirmation: []` — dibuang naskah 10, tidak kembali di §11.5 |
> | **policy** §8.18 & §11.37 | `require_confirmation: [booking.hotel, booking.flight]` |
> | **action object** §11.13 | `requires_confirmation: false` |
>
> Yang paling masuk akal: **policy adalah sumbernya, action object adalah
> hasilnya** — nilai `false` di atas dihitung dari policy, bukan ditulis agent.
> Kalau agent yang menuliskannya, seluruh alasan memindahkannya ke policy
> (naskah 12: supaya penulis agent tidak menentukan sendiri kapan penggunanya
> dimintai izin) batal.
>
> Satu kalimat cukup: *"`requires_confirmation` pada Action Object adalah
> keluaran Action Gateway, bukan masukan dari agent."* Lihat **G-12**.

> ⚠️ **Ejaan masih dua**: `require_confirmation` (policy §8.18, §11.37) vs
> `requires_confirmation` (§11.13, naskah 5). Sepele, dan akan hidup
> bertahun-tahun kalau tidak diputuskan sekarang.

---

## §11.14 — Action Gateway

> Ini menjadi **firewall untuk tindakan AI**.

```
Agent
 ↓
Action Gateway
 ├── Schema Validator     ├── Risk
 ├── Authentication       ├── Policy
 ├── Authorization        ├── Rate Limit
 ├── Consent              ├── Budget Check
 └──────────────────────  └── Confirmation
 ↓
Tool
```

> Agent **tidak boleh bypass gateway**.

---

> ⭐⭐⭐ **Sembilan pemeriksaan dalam satu gerbang, dan tiga di antaranya belum
> pernah ada di rantai mana pun.**
>
> | Pemeriksaan | Sudah ada di |
> |---|---|
> | Schema Validator | §8.21 `Tool Validator` |
> | Authentication · Authorization | §8.2, §8.5, §8.6 |
> | Consent | §8.9 |
> | Risk · Policy | §8.16, §8.18, spec/05 |
> | **Rate Limit** | 🆕 di gerbang — sebelumnya hanya field tool registry (`60/min/user`) |
> | **Budget Check** | 🆕 — §11.17/§11.18 |
> | Confirmation | §8.17 |
>
> **`Budget Check` yang paling berkonsekuensi.** Ia mengubah pagu biaya
> (**B-2**, **H-6**) dari niat menjadi gerbang: agent yang kehabisan anggaran
> **berhenti**, bukan melambat. Itu juga satu-satunya mekanisme di lima belas
> naskah yang membatasi biaya **per agent**, bukan per sistem.
>
> Dan *"agent tidak boleh bypass gateway"* adalah versi agent dari batas
> Control Plane §8.42 (*"tidak ada modul agent yang boleh mengimpor
> `security/`"*). Keduanya perlu ditegakkan CI, bukan diniatkan —
> [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) sudah punya mekanismenya.

> ⚠️ **`Consent` dan `Authorization` sebagai dua pemeriksaan berbeda** benar,
> dan bedanya perlu ditulis sekali: *authorization* menjawab **agent ini boleh
> menyentuh scope ini**; *consent* menjawab **pengguna masih mengizinkan
> tujuannya**. Yang kedua bisa dicabut tanpa mengubah yang pertama — itu
> gunanya `condition: { consent: true }` §8.7.

> ⚠️ **Urutannya belum ditetapkan, dan urutan menentukan biaya.**
> `Schema Validator` harus pertama (permintaan tak berbentuk tidak perlu
> sampai ke mesin izin — §8.21 sudah benar soal ini), dan `Confirmation` harus
> **terakhir** (jangan pernah bertanya kepada pengguna untuk aksi yang
> ternyata akan ditolak policy). Delapan pemeriksaan di antaranya bebas
> urutan, kecuali `Risk` sebelum `Policy` — karena policy menerima risk sebagai
> masukan.
