# 176 — Phase 11: Agentic Intelligence & Agency Layer (ikhtisar naskah kelimabelas)

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Penomoran

Naskah ini menomori bagiannya berawalan fase — `11.1`–`11.64` — seperti naskah
14. Berkas rapi memakainya apa adanya sebagai **`§11.1`–`§11.64`**. Enam puluh
empat bagian: **naskah terpanjang dari lima belas**.

---

## Posisi pemilik

> Phase 11 adalah salah satu fase **paling penting**, karena di sini HumanVerse
> mulai berubah dari sistem yang *"bisa memahami dan memberi saran"* menjadi
> sistem yang **mampu bertindak secara terkontrol**.

> Perception membuat HumanVerse bisa **melihat**.
> Cognition membuat HumanVerse bisa **memahami**.
> Agency membuat HumanVerse bisa **bertindak**.

Prinsip fundamentalnya:

> ## Autonomy must be earned, bounded, observable, reversible, and revocable.

> Kita **tidak** membuat satu AI yang memiliki akses penuh terhadap kehidupan
> pengguna. Kita membuat **Agentic Operating Layer** dengan permission, policy,
> risk, planning, verification, execution, monitoring, dan human approval.

---

> ⭐⭐⭐ **Lima kata sifat di kalimat prinsip itu adalah kontribusi terbesar
> naskah ini, dan tiga di antaranya belum pernah ada.**
>
> | Sifat | Sudah ada sebelumnya? | Di mana ia dijalankan |
> |---|---|---|
> | **bounded** | ✅ §8.17, §8.18 | tangga risiko + policy |
> | **observable** | ✅ §8.25, §10.25 | audit trail + provenance |
> | **earned** | 🆕 | §11.35 simulasi + §11.56 sertifikasi sebelum otonomi diberikan |
> | **reversible** | 🆕 | §11.27 Reversibility Engine |
> | **revocable** | 🆕 | §11.24 watchdog freeze + §11.61 revoke/kill |
>
> **`reversible` yang paling menentukan.** Empat belas naskah mengukur risiko
> dari **akibat** sebuah aksi; §11.27 menambahkan sumbu yang berbeda: **seberapa
> sulit aksi itu dibatalkan**. Itu menjelaskan kenapa transaksi finansial
> berbahaya bukan karena nilainya, melainkan karena **tidak bisa ditarik**.
>
> Dan **`earned`** membalik bawaan yang selama ini tersirat: otonomi bukan
> sesuatu yang dimiliki agent lalu dibatasi, melainkan sesuatu yang **harus
> dibuktikan dulu**.

---

## §11.1 — Evolusi HumanVerse

```
Perception → Cognition → Agency → Action → Observation → Feedback → Learning
```

```
              HUMANVERSE
       ┌───────────┴───────────┐
   PERCEPTION              COGNITION
       └───────────┬───────────┘
              AGENTIC LAYER
        ┌──────────┼──────────┐
     PLAN       DECIDE      ACT
        └──────────┼──────────┘
                VERIFY → OBSERVE → LEARN
```

---

> ⭐ **`VERIFY` sebelum `OBSERVE` adalah urutan yang benar dan jarang ditulis.**
> Verifikasi menjawab *"apakah aksinya benar-benar terjadi seperti yang
> diminta"*; observasi menjawab *"apa akibatnya"*. Sistem yang melewatkan yang
> pertama akan belajar dari aksi yang sebenarnya gagal — persis yang §9.26
> `Verify` isyaratkan dan §11.25 kerjakan.

---

## §11.2 — Apa yang dimaksud Agency

> Agency bukan sekadar *"AI menjalankan tool"*.

```
Understand Goal → Understand Context → Generate Plan → Evaluate Options
→ Select Strategy → Request Permission → Execute Actions → Verify Results
→ Handle Failure → Observe Outcome → Learn
```

> **Agent = Reasoning + Planning + Tools + Memory + Policy + Execution +
> Feedback**

---

> ⭐ **`Handle Failure` sebagai langkah setara, bukan sebagai catatan kaki.**
> Sebelas langkah, dan salah satunya khusus untuk kegagalan — itu yang
> membedakan sistem yang dirancang untuk dijalankan dari sistem yang dirancang
> untuk didemokan. §11.25 mengisinya dengan klasifikasi kegagalan yang benar.

> ⚠️ **`Request Permission` berada di tengah, sesudah `Select Strategy`.**
> Artinya agent memilih strateginya **sebelum** tahu apakah ia diizinkan —
> lalu bisa jadi harus mengulang. Urutan yang lebih hemat: batasan izin masuk
> sebagai **constraint** ke `Generate Plan` (§11.8 memang menerima
> `Constraints`), dan `Request Permission` di sini hanya untuk konfirmasi
> manusia. Kalau tidak, setiap penolakan izin berarti satu siklus perencanaan
> terbuang.

---

## §11.3 — Agentic Architecture

```
HUMAN → INTERFACE → COGNITIVE RUNTIME
                  ┌─────┴─────┐
              CONTEXT      MEMORY
                  └─────┬─────┘
                     PLANNER
                  AGENT MANAGER
              ┌────────┴────────┐
          SPECIALIST        SPECIALIST
             AGENT             AGENT
              └────────┬────────┘
                 POLICY ENGINE
                  RISK ENGINE
               PERMISSION ENGINE
                  ACTION GATE
                 TOOL EXECUTOR
                EXTERNAL WORLD
                  OBSERVATION
                 VERIFICATION
                   FEEDBACK
```

---

> ⭐⭐ **Empat gerbang berderet antara agent dan dunia luar** — Policy → Risk →
> Permission → Action Gate. Bandingkan dengan risk gate
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) yang punya tiga, dan §8.2 yang
> menempatkan Policy sebelum Risk.
>
> ⚠️ Urutannya **berbeda lagi**: di sini Policy → Risk; di §8.18 Risk → Policy;
> di §8.2 Policy → Risk. Dua dari tiga menaruh Policy dulu, tapi §8.18 yang
> benar secara isi — Policy Engine **menerima `risk` sebagai masukan**
> (`policy: { risk: R4, require_confirmation: true }`), jadi risiko harus sudah
> dihitung sebelum policy memutuskan. Ini tabrakan urutan yang sama, kini di
> naskah ketiga; sebaiknya ditetapkan sekali.

> ⚠️ **`AGENT MANAGER` adalah nama baru untuk sesuatu yang sudah punya dua
> nama.** Naskah 5 §13 memakai **Orchestrator**; §11.4 memakai **Supreme
> Orchestrator**; di sini **Agent Manager** berdiri di antara Planner dan
> agent. Kalau ketiganya benda yang sama, satu nama sudah cukup; kalau tidak,
> bedanya perlu ditulis — karena §11.38 mendaftarkan `Agent Loader`,
> `Agent Registry`, dan `Task Scheduler` sebagai komponen terpisah lagi.
