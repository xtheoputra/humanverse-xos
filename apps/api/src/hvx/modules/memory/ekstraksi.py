"""Ekstraksi memori dari jurnal & mood — spec/07 3.6.

Selesai bila: *tiap memori punya `kind`, `scope`, `confidence`, `evidence_count`,
`source_event_id`.*

Konsumen stream `memori` (spec/03 *Consumer V0*: **Memory extractor** —
`journal.created`, `mood.logged`, boleh gagal & diulang). Penangannya berjalan
di transaksi pemilik event (`events.KonsumenStream`), jadi memori dan
pembacaan sumbernya commit bersama, di bawah RLS.

* **Isi sumber dibaca dari modul pemiliknya**, bukan dari event: isi jurnal
  sengaja tidak pernah masuk event (spec/03), `note` mood juga tidak.
  `memory` berada di atas modul domain (K-17), jadi boleh mengimpornya.
* **Idempoten** — id memori diturunkan dari (jenis event, subjek, kind):
  event yang diserahkan lagi menabrak baris yang sudah ada dan tidak menulis
  apa pun. Pendengar jurnal menemukan memorinya dengan rumus yang sama.
* **Episodik, bukan kesimpulan.** Tanpa model bahasa (penyedianya milik
  pemilik, arch/05 §6), V0 hanya mencatat APA YANG DILAPORKAN atau DITULIS
  pengguna, kapan — `kind='episodic'` (naskah 15: *Episodic = kejadian*).
  Memori TURUNAN (fakta, preferensi — `semantic`, `preference`) menyusul
  bersama AI Gateway (4.1) dan membawa keyakinannya sendiri.
* **Keyakinan 1.000, bukti 1 (K-27).** Yang diyakini memori episodik adalah
  BAHWA pengguna melaporkan atau menulisnya — bukan bahwa isinya benar tentang
  dirinya (mood *dilaporkan*, bukan ditaksir: spec/01 E-34). Ambang keyakinan
  untuk BERTINDAK tetap milik pemilik (#34).
* **Scope** menentukan siapa boleh membacanya (`identity.SCOPE_RESMI`): mood →
  `mood`; jurnal → `journal_raw`, scope SENSITIF yang tidak pernah terbuka
  karena bawaan (naskah 5 §15: *private journal* tidak boleh otomatis).
* **Vektor bukan urusan ekstraksi** — memori lahir dengan `embedding_model`
  NULL, dan `PenyelarasVektor` menyematnya sesudah commit. Ekstraksi tidak
  pernah gagal karena Qdrant. `model_version` mencatat CARA memori ini lahir
  (`VERSI_EKSTRAKSI`), bukan penyematnya.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid5

from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import checkins, events, journal

from . import repository

JENIS_EVENT = frozenset({"journal.created", "mood.logged"})
KEYAKINAN_LAPORAN_SENDIRI = Decimal("1.000")
BUKTI_SATU_KEJADIAN = 1
# `memories.model_version` — cara memori ini dan keyakinannya dihasilkan (tempat
# ambang #34, arch/README). Naik bila aturan ekstraksi episodik berubah.
VERSI_EKSTRAKSI = "hvx-episodik-v1"
# Ruang nama uuid5 id memori — TETAP selamanya: mengubahnya membuat event lama
# melahirkan memori kembar saat diproses ulang.
_RUANG_ID_MEMORI = UUID("58904fe6-22dc-41df-a02a-54f192720a00")


def id_memori(event_type: str, subjek_id: UUID, kind: str) -> UUID:
    return uuid5(_RUANG_ID_MEMORI, f"{event_type}:{subjek_id}:{kind}")


def teks_mood(mood: checkins.Mood) -> str:
    teks = f"Mood dilaporkan {mood.valence}/5"
    if mood.label:
        teks += f" ({mood.label})"
    if mood.note:
        teks += f": {mood.note}"
    return teks


def teks_jurnal(jurnal: journal.Jurnal) -> str:
    return f"{jurnal.title}\n\n{jurnal.body}" if jurnal.title else jurnal.body


async def ekstrak(conn: AsyncConnection, ev: events.EventMasuk) -> None:
    """Penangan konsumen `memori` — satu event → paling banyak satu memori episodik."""
    if ev.subject_id is None:
        # Kontrak kedua event ini selalu bersubjek (3.2). Galat, bukan dilewati:
        # event yang tidak bisa diekstrak harus berakhir terlihat di stream mati.
        raise ValueError(f"{ev.event_type} tanpa subject_id — tidak ada yang bisa diekstrak")
    if ev.event_type == "mood.logged":
        mood = await checkins.mood_untuk_ekstraksi(conn, ev.subject_id)
        if mood is None:
            return
        isi, scope, sejak = teks_mood(mood), "mood", mood.occurred_at
    elif ev.event_type == "journal.created":
        jurnal = await journal.isi_untuk_ekstraksi(conn, ev.subject_id)
        if jurnal is None:
            return  # dihapus sebelum diekstrak — tidak ada yang boleh diingat
        isi, scope, sejak = teks_jurnal(jurnal), "journal_raw", jurnal.occurred_at
    else:
        raise ValueError(f"ekstraktor memori tidak menangani {ev.event_type}")
    await repository.sisip(
        conn,
        id_=id_memori(ev.event_type, ev.subject_id, "episodic"),
        user_id=ev.user_id,
        kind="episodic",
        scope=scope,
        content=isi,
        confidence=KEYAKINAN_LAPORAN_SENDIRI,
        evidence_count=BUKTI_SATU_KEJADIAN,
        model_version=VERSI_EKSTRAKSI,
        source_event_id=ev.id,
        valid_from=sejak,
    )


async def selaraskan_jurnal(conn: AsyncConnection, jurnal_id: UUID) -> None:
    """Pendengar `journal` (K-23): jurnal diubah → memorinya mengikuti; dihapus →
    isinya dikosongkan SEKARANG, di transaksi penghapusnya. Titik vektornya dibuang
    atau disemat ulang penyelaras sesudah commit — naskah: *“tidak boleh hanya
    menghapus row di PostgreSQL”* (docs/139)."""
    mid = id_memori("journal.created", jurnal_id, "episodic")
    jurnal = await journal.isi_untuk_ekstraksi(conn, jurnal_id)
    if jurnal is None:
        await repository.lupakan(conn, mid)
    else:
        await repository.ganti_isi(conn, mid, teks_jurnal(jurnal), jurnal.occurred_at)
