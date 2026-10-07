"""spec/07 6.4 — Privacy Center melihat SEMUA yang disimpan, dan hapus membawa turunannya.

*“Apa yang kamu tahu tentang saya”* (naskah 5 §26) hanya jujur bila tidak ada tabel yang
terlupa. Daftar tabel milik pengguna dibaca DARI spec/01 (tiap `CREATE TABLE` yang punya
kolom `user_id`, plus `users`), dan kepemilikannya dari spec/06 — bukan disalin ke sini:
tabel ke-24 yang lupa dinyatakan di Privacy Center membuat berkas ini merah (K-41).
"""

from __future__ import annotations

import importlib
import re
from collections import Counter
from pathlib import Path

import pytest
from fastapi import FastAPI

from hvx.main import create_app
from hvx.modules import events, identity, memory
from hvx.modules.platform import Settings

AKAR = Path(__file__).resolve().parents[2]
SPEC01 = AKAR / "spec" / "01-DATABASE-SCHEMA.md"
SPEC06 = AKAR / "spec" / "06-MODULE-BOUNDARIES.md"


def _app() -> FastAPI:
    return create_app(Settings(database_url="postgresql://x", redis_url="redis://x", env="test"))


def tabel_milik_pengguna() -> set[str]:
    """Tabel spec/01 yang barisnya milik seorang pengguna: ber-`user_id`, dan `users` sendiri."""
    teks = SPEC01.read_text(encoding="utf-8")
    hasil = {"users"}
    for nama, isi in re.findall(r"CREATE TABLE (\w+) \((.*?)\n\);", teks, re.S):
        if re.search(r"^\s*user_id\s", isi, re.M):
            hasil.add(nama)
    return hasil


def kepemilikan() -> dict[str, set[str]]:
    teks = SPEC06.read_text(encoding="utf-8")
    bagian = teks.split("## Kepemilikan tabel", 1)[1].split("\n## ", 1)[0]
    return {
        modul: set(re.findall(r"`([a-z_]+)`", tabel))
        for modul, tabel in re.findall(r"^\| `([a-z]+)` \| (.+?) \|$", bagian, re.M)
    }


def _modul(nama: str) -> object:
    return importlib.import_module(f"hvx.modules.{nama}")


def test_pembaca_spec01_menemukan_semua_tabel_milik_pengguna() -> None:
    tabel = tabel_milik_pengguna()
    assert len(tabel) == 21, f"tabel milik pengguna terbaca dari spec/01: {sorted(tabel)}"
    assert {"agents", "agent_tools"}.isdisjoint(tabel), "katalog sistem terbaca milik pengguna"


def test_tiap_tabel_milik_pengguna_dinyatakan_tepat_sekali() -> None:
    bagian = _app().state.bagian_privasi
    hitung = Counter(b.tabel for b in bagian)
    kurang = sorted(tabel_milik_pengguna() - set(hitung))
    ganda = sorted(t for t, n in hitung.items() if n > 1)
    asing = sorted(set(hitung) - tabel_milik_pengguna())

    assert not kurang, f"tabel milik pengguna yang TIDAK terlihat di Privacy Center: {kurang}"
    assert not ganda, f"tabel yang diekspor/dihitung lebih dari sekali: {ganda}"
    assert not asing, f"bagian Privacy Center untuk tabel yang bukan milik pengguna: {asing}"


def test_titik_rakit_memasang_bagian_dan_penghapus_semua_modul() -> None:
    """Modul yang menyatakan bagiannya tetapi lupa dirakit `hvx.main` sama dengan tidak ada."""
    app = _app()
    for modul in kepemilikan():
        m = _modul(modul)
        for b in getattr(m, "BAGIAN_PRIVASI", ()):
            assert b in app.state.bagian_privasi, f"{modul}: bagian {b.tabel} tidak dirakit"
        for p in getattr(m, "PENGHAPUS_PRIVASI", ()):
            assert p in app.state.penghapus_privasi, f"{modul}: penghapus {p.tabel} tidak dirakit"


