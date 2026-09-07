# 209 — §14.7–§14.10 Agent Protocol, Contract, Discovery & Trust

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.7 — Agent-to-Agent Protocol

```
Agent A → Request → Agent B → Proposal → Agent A → Evaluation → Agreement
```

```json
{
  "message_id": "msg_123",
  "sender":   "travel-agent",
  "receiver": "weather-agent",
  "intent":   "request_weather_forecast",
  "payload":  {},
  "constraints": {},
  "deadline": "...",
  "risk_level": "R0"
}
```

---

> ⭐⭐ **`risk_level` dan `deadline` di dalam amplop pesan adalah dua field yang
> tidak ada di §11.20** — dan keduanya menutup lubang nyata.
>
> `risk_level` per pesan berarti gerbang bisa memutuskan **tanpa membuka
> payload**: permintaan R0 lewat cepat, R3 berhenti. Itu yang membuat federasi
> bisa diperiksa di batas, bukan di dalam.
>
> `deadline` menutup masalah yang §11.25 tinggalkan: agent yang menunggu
> jawaban agent lain **selamanya**. Dengan tenggat, kegagalan menjadi
> peristiwa yang bisa ditangani (§14.63) alih-alih menggantung.

> ⚠️ **`authorization.scope` §11.20 HILANG dari amplop ini.** Naskah 15
> memberi tiap pesan lingkupnya sendiri (`scope: travel_planning`), dan saya
> catat itu sebagai *"yang mencegah agent yang didelegasikan mewarisi lebih
> dari lingkup pesannya"*.
>
> ⭐ Tapi naskah ini menggantinya dengan sesuatu yang **lebih kuat**: §14.42
> (*delegation cannot exceed the authority of the delegator*) dan §14.43
> (*capability attenuation*) menetapkannya sebagai **aturan sistem**, bukan
> field yang bisa diisi salah. Lihat berkas
> [`217`](217-DELEGASI-GOVERNANCE-COLLECTIVE-RUNTIME.md).

---

## §14.8 — Agent Contract

```yaml
agent: { id: travel.planner, version: 1.0 }
purpose:      [ travel planning ]
capabilities: [ search_transport, search_hotel, build_itinerary ]
inputs:       [ destination, dates, preferences ]
outputs:      [ itinerary, estimated_cost ]
constraints:  [ cannot_purchase, cannot_transfer_money ]
risk:         { level: R2 }
```

> Agent lain dapat mengetahui *"apa yang bisa dilakukan agent ini?"* **tanpa
> harus mengetahui implementasi internalnya**.

---

> ⭐⭐⭐ **`inputs`/`outputs` dan `constraints` yang menyatakan LARANGAN adalah
> dua hal yang belum pernah ada di tujuh versi manifest sebelumnya.**
>
> Enam manifest sebelumnya menyatakan **apa yang boleh** (`capabilities`,
> `tools`, `memory.read`). Ini yang pertama menyatakan **apa yang tidak akan
> pernah dilakukan** (`cannot_purchase`, `cannot_transfer_money`) — dan itu
> perbedaan besar untuk federasi: agent lain bisa memeriksa larangan sebuah
> agent **sebelum** mendelegasikan kepadanya.
>
> `inputs`/`outputs` melengkapinya dengan kontrak bentuk data — yang membuat
> *Agent Discovery* §14.9 bisa mencocokkan agent tanpa mencoba memanggilnya.

> ⚠️ **Ini kontrak KEDUA di samping manifest §14.55**, dan keduanya memuat
> `purpose`, `capabilities`, dan `risk`. Bedanya: kontrak ini **menghadap
> keluar** (dibaca agent lain), manifest menghadap ke dalam (dibaca registry).
> Pembedaan itu masuk akal dan sebaiknya ditulis — kalau tidak, dua berkas
> untuk satu agent akan berbeda cepat atau lambat.

---

## §14.9 — Agent Discovery

> Jika terdapat ribuan agent, orchestrator membutuhkan **Agent Discovery
> Service**.

```
Find agents capable of: "optimize my trip under $500"
        ↓
Travel Planner · Budget · Transportation · Hotel · Currency · Weather
        ↓
memilih kombinasi terbaik
```

---

> ⭐ **`inputs`/`outputs` §14.8 adalah yang membuat ini mungkin tanpa
> memanggil.** Discovery yang harus mencoba tiap agent untuk tahu ia bisa apa
> adalah discovery yang mahal dan berisiko.

> ⚠️ **"Memilih kombinasi terbaik" adalah masalah optimasi yang belum punya
> fungsi tujuan.** §14.39 memberi kriterianya (Quality · Cost · Latency · Trust
> · Security · Specialization) — enam sumbu tanpa bobot, dan bobotnya adalah
> **Personal Utility Model** §12.21 yang sendirinya masih punya tiga daftar
> berbeda (**E-104**). Discovery yang memilih atas bobot yang belum ditetapkan
> akan memilih menurut bobot bawaan yang tak pernah dinyatakan siapa pun.

---

## §14.10 — Agent Trust & Reputation

Trust Score dari: **Reliability · Safety · Security · Accuracy · Latency ·
Cost · User Satisfaction · Incident History · Evaluation Results · Developer
Reputation**

> Namun: ## Trust score bukan security boundary.
>
> Agent dengan rating tinggi **tetap tidak boleh melewati permission system**.

---

> ⭐⭐⭐ **Kalimat itu diulang untuk ketiga kalinya — §11.33, §14.10, dan
> semangat yang sama di §8.28 setelah saya keluhkan.** Tiga naskah menegaskan
> hal yang sama: skor adalah **informasi untuk memilih**, bukan **gerbang**.
>
> Itu peran yang benar untuk angka yang tidak punya rumus — dan sepuluh
> komponen di atas memang belum punya satu pun. Bandingkan dengan **B-15**
> (angka pengguna tanpa rumus): di sini ketiadaan rumus **tidak berbahaya**,
> justru karena skornya tidak menjaga apa pun.

> ⚠️ **Sepuluh komponen, dan tiga di antaranya bertabrakan arah.** `Cost` dan
> `Latency` — makin rendah makin baik; delapan lainnya makin tinggi makin baik.
> Menjumlahkannya tanpa penanda arah menghasilkan skor terbalik untuk agent
> murah dan cepat. Masalah yang sama dengan `Risk: 4/10` §9.24, `Risk = 18`
> §12.12, dan `w6 Risk` §12.21 (**E-104**): **setiap dimensi butuh
> `higher_is_better`**. Ini kali keempat.
