"""`orchestrator-agent` — spec/07 4.6: *`parent_run_id` membentuk pohon eksekusi*.

Satu keputusan per giliran: agent mana yang menangani pesan ini. Pilihannya
dari niat (aturan, bukan model — memanggil model untuk memutuskan apakah perlu
model menggagalkan tujuannya, naskah 4 §48), dan pemanggilannya adalah TOOL
`kind: agent` (K-14): lewat pelaksana, batas laju, dan gerbang yang sama dengan
tool lain, dan run agent yang dipanggil menjadi ANAK run ini (`parent_run_id`,
`trigger='agent'`). Satu permintaan pengguna = satu pohon yang bisa ditelusuri
dari akarnya.

Orchestrator tidak menambah apa pun pada balasan anaknya: keyakinan dan alasan
yang sampai ke pengguna adalah milik agent yang menjawab, bukan dikarang ulang.
Perintah `deterministic` (*“catat mood 3”*) tidak pernah sampai ke sini — lapisan
percakapan menjalankannya tanpa agent dan tanpa model (4.1).
"""

from __future__ import annotations

from decimal import Decimal

from .niat import JenisNiat, kenali
from .runtime import Keputusan, KonteksAgent

# Niat → tool `kind: agent` yang menanganinya (manifest orchestrator-agent, spec/05).
AGENT_UNTUK: dict[JenisNiat, str] = {
    "tandai_habit": "agent.habit",
    "ingat": "agent.memory",
    "cari_ingatan": "agent.memory",
    "tanya": "agent.coach",
}


async def orkestrator(k: KonteksAgent, pesan: str) -> Keputusan:
    niat = kenali(pesan)
    alat = AGENT_UNTUK.get(niat.jenis)
    if alat is None:  # catat_mood · catat_mood_salah — jalurnya tanpa agent (4.1)
        raise ValueError(f"niat {niat.jenis} tidak dijalankan agent")
    balasan = await k.alat(alat, {"pesan": pesan})
    return Keputusan(
        balasan["teks"],
        Decimal(str(balasan["confidence"])),
        tuple(balasan["rationale"]),
        {"action": "delegate", "agent": alat.removeprefix("agent.") + "-agent"},
    )
