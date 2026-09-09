# Sensus rantai keputusan & keselamatan

> ⚠️ **Bukan kata pemilik.** Pengukuran. Ia tidak menambahkan gerbang dan tidak
> mengubah rantai mana pun — itu tetap [#93](../../issues/93) ·
> [#106](../../issues/106) · [#111](../../issues/111) · [#140](../../issues/140).

---

## Kenapa berkas ini ada

Rantai yang berakhir di tindakan **tanpa gerbang** dicatat satu per satu:
*“rantai kelima”* · *“keenam dan ketujuh”*. Tujuh catatan, tujuh berkas.

🛑 **Tak satu pun pernah menyebut penyebutnya.** *“Rantai ketujuh tanpa
gerbang”* tidak bisa dibaca tanpa tahu **dari berapa**. Berkas ini menghitung
denominatornya.

---

## Cara mengukur, dan dua kekeliruan yang harus dilewati

Dipanen dari **kata pemilik saja** (blok `>` diklasifikasi dari baris
pertamanya), di dalam blok ber-fence.

| Percobaan | Kekeliruan | Akibat |
|---|---|---|
| 1 | hanya membaca rantai **mendatar** (`→`) | rantai **vertikal** (`↓` 507 sebutan, `▼` 311) terlewat seluruhnya — padahal justru bentuk itu yang dipakai naskah 5 untuk menggambar jalur konfirmasi |
| 2 | memperlakukan kata `HUMAN` sebagai gerbang | **`Human Detection` terhitung sebagai persetujuan manusia** — kebalikan artinya. Mendeteksi orang bukan meminta izin orang |
| 3 | dua bentuk panah + kosakata gerbang yang menahan, bukan yang mengamati | ✅ dipakai |

> 💡 Kekeliruan (2) layak diingat: **kata yang sama bisa menandai pengaman atau
> justru sensor yang memicu tindakan.** `Human Detection` di rantai robot adalah
> pemicu, bukan rem.

---

## 🔴 Hasil — dan denominatornya baru pertama kali ada

| | |
|---|---|
| rantai ber-panah di naskah | **387** |
| berakhir di **tindakan** | **36** (di 31 berkas) |
| **punya gerbang di dalam rantainya** | **20** |
| tidak punya | **16** |

⭐ **Dua puluh dari tiga puluh enam rantai tindakan MEMANG punya gerbang.**
Angka itu belum pernah ditulis — tujuh catatan sebelumnya hanya melaporkan yang
gagal. Sebagian besar jalur tindakan di repo ini **sudah dijaga**.

---

## Klasifikasi keenam belas — dan sepuluh di antaranya BUKAN cacat

Pemindai menandai 16. Diperiksa satu per satu:

| Berkas | Rantai | Vonis |
|---|---|---|
| [`55`](55-GOAL-INTELLIGENCE.md) | `Goal → Milestones → Projects → Habits → Daily Actions` | ❌ dekomposisi tujuan — tindakan **penggunanya sendiri** |
| [`69`](69-PRIVACY-CENTER-VAULT-AUDIT.md) | `Request → Agent → … → Recommendation → User action` | ❌ berakhir di tindakan **pengguna** |
| [`74`](74-EKOSISTEM-AKHIR-DAN-LOOP.md) | `HUMAN → ACTION → OBSERVATION → … → RECOMMEND → HUMAN → ACTION` | ❌ gelung observasi; manusia yang bertindak |
| [`137`](137-PIPELINE-QUALITY-LINEAGE.md) | `Recommendation → Model → Feature → Event → Original User Action` | ❌ rantai **provenans**, arahnya mundur |
| [`147`](147-AI-SAFETY-LAYER.md) | `Input Safety → … → Action Safety` | ❌ ini justru **rantai lapisan keselamatan** |
| [`149`](149-AGENT-TRUST-SANDBOX-SUPPLY-CHAIN.md) | `Code → SAST → … → Deploy` | ❌ pipeline CI/CD |
| [`150`](150-THREAT-MODEL-RED-TEAM-INSIDEN-KILL-SWITCH.md) | `KILL SWITCH → Stop Agents/Tools/Actions` | ❌ mekanisme **penghenti** |
| [`162`](162-COGNITIVE-ORCHESTRATOR-DAN-RUNTIME.md) | `USER REQUEST → COGNITIVE ORCHESTRATOR → …` | ❌ diagram alur kognitif, bukan jalur eksekusi |
| [`178`](178-PLANNING.md) | `Goal → … → Subtask → Action` | ❌ dekomposisi tujuan |
| [`199`](199-INTENT-CONTEXT-MEMORY-KNOWLEDGE-OS.md) | `Intent → Goal → … → Plan → Actions` | ❌ struktur perencanaan |
| [`241`](241-OPTIMASI-GOAL-AGEN-KLINIS-REKAM-MEDIS.md) | `Goal → … → Weekly Target → Daily Action` | ❌ rencana latihan pengguna |
| [`233`](233-ROS-EMBODIED-MEMORY-SKILL-TASK.md) | `Goal → Skill Composition → Execution` | ⚠️ **diringankan** — catatan naskahnya menyatakan tiap keterampilan sudah lulus §16.26 lebih dulu; gerbangnya ada di **hulu**, bukan di rantainya |
| [`266`](266-PHASE-20-POSITIONING-CORE-PRINCIPLE-DAN-ARSITEKTUR.md) | `Human → Intent → AI → Recommendation → Decision → Action` | ⚠️ sudah tercakup **[#140](../../issues/140)** (§20.35 ada, lima jalur tak melewatinya) |
| **[`223`](223-XR-INTERACTION-GESTURE-EYE-TRACKING.md)** | **§15.15** `Hand Tracking → Gesture Recognition → Intent → Action` | 🆕 **cacat** |
| **[`229`](229-HUMANOID-LOKOMOSI-MOTION-MANIPULASI.md)** | **§16.5** `Human Goal → World Model → Motion Planner → Joint Controller → Execution` | 🆕 **cacat** |
| **[`229`](229-HUMANOID-LOKOMOSI-MOTION-MANIPULASI.md)** | **§16.7** `Target → Obstacle Map → Trajectory → Collision Check → Optimization → Execution` | 🆕 **cacat** |

⇒ **Dari 16 yang ditandai, 10 bukan cacat, 2 sudah tertangani, dan 3 benar-benar
baru.** Pemindai tanpa pemeriksaan tangan akan melaporkan 16.

---

## 🛑 Tiga yang baru — dan ketiganya menggerakkan benda fisik

**§15.15 Gesture Engine** —
`Hand Tracking → Gesture Recognition → Intent → Action`.
Tabel di bagian yang sama memetakan gestur ke perintah (*Wave → Dismiss*).
**Lambaian tangan menjadi tindakan tanpa satu simpul pun di antaranya.** Tidak
ada `Permission`, `Risk`, maupun `Confirmation`. Bandingkan §15.22 (Spatial
Safety) yang **punya** `Permission` — dua rantai di naskah yang sama, satu
dijaga, satu tidak, dan yang tidak dijaga justru yang dipicu **gerakan tubuh**,
bentuk masukan yang paling mudah keliru terbaca.

**§16.5 Humanoid Intelligence** —
`Human Goal → World Model → Motion Planner → Joint Controller → Execution`.
Ini pipa utama humanoidnya, dan ia berjalan **dari tujuan manusia langsung ke
kendali sendi**. Kemampuan yang didaftarkan bagian itu termasuk *“membuka
pintu”* — catatan audit yang sudah ada membahas akibat keamanannya, tetapi
**tidak mencatat bahwa rantainya sendiri tak punya gerbang.**

**§16.7 Motion Planning Engine** —
`Target → Obstacle Map → Trajectory → Collision Check → Optimization → Execution`.
⭐ Ia **punya `Collision Check`** — dan itu berarti sesuatu: ia mencegah
tabrakan. 🛑 Tetapi `Collision Check` menjawab *“apakah geraknya aman secara
fisik”*, bukan *“apakah gerak ini boleh dilakukan”*. Tidak ada policy, risiko,
izin, maupun konfirmasi.

> ⚠️ **Ketiganya di luar cakupan issue yang sudah ada.**
> [#106](../../issues/106) mencakup §15.22 · [#111](../../issues/111) mencakup
> §16.18, §16.13, §16.34. §15.15, §16.5, dan §16.7 tidak tercakup satu pun.

---

## Yang sensus ini **tidak** putuskan

Tidak menambahkan gerbang, tidak menetapkan gerbang mana yang wajib, dan tidak
mengubah urutan rantai mana pun. Ia menambahkan **denominator** yang selama ini
hilang — **20 dari 36 rantai tindakan sudah dijaga** — dan menunjukkan tiga
rantai yang belum pernah diperiksa, ketiganya menggerakkan benda fisik.

Terbit sebagai **[#153](../../issues/153)** (**E-157**).
