# 168 — §10.12–§10.15 Document Intelligence, Embeddings, Cross-Modal Retrieval & Multimodal RAG

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.12 — Document Intelligence

> HumanVerse juga harus bisa membaca: **PDF · DOCX · PPTX · Spreadsheet ·
> Receipt · Invoice · Ticket · Schedule · Contract · Screenshot · Web page ·
> Forms**

```
Document → File Type Detection → OCR → Layout Analysis → Table Detection
→ Entity Extraction → Semantic Parsing → Document Embedding
→ Knowledge Extraction → Memory / Knowledge Graph
```

Contoh receipt:

```
Receipt → OCR → Merchant → Date → Items → Price → Category
→ Transaction Event
```

Bisa menghasilkan: `PurchaseEvent`

---

> ⭐ **`purchase.created` sudah ada di 21 event naskah 5 §7 dan di
> [`../spec/03`](../spec/03-EVENT-CONTRACTS.md)** — jadi jalur struk ke event
> domain sudah punya tujuan. Ini pertama kalinya sebuah naskah menunjukkan
> **dari mana** event pembelian itu datang tanpa integrasi bank.
>
> ⚠️ Tapi namanya di sini **`PurchaseEvent`**, bukan `purchase.created`.
> Lihat **E-88**.

> 🛑 **Struk, faktur, tiket, dan kontrak memuat data orang lain.** Kontrak
> punya dua pihak; tiket punya nama penumpang lain; struk restoran menunjukkan
> berapa orang makan. `Entity Extraction` akan mengeluarkan nama-nama itu, dan
> `Knowledge Extraction` akan memasukkannya ke Knowledge Graph.
>
> Ini permukaan ketiga di naskah yang sama menuju masalah yang sama:
> kamera (§10.6), mikrofon (§10.8), dan sekarang dokumen. Model izin tetap
> hanya mengenal `scope: user-owned`. Lihat **C-17**/**C-18**.

> ⚠️ **`Screenshot` adalah butir yang paling luas di daftar itu** — tangkapan
> layar bisa memuat apa saja: percakapan orang lain, saldo rekening, data
> kesehatan, layar kerja milik pemberi kerja. Ia tidak punya bentuk yang bisa
> diklasifikasikan lebih dulu, jadi ia satu-satunya jenis dokumen yang
> **klasifikasi privasinya baru diketahui setelah dibaca** — dan §10.2
> menempatkan `Privacy Check` **sebelum** pemrosesan.

---

## §10.13 — Multimodal Embedding System

```
Text · Image · Audio · Video · Document · Sensor Embedding
        ↓
Multimodal Representation
```

Tujuannya: `"black sneakers"` bisa dicocokkan dengan **image of black
sneakers**, **user's wardrobe item**, **product**, atau **fashion trend**.

---

## §10.14 — Cross-Modal Retrieval

User: *"Cari sepatu yang mirip ini."*

```
Image → Visual Embedding → Vector Search → Wardrobe · Products · Trends
```

Sebaliknya — *"Tampilkan outfit yang cocok dengan sepatu ini."*

```
Image → Visual Understanding → Wardrobe Graph → Preference Model
→ Recommendation
```

---

> ⭐⭐ **Ini fitur yang paling terasa berbeda bagi pengguna, dan biayanya paling
> rendah dibanding sisa fase ini** — ia tidak menuntut kamera menyala, tidak
> menuntut pemantauan, dan tidak menyentuh orang lain. Satu foto yang dikirim
> pengguna, satu jawaban. Kalau ada satu bagian Phase 10 yang layak dibangun
> lebih dulu, ini kandidat terkuatnya.

> ⚠️ **Qdrant ada sejak V0, tetapi untuk teks.** [`../spec/01`](../spec/01-DATABASE-SCHEMA.md)
> menyimpan `memories.embedding_id`; embedding visual adalah koleksi baru
> dengan dimensi berbeda dan model berbeda. §10.36 menambahkannya sebagai
> `visual_embeddings`. Yang perlu ditetapkan: **koleksi terpisah**, karena
> pencarian lintas-modal tetap membutuhkan ruang yang sama — dan itu berarti
> model *joint embedding*, bukan dua model yang hasilnya ditempel.
>
> Perbedaan itu menentukan: `"black sneakers"` hanya bisa menemukan foto
> sepatu hitam kalau teks dan gambar berada di **satu ruang vektor**.

---

## §10.15 — Multimodal RAG

```
User Query → Query Understanding → Modality Detection → Hybrid Retrieval
     │
     ├── Text  ├── Image  ├── Memory
     ├── Vector ├── Graph  └── Metadata
     ↓
Reranking → Context Assembly → LLM / Reasoning
```

Contoh — user mengirim gambar + *"Apakah outfit ini cocok untuk meeting
besok?"*

System menggunakan: **Image + Calendar + Weather + User Style + Meeting Type +
Past Preferences + Fashion Knowledge**

> Ini baru benar-benar **multimodal personal intelligence**.

---

> ⭐⭐ **`Context Assembly` adalah §9.31 dengan nama lain — dan itu kabar
> baik.** *Context package* naskah 13 (`filtered · scoped · ranked ·
> sanitized`) dan `Reranking → Context Assembly` di sini mengerjakan hal yang
> sama: menyusun satu paket sebelum LLM dipanggil. Keduanya sebaiknya **satu
> komponen**, bukan dua — kalau tidak, izin akan diperiksa di satu jalur dan
> tidak di jalur lain, yang persis membatalkan alasan **H-19** ditutup.

> ⭐ **Tujuh sumber di contoh itu semuanya sudah punya tempat**: Image
> (§10.3), Calendar & Weather (tool, **H-11**), User Style & Past Preferences
> (Preference Model, §9.4), Meeting Type (kalender), Fashion Knowledge
> (*General Knowledge*, §9.10). Tidak ada yang perlu diciptakan — hanya
> dirangkai. Itu tanda arsitektur yang mulai menyatu.

> ⚠️ **Tapi Calendar dan Weather adalah tool V2**, bukan V0
> ([`../spec/05`](../spec/05-AGENT-CONTRACTS.md)), dan Fashion baru masuk V2
> juga. Contoh ini menggambarkan V2+, dan sebaiknya dibaca begitu.

> ⚠️ **`Modality Detection` pada query, bukan hanya pada masukan.** Pertanyaan
> *"apakah outfit ini cocok"* yang datang bersama gambar harus memicu jalur
> yang berbeda dari pertanyaan yang sama tanpa gambar. Itu pekerjaan
> `Intent Classifier` §9.21 — dan seperti dicatat di sana, **salah memilih
> jalur berarti melewati pemeriksaan**, jadi ia komponen keselamatan.
