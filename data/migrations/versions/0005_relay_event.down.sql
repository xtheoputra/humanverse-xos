-- Migrasi 0005 turun. Peran `hvx_pekerja` SENGAJA tidak dilepas: peran berlaku
-- sekluster, dan basis data lain di klaster yang sama bisa sedang memakainya.
DROP FUNCTION events_untuk_relay(timestamptz, uuid, integer);
