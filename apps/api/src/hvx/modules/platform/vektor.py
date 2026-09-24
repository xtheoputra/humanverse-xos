"""Klien Qdrant (REST) — spec/07 3.5, ADR-003. Satu-satunya jalan keluar ke basis data
vektor, di `platform` (B-2: klien jaringan hanya di sini).

REST lewat `httpx`, bukan `qdrant-client`: empat panggilan (koleksi · simpan ·
cari · hapus) tidak sepadan dengan dependensi gRPC dan numpy, dan tiap panggilan
di sini terbaca sebagai HTTP biasa di uji.

🔒 **Tiap titik membawa `user_id` di payload, dan tiap pencarian WAJIB
menyaringnya** — `cari()` menolak dipanggil tanpa `user_id`. Qdrant tidak punya
RLS: saringan inilah yang menjaga H-27 di sisi vektor, jadi ia bukan parameter
opsional. Barisnya sendiri tetap dibaca dari PostgreSQL di bawah RLS sesudahnya.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx

from .config import Settings


class GalatVektor(RuntimeError):
    """Qdrant menjawab galat atau tidak terjangkau — isinya tidak memuat vektor atau payload."""


@dataclass(frozen=True)
class Titik:
    id: UUID
    vektor: list[float]
    payload: dict[str, Any]


@dataclass(frozen=True)
class HasilCari:
    id: UUID
    skor: float
    payload: dict[str, Any]


class KlienVektor:
    def __init__(self, url: str, *, kunci_api: str | None = None, timeout_s: float = 5.0) -> None:
        kepala = {"api-key": kunci_api} if kunci_api else {}
        self._http = httpx.AsyncClient(base_url=url.rstrip("/"), headers=kepala, timeout=timeout_s)

    async def tutup(self) -> None:
        await self._http.aclose()

    async def _minta(self, metode: str, jalur: str, isi: Any | None = None) -> Any:
        try:
            r = await self._http.request(metode, jalur, json=isi)
        except httpx.HTTPError as galat:
            raise GalatVektor(f"qdrant tidak terjangkau: {type(galat).__name__}") from None
        if r.status_code >= 400:
            # Hanya kode status — badan galat Qdrant bisa memantulkan isi permintaan.
            raise GalatVektor(f"qdrant {metode} {jalur.split('?')[0]} → {r.status_code}")
        # `/readyz` menjawab teks polos; sisanya JSON.
        if r.content and r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        return None

    async def ping(self) -> None:
        await self._minta("GET", "/readyz")

    async def pastikan_koleksi(self, nama: str, dimensi: int, indeks: list[str]) -> None:
        """Koleksi kosinus berdimensi `dimensi` + indeks kata kunci payload — idempoten.

        Koleksi yang SUDAH ada dengan dimensi atau jarak lain ditolak, bukan dipakai:
        penyemat yang berganti diam-diam membuat tiap `simpan` gagal satu per satu
        (dan event-nya berakhir di stream mati) — lebih baik pekerja menolak mulai.
        """
        ada = await self._minta("GET", f"/collections/{nama}/exists")
        if not (ada and ada.get("result", {}).get("exists")):
            await self._minta(
                "PUT", f"/collections/{nama}", {"vectors": {"size": dimensi, "distance": "Cosine"}}
            )
        else:
            info = await self._minta("GET", f"/collections/{nama}")
            vektor = (
                (info or {}).get("result", {}).get("config", {}).get("params", {}).get("vectors")
            )
            if not isinstance(vektor, dict) or (vektor.get("size"), vektor.get("distance")) != (
                dimensi,
                "Cosine",
            ):
                raise GalatVektor(f"koleksi {nama} bukan kosinus berdimensi {dimensi}")
        for medan in indeks:
            await self._minta(
                "PUT",
                f"/collections/{nama}/index?wait=true",
                {"field_name": medan, "field_schema": "keyword"},
            )

    async def simpan(self, nama: str, titik: list[Titik]) -> None:
        """Upsert — id yang sama menimpa titik lama, jadi pengulangan aman."""
        if not titik:
            return
        await self._minta(
            "PUT",
            f"/collections/{nama}/points?wait=true",
            {
                "points": [
                    {"id": str(t.id), "vector": t.vektor, "payload": t.payload} for t in titik
                ]
            },
        )

    async def cari(
        self,
        nama: str,
        vektor: list[float],
        *,
        user_id: UUID,
        saring: dict[str, list[str]],
        batas: int,
        offset: int = 0,
    ) -> list[HasilCari]:
        if not isinstance(user_id, UUID):
            raise TypeError("pencarian vektor wajib dibatasi satu user_id (H-27)")
        wajib: list[dict[str, Any]] = [{"key": "user_id", "match": {"value": str(user_id)}}]
        for medan, nilai in saring.items():
            if not nilai:
                return []  # saringan kosong = tidak ada yang boleh cocok, bukan "semua"
            wajib.append({"key": medan, "match": {"any": list(nilai)}})
        jawab = await self._minta(
            "POST",
            f"/collections/{nama}/points/search",
            {
                "vector": vektor,
                "filter": {"must": wajib},
                "limit": batas,
                "offset": offset,
                "with_payload": True,
            },
        )
        hasil = jawab.get("result", []) if jawab else []
        return [
            HasilCari(UUID(str(h["id"])), float(h["score"]), h.get("payload") or {}) for h in hasil
        ]

    async def hapus(self, nama: str, ids: list[UUID]) -> None:
        """Titik menurut id — id yang tidak ada bukan galat, jadi pengulangan aman."""
        if not ids:
            return
        await self._minta(
            "POST",
            f"/collections/{nama}/points/delete?wait=true",
            {"points": [str(i) for i in ids]},
        )

    async def hapus_milik(self, nama: str, user_id: UUID) -> None:
        """Semua titik satu pengguna — hapus akun tahap 4 (spec/01): menurut SARINGAN,
        bukan daftar id, supaya titik yatim (memori yang gagal commit) ikut terhapus."""
        await self._minta(
            "POST",
            f"/collections/{nama}/points/delete?wait=true",
            {"filter": {"must": [{"key": "user_id", "match": {"value": str(user_id)}}]}},
        )


def klien_vektor_dari(settings: Settings) -> KlienVektor | None:
    """Klien Qdrant proses ini — `None` bila `HVX_QDRANT_URL` kosong (memori tanpa vektor)."""
    if not settings.qdrant_url:
        return None
    kunci = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
    return KlienVektor(settings.qdrant_url, kunci_api=kunci)
