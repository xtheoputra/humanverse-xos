# 181 — §11.19–§11.22 Multi-Agent Collaboration, Communication, Negotiation & Conflict Resolution

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.19 — Multi-Agent Collaboration

*"Siapkan perjalanan saya."*

```
Travel Agent
      ├── Weather Agent
      ├── Calendar Agent
      ├── Transportation Agent
      ├── Hotel Agent
      └── Budget Agent
              ↓
         Travel Plan
```

> Tetapi mereka **tidak boleh saling memberikan unlimited permissions**.

---

> ⭐⭐ **Butir E-52 mencatat *Multi-Agent Collective Intelligence* dibuang dari
> sembilan arah riset Phase 5 — dan saya menandainya serius, karena *"ratusan
> AI Agent bekerja secara bersamaan"* adalah janji pembuka naskah 2 dan alasan
> seluruh AgentOS ada.** §11.19–§11.22 mengembalikannya sebagai **rekayasa**,
> bukan riset. Janjinya tidak perlu diturunkan.

> 🛑 **Empat dari lima agent di diagram ini tidak ada di hierarki §11.4** —
> Weather, Transportation, Hotel, Budget. Bersama Productivity Agent §11.59,
> itu lima agent yang hidup di contoh tanpa terdaftar. Pola **E-38**
> (*PreparationAgent*) pada skala lima kali lipat. Lihat **E-95**.

> 🛑🛑 **Dan `Weather Agent` menggerus H-11 secara langsung.** H-11 ditutup
> dengan *"Weather & Calendar = **TOOL**, bukan agent"*. Butir **E-28** mencatat
> alasan butir itu pernah terbuka: naskah 4 §13 memakai `WeatherAgent` sebagai
> contoh komunikasi antar-agent. **Contoh yang sama kembali di sini, dalam
> peran yang sama** — dan §11.20 memperkuatnya dengan `to: "weather-agent"`.
> Lihat **E-94**.

---

## §11.20 — Agent Communication Protocol

```json
{
  "message_id": "msg_001",
  "from": "travel-agent",
  "to":   "weather-agent",
  "intent": "request_forecast",

  "payload": { "location": "Tokyo", "date": "2026-10-10" },

  "authorization": { "scope": "travel_planning" }
}
```

> Semua communication: **authenticated · authorized · validated · logged ·
> traceable**

---

