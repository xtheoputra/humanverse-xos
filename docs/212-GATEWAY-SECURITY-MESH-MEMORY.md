# 212 — §14.19–§14.22 Federation Gateway, Security Mesh, Memory Federation & Collective Memory

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.19 — Agent Federation Gateway

```
Internet → WAF → API Gateway → Federation Gateway
→ Identity Verification → Capability Verification → Policy → Risk
→ Agent Runtime
```

> Jangan: **External Agent → Internal Services** secara langsung.

---

> ⭐⭐ **Tujuh lapisan, dan `Capability Verification` di antaranya adalah yang
> membuat federasi berbeda dari sekadar API terbuka.** Identity menjawab
> *"siapa kamu"*; capability verification menjawab *"apa yang kamu klaim bisa
> lakukan, dan apakah klaim itu diverifikasi kami"*.
>
> Itu langsung menyentuh keberatan §14.5: `trust_level: certified` yang
> dideklarasikan agent tidak berarti apa-apa — yang berarti adalah
> **verifikasi di gerbang**.

> ⚠️ **`WAF` dan `API Gateway` adalah komponen infrastruktur yang belum pernah
> disebut di delapan belas naskah** — dan keduanya wajar di sini. Tapi ia
> mengingatkan bahwa Phase 14 menuntut infrastruktur produksi (multi-region,
> DR, edge) yang **hilang dari peta 15 fase** bersama *HumanVerse Cloud*
> (**E-86**). Enterprise kembali di §14.17; infrastrukturnya belum.

---

## §14.20 — Agent Security Mesh

```
Agent → Identity → Authentication → Authorization → Capability Check
→ Memory Scope → Data Scope → Policy → Risk → Budget → Tool Gateway
→ Execution
```

---

> ⭐⭐ **Sebelas gerbang — dan `Memory Scope` serta `Data Scope` sebagai dua
> langkah TERPISAH adalah pembedaan yang benar dan baru.**
>
> *Memory scope* membatasi **apa yang boleh diingat agent** (`travel.preferences`,
> bukan `private.journal`). *Data scope* membatasi **data siapa** yang boleh
> disentuh — dan itulah sumbu yang **C-10** ([#40](../../issues/40)) minta sejak
> naskah 7 dan yang §14.18 (multi-tenant) buat mendesak.
>
> Memisahkan keduanya berarti agent bisa punya izin membaca *jenis* data
> tertentu tanpa otomatis boleh membaca *milik siapa pun*. Itu prasyarat untuk
> Enterprise, dan ia akhirnya ada di rantai.

> ⚠️ **Bandingkan dengan sembilan gerbang §11.14 Action Gateway:** yang ini
> menambah `Capability Check`, `Memory Scope`, `Data Scope`, dan `Tool
> Gateway`, tetapi **menghilangkan `Consent`, `Rate Limit`, dan
> `Confirmation`**.
>
> Kehilangan `Confirmation` yang paling perlu diperhatikan — ini rantai
> keamanan **ketiga** yang mengakhiri diri di `Execution` tanpa titik di mana
> manusia bisa menahan (setelah §13.34 yang kehilangan `Rollback`, **E-109** /
> [#91](../../issues/91)). Kemungkinan besar ia diasumsikan hidup di lapisan
> lain — tapi rantai yang digambar lengkap akan dibangun seperti yang digambar.

---

## §14.21 — Agent Memory Federation

> Masalah besar: **bagaimana agent berbagi informasi tanpa membocorkan
> memory?** Jawabannya: **Memory Scope**.

```yaml
travel_agent:
  memory:
    read:
      - travel.preferences
      - calendar.travel
      - budget.travel
    deny:
      - private.journal
      - medical.records
      - unrelated.finance
```

> Agent **tidak mendapatkan seluruh Human Memory**.

---

> ⭐⭐⭐ **`private.journal` disebut dengan NAMANYA — dan itu perbaikan nyata
> setelah dua naskah memakai kata pengganti.**
>
> Butir **G-9** mencatat naskah 12 tidak menyebut jurnal **satu kali pun** di 46
> bagian; naskah 15 menjaganya lewat *"private documents"* (§11.6) dan
> *"private conversations"* (§11.30) — kata pengganti yang **tidak bisa
> ditegakkan validator**.
>
> `deny: private.journal` bisa. Ia cocok dengan aturan 6
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) (agent `third_party` tidak boleh
> meminta scope `journal`, `finance`, `health`), dan dengan naskah 5 §15 yang
> menempatkan *private journal* di daftar DENY bahkan untuk agent internal.
>
> ⭐ Dan `deny` sebagai **daftar eksplisit** — bukan sekadar "yang tidak ada di
> `read` berarti ditolak" — lebih baik untuk federasi: agent eksternal bisa
> membaca larangannya sendiri dan tidak perlu mencoba.

> ⚠️ **`unrelated.finance` mengulang masalah §8.15.** Butir itu mencatat
> *"access unrelated health data"* sebagai satu-satunya larangan **bersyarat**
> di seluruh naskah 12 — siapa yang memutuskan *"unrelated"*, dan berdasarkan
> apa? Jawaban yang tersedia sejak §8.10: **`purpose`**. Kalau itu maksudnya,
> sebaiknya ditulis `finance.*` dengan `purpose` sebagai penyaring, bukan kata
> sifat di nama scope.

---

## §14.22 — Collective Memory

```
Personal Memory → Agent Memory → Team Memory
→ Organization Memory → Public Knowledge
```

> Setiap layer memiliki **boundary**.

---

> ⭐⭐ **Lima tingkat ini melengkapi tiga sumbu memory H-16 dengan sumbu
> KELIMA.** Yang sudah ada: `kind` (6 jenis) · `scope` (izin & pengambilan) ·
> `tier` (5 tingkat kompresi naskah 9) · `modality` (naskah 14 §10.23). Yang
> baru: **`level`** — milik siapa memori itu.
>
> Kelimanya tegak lurus, dan bisa diuji dengan satu baris: sebuah catatan rapat
> tim bisa **episodic** (kind) di scope **project** dengan tier **summary**,
> modality **audio**, level **team**. Lima sumbu, satu memori.

> 🛑 **Tetapi `Organization Memory` dan `Team Memory` adalah tempat pertama di
> delapan belas naskah di mana memori seseorang bisa dibaca orang lain
> secara sah — dan aturan naiknya belum ada.**
>
> Pertanyaan yang harus dijawab sebelum satu baris kode: **apa yang membuat
> sebuah memori naik dari Personal ke Team?** Tiga kemungkinan, dan yang mana
> dipilih menentukan seluruh sifat sistemnya:
>
> | Aturan naik | Konsekuensi |
> |---|---|
> | otomatis, kalau relevan dengan proyek tim | paling berguna, paling berbahaya — catatan pribadi bisa naik tanpa disadari |
> | **eksplisit, orangnya yang menaikkan** | paling aman, dan sejalan dengan `Edit` yang diminta **E-74** |
> | menurut kebijakan organisasi | benar untuk data perusahaan, **salah** untuk data pribadi karyawan (**C-12**) |
>
> Dan arah **turun** juga belum ada: apakah memori tim bisa turun jadi personal
> ketika seseorang keluar dari tim? Butir **C-9** ([#22](../../issues/22))
> berlaku di sini dengan bentuk baru — **hak hapus milik siapa, kalau memorinya
> sudah naik ke tingkat organisasi?**
>
> Ketiganya keputusan pemilik, bukan detail teknis. Lihat **A-30** /
> [#92](../../issues/92), dan **C-10** ([#40](../../issues/40)) yang perlu
> ditambah nilai `organization-owned`.
