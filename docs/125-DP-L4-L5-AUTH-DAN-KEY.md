# 125 — DP-L4–L5: Authentication Platform & API Key Management

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L4 — Authentication Platform

> Gunakan **standar industri**.

```
OAuth 2.1 · PKCE · Refresh Token · Scoped Access
```

Contoh scope:

```
profile.read     habit.read      wardrobe.read
profile.write    habit.write     journal.read
                                 agent.execute
```

> **Developer hanya mendapat izin yang diberikan user.**

> ⭐ **OAuth 2.1 dengan PKCE** adalah pilihan yang benar dan tidak sepele —
> PKCE menutup celah yang paling sering dipakai untuk membajak izin di aplikasi
> ponsel, tempat sebagian besar pengguna produk ini akan berada.

---

> 🛑 **`journal.read` ada di daftar scope untuk developer pihak ketiga.**
>
> Ini bertabrakan langsung dengan dua hal yang sudah ditulis:
>
> | Sumber | Isi |
> |---|---|
> | Naskah 5 §15 | *private journal* ada di daftar **DENY** — bahkan untuk agent internal seperti FashionAgent |
> | [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) aturan 6 | agent `kind: third_party` **tidak boleh** meminta scope `journal`, `finance`, atau `health` |
>
> Jurnal adalah tulisan paling pribadi di seluruh produk, dan satu-satunya
> tempat yang naskah 4 §C-3 tandai sebagai kemungkinan memuat isyarat krisis.
> Membukanya ke developer pihak ketiga adalah keputusan yang berbeda kelas dari
> membuka `habit.read`.
>
> Kalau memang disengaja, ia butuh: persetujuan terpisah (bukan satu layar izin
> bersama scope lain), masa berlaku, pencatatan tiap akses, dan larangan
> menyimpan salinan di server developer. Lihat butir **E-61** dan **C-14**.

---

## DP-L5 — API Key Management

Setiap aplikasi memiliki:

```
Development Key · Staging Key · Production Key
```

Key dapat: **rotate · revoke · expire**.

```
hv_dev_xxx
hv_prod_xxx
```

> ⭐ Awalan `hv_dev_` / `hv_prod_` yang berbeda bentuk membuat kunci produksi
> **bisa dikenali otomatis** — itu yang memungkinkan pemindai rahasia
> menangkapnya sebelum ter-commit. Detail kecil yang sering terlewat.
>
> ⚠️ Belum ada **masa berlaku default**. Kunci yang tidak pernah kedaluwarsa
> adalah kunci yang bocor perlahan; `expire` sudah didukung, tinggal
> ditetapkan defaultnya.
