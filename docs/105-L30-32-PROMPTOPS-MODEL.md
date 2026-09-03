# 105 — Layer 30–32: PromptOps, Model Lifecycle & Cost Optimization

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 30 — Prompt Engineering Framework

> Prompt **jangan disimpan sembarangan**.

```
prompts/
  system/
  planner/
  fashion/
  health/
  career/
  evaluation/
  safety/
```

Setiap prompt memiliki metadata:

```yaml
name:
version:
owner:
model:
temperature:
tools:
memory_scope:
evaluation:
```

> Ini disebut **PromptOps**.

> ⚠️ **Daftar folder berubah lagi.** Naskah 3 punya 7 folder: planner, fashion,
> health, **finance**, career, **social**, evaluation. Naskah 7 punya 7 juga
> tetapi **membuang finance & social** dan **menambah system & safety**.
> Sementara itu daftar agent sudah 22 (naskah 5 §12). Tujuh folder untuk 22
> agent. Lihat butir **E-23** dan **E-46**.
>
> ⭐ Metadata prompt di sini **lebih lengkap** daripada manifest agent
> naskah 5 §14 — ada `temperature` dan `owner`, yang belum pernah muncul.

---

## Layer 31 — Model Lifecycle Management

> Model AI memiliki **siklus hidup**.

```
Experiment
    ↓
Evaluation
    ↓
Approval
    ↓
Deployment
    ↓
Monitoring
    ↓
Improvement
```

> **Jangan langsung mengganti model production.**

> ⭐ Langkah **Approval** adalah yang baru — naskah 5 §23 langsung dari
> *Evaluation → Score → Production* dengan rollback otomatis. Menyisipkan
> persetujuan manusia sejalan dengan *"governance tetap manusia"* (§27).

---

## Layer 32 — AI Cost Optimization

> Semakin banyak agent, **biaya meningkat**.

| Task | Model |
|---|---|
| Mood logging | **Small** |
| Habit suggestion | **Medium** |
| Deep planning | **Large** |

> Ini bisa **menghemat biaya signifikan**.

> ℹ️ Ini pernyataan **ketiga** untuk hal yang sama: naskah 4 §48–§49 (AI Cost
> Engine + Model Router) dan naskah 5 §22 (Model Router). Isinya konsisten,
> jadi bukan tabrakan — hanya pengulangan.
>
> ⚠️ Naskah 5 §22 lebih tegas dan lebih hemat: *"Catat mood saya"* di sana
> dirutekan ke **`deterministic`**, bukan model kecil. Mencatat mood adalah
> `INSERT`, bukan inferensi. Versi naskah 5 yang sebaiknya dipakai.
