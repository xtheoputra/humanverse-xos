"""Bagian `agents` di Privacy Center — spec/07 6.4 (K-41 · K-42), naskah 5 §26.

* **Percakapan** (`ai_conversations` + `ai_messages`) — kategori `conversations`, bisa
  dihapus; run yang menautnya tetap, dengan `conversation_id` dilepas basis data (spec/01).
* **Jejak kerja asisten** (`agent_runs`) — AI Audit Trail naskah 5 §24: tool yang dipakai,
  scope yang disentuh, keputusan, biaya — **tanpa isi** percakapan. Masuk kategori `audit`:
  diekspor, tidak dihapus di sini — ia ikut terhapus bersama akunnya (cascade, spec/01).
* **Izin per agent** (*FashionAgent ✓ Wardrobe ✓ Weather ○ Calendar ✗ Finance*) — dari
  registry yang sama dengan yang ditegakkan gerbang risiko (4.5), bukan daftar kedua:
  tiap (scope, aksi) yang SUNGGUH bisa ditanyakan gerbang untuk agent itu.
"""

from __future__ import annotations

from hvx.modules import identity

from .gerbang import RISIKO_BAWAAN_IZINKAN, RISIKO_KONFIRMASI
from .registri import AKSI_IZIN, RegistriAgent

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "conversations",
        "ai_conversations",
        "SELECT count(*) FROM ai_conversations WHERE user_id = :u",
        "SELECT * FROM ai_conversations WHERE user_id = :u ORDER BY created_at, id",
    ),
    identity.bagian_sql(
        "conversations",
        "ai_messages",
        "SELECT count(*) FROM ai_messages WHERE user_id = :u",
        "SELECT * FROM ai_messages WHERE user_id = :u ORDER BY conversation_id, created_at, id",
    ),
    identity.bagian_sql(
        "audit",
        "agent_runs",
        "SELECT count(*) FROM agent_runs WHERE user_id = :u",
        "SELECT * FROM agent_runs WHERE user_id = :u ORDER BY started_at, id",
        turunan=True,
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    # `ai_messages` hanya-tambah bagi `hvx_app` (spec/01 §10 — tanpa DELETE): pesan terhapus
    # lewat `ON DELETE CASCADE` percakapannya. Langkah ini HANYA menghitungnya lebih dulu,
    # supaya jawaban `deleted` jujur — cascade tidak melaporkan baris.
    identity.penghapus_sql(
        "conversations", "ai_messages", "SELECT count(*) FROM ai_messages WHERE user_id = :u"
    ),
    identity.penghapus_sql(
        "conversations", "ai_conversations", "DELETE FROM ai_conversations WHERE user_id = :u"
    ),
)


def izin_diminta(registri: RegistriAgent) -> tuple[identity.IzinDiminta, ...]:
    """Tiap (agent aktif, scope, aksi) yang bisa ditanyakan gerbang risiko — dan bawaannya.

    Scope satu pemanggilan = `scope_panggilan` (pelaksana): tool yang menyaring izinnya
    sendiri (`memory.search`) hanya menyentuh scope `memory.read` manifest; tool ber-masukan
    `scope` (`memory.write`) hanya pagu manifest; tool lain seluruh `scopes`-nya. Bawaan
    mengikuti `GerbangRisiko.periksa`: delegasi dan R0·R1 `allow`, R2 ke atas `ask`; R3 ke
    atas dikonfirmasi tiap kali. Satu (scope, aksi) yang disentuh beberapa tool memakai yang
    PALING ketat — layar tidak boleh menjanjikan `allow` yang tidak berlaku bagi semuanya.
    """
    hasil: list[identity.IzinDiminta] = []
    for nama in sorted(registri.agent):
        m = registri.agent[nama]
        diminta: dict[tuple[str, identity.Aksi], tuple[bool, bool]] = {}
        for t in m.tools:
            alat = registri.alat[t]
            aksi = AKSI_IZIN[alat.kind]
            if alat.menyaring_izin:
                scopes = [s for s in alat.scopes if s in m.memory.read]
            elif "scope" in alat.input:
                pagu = m.memory.write if alat.kind == "write" else m.memory.read
                scopes = [s for s in alat.scopes if s in pagu]
            else:
                scopes = list(alat.scopes)
            delegasi = alat.kind == "agent"
            if delegasi:
                # E-227: bawaan delegasi di scope sensitif TETAP `allow` (`MesinIzin.cek`
                # delegasi=True) — layar Privacy Center memaksanya `ask`, jadi tidak ditampilkan;
                # izin yang bermakna milik agent yang MEMBACA (coach · mood).
                scopes = [s for s in scopes if not identity.SCOPE_RESMI[s].sensitif]
            izinkan = delegasi or alat.risk_level <= RISIKO_BAWAAN_IZINKAN
            konfirmasi = not delegasi and alat.risk_level >= RISIKO_KONFIRMASI
            for s in scopes:
                lama_izinkan, lama_konfirmasi = diminta.get((s, aksi), (True, False))
                diminta[(s, aksi)] = (lama_izinkan and izinkan, lama_konfirmasi or konfirmasi)
        for (scope, aksi), (izinkan, konfirmasi) in sorted(diminta.items()):
            hasil.append(
                identity.IzinDiminta(
                    agent=nama,
                    tujuan=tuple(m.purpose),
                    scope=scope,
                    aksi=aksi,
                    bawaan="allow" if izinkan else "ask",
                    konfirmasi_tiap_kali=konfirmasi,
                )
            )
    return tuple(hasil)
