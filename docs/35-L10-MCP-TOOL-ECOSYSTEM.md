# 35 — Layer 10: MCP Tool Ecosystem

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Ini yang membuat AI menjadi super power.**
>
> AI tidak hanya berbicara. **AI menggunakan tools.**

---

## Tool Categories

| Tool | Fungsi |
|---|---|
| **Calendar** | Jadwal |
| **Weather** | Cuaca |
| **Maps** | Lokasi |
| **Camera** | Foto |
| **Shopping** | Belanja |
| **Health** | Wearable |
| **Music** | Playlist |
| **Finance** | Budget |
| **Fashion** | Outfit |

---

## Tool Registry

```
tools/
├── calendar/
├── weather/
├── maps/
├── camera/
├── shopping/
├── fashion/
├── health/
├── music/
└── travel/
```

> **Setiap tool memiliki manifest.**

---

> ⚠️ Daftar kategori dan daftar folder **tidak sama**: tabel punya `Finance`
> yang tidak punya folder, dan folder punya `travel/` yang tidak ada di tabel.
> Lihat butir **E-13** di berkas audit.
