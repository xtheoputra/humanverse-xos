# `apps/api` — HumanVerse XOS API (V0)

Satu proses FastAPI, dua belas modul di `src/hvx/modules/`
([`spec/06`](../../spec/06-MODULE-BOUNDARIES.md)). Arsitektur kode yang sudah
ada, dan kenapa bentuknya begitu: [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

```bash
# butuh HVX_ENV, HVX_DATABASE_URL, HVX_REDIS_URL
uv run --locked uvicorn hvx.main:create_app --factory --reload
```

| Variabel | Wajib | Bawaan · catatan |
|---|---|---|
| `HVX_ENV` | ✅ | `local` · `test` · `ci` · `production` — **tanpa bawaan**; dokumentasi interaktif hanya terbuka di tiga yang pertama |
| `HVX_DATABASE_URL` | ✅ | `postgresql://…` — **tanpa parameter kueri**; opsi koneksi lewat `PGSSLMODE`, `PGSSLROOTCERT`, `PGCONNECT_TIMEOUT`, `PGAPPNAME` |
| `HVX_REDIS_URL` | ✅ | `redis://…` |
| `HVX_LOG_LEVEL` | | `INFO` — berlaku juga bagi pencatat uvicorn |
| `HVX_LOG_JSON` | | `true` |
| `HVX_HEALTH_TIMEOUT_S` | | `1.0` — hanya untuk `/health` |
| `HVX_REDIS_SOCKET_TIMEOUT_S` | | `5.0` — klien Redis bersama; konsumen Streams yang memblokir wajib punya klien sendiri |
| `HVX_REDIS_CONNECT_TIMEOUT_S` | | `2.0` |

Rute yang ada: `GET /health` → `200 {status, version, db, redis}`, atau `503`
dengan bentuk yang sama kalau satu ketergantungan mati. Galat yang tak
tertangani dijawab `500 {"error": {"code": "internal_error", "message": …}}`
dengan `X-Request-ID`.
