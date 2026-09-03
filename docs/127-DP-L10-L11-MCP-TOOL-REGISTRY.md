# 127 — DP-L10–L11: MCP Compatibility & Tool Registry

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L10 — MCP Compatibility

> Karena kamu ingin memakai **AI Agent modern**, HumanVerse mendukung:

```
MCP-compatible tools · Tool Registry · Capability Discovery
```

Contoh: `weather` · `calendar` · `wardrobe` · `trend`

> **Agent dapat menemukan tool secara otomatis.**

---

## DP-L11 — Tool Registry

| Tool | Capability |
|---|---|
| Weather | forecast |
| Calendar | events |
| Wardrobe | clothing |
| Trend | fashion |

```json
{
  "tool": "weather",
  "version": "2.0",
  "permissions": [ "weather.read" ]
}
```

---

> ⭐ **`weather` dan `calendar` muncul lagi sebagai TOOL, bukan agent** —
> menguatkan butir **H-11** yang ditutup di naskah 5. Tiga naskah sekarang
> sepakat.
>
> ⚠️ **`Capability Discovery` membalik arah aturan yang sudah ditulis.**
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) aturan 1 menolak manifest yang
> menyebut tool di luar registry — artinya tool ditetapkan **sebelum** agent
> dijalankan. *Capability Discovery* berarti agent menemukan tool **saat
> berjalan**.
>
> Keduanya bisa hidup bersama, tapi aturannya harus ditulis: agent boleh
> **menemukan** tool baru, tetapi **tidak boleh memakainya** sebelum manifest
> versi barunya divalidasi dan izin penggunanya diminta. Tanpa itu, sebuah
> agent bisa memperoleh kemampuan baru setelah pengguna menyetujuinya.
>
> ⚠️ Metadata tool di sini (`tool`, `version`, `permissions`) **lebih miskin**
> daripada yang sudah ditulis di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> (`kind`, `risk_level`, `input`, `output`, `side_effects`, `rate_limit`).
> `side_effects` khususnya penting untuk tool pihak ketiga: ia membedakan tool
> yang hanya membaca dari tool yang mengubah dunia luar.