@pytest.mark.parametrize("jenis", ["BAGIAN_PRIVASI", "PENGHAPUS_PRIVASI"])
def test_tiap_modul_hanya_menyatakan_tabel_miliknya(jenis: str) -> None:
    """spec/06 aturan 5 untuk Privacy Center: SQL bagian & penghapus ditulis modul PEMILIKNYA."""
    salah = [
        f"{modul}: {x.tabel}"
        for modul, milik in kepemilikan().items()
        for x in getattr(_modul(modul), jenis, ())
        if x.tabel not in milik
    ]
    assert not salah, f"{jenis} menyatakan tabel milik modul lain: {salah}"


def test_kategori_tiap_bagian_dan_penghapus_dikenal_layar() -> None:
    app = _app()
    dipakai = {b.kategori for b in app.state.bagian_privasi}
    dipakai |= {p.kategori for p in app.state.penghapus_privasi}

    assert dipakai <= set(identity.KATEGORI), f"kategori asing: {dipakai - set(identity.KATEGORI)}"
    kosong = sorted(set(identity.KATEGORI) - {b.kategori for b in app.state.bagian_privasi})
    assert not kosong, f"kategori layar tanpa satu tabel pun: {kosong}"


def test_kategori_yang_bisa_dihapus_menghapus_tiap_tabelnya_sendiri() -> None:
    """Hapus kategori yang meninggalkan salah satu tabelnya bukan hapus (naskah 11 §7.25)."""
    app = _app()
    for kunci, kat in identity.KATEGORI.items():
        sumber = {p.tabel for p in app.state.penghapus_privasi if p.kategori == kunci}
        utama = {p for p in app.state.penghapus_privasi if p.kategori == kunci and not p.turunan}
        tabel = {b.tabel for b in app.state.bagian_privasi if b.kategori == kunci}
        if kat.tidak_bisa_dihapus is not None:
            assert not utama, f"`{kunci}` dinyatakan tak bisa dihapus tetapi punya penghapus"
            continue
        assert utama, f"`{kunci}` bisa dihapus tetapi tanpa penghapus"
        assert tabel <= sumber, f"hapus `{kunci}` meninggalkan tabel {sorted(tabel - sumber)}"


def test_tiap_jenis_event_ikut_terhapus_bersama_kategori_sumbernya() -> None:
    """Event jenis baru di REGISTRY tanpa kategori sumber = teks yang tak bisa dicabut (C-33)."""
    app = _app()
    for jenis in events.REGISTRY:
        domain = jenis.split(".", 1)[0]
        assert domain in events.KATEGORI_EVENT, f"{jenis}: tanpa kategori Privacy Center"
        kategori = events.KATEGORI_EVENT[domain]
        assert kategori in identity.KATEGORI, f"{jenis} → kategori asing {kategori}"
        assert jenis in events.jenis_untuk(kategori)
        assert any(
            p.kategori == kategori and p.tabel == "events" and p.turunan
            for p in app.state.penghapus_privasi
        ), f"hapus `{kategori}` tidak membuang event {jenis}"


def test_memori_turunan_ikut_terlupa_bersama_kategori_sumbernya() -> None:
    app = _app()
    for kategori, scope in memory.SCOPE_SUMBER.items():
        assert kategori in identity.KATEGORI
        assert scope in identity.SCOPE_RESMI, f"{kategori} → scope asing {scope}"
        assert any(
            p.kategori == kategori and p.tabel == "memories" and p.turunan
            for p in app.state.penghapus_privasi
        ), f"hapus `{kategori}` tidak melupakan memori ber-scope {scope}"


def test_katalog_izin_agent_sama_dengan_registry_yang_ditegakkan() -> None:
    """Tiap agent aktif muncul; scope sensitif tidak pernah berbawaan `allow` di layar."""
    from hvx.modules import agents

    app = _app()
    katalog = app.state.katalog_izin_agent
    assert {d.agent for d in katalog} == set(app.state.registri_agent.agent)
    assert katalog == agents.izin_diminta(app.state.registri_agent)
    for d in katalog:
        assert d.scope in identity.SCOPE_RESMI, f"{d.agent}: scope asing {d.scope}"
