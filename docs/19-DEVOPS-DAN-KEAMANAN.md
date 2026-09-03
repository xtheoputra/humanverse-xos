# 19 — DevOps, Observability & Security

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DevOps Enterprise

**Stack:**

- GitHub Actions
- Docker
- Kubernetes
- ArgoCD
- Terraform
- Vault

**Deployment:**

```
  Development  →  Staging  →  Production
```

---

## Observability

**Gunakan:**

| Alat | |
|---|---|
| OpenTelemetry | Loki |
| Prometheus | Tempo |
| Grafana | Sentry |

> **Semua agent dapat dipantau.**

---

## Security Architecture

| Layer | Teknologi |
|---|---|
| **Authentication** | OAuth |
| **Authorization** | RBAC |
| **Secrets** | Vault |
| **Encryption** | AES-256 |
| **TLS** | HTTPS |
| **Audit** | Immutable Log |

> **Privacy menjadi fitur utama.**

Sejalan dengan prinsip #4 di [`07-PRINSIP.md`](07-PRINSIP.md).
