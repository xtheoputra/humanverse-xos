"""Implementasi 9 tool V0 + 3 entri `kind: agent` — spec/05 *Tool registry*, spec/07 4.3.

Tiap tool memanggil PINTU KELUAR modul pemilik datanya — layanan yang sama dengan rute
HTTP-nya, di bawah RLS pengguna yang dilayani run itu. Tidak ada SQL di sini, dan
tidak ada jalan pintas: `habit.complete` menerbitkan `habit.completed`-nya sendiri,
persis seperti `POST /habits/{id}/completions`.

Yang sengaja TIDAK dikembalikan: catatan bebas check-in dan mood (`note`) — coach
membaca angka dan label, bukan tulisan pengguna (C-32, spec/05 kolom *Scope*). Skema
`output` tiap tool menjaganya: medan yang tidak dinyatakan adalah cacat
(`pelaksana_alat.periksa_keluaran`).

Scope yang benar-benar disentuh dicatat ke run (`agent_runs.memory_scopes`, 4.4) oleh
tiap implementasi — untuk `memory.search` itu scope yang DIIZINKAN, bukan yang diminta.

🔧 Tiga tool TULIS (`habit.complete` · `memory.write` · `recommendation.create`):
**pemeriksa** pemilik datanya dijalankan pelaksana sebelum gerbang (E-204), dan
tulisannya meninggalkan `audit_logs` `agent.tool_executed` di transaksi tulisan itu
(`KonteksAlat.jejak`, E-205); event `habit.completed` yang lahir dari agent bersumber
`agent` (spec/03), bukan `app`.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from hvx.modules import checkins, goals, habits, intelligence, memory, profile

from .pelaksana_alat import AlatDitolak, AlatGagal, Implementasi, ImplementasiAlat, KonteksAlat

# Batas NILAI masukan ada di skema tool (`alat/*.yaml`, enum/min/max) — pelaksana
# menolaknya sebelum gerbang; yang di sini hanya ukuran jawaban.
GOAL_MAKS = 100  # `terpotong` bila pengguna punya lebih (≤ goals.MAKS_GOAL)
MOOD_HARI_BAWAAN = 7
MOOD_MAKS = 50


async def _habit_list(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("habits")
    daftar = await habits.daftar_habit(
        k.engine,
        k.jalannya.user_id,
        status="active",
        for_date=m.get("for_date"),
        pembaca_energi=checkins.energi_pada,
    )
    items = []
    for h in daftar.items:
        item: dict[str, Any] = {
            "id": str(h.id),
            "title": h.title,
            "period": h.period,
            "target_count": h.target_count,
            "tiers": [t.get("label") for t in h.adaptive_tiers],
        }
        if h.day is not None:
            item["day"] = {
                "for_date": h.day.for_date.isoformat(),
                "status": h.day.completion.status if h.day.completion else None,
                "suggested_tier": h.day.suggested_tier,
                "energy": h.day.energy,
            }
        items.append(item)
    return {"items": items}


async def _habit_streak(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("habits")
    r = await habits.rentetan_habit(
        k.engine, k.jalannya.user_id, m["habit_id"], pembaca_zona_waktu=profile.zona_waktu
    )
    return {
        "current": r.current,
        "longest": r.longest,
        "completion_rate_30d": r.completion_rate_30d,
    }


def _badan_penyelesaian(m: dict[str, Any]) -> habits.CatatPenyelesaian:
    """Skema `POST /habits/{id}/completions` yang sama — `ValueError` bila ditolaknya."""
    return habits.CatatPenyelesaian(
        for_date=m["for_date"], status=m["status"], tier_used=m.get("tier_used")
    )


def _periksa_habit_complete(m: dict[str, Any]) -> None:
    _badan_penyelesaian(m)


async def _habit_complete(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("habits")
    try:
        badan = _badan_penyelesaian(m)
    except ValueError:
        raise AlatDitolak("masukan_salah", "habit.complete: status atau tier tidak sah") from None
    hasil = await habits.catat_penyelesaian(
        k.engine, k.jalannya.user_id, m["habit_id"], badan, sumber="agent", jejak=k.jejak
    )
    return {"id": str(hasil.penyelesaian.id), "status": hasil.penyelesaian.status}


async def _goal_list(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("goals")
    halaman = await goals.daftar_goal(
        k.engine, k.jalannya.user_id, status=m.get("status"), batas=GOAL_MAKS, kursor=None
    )
    return {  # daftar yang dipotong diam-diam adalah jawaban yang salah (K-24)
        "terpotong": halaman.next_cursor is not None,
        "items": [
            {
                "id": str(g.id),
                "title": g.title,
                "status": g.status,
                "domain": g.domain,
                "target_date": g.target_date.isoformat() if g.target_date else None,
            }
            for g in halaman.items
        ],
    }


async def _checkin_get(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("checkins")
    tanggal: date = m["for_date"]
    daftar = await checkins.daftar_checkin(
        k.engine, k.jalannya.user_id, dari=tanggal, sampai=tanggal
    )
    if not daftar.items:
        return {"checkin": None}
    c = daftar.items[0]
    return {  # tanpa `note` — tulisan pengguna bukan bahan coach (C-32)
        "checkin": {
            "for_date": c.for_date.isoformat(),
            "energy": c.energy,
            "focus": c.focus,
            "sleep_hours": c.sleep_hours,
        }
    }


async def _mood_recent(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("mood")
    hari = m.get("hari", MOOD_HARI_BAWAAN)
    halaman = await checkins.daftar_mood(
        k.engine,
        k.jalannya.user_id,
        dari=datetime.now(UTC) - timedelta(days=hari),
        sampai=None,
        batas=MOOD_MAKS,
        kursor=None,
    )
    return {  # tanpa `note` (C-32)
        "terpotong": halaman.next_cursor is not None,
        "items": [
            {"valence": x.valence, "label": x.label, "occurred_at": x.occurred_at.isoformat()}
            for x in halaman.items
        ],
    }


async def _memory_search(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    pencari = k.layanan.pencari_memori
    if pencari is None:  # tanpa Qdrant (HVX_QDRANT_URL kosong): tidak ada yang bisa dicari
        return {"items": [], "perlu_izin": []}
    try:
        hasil = await pencari.cari(
            user_id=k.jalannya.user_id,
            agent=k.jalannya.agent.name,
            scope_manifest=k.jalannya.agent.memory.read,
            kueri=m["kueri"],
            batas=m.get("batas", 5),
        )
    except ValueError:
        raise AlatDitolak("masukan_salah", "memory.search: kueri atau batas tidak sah") from None
    k.jalannya.catat_scope(*hasil.scope_dipakai)
    return {
        "items": [
            {
                "id": str(h.memori.id),
                "kind": h.memori.kind,
                "scope": h.memori.scope,
                "content": h.memori.content,
                "skor": h.skor,
            }
            for h in hasil.items
        ],
        "perlu_izin": list(hasil.perlu_izin),
    }


def _periksa_memory_write(m: dict[str, Any]) -> None:
    memory.periksa_ingatan(scope=m["scope"], isi=m["isi"])


async def _memory_write(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    agent = k.jalannya.agent  # scope-nya sudah di pagu manifest (pelaksana, sebelum gerbang)
    k.jalannya.catat_scope(m["scope"])
    try:
        hasil = await memory.ingat(
            k.engine,
            k.jalannya.user_id,
            scope=m["scope"],
            isi=m["isi"],
            penulis=f"{agent.name}@{agent.version}",
            jejak=k.jejak,
        )
    except ValueError:
        raise AlatDitolak("masukan_salah", "memory.write: isi atau scope tidak sah") from None
    return {"id": str(hasil.id), "baru": hasil.baru}


def _isi_rekomendasi(m: dict[str, Any]) -> dict[str, Any]:
    return {
        "domain": m["domain"],
        "title": m["title"],
        "body": m.get("body"),
        "confidence": Decimal(str(m["confidence"])),
        "rationale": m["rationale"],
    }


def _periksa_recommendation_create(m: dict[str, Any]) -> None:
    intelligence.periksa_rekomendasi(**_isi_rekomendasi(m))


async def _recommendation_create(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
    k.jalannya.catat_scope("coaching_notes")
    try:
        rid = await intelligence.buat_rekomendasi(
            k.engine,
            k.jalannya.user_id,
            agent_id=k.jalannya.agent.id_katalog,
            agent_run_id=k.jalannya.id if k.jalannya.tersimpan else None,
            jejak=k.jejak,
            **_isi_rekomendasi(m),
        )
    except ValueError:
        raise AlatDitolak("masukan_salah", "recommendation.create: isi tidak sah") from None
    return {"id": str(rid)}


def _agent(nama: str) -> ImplementasiAlat:
    async def panggil(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
        pelaksana = k.layanan.pelaksana_agent
        if pelaksana is None:
            raise AlatGagal("agent_unavailable", f"{nama} tidak bisa dipanggil di sini")
        return await pelaksana(nama, m["pesan"], k.jalannya)

    return panggil


IMPLEMENTASI: dict[str, ImplementasiAlat] = {
    "habit.list": _habit_list,
    "habit.streak": _habit_streak,
    "habit.complete": Implementasi(_habit_complete, _periksa_habit_complete),
    "goal.list": _goal_list,
    "checkin.get": _checkin_get,
    "mood.recent": _mood_recent,
    "memory.search": _memory_search,
    "memory.write": Implementasi(_memory_write, _periksa_memory_write),
    "recommendation.create": Implementasi(_recommendation_create, _periksa_recommendation_create),
    "agent.coach": _agent("coach-agent"),
    "agent.habit": _agent("habit-agent"),
    "agent.memory": _agent("memory-agent"),
}
