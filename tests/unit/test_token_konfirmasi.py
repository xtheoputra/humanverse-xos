"""spec/07 4.5 — token konfirmasi: bertanda tangan, milik satu pengguna, dan kini membawa
giliran yang ditanyainya (E-199). Tanpa basis data — tanda tangannya murni HMAC berlabel.
"""

from __future__ import annotations

import base64
import json
from uuid import UUID, uuid4

import pytest

from hvx.modules.agents import (
    KonfirmasiTidakSah,
    PermintaanKonfirmasi,
    PersetujuanAksi,
    TokenKonfirmasi,
)
from hvx.modules.agents.schemas import JawabKonfirmasi

TANDA = TokenKonfirmasi(lambda isi: f"{len(isi):064x}")


def _buat(
    *,
    pesan_id: UUID | None = None,
    persetujuan_lalu: frozenset[PersetujuanAksi] = frozenset(),
) -> tuple[UUID, PermintaanKonfirmasi]:
    uid = uuid4()
    p = TANDA.buat(
        jenis="izin",
        user_id=uid,
        run_id=uuid4(),
        agent="habit-agent",
        alat="habit.complete",
        risk_level=2,
        scopes=("habits",),
        aksi="write",
        sidik="a" * 64,
        pesan_id=pesan_id,
        persetujuan_lalu=persetujuan_lalu,
    )
    return uid, p


def test_token_membawa_pesan_giliran_dan_persetujuan_sebelumnya() -> None:
    """E-199: run ULANGAN tidak punya pesannya sendiri — tokenlah yang membawanya, beserta
    persetujuan yang sudah dipegang giliran itu."""
    pesan = uuid4()
    lalu = frozenset({PersetujuanAksi("habit-agent", "habit.list", "b" * 64)})
    uid, p = _buat(pesan_id=pesan, persetujuan_lalu=lalu)

    dibaca = TANDA.baca(p.token, uid)

    assert dibaca.pesan_id == pesan
    assert set(dibaca.persetujuan_lalu) == set(lalu)


def test_persetujuan_yang_diselundupkan_ke_token_merusak_tanda_tangannya() -> None:
    uid, p = _buat()
    isi_b64, tanda = p.token.split(".", 1)
    isi = json.loads(base64.urlsafe_b64decode(isi_b64 + "=" * (-len(isi_b64) % 4)))
    isi["p"] = [["habit-agent", "habit.complete", "c" * 64]]
    palsu = base64.urlsafe_b64encode(json.dumps(isi).encode()).rstrip(b"=").decode()

    with pytest.raises(KonfirmasiTidakSah):
        TANDA.baca(f"{palsu}.{tanda}", uid)


@pytest.mark.parametrize("tanda", ["é", "0" * 63 + "é", "​" * 64])
def test_tanda_tangan_non_ascii_ditolak_sebagai_token_rusak(tanda: str) -> None:
    """Tinjauan keamanan Sprint 4: `compare_digest` atas `str` ber-non-ASCII melempar
    TypeError — token rusak menjadi 500, bukan `422 invalid_confirmation` (spec/04)."""
    token = f"e30.{tanda}"  # isi base64 sah (`{}`)
    JawabKonfirmasi(token=token, decision="reject")  # lolos skema rute

    with pytest.raises(KonfirmasiTidakSah):
        TANDA.baca(token, uuid4())
