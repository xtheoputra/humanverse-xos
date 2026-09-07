# 208 — §14.4–§14.6 Agent Federation Layer, Agent Identity & Capability System

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.4 — Agent Federation Layer

> HumanVerse **tidak boleh menganggap semua agent harus berada di dalam server
> HumanVerse**.

```
HumanVerse Agent ↕ Federation Gateway ↕ External Agent
```

Agent eksternal bisa berada di: **cloud · perusahaan lain · perangkat lokal ·
edge device · developer server · enterprise infrastructure**

---

> ⭐⭐ **Ini pergeseran arsitektur terbesar naskah ini, dan konsekuensinya
> menyentuh hampir semua butir keamanan yang sudah ada.**
>
> Sampai naskah 17, setiap agent berjalan **di dalam** HumanVerse: manifestnya
> tervalidasi ([`../spec/05`](../spec/05-AGENT-CONTRACTS.md)), risknya terhitung,
> anggarannya terpantau, dan watchdog bisa membekukannya. Federasi membalik
> asumsi itu — **agent yang kodenya tidak pernah dilihat siapa pun, berjalan di
> mesin orang lain**, kini bisa ikut dalam rantai keputusan.
>
> Yang tetap bisa ditegakkan: **apa yang diminta** dan **apa yang diberikan**.
> Yang tidak bisa lagi ditegakkan: **apa yang terjadi di dalamnya**. Karena itu
> §14.19 (Federation Gateway) dan §14.55 (`security: sandbox: required`) bukan
> pelengkap, melainkan syarat.

> ⚠️ **Enam tempat di daftar itu punya sifat keamanan yang sangat berbeda, dan
> naskah memperlakukannya sama.** *Perangkat lokal* milik penggunanya sendiri
> tidak sebanding dengan *server developer pihak ketiga*. Federasi sebaiknya
> punya **tingkat kepercayaan per asal** — dan §14.10 sudah menyediakan
> bahannya (`trust_level: certified`), hanya belum disambungkan ke asal.

---

## §14.5 — Agent Identity

```yaml
agent_id:        agent.travel.planner
organization_id: humanverse
developer_id:    dev_123
version:         2.1.0
trust_level:     certified
```

Identity harus berbeda dari: **Human · Agent · Developer · Organization ·
Device · Service Identity**

---

> ⭐⭐ **Enam jenis identity — dan ini melengkapi tujuh jenis §8.4 dengan yang
> paling penting: `Organization`.**
>
> Butir **C-10** ([#40](../../issues/40)) mencatat bahwa §8.4 memberi tujuh
> jenis identity (User · Agent · Service · Device · Developer · Application ·
> Integration) dan **tak satu pun bisa menampung manusia yang melihat data
> manusia lain**. Organization tidak menyelesaikan itu — ia bukan manusia —
> tetapi ia menyelesaikan setengah masalah lain: **atas nama siapa sebuah agent
> bertindak**, yang selama ini tidak bisa dinyatakan.
>
> Dan `organization_id` + `developer_id` bersama-sama membuat **Developer
> Reputation** §14.10 bisa dihitung, serta membuat pertanyaan *"siapa yang
> bertanggung jawab kalau agent ini merugikan"* punya jawaban di tingkat skema.

> ⚠️ **`trust_level: certified` di dalam identity adalah penempatan yang
> berisiko.** Identity dideklarasikan agent; tingkat kepercayaan **ditetapkan
> HumanVerse**. Kalau keduanya di satu berkas, agent eksternal bisa
> mendeklarasikan dirinya `certified`. §14.10 sendiri menegaskan *"trust score
> bukan security boundary"* — konsisten dengan itu, `trust_level` semestinya
> hidup di **registry HumanVerse**, bukan di identity agent.

---

## §14.6 — Agent Capability System

> Agent tidak diberikan `"access everything"`, tetapi capability tertentu.

```yaml
capabilities:
  - calendar.read
  - calendar.create
  - weather.read
  - travel.search
  - hotel.search
```

Tidak otomatis memiliki: `email.send` · `money.transfer` · `device.control` ·
`account.delete`

---

> ⭐ **Empat larangan itu memetakan tepat ke tangga risiko §11.15**:
> `email.send` = R3 (*important communication*), `money.transfer` = R3–R4,
> `device.control` = R2–R3, `account.delete` = R4 (*irreversible*). Larangan
> dan tangga konsisten — sama seperti §8.8 dan §11.6. **Tiga naskah, satu
> pemetaan.**

> ⚠️ **Bentuk `<resource>.<verb>` di sini** (`calendar.read`), sementara policy
> §11.37 memakai `<verb>.<resource>` (`read.calendar`), dan tool registry
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) memakai `<resource>.<verb>`
> (`habit.streak`).
>
> Dua lawan satu — dan yang menyimpang adalah **policy §11.37**. Itu kabar
> baik, karena policy adalah yang paling belakangan dibangun dan paling mudah
> diselaraskan. Tapi ia harus diselaraskan sebelum baris pertama: policy yang
> memakai bentuk berbeda dari capability **tidak akan cocok tanpa penerjemah**.
