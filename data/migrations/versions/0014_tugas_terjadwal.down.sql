-- Migrasi 0014 turun — tugas terjadwal (spec/08 7.3).
DROP FUNCTION tugas_jatuh_tempo(text, integer, integer, date, uuid);
DROP TABLE scheduled_runs;
