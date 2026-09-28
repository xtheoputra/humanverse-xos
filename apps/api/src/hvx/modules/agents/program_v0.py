"""Program tiga agent V0 — spec/07 4.7: *tiap balasan membawa `confidence` + `rationale`*.

Tiap program hanya memegang `KonteksAgent` (4.4): data lewat tool — dengan gerbang
dan jejaknya — dan kalimat lewat AI Gateway. Penyedia model V0 merangkai BAHAN yang
disiapkan di sini dan tidak menambah satu fakta pun (K-28, arch/08 Pasal 8), jadi
yang dijaga di sini adalah bahan itu: hanya fakta yang dibaca tool, masing-masing
cukup pendek untuk menjadi `rationale` yang bisa diperiksa pengguna.

**Keyakinan V0 bukan peluang yang dikalibrasi.** Ia menyatakan seberapa banyak data
di balik sebuah jawaban (coach: jumlah sumber yang berisi) atau seberapa pasti
sebuah aksi mengenai sasarannya (habit: judul yang cocok persis atau sebagian).
Ambang untuk BERTINDAK atas keyakinan — issue #34 — milik pemilik; angka di sini
hanya dilaporkan, tidak pernah dipakai untuk memutuskan.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

from .niat import kenali
from .orkestrator import orkestrator
from .pelaksana_alat import AlatDitolak
from .runtime import Keputusan, KonteksAgent, ProgramAgent

# coach-agent: jumlah sumber berisi (habit, check-in, mood, goal, ingatan) → keyakinan.
KEYAKINAN_SUMBER = (
    Decimal("0.10"),
    Decimal("0.35"),
    Decimal("0.50"),
    Decimal("0.65"),
    Decimal("0.75"),
    Decimal("0.85"),
)
# memory-agent, mengingat kembali: 0 · 1 · ≥2 ingatan yang cocok.
KEYAKINAN_INGATAN = (Decimal("0.10"), Decimal("0.50"), Decimal("0.75"))
KEYAKINAN_JUDUL_PERSIS = Decimal("0.95")
KEYAKINAN_JUDUL_SEBAGIAN = Decimal("0.80")
KEYAKINAN_PASTI = Decimal("0.95")  # hal yang dibaca atau ditulis apa adanya
HABIT_MAKS = 5
_KATA_STATUS = {"done": "selesai", "skipped": "dilewati", "partial": "sebagian"}
INGATAN_MAKS = 3
_TUGAS_COACH = (
    "Jawab pertanyaan pengguna HANYA dari fakta berikut, dalam bahasa pengguna. "
    "Jangan menambah fakta; bila faktanya tidak cukup, katakan begitu."
)
_TUGAS_INGATAN = "Sebutkan kembali ingatan berikut apa adanya; jangan menambah apa pun."


def _baca_ditolak(galat: AlatDitolak) -> bool:
    """`deny` pengguna atas satu sumber BACAAN: sumber itu dilewati, jawaban tetap ada.
    `ask` (perlu izin) tidak dilewati — pengguna yang memintanya ditanya."""
    return galat.kode == "ditolak_pengguna"


async def _baca(k: KonteksAgent, alat: str, masukan: Mapping[str, Any]) -> dict[str, Any] | None:
    try:
        return await k.alat(alat, masukan)
    except AlatDitolak as galat:
        if _baca_ditolak(galat):
            return None
        raise


def _fakta_habit(daftar: Sequence[Mapping[str, Any]]) -> list[str]:
    fakta = []
    for h in daftar[:HABIT_MAKS]:
        hari = h.get("day") or {}
        status = _KATA_STATUS.get(hari.get("status") or "", "belum dicatat")
        kalimat = f"Habit “{h['title']}” hari ini: {status}"
        saran, tier = hari.get("suggested_tier"), h.get("tiers") or []
        if isinstance(saran, int) and 0 <= saran < len(tier) and tier[saran]:
            kalimat += f"; tier yang disarankan untuk energimu: {tier[saran]}"
        fakta.append(kalimat + ".")
    return fakta


def _fakta_checkin(c: Mapping[str, Any]) -> str:
    bagian = [
        f"energi {c['energy']}/5" if c.get("energy") is not None else None,
        f"fokus {c['focus']}/5" if c.get("focus") is not None else None,
        f"tidur {c['sleep_hours']} jam" if c.get("sleep_hours") is not None else None,
    ]
    isi = ", ".join(b for b in bagian if b) or "tanpa angka"
    return f"Check-in {c['for_date']}: {isi}."


def _fakta_mood(items: Sequence[Mapping[str, Any]]) -> str:
    rata = sum(x["valence"] for x in items) / len(items)
    terakhir = items[0]
    label = f" ({terakhir['label']})" if terakhir.get("label") else ""
    return (
        f"Mood 7 hari terakhir: {len(items)} catatan, rata-rata {rata:.1f}/5; "
        f"terakhir {terakhir['valence']}/5{label}."
    )


async def coach(k: KonteksAgent, pesan: str) -> Keputusan:
    """Jawab dari data pengguna sendiri — habit, check-in, mood, goal, dan ingatan.

    Sumber yang DITOLAK dilewati dan dinyatakan; scope ingatan yang belum diputuskan
    (*“tanya aku”*) dinyatakan juga — `memory.search` menyaringnya sendiri dan tidak
    menahan jawaban (E-193), jadi alasanlah tempat pengguna melihatnya. 🔧 E-208: dulu
    coach diam saja, dan alasannya malah berbunyi *“belum ada … ingatan yang tercatat”*.
    """
    niat = kenali(pesan)
    hari = (await k.tanggal_lokal()).isoformat()
    fakta: list[str] = []
    dilewati: list[str] = []
    sumber = 0

    habit = await _baca(k, "habit.list", {"for_date": hari})
    checkin = await _baca(k, "checkin.get", {"for_date": hari})
    mood = await _baca(k, "mood.recent", {"hari": 7})
    goal = await _baca(k, "goal.list", {"status": "active"})
    ingatan = await _baca(k, "memory.search", {"kueri": pesan, "batas": INGATAN_MAKS})

    for nama, hasil in (
        ("habit", habit),
        ("check-in", checkin),
        ("mood", mood),
        ("goal", goal),
        ("ingatan", ingatan),
    ):
        if hasil is None:
            dilewati.append(nama)
    if habit and habit["items"]:
        fakta += _fakta_habit(habit["items"])
        sumber += 1
    if checkin and checkin["checkin"]:
        fakta.append(_fakta_checkin(checkin["checkin"]))
        sumber += 1
    if mood and mood["items"]:
        fakta.append(_fakta_mood(mood["items"]))
        sumber += 1
    if goal and goal["items"]:
        judul = ", ".join(f"“{g['title']}”" for g in goal["items"][:5])
        fakta.append(f"{len(goal['items'])} goal aktif: {judul}.")
        sumber += 1
    if ingatan and ingatan["items"]:
        fakta += [f"Pernah tercatat: {x['content']}" for x in ingatan["items"]]
        sumber += 1

    jawaban = await k.model(
        tugas=_TUGAS_COACH,
        pertanyaan=pesan,
        bahan=fakta,
        kelas="reasoning" if niat.rute == "reasoning" else "simple",
    )
    # ≤ 8 fakta + 2 kalimat sumber — `rationale` paling banyak 10 (runtime.ALASAN_MAKS).
    alasan = [f[:300] for f in fakta][:8] or [
        "Belum ada habit, check-in, mood, goal, atau ingatan yang tercatat."
    ]
    if dilewati:
        alasan.append(f"Tidak dibaca karena kamu menolak aksesnya: {', '.join(dilewati)}.")
    perlu_izin = list(ingatan["perlu_izin"]) if ingatan else []
    if perlu_izin:
        alasan.append(
            f"Ingatan yang belum kamu izinkan kubaca: {', '.join(perlu_izin)} — tidak dipakai."
        )
    return Keputusan(
        jawaban.teks,
        KEYAKINAN_SUMBER[sumber],
        tuple(alasan),
        {
            "action": "reply",
            "sumber": sumber,
            "dilewati": len(dilewati),
            "perlu_izin": len(perlu_izin),
        },
    )


def _normal(teks: str) -> str:
    return " ".join(teks.lower().split())


def _cocokkan(
    daftar: Sequence[Mapping[str, Any]], sasaran: str
) -> tuple[list[Mapping[str, Any]], bool]:
    """(habit yang cocok, persis?) — judul yang sama persis menang atas yang memuatnya."""
    s = _normal(sasaran)
    persis = [h for h in daftar if _normal(h["title"]) == s]
    if persis:
        return persis, True
    return [h for h in daftar if _normal(h["title"]) in s or s in _normal(h["title"])], False


async def habit(k: KonteksAgent, pesan: str) -> Keputusan:
    """Tandai satu habit hari ini — hanya bila tepat SATU habit aktif cocok dengan yang disebut."""
    niat = kenali(pesan)
    if niat.jenis != "tandai_habit" or not niat.sasaran or niat.status is None:
        return Keputusan(
            "Sebut habit yang mau ditandai — mis. “tandai lari pagi selesai”.",
            KEYAKINAN_PASTI,
            ("Pesanmu tidak menyebut habit yang ditandai.",),
            {"action": "clarify"},
        )
    hari = (await k.tanggal_lokal()).isoformat()
    daftar = (await k.alat("habit.list", {"for_date": hari}))["items"]
    cocok, persis = _cocokkan(daftar, niat.sasaran)
    if not cocok:
        return Keputusan(
            f"Tidak ada habit aktif yang cocok dengan “{niat.sasaran}”.",
            KEYAKINAN_PASTI,
            (f"Dicari di {len(daftar)} habit aktif.",),
            {"action": "not_found", "habits": len(daftar)},
        )
    if len(cocok) > 1:
        # Menebak di antara beberapa berarti MENULIS sesuatu yang mungkin tidak dimaksud.
        pilihan = ", ".join(f"“{h['title']}”" for h in cocok[:HABIT_MAKS])
        return Keputusan(
            f"Ada {len(cocok)} habit yang cocok: {pilihan}. Yang mana?",
            KEYAKINAN_PASTI,
            (f"{len(cocok)} habit aktif cocok dengan yang kamu sebut.",),
            {"action": "clarify", "kandidat": len(cocok)},
        )
    h = cocok[0]
    tercatat = (h.get("day") or {}).get("status")
    if tercatat is None:
        hasil = await k.alat(
            "habit.complete", {"habit_id": h["id"], "for_date": hari, "status": niat.status}
        )
        tercatat = hasil["status"] if hasil["status"] != niat.status else None
    if tercatat is not None:
        # Tanggal yang sudah tercatat tidak diubah (spec/04: kirim ulang = baris lama) —
        # dan tidak ditanyakan izinnya: tidak ada yang akan ditulis. Mengaku menandai
        # yang tidak berubah adalah balasan yang bohong.
        return Keputusan(
            f"“{h['title']}” sudah tercatat {_KATA_STATUS[tercatat]} untuk {hari} — tidak diubah.",
            KEYAKINAN_PASTI,
            (
                f"Catatan {hari} untuk habit ini sudah ada.",
                "Catatan yang sudah ada diubah dengan membatalkannya lebih dulu.",
            ),
            {"action": "already_recorded", "habit_id": h["id"], "status": tercatat},
        )
    return Keputusan(
        f"“{h['title']}” ditandai {_KATA_STATUS[niat.status]} untuk {hari}.",
        KEYAKINAN_JUDUL_PERSIS if persis else KEYAKINAN_JUDUL_SEBAGIAN,
        (
            f"Judul habit “{h['title']}” {'sama dengan' if persis else 'memuat'} yang kamu sebut.",
            f"Tanggal menurut zona waktumu: {hari}.",
        ),
        {"action": "habit.complete", "habit_id": h["id"], "status": niat.status},
    )


async def memori(k: KonteksAgent, pesan: str) -> Keputusan:
    """Mengingat yang pengguna minta diingat — HANYA bila belum diingat — atau menyebutkannya.

    Memutuskan apakah sebuah memori ditulis (arch/08 §2.2): permintaan tanpa isi tidak
    ditulis, dan isi yang sudah diingat tidak melahirkan baris kedua. Karena itu
    `memory-agent` di percakapan adalah AGENT; jalur ekstraksi dari event tetap service
    (K-27).
    """
    niat = kenali(pesan)
    if niat.jenis == "ingat" and niat.sasaran:
        tulis = await k.alat("memory.write", {"scope": "coaching_notes", "isi": niat.sasaran})
        if not tulis["baru"]:
            return Keputusan(
                "Itu sudah kuingat.",
                KEYAKINAN_PASTI,
                ("Ingatan yang sama sudah ada — tidak ditulis dua kali.",),
                {"action": "already_remembered", "memory_id": tulis["id"]},
            )
        return Keputusan(
            "Baik, akan kuingat.",
            KEYAKINAN_PASTI,
            ("Kamu memintanya diingat.",),
            {"action": "memory.write", "memory_id": tulis["id"]},
        )
    if niat.jenis == "cari_ingatan":
        cari = await k.alat(
            "memory.search", {"kueri": niat.sasaran or pesan, "batas": INGATAN_MAKS}
        )
        isi = [x["content"] for x in cari["items"]]
        jawaban = await k.model(tugas=_TUGAS_INGATAN, pertanyaan=pesan, bahan=isi)
        alasan = [f"{len(isi)} ingatan yang cocok."]
        if cari["perlu_izin"]:
            alasan.append(f"Belum kamu izinkan dibaca: {', '.join(cari['perlu_izin'])}.")
        return Keputusan(
            jawaban.teks,
            KEYAKINAN_INGATAN[min(len(isi), 2)],
            tuple(alasan),
            {"action": "reply", "ingatan": len(isi)},
        )
    return Keputusan(
        "Katakan “ingat bahwa …” untuk kuingat, atau “apa yang kamu ingat tentang …”.",
        KEYAKINAN_PASTI,
        ("Pesanmu bukan permintaan mengingat atau mengingat kembali.",),
        {"action": "clarify"},
    )


# Satu program per agent aktif di registry — `hvx.main` merakitnya (4.8).
PROGRAM_V0: Mapping[str, ProgramAgent] = {
    "orchestrator-agent": orkestrator,
    "coach-agent": coach,
    "habit-agent": habit,
    "memory-agent": memori,
}
