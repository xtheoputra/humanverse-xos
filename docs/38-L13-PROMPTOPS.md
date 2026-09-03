# 38 — Layer 13: PromptOps

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Prompt tidak boleh berantakan.**

---

## Struktur

```
prompts/
├── planner/
├── fashion/
├── health/
├── finance/
├── career/
├── social/
└── evaluation/
```

---

## Setiap prompt memiliki

- system prompt
- user template
- tool rules
- evaluation

---

## Contoh manifest

```yaml
agent: FashionAgent
version: 1.2
temperature: 0.3
tools:
  - wardrobe
  - weather
  - trend
```

> **Prompt menjadi versioned.**