> ⭐⭐ **`authorization.scope` di dalam pesan adalah bentuk pembatasan delegasi
> yang belum pernah ada.** Naskah 5 §13 memberi protocol antar-agent yang
> *"authenticated, logged, traceable, permission-controlled"* — tetapi tanpa
> menunjukkan **bagaimana** izinnya dibatasi. Di sini setiap pesan membawa
> lingkupnya sendiri: `weather-agent` menerima permintaan **untuk keperluan
> travel_planning**, bukan akses umum.
>
> Itu yang mencegah masalah yang §11.19 peringatkan (*"tidak boleh saling
> memberikan unlimited permissions"*): agent yang didelegasikan **tidak bisa
> mewarisi lebih dari lingkup pesannya**.
>
> Digabung dengan rantai delegasi §11.7 (`USER → ORCHESTRATOR → TRAVEL_AGENT →
> BOOKING_AGENT`), ini memberi apa yang `audit_logs` butuhkan: bukan satu
> `actor_id`, melainkan **jalur** dengan lingkup yang menyempit di tiap
> langkah.

> ⚠️ **Aturan yang belum ditulis, dan ia satu kalimat:** *lingkup pesan tidak
> boleh lebih luas daripada lingkup pengirimnya.* Tanpa itu, agent berlingkup
> sempit bisa meminta agent lain melakukan hal yang ia sendiri tidak boleh —
> **privilege escalation lewat delegasi**, yang §8.27 daftarkan sebagai
> penyalahgunaan tapi belum punya penangkalnya di jalur ini.

> ⚠️ **`payload` berisi `location: "Tokyo"` — data pengguna menyeberang antar
> agent.** Setiap pesan adalah pemindahan data, dan §9.31 sudah menetapkan
> bahwa agent menerima **context package** yang sudah disaring, bukan mengambil
> sendiri. Pesan antar-agent semestinya tunduk pada aturan yang sama:
> **paketnya dibangun Context Engine, bukan disusun agent pengirim.**

---

## §11.21 — Agent Negotiation

```
Travel Agent:      Need hotel under budget.
Budget Agent:      Maximum = $150/night.
Location Agent:    Preferred distance < 2km.
Preference Agent:  User prefers quiet area.
        ↓
Constraint Resolution → Best Candidate
```

> **Bukan agent pertama yang memutuskan sendiri.**

---

> ⭐ **Ini penyelesaian kendala, bukan negosiasi.** Empat agent menyumbang
> **batasan**, dan satu langkah menyelesaikannya — tidak ada tawar-menawar,
> tidak ada agent yang mengalah kepada agent lain. Itu bentuk yang jauh lebih
> mudah diuji dan diaudit daripada negosiasi sungguhan, dan hasilnya bisa
> dijelaskan: *"kandidat ini yang memenuhi keempat batasan"*.
>
> Namanya sebaiknya mengikuti isinya: **Constraint Resolution**, bukan
> *Negotiation*.

> ⚠️ **`Location Agent` dan `Preference Agent` adalah agent keenam dan ketujuh
> yang tidak ada di §11.4.** Tujuh sekarang, bukan lima.

> ⚠️ **Apa yang terjadi kalau tidak ada kandidat yang memenuhi semua batasan?**
> Itu keadaan yang paling sering terjadi di dunia nyata, dan tidak ada
> jawabannya di sini. Tiga pilihan, dan yang mana dipakai harus ditulis:
> melonggarkan batasan yang mana (dan siapa yang boleh memutuskan), mengembalikan
> daftar kosong, atau **bertanya kepada pengguna** — yang terakhir paling
> sejalan dengan §11.16 L3.

---

## §11.22 — Conflict Resolution

```
Health Agent:    Need more sleep.
Learning Agent:  Need study tonight.
Career Agent:    Deadline tomorrow.
```

Orchestrator melakukan: **Priority + Constraints + User Preferences + Risk +
Long-term Goals** → **Decision**

> *"Karena deadline besok dan waktu tidur masih memungkinkan 7 jam, sesi
> belajar dipersingkat menjadi 60 menit."*

---

> ⭐⭐⭐ **Ini contoh terbaik di seluruh naskah, dan ia memperagakan sesuatu
> yang belum pernah ditunjukkan: sistem yang menengahi kepentingan yang
> bertabrakan di dalam satu hidup.**
>
> Tiga agent, tiga kebenaran, dan **tidak satu pun salah**. Yang menyelesaikan
> bukan agent mana yang paling kuat, melainkan **batasan yang bisa dihitung**:
> tidur 7 jam masih muat. Kalimat keluarannya juga menyebutkan alasannya —
> persis bentuk provenance §10.25.
>
> ⚠️ Dan justru karena itu ia memperlihatkan apa yang belum ada: **`Priority`
> dan `Long-term Goals` tidak punya angka.** Personal Utility Model §9.25
> (`0.30 Career Growth + 0.25 Income + …`) adalah tempat angka itu seharusnya
> berada — dan §9.25 menuntut *"user harus dapat mengubahnya"*
> ([#71](../../issues/71)). Jadi keputusan seperti di atas hanya bisa dibenarkan
> kalau bobotnya **terlihat dan bisa disunting** pengguna.
>
> Tanpa itu, kalimat *"sesi belajar dipersingkat menjadi 60 menit"* adalah
> sistem yang memutuskan apa yang lebih penting bagi seseorang tanpa pernah
> menunjukkan atas dasar apa.

> 🛑 **B-12 belum tertutup, dan sekarang bentuknya lebih jelas.** Butir itu
> mencatat: ratusan agent pada satu graf tanpa aturan kepemilikan simpul akan
> saling menimpa; protocol antar-agent naskah 5 mengatur **percakapan**, bukan
> **tulisan ke graf**.
>
> §11.20–§11.22 memberi jauh lebih banyak untuk percakapan — dan tetap nol
> untuk tulisan. §11.53 memberi *namespace* per agent, yang memisahkan **ruang
> kerja** mereka; tapi Knowledge Graph justru sengaja **dibagi bersama** (itu
> gunanya). Kalau Health Agent dan Learning Agent sama-sama menulis simpul
> *"kebiasaan tidur"*, siapa yang menang masih belum ditulis. Lihat
> [#28](../../issues/28).
