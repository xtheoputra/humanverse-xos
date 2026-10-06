-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0012 — set_updated_at() naik KETAT per baris (E-223)
--
-- `now()` adalah awal TRANSAKSI, bukan saat baris ditulis. Akibatnya dua versi
-- baris yang isinya berbeda bisa mendapat `updated_at` yang SAMA persis: dua UPDATE
-- dalam satu transaksi, atau dua transaksi serentak yang mulai di mikrodetik yang
-- sama (diukur di tumpukan lokal: 175 dari 400 percobaan, lima transaksi serentak,
-- punya sedikitnya dua `now()` kembar). Sebaliknya transaksi yang MULAI lebih awal
-- tetapi menulis belakangan memundurkan `updated_at` baris itu.
--
-- Itu bukan soal kosmetik: kunci event `checkin.logged` adalah
-- `checkin:<tanggal>:<updated_at>` — identitas VERSI baris. Dua versi berbeda dengan
-- kunci yang sama → `EventTidakSah` → `PUT /checkins/{tanggal}` serentak menjawab 500
-- (gerbang penuh 6 Okt 2026, test_put_serentak_tanggal_sama_satu_baris).
--
-- Perbaikan di sumbernya: tiap UPDATE menaikkan `updated_at` paling sedikit 1 µs di
-- atas nilai lamanya. Pembaruan satu baris selalu berurutan (kunci baris), jadi nilai
-- itu tak pernah kembar dan tak pernah mundur — tanpa kolom baru. Berlaku untuk
-- semua tabel ber-`updated_at` (pemicunya satu fungsi). Komentar di LUAR badan fungsi:
-- uji kesetaraan membandingkan `pg_get_functiondef` dengan spec/01 apa adanya.
-- ════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = GREATEST(now(), OLD.updated_at + interval '1 microsecond');
  RETURN NEW;
END $$ LANGUAGE plpgsql;
