# 211 — §14.15–§14.18 Agent Market, Team Architecture, Organizational & Multi-Tenant

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.15 — Agent Market

```
HumanVerse Marketplace
├── Agents · Skills · Tools · Plugins
├── Workflows · Automations · Models
└── Agent Teams          ← konsep baru
```

Contoh **"Personal Travel Team"**: Travel Planner · Weather · Budget · Flight ·
Hotel · Translation · Calendar Agent.

> User cukup mengaktifkan **satu team**.

---

> ⭐⭐ **Agent Team sebagai unit yang bisa dipasang adalah gagasan yang
> menyelesaikan masalah nyata dari §14.9.** Discovery yang harus memilih
> kombinasi terbaik dari ribuan agent adalah masalah optimasi tanpa fungsi
> tujuan; **team yang sudah teruji bersama** memotong masalah itu — pengguna
> memasang satu benda, bukan tujuh.
>
> Dan §14.49 (Agent Team Memory) membuatnya makin masuk akal: kombinasi yang
> sudah terbukti punya riwayat kinerja, jadi ia bukan sekadar bundel melainkan
> **unit yang terkalibrasi**.

> ⚠️ **Tapi satu izin untuk tujuh agent adalah pelonggaran yang tidak
> dinyatakan.** Memasang *Travel Team* berarti menyetujui capability tujuh
> agent sekaligus — termasuk Translation Agent yang membaca teks dan Flight
> Agent yang menyentuh pembelian. §11.28 Action Center menampilkan izin
> **per aksi**; §14.15 memasang **per team**.
>
> Yang perlu ditulis: **izin team adalah gabungan izin anggotanya, dan
> ditampilkan sebagai gabungan itu** — bukan sebagai satu kotak centang.
> Ini kerabat langsung **E-108** ([#90](../../issues/90)), di mana satu pilihan
> antarmuka membatalkan dua pengaman yang sudah ditetapkan.

---

## §14.16 — Agent Team Architecture

```
                 Team Orchestrator
       ┌────────────────┼────────────────┐
   Planner          Researcher        Evaluator
       └────────────────┼────────────────┘
                    Executor
                    Verifier
```

Team juga memiliki: **Team Policy · Budget · Memory · Permissions · Risk ·
Identity**

---

> ⭐⭐⭐ **`Evaluator` dan `Verifier` sebagai peran tersendiri di dalam team
> adalah pemisahan yang benar dan jarang dibuat.**
>
> `Evaluator` menilai **rencana** sebelum dijalankan (§11.11 *Plan
> Verification*); `Verifier` memeriksa **hasil** sesudahnya (§11.1
> `VERIFY → OBSERVE`). Menempatkan keduanya di dalam team — bukan di luar
> sebagai layanan — berarti tiap team membawa pemeriksanya sendiri.
>
> ⚠️ Tapi itu juga masalahnya: **pemeriksa yang menjadi anggota team punya
> kepentingan yang sama dengan yang diperiksanya.** §14.3 dan §11.4 sama-sama
> menetapkan bahwa governance harus **di luar jalur kepentingan**. Evaluator
> internal boleh ada — tapi ia tidak menggantikan Risk Agent dengan veto
> (§14.13), dan itu perlu dinyatakan.

> ⭐ **`Team Identity` melengkapi enam jenis identity §14.5 dengan yang
> ketujuh** — dan ia yang membuat jejak audit tetap terbaca ketika tujuh agent
> bertindak sebagai satu: `agent_teams` dan `agent_team_members` §14.52
> memberinya tabel.

---

## §14.17 — Organizational Agent

```
Company
 ├── HR Agent          ├── Engineering Agent
 ├── Finance Agent     ├── Security Agent
 ├── Sales Agent       └── Executive Agent
 └── Marketing Agent
```

> Tetapi **HR Agent tidak boleh membaca Finance private data tanpa
> permission**.

---

> ⭐ **Ini mengembalikan Enterprise ke peta.** Butir **E-86** mencatat bahwa
> peta 15 fase §10.41 membuang seluruh blok *Enterprise & Business Platform*
> tanpa rumah baru; §14.17–§14.18 memberinya tempat di Phase 14.

> 🛑 **Tetapi contoh larangannya memilih pasangan yang paling mudah, dan
> melewatkan yang paling sulit.** *HR Agent tidak boleh membaca Finance private
> data* adalah pemisahan **antar-departemen** — masalah yang sudah lama punya
> jawaban (namespace, tenant, RBAC).
>
> Yang belum dijawab, dan yang **C-12** ([#46](../../issues/46)) tanyakan sejak
> naskah 8: **apakah HR Agent boleh membaca data pribadi karyawan, dan per
> orang atau hanya agregat?** Larangan §8.10 sudah menutup *employment
> scoring* — pemberi kerja tidak boleh **menilai** pekerja dari data
> kesehatannya. Ia tidak menutup **melihat**.
>
> Dan `Executive Agent` menambah satu lapisan lagi: agent yang bertindak atas
> nama pimpinan, di atas agent departemen. Ketimpangan kekuasaan yang **C-12**
> catat kini punya bentuk teknis.

---

## §14.18 — Multi-Tenant Agent Architecture

```
HumanVerse
├── Tenant A ── Users · Agents · Data · Policies
├── Tenant B ── Users · Agents · Data · Policies
└── Tenant C
```

Harus ada isolasi: **Tenant · Data · Memory · Agent · Network · Credential ·
Policy**

---

> ⭐⭐ **Tujuh sumbu isolasi, dan `Credential Isolation` adalah yang paling
> sering dilupakan.** Isolasi data yang benar tetap bocor kalau dua tenant
> memakai kredensial layanan yang sama ke satu API pihak ketiga — jejaknya
> bercampur di sisi luar, di luar jangkauan HumanVerse.
>
> Ini juga melengkapi §11.53 (isolasi agent: namespace · network · filesystem ·
> secrets · tools · memory · data scope · CPU · runtime) satu tingkat di atas:
> **agent diisolasi di dalam tenant, tenant diisolasi dari tenant.**

> 🛑 **Tetapi multi-tenant menabrak sesuatu yang belum pernah diselesaikan:
> `scope: user-owned`.** §8.7 memberi satu-satunya nilai scope, dan **C-10**
> ([#40](../../issues/40)) mencatat ia secara struktur tidak bisa menyatakan
> *"data orang lain"*.
>
> Dalam tenant perusahaan, hampir **semua** data adalah data orang lain: data
> karyawan dimiliki perusahaan, dilihat HR Agent, atas perintah Executive
> Agent. Tiga pihak, dan model izin hanya punya kata untuk satu.
>
> Ini bukan penundaan yang bisa dilanjutkan: begitu Phase 14 dibangun,
> `user-owned` harus sudah punya saudara. Usul di
> [#40](../../issues/40) tetap: `subject_type = 'human'`, dan
> `scope IN ('user-owned', 'delegated', 'bystander')` — ditambah satu untuk
> lapisan ini: **`organization-owned`**, dengan aturan bahwa data pribadi
> karyawan **tidak pernah** masuk kategori itu hanya karena ia tersimpan di
> tenant perusahaan.
