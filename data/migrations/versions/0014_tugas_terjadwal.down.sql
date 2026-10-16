-- Migrasi 0014 turun — tugas terjadwal (spec/08 7.3).
DROP FUNCTION tugas_jatuh_tempo(text, integer, integer);
DROP TABLE scheduled_runs;
