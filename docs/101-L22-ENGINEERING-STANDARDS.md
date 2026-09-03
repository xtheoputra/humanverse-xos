# 101 — Layer 22: Engineering Standards

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> Kalau proyek ini dikerjakan oleh **AI Agent**, coding standard menjadi
> **wajib**.

---

## Repository Rules

> **Setiap folder memiliki kontrak.**

```
/apps
/services
/intelligence
/agents
/platform
/packages
/docs
/tests
```

Setiap folder memiliki:

```
README.md
AGENTS.md
OWNERS.md
CONTRACT.md
```

> **AI Agent harus membaca berkas tersebut sebelum mengubah kode.**

---

## Naming Convention

| Item | Format |
|---|---|
| **Service** | `fashion-service` |
| **Agent** | `FashionAgent` |
| **Event** | `fashion.outfit.selected` |
| **API** | `/v1/fashion/outfits` |
| **Table** | `wardrobe_items` |
| **Enum** | `OutfitStyle` |

> Ini terlihat sederhana, tetapi pada proyek besar **konsistensi menghemat
> banyak waktu**.

---

> ⚠️ **Dua format di tabel ini bertabrakan dengan naskah kelima:**
>
> - **Event tiga segmen** (`fashion.outfit.selected`) vs **dua segmen** di
>   naskah 5 §7 (`workout.completed`, `habit.completed`) — dan 21 event di sana
>   semuanya dua segmen.
> - **API `/v1/fashion/outfits`** (berawalan domain) vs endpoint V0 yang sudah
>   ditulis di [`../spec/04`](../spec/04-API-CONTRACTS.md).
>
> Keduanya harus dipilih **sebelum** Sprint 3, karena nama event tidak boleh
> diganti setelah dipakai. Lihat butir **E-43**.
>
> ⚠️ **Empat berkas kontrak × 8 folder = 32 berkas** yang harus ditulis dan
> dijaga tetap benar. Naskah 5 §4 hanya meminta empat berkas di akar repo.
> Lihat butir **E-44**.
