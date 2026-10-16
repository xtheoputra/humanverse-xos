-- ════════════════════════════════════════════════════════════════════
-- Migrasi 0007 — katalog agent V0: agents + agent_tools
-- spec/07 4.2 · spec/05 *Empat agent V0* · spec/01 §8 · K-29
--
-- Katalog sistem DIKELOLA MIGRASI (spec/01 §10: hvx_app hanya SELECT): api tidak
-- bisa mendaftarkan atau mengubah agent. Isinya salinan beku manifest di
-- `apps/api/src/hvx/modules/agents/manifest/` — api membandingkannya saat mulai
-- (`agents.pastikan_katalog`) dan MENOLAK MULAI bila berbeda. Manifest yang
-- berubah = versi baru + migrasi baru; baris lama turun ke `deprecated`.
--
-- id = uuid5(RUANG_ID_AGENT, 'nama@versi') — `agents.RUANG_ID_AGENT`.
-- ════════════════════════════════════════════════════════════════════

INSERT INTO agents (id, name, version, kind, status, max_risk, manifest) VALUES (
  'b339c963-8482-5ba6-9013-108a01f08833', 'coach-agent', '1.0.0', 'core', 'active', 1,
  $manifest${"autonomy":{"kill_condition":[],"max_level":"L2"},"capabilities":["daily_coaching","weekly_review"],"deploy":"cloud","evaluation":{"budget":{"cost_usd_per_run":0.02,"p95_latency_ms":4000},"gates":{"safety":0.99,"user_satisfaction":0.7},"suite":"coach-agent-v1"},"kind":"core","max_risk":"R1","memory":{"read":["habits","goals","checkins","mood","coaching_notes"],"write":["coaching_notes"]},"model":{"class":"reasoning","fallback":"simple"},"name":"coach-agent","purpose":["percakapan coaching harian","tinjauan mingguan"],"status":"active","tools":["habit.list","habit.streak","goal.list","checkin.get","mood.recent","memory.search","recommendation.create"],"version":"1.0.0"}$manifest$::jsonb
);
INSERT INTO agent_tools (agent_id, tool_name) VALUES
  ('b339c963-8482-5ba6-9013-108a01f08833', 'checkin.get'),
  ('b339c963-8482-5ba6-9013-108a01f08833', 'goal.list'),
  ('b339c963-8482-5ba6-9013-108a01f08833', 'habit.list'),
  ('b339c963-8482-5ba6-9013-108a01f08833', 'habit.streak'),
  ('b339c963-8482-5ba6-9013-108a01f08833', 'memory.search'),
  ('b339c963-8482-5ba6-9013-108a01f08833', 'mood.recent'),
  ('b339c963-8482-5ba6-9013-108a01f08833', 'recommendation.create');

INSERT INTO agents (id, name, version, kind, status, max_risk, manifest) VALUES (
  '2bfa7069-9aa5-5d64-a31f-de60531e27d9', 'habit-agent', '1.0.0', 'core', 'active', 2,
  $manifest${"autonomy":{"kill_condition":[],"max_level":"L2"},"capabilities":["habit_status","habit_completion"],"deploy":"cloud","evaluation":{"budget":{"cost_usd_per_run":0.02,"p95_latency_ms":4000},"gates":{"safety":0.99,"user_satisfaction":0.7},"suite":"habit-agent-v1"},"kind":"core","max_risk":"R2","memory":{"read":["habits"],"write":[]},"model":{"class":"simple","fallback":"simple"},"name":"habit-agent","purpose":["menjawab pertanyaan tentang habit dan rentetannya","menandai habit selesai atas permintaan pengguna"],"status":"active","tools":["habit.list","habit.streak","habit.complete"],"version":"1.0.0"}$manifest$::jsonb
);
INSERT INTO agent_tools (agent_id, tool_name) VALUES
  ('2bfa7069-9aa5-5d64-a31f-de60531e27d9', 'habit.complete'),
  ('2bfa7069-9aa5-5d64-a31f-de60531e27d9', 'habit.list'),
  ('2bfa7069-9aa5-5d64-a31f-de60531e27d9', 'habit.streak');

INSERT INTO agents (id, name, version, kind, status, max_risk, manifest) VALUES (
  '334f6466-344a-54e0-a5e9-9dc57918c240', 'memory-agent', '1.0.0', 'core', 'active', 2,
  $manifest${"autonomy":{"kill_condition":[],"max_level":"L2"},"capabilities":["memory_recall","memory_capture"],"deploy":"cloud","evaluation":{"budget":{"cost_usd_per_run":0.02,"p95_latency_ms":4000},"gates":{"safety":0.99,"user_satisfaction":0.7},"suite":"memory-agent-v1"},"kind":"core","max_risk":"R2","memory":{"read":["habits","goals","checkins","mood","coaching_notes"],"write":["habits","goals","checkins","mood","coaching_notes"]},"model":{"class":"simple","fallback":"simple"},"name":"memory-agent","purpose":["mencari yang pernah dicatat pengguna","mengingat hal yang pengguna minta diingat — bila belum diingat"],"status":"active","tools":["memory.search","memory.write"],"version":"1.0.0"}$manifest$::jsonb
);
INSERT INTO agent_tools (agent_id, tool_name) VALUES
  ('334f6466-344a-54e0-a5e9-9dc57918c240', 'memory.search'),
  ('334f6466-344a-54e0-a5e9-9dc57918c240', 'memory.write');

INSERT INTO agents (id, name, version, kind, status, max_risk, manifest) VALUES (
  '149486a2-334a-5f43-a6e7-2ba52885ac83', 'orchestrator-agent', '1.0.0', 'core', 'active', 2,
  $manifest${"autonomy":{"kill_condition":[],"max_level":"L2"},"capabilities":["request_routing","response_composition"],"deploy":"cloud","evaluation":{"budget":{"cost_usd_per_run":0.02,"p95_latency_ms":4000},"gates":{"safety":0.99,"user_satisfaction":0.7},"suite":"orchestrator-agent-v1"},"kind":"core","max_risk":"R2","memory":{"read":[],"write":[]},"model":{"class":"simple","fallback":"simple"},"name":"orchestrator-agent","purpose":["memahami permintaan pengguna dan menyerahkannya kepada agent yang tepat","menggabungkan jawaban mereka menjadi satu balasan"],"status":"active","tools":["agent.coach","agent.habit","agent.memory"],"version":"1.0.0"}$manifest$::jsonb
);
INSERT INTO agent_tools (agent_id, tool_name) VALUES
  ('149486a2-334a-5f43-a6e7-2ba52885ac83', 'agent.coach'),
  ('149486a2-334a-5f43-a6e7-2ba52885ac83', 'agent.habit'),
  ('149486a2-334a-5f43-a6e7-2ba52885ac83', 'agent.memory');
