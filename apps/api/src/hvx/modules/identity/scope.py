"""Daftar scope resmi V0 — spec/05 aturan 2 (E-180, spec/07 3.7).

Scope menjawab **siapa** boleh membaca sebuah data milik pengguna
(`permissions.scope`, `memories.scope`); `kind` memori menjawab **bagaimana** ia
diambil (spec/01 §5, issue #33). spec/05 aturan 2 merujuk *“daftar scope
resmi”* sejak Sprint 0 — tetapi daftarnya tidak pernah ditulis di mana pun,
sehingga tidak satu penegak pun bisa memeriksanya. Satu daftar, tiga penegak:

* mesin izin (1.5) — keputusan atas scope di luar daftar DITOLAK, bukan disimpan
  sebagai baris yang tidak pernah ditanyakan siapa pun;
* pencarian memori (3.7) — scope manifest di luar daftar ditolak;
* registry agent (4.2) — manifest yang meminta scope di luar daftar ditolak.

🔒 **Scope SENSITIF tidak pernah `allow` karena bawaan** — hanya karena
keputusan `allow` yang disimpan pengguna sendiri (`MesinIzin.cek`). Naskah 5
§15 menaruh *private journal* di daftar *“tidak boleh otomatis”*, bahkan untuk
agent yang bekerja di atasnya.

Scope baru masuk lewat spec/05 dulu, lalu di sini — di PR yang sama.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Scope:
    isi: str
    sensitif: bool


SCOPE_RESMI: Mapping[str, Scope] = MappingProxyType(
    {
        "habits": Scope("habit dan penyelesaiannya", sensitif=False),
        "goals": Scope("goal dan milestone", sensitif=False),
        "checkins": Scope("check-in harian: energi, fokus, jam tidur", sensitif=False),
        "mood": Scope("mood yang dilaporkan, dan memori episodiknya (3.6)", sensitif=False),
        "coaching_notes": Scope(
            "catatan coaching: ditulis coach-agent, atau diminta pengguna untuk diingat",
            sensitif=False,
        ),
        "journal_raw": Scope("isi jurnal apa adanya, dan memori episodiknya (3.6)", sensitif=True),
    }
)
