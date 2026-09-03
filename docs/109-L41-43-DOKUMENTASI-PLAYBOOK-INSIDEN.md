# 109 — Layer 41–43: Documentation OS, Playbooks & AI Incident Response

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 41 — Documentation Operating System

> **Dokumentasi harus menjadi bagian dari produk.**

```
docs/
  architecture/
  api/
  agents/
  prompts/
  security/
  design/
  decisions/
  playbooks/
```

> Target: **AI Agent dapat membaca dokumentasi sebelum coding.**

> ℹ️ Ini memperluas `docs/` naskah 5 §4 (`architecture api agents domain
> security decisions`) dengan **`prompts/`**, **`design/`**, dan
> **`playbooks/`**, sekaligus **membuang `domain/`**.

---

## Layer 42 — Playbooks

> Setiap situasi memiliki playbook.

```
Bug Playbook          AI Failure Playbook
Incident Playbook     Security Playbook
Deployment Playbook   Rollback Playbook
```

> Ini membuat operasi **lebih stabil**.

---

## Layer 43 — AI Incident Response

> Kalau AI salah rekomendasi:

```
Detection
    ↓
Logging
    ↓
Classification
    ↓
Containment
    ↓
Fix
    ↓
Evaluation
    ↓
Postmortem
```

> Sama seperti **incident engineering**.

---

> ⭐ **Layer 43 adalah lapisan yang paling jarang dipikirkan orang, dan justru
> paling dibutuhkan produk ini.** *"AI salah rekomendasi"* pada aplikasi tidur,
> uang, dan tubuh bukan bug biasa.
>
> `agent_runs` di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) sudah menyimpan
> bahan untuk **Detection** dan **Logging**: agent mana, tool apa, memory scope
> mana, keputusan apa, dan berapa `confidence`-nya.
>
> ⚠️ Yang belum ada dan tidak bisa ditebak: **siapa yang menerima
> pemberitahuan** ketika insiden terjadi, dan **dalam waktu berapa lama**.
> Selama pengguna hanya pemiliknya sendiri, jawabannya sepele; begitu ada orang
> lain, itu janji yang mengikat. Bertaut ke **C-3** (eskalasi krisis Journal).
