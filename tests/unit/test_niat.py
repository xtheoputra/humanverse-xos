"""spec/07 4.1 — pengenal niat: *“catat mood” tidak memanggil model besar*.

Naskah 5 §22: *“Catat mood saya” → deterministic* — `INSERT`, bukan inferensi.
Rute diputuskan dari teksnya saja, sebelum model mana pun disentuh.
"""

from __future__ import annotations

import pytest

from hvx.modules.agents import kenali


@pytest.mark.parametrize(
    ("teks", "valensi", "label", "catatan"),
    [
        ("catat mood 3", 3, None, None),
        ("Catat mood saya: 2 cemas", 2, "cemas", None),
        ("log mood 4/5 lega, habis lari pagi", 4, "lega", "habis lari pagi"),
        ("catat mood hari ini 1 — rapat seharian", 1, None, "rapat seharian"),
        # Kata sesudah valensi tidak ditebak artinya: disimpan apa adanya.
        ("catat mood 2 cemas banget hari ini", 2, None, "cemas banget hari ini"),
    ],
)
def test_perintah_mood_dirutekan_deterministik_tanpa_model(
    teks: str, valensi: int, label: str | None, catatan: str | None
) -> None:
    niat = kenali(teks)

    assert niat.rute == "deterministic", f"“{teks}” dirutekan ke model {niat.rute}"
    assert niat.jenis == "catat_mood"
    assert niat.mood is not None
    assert (niat.mood.valensi, niat.mood.label, niat.mood.catatan) == (valensi, label, catatan)


@pytest.mark.parametrize(
    "teks", ["catat mood", "catat mood 7", "catat mood 3.5", "catat mood 34", "catat mood tiga"]
)
def test_perintah_mood_tanpa_valensi_utuh_dijawab_bukan_ditebak(teks: str) -> None:
    """Perintahnya jelas, angkanya tidak: tetap tanpa model — dan tidak menebak angka."""
    niat = kenali(teks)

    assert (niat.rute, niat.jenis, niat.mood) == ("deterministic", "catat_mood_salah", None), (
        f"“{teks}” ditebak: {niat}"
    )


@pytest.mark.parametrize(
    "teks",
    [
        "aku mau catat mood nanti",
        "mood saya jelek hari ini",
        "kapan terakhir aku catat mood 3?",
        "tolong jangan catat mood 3",
        # Tanpa kata perintah = bercerita (E-198) — dulu tercatat sebagai mood BARU saat
        # ini: valensi 3, catatan "hari lalu buruk sekali".
        "mood 5",
        "mood 3 hari lalu buruk sekali",
        "mood 2 minggu terakhir jelek",
    ],
)
def test_yang_bukan_perintah_tidak_dijalankan(teks: str) -> None:
    """Salah rute ke `deterministic` BERTINDAK atas teks yang tidak dimaksudkan."""
    assert kenali(teks).rute != "deterministic", f"“{teks}” dijalankan sebagai perintah"


@pytest.mark.parametrize(
    "teks",
    [
        "analisis pola kebiasaan saya",  # naskah 5 §22 — contoh rute reasoning
        "kenapa aku capek terus minggu ini?",
        "Why do I keep skipping workouts?",
        "bagaimana cara supaya aku konsisten lari pagi",
        " ".join(["kata"] * 40),
    ],
)
def test_permintaan_analisis_ke_model_besar(teks: str) -> None:
    assert kenali(teks).rute == "reasoning"


@pytest.mark.parametrize("teks", ["halo", "habit apa hari ini?", "terima kasih"])
def test_selainnya_model_kecil(teks: str) -> None:
    assert kenali(teks).rute == "simple"


@pytest.mark.parametrize(
    ("teks", "jenis", "sasaran", "status"),
    [
        ("tandai lari pagi selesai", "tandai_habit", "lari pagi", "done"),
        ("centang meditasi", "tandai_habit", "meditasi", "done"),
        ("Tolong tandai Baca 10 halaman sudah selesai.", "tandai_habit", "Baca 10 halaman", "done"),
        ("lewati lari hari ini", "tandai_habit", "lari", "skipped"),
        ("tandai lari dilewati", "tandai_habit", "lari", "skipped"),
        ("ingat bahwa aku alergi kacang", "ingat", "aku alergi kacang", None),
        ("tolong ingat, aku vegetarian", "ingat", "aku vegetarian", None),
        ("apa yang kamu ingat tentang tidurku?", "cari_ingatan", "tidurku", None),
        ("apa yang kamu tahu", "cari_ingatan", None, None),
    ],
)
def test_niat_memilih_agent(teks: str, jenis: str, sasaran: str | None, status: str | None) -> None:
    """4.6 — orchestrator memilih agent dari niat; tanpa model."""
    niat = kenali(teks)

    assert (niat.rute, niat.jenis, niat.sasaran, niat.status) == (
        "simple",
        jenis,
        sasaran,
        status,
    ), f"“{teks}” dibaca {niat}"


