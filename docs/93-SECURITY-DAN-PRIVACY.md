# 93 — §25–§26 Security Architecture & Privacy Center

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §25 — Security Architecture

```
Internet
   │
   ▼
  CDN
   │
   ▼
  WAF
   │
   ▼
API Gateway
   │
   ▼
Authentication
   │
   ▼
Authorization
   │
   ▼
Permission Engine
   │
   ▼
Service
   │
   ▼
Data Access Policy
```

Tambahkan:

```
Encryption at rest       Encryption in transit
Secret management        RBAC
ABAC                     Rate limiting
Audit logs               Data retention
Data deletion            Consent management
```

---

## §26 — Privacy Center

> User harus bisa membuka:

```
                    PRIVACY CENTER

What HumanVerse knows

Profile                 ✓
Goals                   ✓
Habits                  ✓
Fashion preferences     ✓
Journal                 ✓
Location                ○
Calendar                ○
Health data             ○
Financial data          ○

[ View ] [ Edit ] [ Delete ] [ Export ]
```

Dan **agent permissions**:

```
FashionAgent

✓ Wardrobe
✓ Fashion Preferences
✓ Weather

○ Calendar
✗ Finance
✗ Private Journal
```

> ⭐ Dua kemajuan: **Data retention** dan **Data deletion** kini tercantum
> sebagai komponen keamanan, dan Privacy Center memperlihatkan **izin per
> agent** — bukan hanya daftar data.
>
> ⚠️ Yang masih belum: apa yang **tetap tersimpan** setelah Delete, mengingat
> §24 Audit Trail dan *Immutable Log* naskah 2. Lihat butir **C-9**.
