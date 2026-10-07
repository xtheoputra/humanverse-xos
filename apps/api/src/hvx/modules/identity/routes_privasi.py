"""Rute Privacy Center — spec/04 *Privacy Center*, spec/07 6.4 (naskah 5 §26, K-41…K-43).

Bagian data, penghapus, dan katalog izin agent dipasang titik rakit `hvx.main` (K-23):
`identity` tidak mengimpor modul yang datanya ia ringkas. Tanpa sambungannya rute MENOLAK
berjalan (`RuntimeError`) — bukan menjawab *“tidak ada data”* diam-diam.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse

from hvx.modules import platform

from . import privasi, service
from .dependensi import PenggunaDiperlukan
from .izin import MesinIzin, mesin_izin
from .laju import penjaga_gagal_masuk
from .schemas import (
    DaftarIzinAgent,
    IzinBerlaku,
    JawabanEkspor,
    JawabanHapusData,
    PermintaanIzin,
    PermintaanSandiUlang,
    RingkasanPrivasi,
)

router_privasi = APIRouter(prefix="/v1/privacy", tags=["privacy"])

Izin = Annotated[MesinIzin, Depends(mesin_izin)]
SubjekTipeJalur = Annotated[str, Path(pattern=r"^(agent|tool|integration)$")]
SubjekIdJalur = Annotated[str, Path(pattern=r"^[a-z0-9][a-z0-9._-]{0,99}$")]
ScopeJalur = Annotated[str, Path(pattern=r"^[a-z][a-z0-9_]{0,62}$")]
KategoriJalur = Annotated[str, Path(pattern=r"^[a-z][a-z_]{0,39}$")]


def _sambungan(request: Request, nama: str) -> Any:
    nilai = getattr(request.app.state, nama, None)
    if nilai is None:
        raise RuntimeError(f"`app.state.{nama}` belum dipasang titik rakit hvx.main (K-23)")
    return nilai


def _bagian(request: Request) -> Sequence[privasi.BagianData]:
    return cast(Sequence[privasi.BagianData], _sambungan(request, "bagian_privasi"))


def _penghapus(request: Request) -> Sequence[privasi.Penghapus]:
    return cast(Sequence[privasi.Penghapus], _sambungan(request, "penghapus_privasi"))


def _katalog(request: Request) -> Sequence[privasi.IzinDiminta]:
    return cast(Sequence[privasi.IzinDiminta], _sambungan(request, "katalog_izin_agent"))


@router_privasi.get("/summary", response_model=RingkasanPrivasi)
async def ringkasan_privasi(request: Request, pengguna: PenggunaDiperlukan) -> dict[str, Any]:
    return await privasi.ringkasan(
        platform.engine_dari(request), pengguna.user_id, _bagian(request), _penghapus(request)
    )


@router_privasi.get("/permissions", response_model=DaftarIzinAgent)
async def izin_per_agent(request: Request, pengguna: PenggunaDiperlukan) -> dict[str, Any]:
    return await privasi.izin_per_agent(
        platform.engine_dari(request), pengguna.user_id, _katalog(request)
    )


@router_privasi.put("/permissions/{subject_type}/{subject_id}/{scope}", response_model=IzinBerlaku)
async def tetapkan_izin(
    request: Request,
    subject_type: SubjekTipeJalur,
    subject_id: SubjekIdJalur,
    scope: ScopeJalur,
    badan: PermintaanIzin,
    pengguna: PenggunaDiperlukan,
    mesin: Izin,
) -> dict[str, Any]:
    """Idempoten dengan sendirinya — keputusan yang sama dua kali tetap satu baris."""
    if badan.expires_at is not None and badan.expires_at <= datetime.now(UTC):
        raise platform.GalatApi(422, "expires_at_in_past", "Waktu berakhir izin sudah lewat.")
    katalog = _katalog(request)
    await privasi.tetapkan_izin(
        mesin,
        pengguna.user_id,
        katalog,
        subjek_tipe=subject_type,
        subjek_id=subject_id,
        scope=scope,
        aksi=badan.action,
        keputusan=badan.decision,
        expires_at=badan.expires_at,
        ip_hash=platform.sidik_ip(request),
    )
    daftar = await privasi.izin_per_agent(platform.engine_dari(request), pengguna.user_id, katalog)
    return next(
        i
        for a in daftar["agents"]
        if a["subject_id"] == subject_id
        for i in a["permissions"]
        if i["scope"] == scope and i["action"] == badan.action
    )


@router_privasi.post("/export", status_code=202, response_model=JawabanEkspor)
async def minta_ekspor(
    request: Request, badan: PermintaanSandiUlang, pengguna: PenggunaDiperlukan
) -> dict[str, Any]:
    """Tanpa `Idempotency-Key` (dikecualikan test_idempotensi_terpasang): ulangan membuat
    catatan ekspor sekali-pakai lain — tidak menulis data domain apa pun."""
    hasil = await platform.pembatas_laju(request).ambil(privasi.BATAS_EKSPOR, str(pengguna.user_id))
    if not hasil.lolos:
        raise platform.galat_terlalu_sering(hasil)
    engine = platform.engine_dari(request)
    ip_hash = platform.sidik_ip(request)
    await service.verifikasi_sandi_ulang(
        engine,
        pengguna.user_id,
        badan.password.get_secret_value(),
        penjaga=penjaga_gagal_masuk(request),
        aksi_ditolak="data.export_rejected",
        ip_hash=ip_hash,
    )
    return await privasi.minta_ekspor(
        engine,
        platform.redis_dari(request),
        platform.settings_dari(request).redis_prefix,
        pengguna.user_id,
        ip_hash=ip_hash,
    )


@router_privasi.get("/export/{export_id}", response_model=JawabanEkspor)
async def status_ekspor(
    request: Request, export_id: UUID, pengguna: PenggunaDiperlukan
) -> dict[str, Any]:
    return await privasi.status_ekspor(
        platform.redis_dari(request),
        platform.settings_dari(request).redis_prefix,
        pengguna.user_id,
        export_id,
    )


@router_privasi.get("/export/{export_id}/download")
async def unduh_ekspor(
    request: Request, export_id: UUID, pengguna: PenggunaDiperlukan
) -> JSONResponse:
    """Sekali pakai, butuh sesi pemiliknya — tak ada rahasia di URL (ASVS V8.3.1)."""
    dokumen = await privasi.unduh_ekspor(
        platform.engine_dari(request),
        platform.redis_dari(request),
        platform.settings_dari(request).redis_prefix,
        pengguna.user_id,
        export_id,
        _bagian(request),
        ip_hash=platform.sidik_ip(request),
    )
    tanggal = str(dokumen["exported_at"])[:10].replace("-", "")
    return JSONResponse(
        dokumen,
        headers={
            "Content-Disposition": f'attachment; filename="humanverse-export-{tanggal}.json"',
            "Cache-Control": "no-store",
        },
    )


@router_privasi.delete("/data/{category}", status_code=202, response_model=JawabanHapusData)
async def hapus_data(
    request: Request,
    category: KategoriJalur,
    badan: PermintaanSandiUlang,
    pengguna: PenggunaDiperlukan,
) -> JawabanHapusData:
    """Idempoten dengan sendirinya — hapus kedua menghapus nol baris."""
    penghapus = _penghapus(request)
    privasi.periksa_kategori_bisa_dihapus(category, penghapus)  # 404/409 sebelum sandi ditebak
    engine = platform.engine_dari(request)
    ip_hash = platform.sidik_ip(request)
    await service.verifikasi_sandi_ulang(
        engine,
        pengguna.user_id,
        badan.password.get_secret_value(),
        penjaga=penjaga_gagal_masuk(request),
        aksi_ditolak="data.deletion_rejected",
        ip_hash=ip_hash,
    )
    terhapus = await privasi.hapus_kategori(
        engine, pengguna.user_id, category, penghapus, ip_hash=ip_hash
    )
    return JawabanHapusData(category=category, deleted=terhapus)
