#
# Citra apps/api — SATU artefak untuk semua lingkungan (arch/09 §5 aturan 1).
# Yang berbeda antarlingkungan hanya variabel HVX_*, tidak pernah citranya.
#
#   docker build -f infrastructure/docker/api.Dockerfile -t hvx-api:local .
#
# Semua citra luar dipatok ke DIGEST, bukan tag: tag bisa dipindahkan, dan
# alat pemindai yang dipakai repo ini sendiri pernah diterbitkan ulang di tag
# lama dengan pencuri kredensial (trivy, Maret 2026, GHSA-69fq-xp46-6x23). Dijaga
# tests/unit/test_rantai_pasok.py.

ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

# ─────────────────────────────────────────────────────────────── bangun ──
FROM ${PYTHON_IMAGE} AS bangun

COPY --from=ghcr.io/astral-sh/uv:0.12.15@sha256:62f8c047d0a0e9ece6b53fc63df902585a67a47a7f318ddec4a37db586edc8e3 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /repo

# Lapisan dependensi dulu — berubah jauh lebih jarang daripada kode.
COPY pyproject.toml uv.lock ./
COPY apps/api/pyproject.toml apps/api/README.md apps/api/
# --locked, bukan --frozen: kunci yang tidak cocok lagi dengan pyproject GAGAL,
# bukan diam-diam dipakai.
RUN uv sync --locked --no-dev --package hvx-api --no-install-workspace

COPY apps/api/src apps/api/src
RUN uv sync --locked --no-dev --package hvx-api --no-editable

# ─────────────────────────────────────────────────────────────── jalan ──
FROM ${PYTHON_IMAGE} AS jalan

# Pembaruan keamanan paket Debian dipasang saat membangun, bukan ditunggu
# sampai citra dasarnya diterbitkan ulang: pemindaian pertama (trivy, tahap
# `scan`) menemukan dua CVE HIGH di libpcre2 yang perbaikannya sudah ada di
# repositori Debian tetapi belum ada di citra dasar.
# ⚠️ Harganya disebut: dua pembangunan dari commit yang sama bisa berisi paket
# Debian yang berbeda. Dipilih karena citra dasar yang dipatok digest tidak
# pernah menerima tambalan sendiri.
RUN apt-get update \
 && apt-get -y upgrade --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 10001 hvx \
 && useradd --system --uid 10001 --gid hvx --home-dir /app --shell /usr/sbin/nologin hvx

COPY --from=bangun /opt/venv /opt/venv
COPY --chown=root:root data/migrations /app/data/migrations

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
USER hvx
EXPOSE 8000

CMD ["uvicorn", "hvx.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--proxy-headers"]
