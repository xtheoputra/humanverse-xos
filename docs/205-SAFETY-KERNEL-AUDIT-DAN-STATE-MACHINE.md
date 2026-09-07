# 205 — Safety Kernel, Audit & State Machine (naskah ketujuhbelas)

> Merekam **§13.34–§13.36**.

---

## §13.34 — HumanOS Safety Kernel

> Ini tidak boleh menjadi agent biasa.

```
                    ACTION
                       ↓
                 SAFETY KERNEL
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
    Security         Policy          Risk
       │               │               │
       └───────────────┼───────────────┘
                       ↓
                  Permission
                       ↓
                  Confirmation
                       ↓
                    EXECUTE
```

Safety Kernel memiliki kekuasaan untuk:

```
DENY · BLOCK · PAUSE · REQUIRE_CONFIRMATION · REVOKE · KILL
```

> ⭐⭐⭐ **"Ini tidak boleh menjadi agent biasa" adalah kalimat arsitektur yang
> paling penting di naskah ini.** Sebuah pengaman yang berjalan sebagai agent
> tunduk pada penjadwalan, kegagalan, dan kompromi yang sama dengan yang ia
> jaga. Menetapkannya sebagai kernel — bukan peserta — adalah pemisahan yang
> benar.

> ⭐⭐ **`DENY` ada di daftar kekuasaan, dan ia sejalan dengan §11.15 yang
> menjadikan R4 = `DENY`.** Mekanismenya karena itu **ada**; yang menyimpang
> justru layar izin §13.10 yang menawarkan *"Ask Every Time"* untuk hal-hal
> yang §11.15 tolak mentah. Kernel ini sudah mampu menolak — layar izinnya yang
> tidak menyediakan pilihan itu.

> ⚠️ **Urutan di sini BERBEDA lagi dari §13.10.** Di sini:
> `Security/Policy/Risk → Permission → Confirmation → EXECUTE` (risiko dinilai
> **bersama** kebijakan, sebelum izin). Di §13.10:
> `Capability → Permission → Policy → Risk → Action` (risiko **paling akhir**).
> Naskah yang sama memberi dua urutan gerbang. Yang di sini lebih benar; §13.10
> sebaiknya diselaraskan dengannya, bukan sebaliknya.

> ⚠️ **`KILL` tanpa objek.** Membunuh apa — satu tindakan, satu agent, satu
> workflow, atau seluruh runtime? Ini satu-satunya kekuasaan yang tidak bisa
> ditebak dari namanya, dan ia yang paling berat.

---

## §13.35 — HumanOS Audit

Setiap tindakan disimpan di audit trail:

```
Who · What · Why · Which agent · Which tool · Which data
Which permission · Risk · Decision · Outcome
```

> ⭐⭐⭐ **`Why` dan `Which data` ada di jejak audit.** `Why` adalah `purpose`
> dengan nama lain — jadi naskah ini **menuntut** purpose dicatat saat
> bertindak, sementara [§13.26](203-APPLICATION-API-SDK-MANIFEST-MARKETPLACE.md)
> **tidak menyediakan tempat** untuk mendeklarasikannya di manifest app.
>
> Dua bagian dari naskah yang sama saling membantah: yang satu mewajibkan alasan
> dicatat, yang lain menghapus medan tempat alasan itu dinyatakan. Kalau
> manifest app tidak punya `purpose`, `Why` di audit trail harus datang dari
> suatu tempat — dan satu-satunya kandidat adalah tebakan sistem.
>
> Ini memperkuat temuan §13.26: yang hilang bukan medan administratif, melainkan
> **satu-satunya sumber jujur** untuk kolom `Why`.

> ⭐ **`Outcome` ikut dicatat, bukan hanya `Decision`.** Tanpa hasil, audit
> trail hanya membuktikan sistem mengizinkan sesuatu — bukan apa yang terjadi
> sesudahnya.

---

## §13.36 — HumanOS State Machine

```
IDLE
 ↓
OBSERVING
 ↓
UNDERSTANDING
 ↓
CONTEXT_LOADING
 ↓
REASONING
 ↓
SIMULATING
 ↓
PLANNING
 ↓
POLICY_CHECK
 ↓
WAITING_PERMISSION
 ↓
WAITING_CONFIRMATION
 ↓
EXECUTING
 ↓
VERIFYING
 ↓
COMPLETED
 ↓
LEARNING
 ↓
IDLE
```

Failure:

```
FAILED
 ↓
RECOVERING
 ↓
REPLAN
 ↓
WAITING_CONFIRMATION
```

> ⭐⭐⭐ **Ini bentuk terkuat pengaman di seluruh naskah ketujuh belas.** Tiga
> gerbang — `POLICY_CHECK`, `WAITING_PERMISSION`, `WAITING_CONFIRMATION` —
> berdiri sebagai **state**, bukan sebagai pemeriksaan di dalam kode. Sebuah
> state machine tidak bisa "lupa" melewati state; melewatinya berarti transisi
> yang tidak ada. Itu penegakan lewat bentuk, bukan lewat disiplin penulis.
>
> Dan jalur kegagalan berakhir di **`WAITING_CONFIRMATION`**, bukan `EXECUTING`
> — artinya rencana yang disusun ulang sesudah gagal **tidak** berjalan sendiri.
> Itu justru titik ketika sistem paling mungkin salah, dan naskah ini menaruh
> manusia di sana.

> ⚠️ **`LEARNING` berada di jalur sukses saja.** Kegagalan
> (`FAILED → RECOVERING → REPLAN`) tidak pernah melewati `LEARNING`. Kegagalan
> adalah sinyal paling informatif yang dimiliki sistem; membuangnya berarti
> sistem hanya belajar dari apa yang sudah berhasil.

> ⚠️ **Tidak ada state untuk `DENY`.** §13.34 memberi Safety Kernel kekuasaan
> `DENY`, `BLOCK`, `REVOKE`, `KILL` — tak satu pun punya state di mesin ini.
> Kalau R4 ditolak, ke state mana sistem pergi? `FAILED` tidak tepat: penolakan
> bukan kegagalan, dan ia **tidak boleh** masuk `RECOVERING → REPLAN`, karena
> itu berarti sistem mencoba lagi apa yang baru saja ditolak.
