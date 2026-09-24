"""Rute percakapan — spec/04 *AI* (spec/07 4.8).

Layanannya dirakit `hvx.main` di `app.state.percakapan` (K-23): runtime agent, gerbang,
dan model hanya ada di proses api yang hidup — rute MENOLAK berjalan tanpanya, tidak
diam-diam merakit versinya sendiri.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from functools import partial
from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from hvx.modules import identity, platform

from .percakapan import LayananPercakapan
from .schemas import (
    BuatPercakapan,
    HalamanPercakapan,
    HalamanPesan,
    JawabKonfirmasi,
    KirimPesan,
    Percakapan,
    TerimaKonfirmasi,
    TerimaPesan,
)

router = APIRouter(prefix="/v1", tags=["conversations"])


def _layanan(request: Request) -> LayananPercakapan:
    layanan = getattr(request.app.state, "percakapan", None)
    if not isinstance(layanan, LayananPercakapan):
        raise RuntimeError("hvx.main tidak memasang app.state.percakapan (K-23)")
    return layanan


@router.get("/conversations", response_model=HalamanPercakapan)
async def daftar_percakapan(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    limit: platform.Batas = platform.BATAS_BAWAAN,
    cursor: platform.Kursor = None,
) -> HalamanPercakapan:
    return await _layanan(request).daftar(pengguna.user_id, batas=limit, kursor=cursor)


@router.post("/conversations", status_code=201, response_model=Percakapan)
async def buat_percakapan(
    request: Request,
    badan: BuatPercakapan,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    layanan = _layanan(request)

    async def kerja() -> platform.Jawaban:
        p = await layanan.buat(pengguna.user_id, badan)
        return platform.Jawaban(201, p, p.id)

    return await idem.jalankan(pengguna.user_id, kerja, partial(layanan.baca, pengguna.user_id))


@router.get("/conversations/{percakapan_id}/messages", response_model=HalamanPesan)
async def daftar_pesan(
    request: Request,
    percakapan_id: UUID,
    pengguna: identity.PenggunaDiperlukan,
    limit: platform.Batas = platform.BATAS_BAWAAN,
    cursor: platform.Kursor = None,
) -> HalamanPesan:
    return await _layanan(request).pesan(
        pengguna.user_id, percakapan_id, batas=limit, kursor=cursor
    )


@router.post("/conversations/{percakapan_id}/messages", status_code=202, response_model=TerimaPesan)
async def kirim_pesan(
    request: Request,
    percakapan_id: UUID,
    badan: KirimPesan,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    layanan = _layanan(request)

    async def kerja() -> platform.Jawaban:
        t = await layanan.kirim(pengguna.user_id, percakapan_id, badan)
        return platform.Jawaban(202, t, t.message_id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(layanan.baca_terima, pengguna.user_id)
    )


@router.post(
    "/conversations/{percakapan_id}/confirmations",
    status_code=202,
    response_model=TerimaKonfirmasi,
)
async def jawab_konfirmasi(
    request: Request,
    percakapan_id: UUID,
    badan: JawabKonfirmasi,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    """Jawaban atas `confirmation_required` (spec/04, 4.5 — E-195)."""
    layanan = _layanan(request)

    async def kerja() -> platform.Jawaban:
        t = await layanan.jawab(pengguna.user_id, percakapan_id, badan)
        return platform.Jawaban(202, t, t.agent_run_id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(layanan.baca_terima_konfirmasi, pengguna.user_id)
    )


@router.get(
    "/conversations/{percakapan_id}/stream",
    response_class=StreamingResponse,
    responses={
        200: {"content": {"text/event-stream": {}}, "description": "token · tool_call · done"},
        204: {"description": "tidak ada giliran yang sedang atau baru saja berjalan"},
    },
)
async def aliran(
    request: Request, percakapan_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> Response:
    """SSE giliran terakhir, dari peristiwa pertamanya sampai `done`/`error` (spec/04).

    `204` bila tidak ada yang mengalir — di SSE, 204 berarti *jangan menyambung ulang*;
    balasan yang sudah selesai dibaca dari `GET …/messages`.
    """
    layanan = _layanan(request)
    if await layanan.baca(pengguna.user_id, percakapan_id) is None:
        raise platform.GalatApi(404, "not_found", "Percakapan tidak ditemukan.")
    if not layanan.aliran.ada(percakapan_id):
        return Response(status_code=204)

    async def isi() -> AsyncIterator[str]:
        async for jenis, data in layanan.aliran.ikuti(percakapan_id):
            yield f"event: {jenis}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        isi(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
