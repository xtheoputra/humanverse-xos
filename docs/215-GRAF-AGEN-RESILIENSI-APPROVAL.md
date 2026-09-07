# 215 — §14.33–§14.36 Agent Relationship Graph, Dependency, Resilience & Human Approval

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.33 — Agent Relationship Graph

**Node:** Agent · Developer · Organization · Capability · Tool · Memory ·
Resource · Policy · User

**Edge:** `OWNS` · `CREATED_BY` · `USES` · `TRUSTS` · `CAN_ACCESS` ·
`CAN_CALL` · `DEPENDS_ON` · `COLLABORATES_WITH`

> Sehingga bisa query: *"Agent mana yang dapat mengakses data X?"*

---

> ⭐⭐⭐ **Pertanyaan itu adalah alasan seluruh graf ini ada, dan ia belum pernah
> bisa dijawab di delapan belas naskah.**
>
> Izin selama ini disimpan sebagai baris `permissions(user, subject, scope,
> action)` — bagus untuk memeriksa *"boleh tidak agent ini"*, tidak bisa untuk
> *"siapa saja yang bisa"*. Yang kedua adalah pertanyaan yang ditanyakan
> auditor, regulator, dan pengguna yang khawatir — dan ia menuntut arah
> pencarian yang berlawanan.
>
> Graf menjawab keduanya, dan `CAN_CALL` + `DEPENDS_ON` membuatnya **transitif**
> — yang persis dibutuhkan §14.32 untuk mendeteksi jalur eskalasi.

> ⭐ **Delapan relasi ini adalah set relasi paling aman yang pernah masuk graf
> HumanVerse.** Semuanya **struktural dan terukur** — tidak satu pun kausal.
> Bandingkan **E-81** ([#7](../../issues/7)), di mana `influences` kembali ke
> Human Knowledge Graph tanpa bukti kausal. Graf agent tidak punya masalah itu:
> `A CAN_CALL B` benar atau salah, tidak perlu dibuktikan lewat rantai §12.5.

> ⚠️ **Ini graf KEDUA di samping Human Knowledge Graph** — node dan relasinya
> tidak beririsan, dan itu benar (satu tentang hidup pengguna, satu tentang
> sistemnya). Yang perlu ditulis: keduanya **tidak boleh dicampur di satu
> penyimpanan**, karena hak hapus (**C-9**) berlaku pada yang pertama dan tidak
> pada yang kedua.

---

## §14.34–§14.35 — Dependency Graph & Resilience

```
Travel Agent
├── Weather · Hotel · Flight · Currency · Calendar Agent
```

Jika Weather Agent mati: `Dependency Failure → Fallback Agent`

Setiap agent penting punya: **Primary · Fallback · Secondary · Offline Mode ·
Graceful Degradation**

```
Weather Agent → Primary API → Fallback API → Cached Forecast
→ "No current data"
```

> ## Tidak boleh mengarang data.

---

> ⭐⭐⭐ **Empat kata itu adalah aturan terpenting di seluruh bagian ini, dan ia
> menutup bentuk paling berbahaya dari B-14.**
>
> Butir **B-14** ([#26](../../issues/26)) mencatat bahwa Context Engine gagal
> **senyap**: sinyal mati, rekomendasi tetap keluar, hanya jadi salah. Untuk
> model bahasa, kegagalan senyap punya bentuk khusus dan lebih buruk — ia
> **mengisi kekosongan dengan sesuatu yang masuk akal**.
>
> Rantai empat tingkat di atas berakhir pada **kalimat**, bukan pada tebakan:
> *"No current data"*. Degradasi yang benar berakhir di **diam**, bukan di
> karangan. Itu prinsip yang berlaku jauh melampaui cuaca — dan sebaiknya
> ditulis sebagai aturan sistem, bukan sebagai contoh satu agent.
>
> Ia juga melengkapi §12.15 `Main uncertainty` dan §9.32 `sources`: kalau sumber
> kosong, yang keluar adalah **ketiadaan yang dinyatakan**, bukan nilai
> bawaan.

> ⚠️ **`Cached Forecast` adalah tingkat yang paling mudah salah dipakai.**
> Ramalan cuaca kemarin yang disajikan tanpa penanda waktu adalah karangan
> dalam bentuk lain. Tiap keluaran dari cache wajib membawa **umurnya**, dan
> §12.1 sudah punya fieldnya (`timestamp`, dan `volatility` untuk menilai
> apakah umur itu masih layak).

---

## §14.36 — Agent Negotiation + Human Approval

```
Agents → Recommendation → Consensus → Risk Engine → Human Approval → Action
```

> Human tetap berada di **atas** governance hierarchy:
>
> ```
> Human ↑ Governance ↑ Agent Ecosystem
> ```
>
> Bukan: `Agent ↓ Human`

---

> ⭐⭐⭐ **Dua diagram tiga baris itu menyatakan sesuatu yang selama ini hanya
> tersirat: arah kewenangan.**
>
> Enam kalimat penutup berturut-turut sudah menjaga arah yang sama — naskah 4
> (*"jangan menilai baik atau buruk"*), §8.46, §9.41, §11.63, §12 (*Observed ≠
> Certain*), §13.40 — tetapi semuanya **kalimat**. Ini yang pertama
> menggambarnya sebagai **hierarki**, dan menegaskan apa yang **bukan**.
>
> Perbedaannya penting justru di fase ini: dengan puluhan agent yang
> bernegosiasi, mencapai konsensus, dan membentuk team sendiri, godaan
> terbesarnya adalah memperlakukan manusia sebagai **salah satu peserta** —
> suara terakhir di antara banyak suara. Diagram ini menolak itu: manusia bukan
> peserta, ia **atap**.

> ⚠️ **Tapi rantainya menaruh `Human Approval` SETELAH `Consensus`** — artinya
> manusia menyetujui **satu hasil** yang sudah disepakati agent-agent.
> Sementara §14.12 justru menunjukkan bahwa yang paling berguna bagi orang yang
> memutuskan adalah **melihat ketidaksepakatannya** (`Disagreement: Finance
> Agent vs Career Agent`).
>
> Kalau konsensus meratakan perselisihan sebelum sampai ke manusia, informasi
> paling berharga hilang tepat sebelum orang yang membutuhkannya. Yang benar:
> **konsensus menghasilkan rekomendasi, dan perselisihannya ikut naik** — dan
> §14.60 (Human Approval Center V2) memang menampilkan `Consensus: 4/4`, yang
> berarti ia bisa menampilkan `3/4` juga.