@pytest.mark.parametrize(
    "teks",
    [
        "ingatkan aku minum obat jam 7",  # minta DIINGATKAN — bukan minta diingat
        "aku mau tandai lari nanti",  # bukan diawali kata perintahnya
        "kenapa aku selalu lewati lari?",
        "tandai",
    ],
)
def test_yang_bukan_perintah_agent_ke_coach(teks: str) -> None:
    """Salah rute ke habit-agent atau memory-agent MENULIS sesuatu yang tidak diminta."""
    assert kenali(teks).jenis == "tanya", f"“{teks}” dijalankan sebagai perintah agent"


# ── E-197: pengenal niat linear — satu pesan sah tidak membekukan event loop ─────────
# Tiap pesan di bawah SAH menurut `POST /conversations/{id}/messages` (≤ 4.000 karakter)
# dan dulu membuat pola perintah menelusur mundur: deretan spasi atau titik di antara
# dua kata. `kenali` dipanggil sinkron di event loop (percakapan · orchestrator ·
# program agent) — satu pesan 75 detik membekukan seluruh proses api untuk SEMUA pengguna.
PESAN_JAHAT = {
    "spasi_tandai": "tandai x" + " " * 3991 + "y",
    "spasi_selesai": "tandai " + "x " * 1992 + "selesaiy",
    "titik_tandai": "tandai x" + "." * 3991 + "y",
    "spasi_cari_ingatan": "apa yang kamu ingat tentang x" + " " * 3960 + "y",
    "tanya_cari_ingatan": "apa yang kamu ingat tentang x" + "?" * 3960 + "y",
    "spasi_ingat": "ingat" + " " * 3994 + ",",
    "spasi_mood": "catat mood 3" + " " * 3987 + "x",
    "label_mood": "catat mood 3 " + "a" * 50 + " " * 3936 + "b",
}
BATAS_S = 5.0
KODE_ANAK = (
    "import sys, json\n"
    "from hvx.modules.agents import kenali\n"
    "pesan = json.loads(sys.stdin.read())\n"
    "print('siap', flush=True)\n"
    "sys.stdin.close()\n"
    "for teks in pesan: kenali(teks)\n"
    "print('selesai', flush=True)\n"
)


def test_pengenal_niat_linear_atas_pesan_terpanjang_yang_sah() -> None:
    """Proses anak: regex memegang GIL — pola yang menggantung tidak bisa dihentikan dari
    utas, dan uji yang menggantung menahan gerbang. Waktu impor tidak ikut dihitung."""
    import json
    import subprocess
    import sys
    import time

    from hvx.modules.agents.schemas import KirimPesan

    for teks in PESAN_JAHAT.values():
        assert len(teks) <= 4000
        KirimPesan(content=teks)  # lolos skema rute — terjangkau pengguna mana pun
    anak = subprocess.Popen(  # noqa: S603 - interpreter uji sendiri, argumen tetap
        [sys.executable, "-c", "import sys; exec(sys.argv[1])", KODE_ANAK],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        assert anak.stdin is not None
        assert anak.stdout is not None
        anak.stdin.write(json.dumps(list(PESAN_JAHAT.values())))
        anak.stdin.close()
        assert anak.stdout.readline().strip() == "siap"
        mulai = time.perf_counter()
        try:
            anak.wait(timeout=BATAS_S)
        except subprocess.TimeoutExpired:
            pytest.fail(
                f"kenali() atas {len(PESAN_JAHAT)} pesan sah belum selesai sesudah {BATAS_S} "
                "dtk — pola perintah menelusur mundur (E-197): satu POST membekukan proses api"
            )
        assert anak.returncode == 0, "proses anak gagal"
        assert time.perf_counter() - mulai < BATAS_S
    finally:
        anak.kill()
        anak.wait()
        if anak.stdout is not None:
            anak.stdout.close()


def test_pesan_jahat_tetap_dibaca_sama_dengan_bentuk_rapinya() -> None:
    """Merapatkan spasi tidak mengubah ARTI: niatnya sama dengan pesan yang sudah rapi."""
    diubah = "spasi atau tanda baca penutup mengubah niat pesannya"
    assert kenali("tandai   lari\n pagi   selesai . !").sasaran == "lari pagi", diubah
    assert kenali("apa yang kamu ingat tentang   tidur   ku ??").sasaran == "tidur ku", diubah
    assert kenali("ingat   bahwa aku\nalergi kacang.").sasaran == "aku alergi kacang", diubah
    catatan = kenali("catat mood 2 — rapat\n\nseharian").mood
    assert catatan is not None
    assert catatan.catatan == "rapat\n\nseharian", (
        "catatan mood adalah tulisan pengguna — dibaca dari teks aslinya, tidak dirapatkan"
    )
