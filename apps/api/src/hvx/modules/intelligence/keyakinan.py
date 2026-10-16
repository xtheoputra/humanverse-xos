"""Confidence Layer — spec/07 5.4 (issue #34): kapan sistem MENYATAKAN, kapan BERTANYA.

Satu aturan, dipakai di mana pun sebuah kesimpulan tentang pengguna akan keluar
sebagai teks: **tanpa bukti, sistem bertanya — tidak menebak.** spec/01 §6
menuliskannya untuk memori (*“`evidence_count = 0` berarti sistem bertanya, bukan
menebak”*), dan itu sekaligus jawaban *cold start* (**B-1**, naskah): pengguna
hari pertama tidak punya riwayat, maka yang jujur adalah menanyainya, bukan
mengarang keadaan.

🛑 **AMBANG High/Medium/Low DI ATAS nol bukan milik agent.** docs/163 §9.33 dan
butir H-14 / [#34](../../issues/34) menanyakannya sejak naskah kelima; jawaban
audit (docs/99) tetap: *butuh data nyata — menebak lebih buruk daripada
membiarkannya terbuka.* Jadi V0 menetapkan **satu** batas saja, yang tidak
butuh data untuk dibenarkan: nol bukti tidak boleh menjadi pernyataan. Pita
0,50/0,75 menunggu pemilik; `confidence` di sini tidak dipakai untuk memutuskan
sikap — hanya `evidence_count`, karena `confidence` V0 belum terkalibrasi
(arch/08, `program_v0`).

Pengguna aturan ini:

* **coach-agent** (`agents.program_v0`) — giliran penalaran dengan NOL sumber
  berisi tidak dijawab dengan kesimpulan kosong; ia bertanya.
* **pola** (5.2) & **keadaan** (5.3) menegakkan batas yang sama di sisi TULIS:
  tak satu pun menulis baris ber-`evidence_count` nol — pola yang kehilangan
  dasarnya diluruhkan, human_state tanpa metrik tidak dibuat. Jadi sebuah baris
  yang ADA selalu sudah lolos `cukup_untuk_menyatakan`; yang nol muncul sebagai
  KETIADAAN baris, dan di situlah pembacanya bertanya.
"""

from __future__ import annotations

from enum import Enum

# Satu-satunya ambang V0. Di bawah ini: BERTANYA. Pita di atasnya milik pemilik (#34).
BUKTI_MINIMUM = 1


class Sikap(Enum):
    """Cara sebuah taksiran boleh keluar ke pengguna."""

    MENYATAKAN = "state"  # boleh keluar sebagai kesimpulan
    BERTANYA = "ask"  # bukti belum cukup — tanyakan, jangan tebak


def sikap(evidence_count: int) -> Sikap:
    """Sikap untuk sejumlah bukti. Nol (atau negatif, yang mustahil) → BERTANYA."""
    return Sikap.MENYATAKAN if evidence_count >= BUKTI_MINIMUM else Sikap.BERTANYA


def cukup_untuk_menyatakan(evidence_count: int) -> bool:
    """`True` bila bukti cukup untuk MENYATAKAN kesimpulan; `False` → sistem bertanya."""
    return sikap(evidence_count) is Sikap.MENYATAKAN
