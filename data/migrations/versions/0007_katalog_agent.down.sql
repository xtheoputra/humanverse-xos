-- Migrasi 0007 turun — katalog agent V0 dikosongkan (agent_tools ikut, ON DELETE CASCADE).
DELETE FROM agents WHERE id IN (
  'b339c963-8482-5ba6-9013-108a01f08833',
  '2bfa7069-9aa5-5d64-a31f-de60531e27d9',
  '334f6466-344a-54e0-a5e9-9dc57918c240',
  '149486a2-334a-5f43-a6e7-2ba52885ac83'
);
