"""Gerbang risiko — spec/05 *Risk gate*, spec/07 4.5: *risk 2 minta izin sekali; risk 3
minta setiap kali*.

Ditanya pelaksana tool untuk TIAP pemanggilan yang lolos registry, manifest,
masukan, dan batas laju — termasuk pemanggilan agent lain (K-14). Urutannya:

1. **R4 = DENY** — *irreversible*, tidak ada konfirmasi yang membukanya
   (arch/04 §3, H-21: *“Ask Every Time” bukan pengganti penolakan*).
2. **Mesin izin**, per scope yang disentuh pemanggilan itu (`scope_panggilan`),
   subjeknya agent pemanggil, aksinya menurut `kind` tool. Bawaan untuk yang belum
   pernah diputuskan: **R0·R1 `allow`** (tanpa menimpa *“tanya aku”* yang disetel
   pengguna — E-167; scope sensitif tidak pernah terbuka karena bawaan — E-180),
   **R2 ke atas `ask`**.
3. **`deny` → tolak & catat** (`audit_logs`), apa pun R-nya.
4. **R3 → konfirmasi manusia SETIAP KALI** — bahkan bila izinnya `allow` (H-15).
5. **`ask` → minta izin** — dijawab sekali lalu diingat (`izinkan_selalu`), atau
   untuk pemanggilan ini saja.

Pemanggilan agent lain (`kind: agent`) melewati jalan yang sama — R4, `deny`, dan
`ask` yang DISETEL pengguna berlaku — tetapi tidak ditanyakan sendiri: bawaannya
`allow` dan tanpa konfirmasi R3, sebab yang berisiko adalah tool di dalam agent itu,
yang ditanyakan di run-nya sendiri. Tanpa itu satu permintaan (*“tandai lari
selesai”*) ditanya dua kali: delegasinya, lalu tulisannya (E-192).

Yang ditahan di (4)·(5) menjadi `AlatDitolak` yang membawa `PermintaanKonfirmasi`
bertanda tangan — run-nya `blocked`, dan giliran yang disetujui diulang dengan
persetujuan itu (`konfirmasi.py`).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import identity, platform

from .jalannya import Jalannya
from .konfirmasi import AKSI_IZIN, JenisKonfirmasi, TokenKonfirmasi, sidik_masukan
from .pelaksana_alat import AlatDitolak, scope_panggilan
from .registri import Alat

RISIKO_TERLARANG = 4
RISIKO_KONFIRMASI = 3
RISIKO_BAWAAN_IZINKAN = 1  # R0·R1: `allow` bila pengguna belum pernah memutuskan


class GerbangRisiko:
    def __init__(
        self, engine: AsyncEngine, mesin_izin: identity.MesinIzin, tanda: TokenKonfirmasi
    ) -> None:
        self._engine = engine
        self._izin = mesin_izin
        self._tanda = tanda

    async def _tolak(self, j: Jalannya, alat: Alat, kode: str) -> AlatDitolak:
        """Tolak & CATAT (spec/05) — jejaknya di transaksinya sendiri: tidak ada yang
        dijalankan, jadi tidak ada perubahan yang bisa ikut dibatalkan bersamanya."""
        async with platform.transaksi_pengguna(self._engine, j.user_id) as conn:
            await identity.audit(
                conn,
                aksi="agent.tool_denied",
                aktor_tipe="agent",
                aktor_id=j.agent.name,
                user_id=j.user_id,
                subjek_tipe="tool",
                subjek_id=alat.name,
                metadata={"risk": alat.risk_level, "kode": kode, "run": str(j.id)},
            )
        return AlatDitolak(kode, f"{alat.name} ditolak gerbang ({kode})", alat=alat.name)

    def _tahan(
        self,
        j: Jalannya,
        alat: Alat,
        jenis: JenisKonfirmasi,
        scopes: tuple[str, ...],
        sidik: str,
    ) -> AlatDitolak:
        permintaan = self._tanda.buat(
            jenis=jenis,
            user_id=j.user_id,
            run_id=j.id,
            agent=j.agent.name,
            alat=alat.name,
            risk_level=alat.risk_level,
            scopes=scopes,
            aksi=AKSI_IZIN[alat.kind],
            sidik=sidik,
        )
        kode = "perlu_konfirmasi" if jenis == "konfirmasi" else "perlu_izin"
        return AlatDitolak(
            kode, f"{alat.name} menunggu {jenis} pengguna", alat=alat.name, konfirmasi=permintaan
        )

    async def periksa(self, jalannya: Jalannya, alat: Alat, masukan: Mapping[str, Any]) -> None:
        if alat.risk_level >= RISIKO_TERLARANG:
            raise await self._tolak(jalannya, alat, "risiko_terlarang")
        scopes = scope_panggilan(alat, masukan)
        # Delegasi (`kind: agent`, K-14) tidak DITANYAKAN sendiri: yang berisiko adalah
        # tool di dalamnya, dan tool itu melewati gerbang ini dengan run agent-nya —
        # satu permintaan tidak ditanya dua kali. `deny`/`ask` yang disetel pengguna
        # untuk delegasinya tetap berlaku, dan R4 tetap ditolak (E-192).
        delegasi = alat.kind == "agent"
        bawaan: identity.Keputusan = (
            "allow" if delegasi or alat.risk_level <= RISIKO_BAWAAN_IZINKAN else "ask"
        )
        subjek = identity.Subjek("agent", jalannya.agent.name)
        aksi = AKSI_IZIN[alat.kind]
        keputusan = (
            []  # tool menanyai mesin izin sendiri, per scope (memory.search, E-193)
            if alat.menyaring_izin
            else [
                await self._izin.cek(jalannya.user_id, subjek, s, aksi, bawaan=bawaan)
                for s in scopes
            ]
        )
        if "deny" in keputusan:
            raise await self._tolak(jalannya, alat, "ditolak_pengguna")

        sidik = sidik_masukan(alat.name, masukan)
        disetujui = any(
            p.agent == jalannya.agent.name and p.alat == alat.name and p.sidik == sidik
            for p in jalannya.persetujuan
        )
        konfirmasi = not delegasi and alat.risk_level >= RISIKO_KONFIRMASI
        if (konfirmasi or "ask" in keputusan) and not disetujui:
            raise self._tahan(jalannya, alat, "konfirmasi" if konfirmasi else "izin", scopes, sidik)
        if disetujui:
            jalannya.dikonfirmasi = True
