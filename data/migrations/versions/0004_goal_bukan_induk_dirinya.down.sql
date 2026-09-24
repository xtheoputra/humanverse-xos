-- Migrasi 0004 turun.
ALTER TABLE goals DROP CONSTRAINT goals_parent_not_self;
