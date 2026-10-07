"""Preferensi notifikasi — spec/07 6.3: *“bisa dimatikan per jenis”* (K-44).

Naskah 7 Layer 38 (*“Jangan spam”* — urgency · relevance · timing · **quiet hours**) dan
naskah 11 §11.43 (*Interruption Manager*: Importance · Urgency · … · **User Preference** ·
Notification Fatigue → *Notify now · Notify later · Silent*), dengan pagu §11.17
(`notification: send: 10/day`). V0 **tidak mengirim** apa pun — A-28: V0 reaktif; kanal
push menuntut aplikasi perangkat dan izin OS-nya. Yang dikerjakan V0 adalah bagian yang
harus ada SEBELUM satu notifikasi pun dikirim: pilihan pengguna per jenis, tersimpan, dan
SATU gerbang (`keputusan_kirim`) yang wajib dilewati pengirim mana pun kelak.

Bawaan mengikuti *privacy/attention by default* (GDPR Art. 25(2); Apple HIG & Android 13
`POST_NOTIFICATIONS`: izin diminta dalam konteks, bukan dinyalakan semua): hanya yang
pengguna jelas harapkan menyala — tinjauan mingguan (ritual §31, sekali seminggu) dan
keamanan akun. Pengingat habit menunggu jam pengingat per habit (belum ada di V0); saran
proaktif menunggu A-28.

🔒 **Keamanan akun tidak bisa dimatikan** — pemberitahuan bahwa akunmu dihapus, diekspor,
atau dimasuki dari tempat baru adalah perlindungan bagi pemiliknya sendiri (lih. GDPR Art. 34
untuk pelanggaran data), bukan pemasaran. Ia juga melewati jam tenang dan pagu harian.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import time
from types import MappingProxyType
from typing import Any, Literal

PAGU_HARIAN = 10  # naskah 11 §11.17 — `notification: send: 10/day`
JAM_TENANG_BAWAAN: tuple[str, str] | None = ("22:00", "07:00")
POLA_JAM = r"^([01][0-9]|2[0-3]):[0-5][0-9]$"

Kirim = Literal["now", "later", "silent"]


@dataclass(frozen=True)
class JenisNotifikasi:
    label: str
    bawaan: bool
    wajib: bool = False  # tidak bisa dimatikan pengguna


JENIS: Mapping[str, JenisNotifikasi] = MappingProxyType(
    {
        "habit_reminder": JenisNotifikasi("Pengingat habit", bawaan=False),
        "weekly_review": JenisNotifikasi("Tinjauan mingguan siap", bawaan=True),
        "recommendation": JenisNotifikasi("Saran baru dari asisten", bawaan=False),
        "account_security": JenisNotifikasi("Keamanan akun", bawaan=True, wajib=True),
    }
)


class PreferensiTidakSah(ValueError):
    def __init__(self, kode: str, pesan: str) -> None:
        super().__init__(pesan)
        self.kode = kode


def _jam(teks: str) -> time:
    if not re.fullmatch(POLA_JAM, teks):
        raise PreferensiTidakSah("invalid_quiet_hours", "jam wajib HH:MM (00:00–23:59)")
    return time(int(teks[:2]), int(teks[3:]))


def berlaku(tersimpan: Mapping[str, Any] | None) -> dict[str, Any]:
    """Preferensi yang BERLAKU — bawaan ditimpa yang disimpan pengguna; jenis yang tidak
    dikenal lagi diabaikan, jenis wajib selalu menyala."""
    simpan = dict(tersimpan or {})
    tersimpan_jenis = simpan.get("types")
    pilihan: dict[str, Any] = tersimpan_jenis if isinstance(tersimpan_jenis, dict) else {}
    jenis: dict[str, bool] = {}
    for k, j in JENIS.items():
        v = pilihan.get(k)
        jenis[k] = True if j.wajib else (v if isinstance(v, bool) else j.bawaan)
    tenang = simpan.get("quiet_hours", "bawaan")
    if tenang == "bawaan":
        jam_tenang = (
            {"start": JAM_TENANG_BAWAAN[0], "end": JAM_TENANG_BAWAAN[1]}
            if JAM_TENANG_BAWAAN
            else None
        )
    else:
        jam_tenang = tenang if isinstance(tenang, dict) else None
    return {"types": jenis, "quiet_hours": jam_tenang}


def gabungkan(
    tersimpan: Mapping[str, Any] | None,
    jenis: Mapping[str, bool] | None,
    jam_tenang: Mapping[str, str] | None,
    *,
    ubah_jam_tenang: bool,
) -> dict[str, Any]:
    """Bentuk tersimpan baru dari permintaan `PATCH` — HANYA pilihan pengguna, bukan bawaan,
    supaya bawaan yang kelak berubah tetap berlaku bagi yang belum pernah memilih."""
    simpan = dict(tersimpan or {})
    pilihan = dict(simpan.get("types") or {})
    for k, nyala in (jenis or {}).items():
        j = JENIS.get(k)
        if j is None:
            raise PreferensiTidakSah("unknown_notification_type", "Jenis notifikasi tak dikenal.")
        if j.wajib and not nyala:
            raise PreferensiTidakSah(
                "notification_required", "Notifikasi keamanan akun tidak bisa dimatikan."
            )
        pilihan[k] = nyala
    simpan["types"] = {k: v for k, v in pilihan.items() if k in JENIS}
    if ubah_jam_tenang:
        if jam_tenang is None:
            simpan["quiet_hours"] = None
        else:
            mulai, akhir = _jam(jam_tenang["start"]), _jam(jam_tenang["end"])
            if mulai == akhir:
                raise PreferensiTidakSah(
                    "invalid_quiet_hours", "Jam tenang mulai dan selesai tidak boleh sama."
                )
            simpan["quiet_hours"] = {"start": jam_tenang["start"], "end": jam_tenang["end"]}
    return simpan


def _dalam_jam_tenang(jam_tenang: Mapping[str, str] | None, kini: time) -> bool:
    if not jam_tenang:
        return False
    mulai, akhir = _jam(jam_tenang["start"]), _jam(jam_tenang["end"])
    if mulai < akhir:  # mis. 13:00–15:00
        return mulai <= kini < akhir
    return kini >= mulai or kini < akhir  # melintasi tengah malam, mis. 22:00–07:00


def keputusan_kirim(
    tersimpan: Mapping[str, Any] | None, jenis: str, jam_lokal: time, terkirim_hari_ini: int
) -> Kirim:
    """Gerbang yang WAJIB dilewati pengirim notifikasi mana pun (Interruption Manager §11.43,
    bagian yang tidak butuh tebakan): dimatikan → `silent`; pagu harian habis → `silent`
    (*Do nothing*, §11.44); jam tenang → `later`. Keamanan akun selalu `now`."""
    j = JENIS.get(jenis)
    if j is None:
        raise ValueError(f"jenis notifikasi tak dikenal: {jenis!r}")
    if j.wajib:
        return "now"
    pref = berlaku(tersimpan)
    if not pref["types"][jenis]:
        return "silent"
    if terkirim_hari_ini >= PAGU_HARIAN:
        return "silent"
    if _dalam_jam_tenang(pref["quiet_hours"], jam_lokal):
        return "later"
    return "now"
