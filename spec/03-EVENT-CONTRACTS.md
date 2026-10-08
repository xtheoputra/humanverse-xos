# 03 — Event Contracts

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menutup tiga celah bagian **D** audit: versi skema, urutan, dan idempotensi.

---

## Envelope

Setiap event memakai amplop yang sama. Yang berbeda hanya `payload`.

```json
{
  "id":              "018f...",
  "event_type":      "habit.completed",
  "schema_version":  1,
  "user_id":         "u_123",
  "occurred_at":     "2026-09-03T06:30:00Z",
  "recorded_at":     "2026-09-03T06:30:04Z",
  "source":          "app",
  "idempotency_key": "habit:9c2f:2026-09-03",
  "subject_type":    "habit",
  "subject_id":      "9c2f...",
  "payload":         { "status": "done", "tier_used": 0 }
}
```

| Field | Aturan |
|---|---|
| `event_type` | `<domain>.<past_tense_verb>`, huruf kecil. Sekali dipakai, **tidak pernah** diganti nama. |
| `schema_version` | Naik hanya saat perubahan **melanggar** kontrak. Menambah field opsional **tidak** menaikkannya. |
| `occurred_at` | Kapan kejadian **terjadi** menurut pengguna. Boleh masa lalu. |
| `recorded_at` | Kapan server menerimanya. **Selalu** `>= occurred_at` kecuali jam klien salah. |
| `idempotency_key` | Dibuat **klien**, deterministik. Unik per pengguna. |
| `source` | `app` · `agent` · `integration` · `backfill` |

---

## Tiga aturan yang menentukan

**1 · Idempotensi.** Kunci dibuat dari isi yang menentukan identitas kejadian,
bukan dari waktu kirim:

```
habit.created               →  habit:<habit_id>:created
habit.completed · skipped   →  habit-completion:<completion_id>
habit.completion_retracted  →  habit-completion:<completion_id>:retracted
mood.logged                 →  mood:<mood_id>
journal.created             →  journal:<journal_id>
goal.created                →  goal:<goal_id>:created
goal.completed              →  goal:<goal_id>:completed:<achieved_at>
checkin.logged              →  checkin:<for_date>:<updated_at>
```

Kirim ulang menghasilkan `UNIQUE` violation yang **ditelan sebagai sukses**,
bukan galat. Ini yang membuat aplikasi luring aman menyinkron ulang.

> 🔧 **Tiga contoh kunci semula MENELAN KOREKSI — dibetulkan 24 Sep 2026
> (E-177), saat tugas 3.2 ditulis.** Kunci harus mengidentifikasi *kejadian*,
> dan tiga contoh lama mengidentifikasi sesuatu yang lebih kasar:
>
> | Kunci lama | Kejadian yang DITELAN sebagai "kirim ulang" |
> |---|---|
> | `habit:<habit_id>:<for_date>` | penyelesaian dibatalkan lalu dicatat lagi (tier lain, atau `skipped`) — satu tanggal, dua kejadian |
> | `mood:<user_id>:<occurred_at menit>` | dua mood yang dilaporkan dalam satu menit — dua baris, satu event |
> | `goal:<goal_id>` | goal dibuka lagi lalu tercapai lagi |
>
> Tiap kasus membuat tabel domain dan `events` berbeda, dan aturan **D**
> [`02`](02-ERD.md) (*"kalau keduanya berbeda, event yang benar"*) lalu
> **membenarkan yang salah**. Kunci kini mengikuti **baris** yang lahir
> (`mood_id` — id buatan klien; `completion_id` — dibuat server, dan kirim ulang
> tanggal yang sama mengembalikan baris LAMA, jadi keduanya tetap satu kunci) atau
> **keadaan** yang lahir (`achieved_at`, `updated_at` check-in).
> Kirim ulang yang sesungguhnya tidak melahirkan baris atau keadaan baru, jadi
> tidak menerbitkan apa pun.

**2 · Urutan.** Consumer **tidak boleh** mengandalkan urutan datang. Urutan
kebenaran adalah `occurred_at`; `recorded_at` hanya untuk memantau
keterlambatan. Event yang datang terlambat (backfill mingguan dari wearable)
harus tetap benar hasilnya.

**3 · Versi.** Consumer wajib mengabaikan field yang tidak dikenalnya.
Perubahan yang melanggar kontrak **menerbitkan `event_type` baru**
(`workout.completed.v2`), bukan menaikkan versi diam-diam.

---

## 23 event — 21 dari naskah 5 §7 + 2 usulan

Tanda ✅ = dipakai V0. Sisanya kontraknya ditulis sekarang, implementasinya
menyusul — supaya nama dan bentuknya tidak berubah nanti.

| Event | V0 | Payload |
|---|---|---|
| `habit.created` | ✅ | `{title, period, target_count}` |
| `habit.completed` | ✅ | `{status, tier_used?, note?, for_date, completion_id}` |
| `habit.skipped` | ✅ | `{reason?, for_date, completion_id}` |
| `habit.completion_retracted` | ✅ | `{for_date, completion_id}` 🔧 |
| `mood.logged` | ✅ | `{valence, label?}` |
| `journal.created` | ✅ | `{word_count}` — **isi jurnal tidak pernah masuk event** |
| `goal.created` | ✅ | `{title, domain?, target_date?}` |
| `goal.completed` | ✅ | `{days_taken}` |
| `checkin.logged` | ✅ | `{energy?, focus?, sleep_hours?, for_date}` |
| `sleep.started` | | `{}` |
| `sleep.completed` | | `{duration_minutes, quality?}` |
| `workout.started` | | `{exercise_type}` |
| `workout.completed` | | `{duration, exercise_type}` |
| `meal.logged` | | `{meal_type, items[]}` |
| `outfit.selected` | | `{outfit_id}` |
| `outfit.worn` | | `{outfit_id, occasion?}` |
| `purchase.created` | | `{category, amount_minor, currency}` |
| `learning.started` | | `{subject}` |
| `learning.completed` | | `{subject, duration}` |
| `meeting.started` | | `{calendar_ref?}` |
| `meeting.completed` | | `{duration}` |
| `travel.started` | | `{destination?}` |
| `travel.completed` | | `{duration}` |

> `checkin.logged` **saya tambahkan** — Daily Check-in ada di V0 tetapi tidak
> punya event di daftar 21 naskah 5 §7. Tanpa itu, Behavior Engine tidak
> melihat salah satu sinyal harian paling padat. 🔧

> 🔧 **`habit.completion_retracted` ditambahkan 24 Sep 2026 (E-178), saat 3.2
> ditulis — event V0 ke-9, event ke-23.** [`04`](04-API-CONTRACTS.md) punya
> `DELETE /habits/{id}/completions/{for_date}`, tetapi tidak satu pun event
> mencatat bahwa penyelesaian **dibatalkan**: proyeksi yang dibangun ulang dari
> `events` (aturan **D** [`02`](02-ERD.md)) menghidupkan kembali penyelesaian
> yang sudah dibatalkan pemiliknya, dan rentetan serta pola (Sprint 5) belajar
> dari hari yang tidak pernah dijalankan.
> ⚠️ Ia lulus uji [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §7 — *yang boleh
> ditambahkan ke V0 hanyalah hal yang TIDAK BISA ditambahkan nanti* —
> dengan alasan yang terbalik dari biasanya: pembatalan yang terjadi sebelum
> event ini ada **tidak meninggalkan jejak apa pun** untuk diterbitkan
> belakangan; barisnya sudah terhapus.
>
> 🔧 **`for_date` dan `completion_id` di `habit.*`, `for_date` di
> `checkin.logged`** (3.2): tanpa keduanya proyeksi tidak bisa dibangun ulang —
> tanggal LOKAL tidak bisa diturunkan dari `occurred_at` tanpa menebak zona
> waktunya, dan pembatalan harus bisa menunjuk penyelesaian mana yang batal.
> Medan WAJIB, bukan opsional: belum satu event pun pernah terbit, jadi
> kontraknya masih bisa dilengkapi tanpa `schema_version` baru.

> **`journal.created` sengaja hanya membawa `word_count`.** Isi jurnal tinggal
> di `journal_entries` yang tunduk pada permission scope. Event mengalir ke
> banyak consumer; menaruh isi jurnal di sana berarti membocorkannya ke semua
> yang mendengarkan.

---

## Consumer V0

| Consumer | Mendengarkan | Wajib? |
|---|---|---|
| **Behavior projector** | semua | ✅ wajib — kegagalannya menahan event |
| **Habit streak** | `habit.*` | ✅ wajib |
| **Memory extractor** | `journal.created`, `mood.logged` | boleh gagal & diulang |
| **Recommendation trigger** | `checkin.logged`, `habit.skipped` | boleh gagal |
| **Analytics** | semua | boleh gagal |

> Consumer yang "boleh gagal" wajib **idempoten**, karena akan diulang.
> Di V0 antreannya Redis Streams dengan consumer group; Kafka baru bila
> skalanya menuntut (naskah 5 §5).
>
> 🔧 **"Wajib" = tanpa stream mati (8 Okt 2026, tinjauan kontrak Sprint 5–6, K6).**
> Konsumen *boleh gagal* memindahkan pesan ke stream mati sesudah 5 kali diserahkan
> (K-25). Konsumen **wajib** tidak: pesannya tetap di daftar tunggu grupnya dan dicoba
> tiap 30 dtk menganggur sampai berhasil — *“kegagalannya menahan event”*, bukan
> membuangnya — sementara pesan lain grup itu tetap mengalir
> (`KonsumenStream(wajib=True)`). Versi pertama Sprint 5 memasang Behavior projector dan
> Habit streak dengan bawaan *boleh gagal*: basis data yang mati ±3 menit membuang event
> ke stream mati, dan proyeksinya diam-diam berbeda dari yang dibangun ulang dari
> `events` (5.1). Konsumen wajib karena itu juga wajib idempoten.

> 🔧 **Bentuk V0-nya (spec/07 3.3 · 3.6, K-25).** Tabel `events` adalah kotak
> keluar: relay di proses pekerja (`hvx/pekerja.py`) menyalin **rujukan** tiap event yang
> sudah commit — `id` · `user_id` · `event_type`, **bukan** `payload` — ke satu
> stream Redis. Tiap consumer adalah satu **grup**; ia membaca isi event dari
> PostgreSQL di transaksi **pemiliknya** (RLS berlaku) dan meng-ACK **sesudah**
> commit. Pesan yang menganggur 30 dtk diklaim anggota grup lain; sesudah 5 kali
> diserahkan ia pindah ke stream **mati**. Yang terpasang di V0: **Memory
> extractor** (grup `memori`, 3.6). Behavior projector, Habit streak,
> Recommendation trigger, dan Analytics menyusul bersama tugasnya (5.1, 5.5) —
> grup baru membaca stream **dari awal**, jadi tidak ada event yang terlewat
> selama stream belum dipangkas melewatinya.

---

## 🔧 Padanan nama event naskah → `domain.verb` (K-3)

> Ditambahkan 9 September 2026 — **keputusan didelegasikan K-3**, lihat
> [`../docs/KEPUTUSAN-DIDELEGASIKAN.md`](../docs/KEPUTUSAN-DIDELEGASIKAN.md).

[#38](../../issues/38) memilih **dua segmen huruf kecil**. Sejak naskah 5,
naskah menamai **128 event baru** dengan `PascalCase` dan **nol** memakai
format yang dipilih ([`../docs/SENSUS-EVENT.md`](../docs/SENSUS-EVENT.md)).

**Berkas naskah tidak diubah** — aturan repo menyatakan naskah merekam kata
pemilik apa adanya. Tabel ini yang menjadi jembatannya, dan **berkas ini
adalah satu-satunya sumber nama yang sampai ke kode**.

### 🔧 K-15 — aturan padanannya dipersempit, dan alasannya terukur

> Diperbarui 11 September 2026 — **[K-15](../docs/KEPUTUSAN-DIDELEGASIKAN.md)**,
> ditemukan [`../tools/periksa_dokumen.py`](../tools/periksa_dokumen.py) **E-1**.

K-3 menulis aturannya *“kata pertama → domain, sisanya → verb `snake_case`”*.
Dijalankan mesin terhadap registry domain [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2,
**66 dari 127 baris** mendarat di domain yang **tidak ada di registry** — dan
sebagiannya membuktikan kenapa: `LargeScaleScenarioCreated` menghasilkan domain
**`large`**, `InterestRateChanged` menghasilkan **`interest`**, `OilPriceChanged`
menghasilkan **`oil`**.

> 🔑 **Kata pertama sebuah nama tidak selalu SUBJEKNYA.** K-3 benar sebagai
> aturan **transkripsi**; ia tidak pernah menjadi aturan **kepemilikan**.

🛑 Yang menentukan arah perbaikannya bukan selera, melainkan kalimat yang sudah
berdiri di [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2 sejak awal:
***“Domain baru ditambahkan hanya bersama konteks pemiliknya — dan penambahan
itu adalah perubahan arsitektur, bukan penamaan.”*** ⇒ **namanya yang pindah,
bukan registry yang tumbuh.**

**Aturan padanan yang berlaku sekarang:**

| | |
|---|---|
| 1 | Kalau kata pertama **adalah domain terdaftar**, ia jadi domain; sisanya jadi verb. |
| 2 | Kalau bukan, domainnya diambil dari [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §4 (domain tujuan per fase) dan **seluruh nama** jadi verb. |
| 3 | Verb wajib berakhir kata kerja **lampau** — [`../arch/11`](../arch/11-PENEGAKAN.md) **E-2**. |

⚠️ Satu-satunya domain yang **ditambahkan** ke registry adalah `health`, dan ia
bukan domain baru: catatan kaki [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §4
sudah menyatakannya milik `human-core` sejak awal — tabel §2 yang melewatkannya.

⚠️ **Enam baris bertanda ⚠️ bukan sekadar beda bentuk — kata kerjanya berbeda
untuk kejadian yang sama**, dan diselesaikan ke arah berkas ini sebab nama itu
sudah ada di DDL. Tiga di antaranya (`TaskCompleted` · `MapUpdated` ·
`SupplyChainDisruption`) **menyatu dengan baris lain** sesudah K-15 — dua nama
naskah, satu `event_type`.

🆕 **`MeetingCreated` ([`167`](../docs/167-AUDIO-VOICE-VIDEO-TEMPORAL.md) L29)
ditambahkan 11 September 2026.** Ia terlewat dari
[`../docs/SENSUS-EVENT.md`](../docs/SENSUS-EVENT.md) karena sensus memanen
**bagian yang judulnya menyebut “Event”**, sementara nama ini berdiri di sebuah
**contoh alur suara**. Ditemukan **E-5** — pemeriksaan yang lahir justru dari
pertanyaan *“apa yang E-1 dan E-2 TIDAK PERNAH lihat?”*, dan jawabannya: nama
yang tidak pernah masuk tabel ini tidak punya `event_type` sama sekali.

⚠️ Tabel ini **tidak** menambahkan satu pun event ke V0. V0 tetap **23 event** (E-178)
di bagian atas berkas ini; sisanya milik Phase 9–20.

| PascalCase di naskah | `domain.verb` | Naskah |
|---|---|---|
| `ActivityDetected` | **`activity.detected`** | `174` |
| `AgentActionApproved` | **`agent.action_approved`** | `187` |
| `AgentActionExecuted` | **`agent.action_executed`** | `187` |
| `AgentActionFailed` | **`agent.action_failed`** | `187` |
| `AgentActionRejected` | **`agent.action_rejected`** | `187` |
| `AgentActionRequested` | **`agent.action_requested`** | `187` |
| `AgentActionVerified` | **`agent.action_verified`** | `187` |
| `AgentAuthenticated` | **`agent.authenticated`** | `218` |
| `AgentBillingCreated` | **`agent.billing_created`** | `218` |
| `AgentBudgetExceeded` | **`agent.budget_exceeded`** | `187` |
| `AgentCertified` | **`agent.certified`** | `218` |
| `AgentConflictDetected` | **`agent.conflict_detected`** | `218` |
| `AgentConsensusFailed` | **`agent.consensus_failed`** | `218` |
| `AgentConsensusReached` | **`agent.consensus_reached`** | `218` |
| `AgentCreated` | **`agent.created`** | `187` |
| `AgentDelegated` | **`agent.delegated`** | `218` |
| `AgentDelegationRejected` | **`agent.delegation_rejected`** | `218` |
| `AgentDiscovered` | **`agent.discovered`** | `218` |
| `AgentKilled` | **`agent.killed`** | `187` · `218` |
| `AgentPermissionGranted` | **`agent.permission_granted`** | `187` |
| `AgentPermissionRequested` | **`agent.permission_requested`** | `187` |
| `AgentPermissionRevoked` | **`agent.permission_revoked`** | `187` |
| `AgentPlanApproved` | **`agent.plan_approved`** | `187` |
| `AgentPlanGenerated` | **`agent.plan_generated`** | `187` |
| `AgentPolicyViolation` | **`agent.policy_violated`** | `187` |
| `AgentProposalCreated` | **`agent.proposal_created`** | `218` |
| `AgentQuarantined` | **`agent.quarantined`** | `218` |
| `AgentResumed` | **`agent.resumed`** | `187` |
| `AgentRevoked` | **`agent.revoked`** | `218` |
| `AgentSecurityViolation` | **`agent.security_violated`** | `218` |
| `AgentStarted` | **`agent.started`** | `187` |
| `AgentStopped` | **`agent.stopped`** | `187` |
| `AgentSuspended` | **`agent.suspended`** | `187` |
| `AgentTaskCompleted` | **`agent.task_completed`** | `187` |
| `AgentTaskCreated` | **`agent.task_created`** | `187` |
| `AgentTaskFailed` | **`agent.task_failed`** | `187` |
| `AgentTrustUpdated` | **`agent.trust_updated`** | `218` |
| `AgentUsageRecorded` | **`agent.usage_recorded`** | `218` |
| `AnchorCreated` | **`spatial.anchor_created`** | `226` |
| `AudioCaptured` | **`perception.audio_captured`** | `174` |
| `BatteryLow` | **`robot.battery_low_detected`** | `235` |
| `CivilizationEventDetected` | **`world.civilization_event_detected`** | `273` |
| `CivilizationRiskChanged` | **`world.civilization_risk_changed`** | `273` |
| `ClimateSignalDetected` | **`world.climate_signal_detected`** | `273` |
| `CompanyAcquired` | **`world.company_acquired`** | `247` |
| `DeadlineApproaching` | **`notification.deadline_approached`** | `201` |
| `DiseaseOutbreakReported` | **`world.disease_outbreak_reported`** | `247` |
| `DocumentUploaded` | **`perception.document_uploaded`** | `174` |
| `EarthquakeDetected` | **`world.earthquake_detected`** | `247` |
| `EconomicStateChanged` | **`world.economic_state_changed`** | `273` |
| `EmergencyStop` | **`emergency.stopped`** | `235` |
| `EnergyChanged` | **`checkin.energy_changed`** | `201` |
| `FlightCancelled` | **`world.flight_cancelled`** | `247` |
| `GestureDetected` | **`perception.gesture_detected`** | `174` |
| `GestureRecognized` | **`spatial.gesture_recognized`** | `226` |
| `GoalChanged` | **`goal.changed`** | `201` |
| `GoalCreated` | **`goal.created`** | `201` |
| `HabitCompleted` | **`habit.completed`** | `201` |
| `HealthAnomalyDetected` | **`health.anomaly_detected`** | `244` |
| `HealthConsentGranted` | **`health.consent_granted`** | `244` |
| `HealthConsentRevoked` | **`health.consent_revoked`** | `244` |
| `HealthInsightGenerated` | **`health.insight_generated`** | `244` |
| `HealthRecommendationCreated` | **`health.recommendation_created`** | `244` |
| `HeartRateRecorded` | **`health.heart_rate_recorded`** | `244` |
| `HumanDetected` | **`robot.human_detected`** | `235` |
| `ImageCaptured` | **`perception.image_captured`** | `174` |
| `ImpactAssessmentCompleted` | **`governance.impact_assessment_completed`** | `273` |
| `InfrastructureFailureDetected` | **`world.infrastructure_failure_detected`** | `273` |
| `InterestRateChanged` | **`world.interest_rate_changed`** | `247` |
| `LargeScaleScenarioCreated` | **`simulation.large_scale_scenario_created`** | `273` |
| `LocationChanged` | **`perception.location_changed`** | `174` · `201` |
| `MapUpdated` | **`spatial.map_updated`** ⚠️ | `226` |
| `MarketMoved` | **`world.market_moved`** | `247` |
| `MealDetected` | **`meal.detected`** | `244` |
| `MeetingCreated` | **`meeting.created`** 🆕 | `167` |
| `MeetingEnded` | **`meeting.completed`** ⚠️ | `201` |
| `MeetingStarted` | **`meeting.started`** | `201` |
| `MissionCompleted` | **`mission.completed`** | `235` |
| `MissionFailed` | **`mission.failed`** | `235` |
| `MoodChanged` | **`mood.logged`** ⚠️ | `201` |
| `NavigationFinished` | **`spatial.navigation_finished`** | `226` |
| `NavigationStarted` | **`spatial.navigation_started`** | `226` |
| `NutritionLogged` | **`health.nutrition_logged`** | `244` |
| `ObjectDetected` | **`perception.object_detected`** | `174` · `226` |
| `ObjectGrasped` | **`robot.object_grasped`** | `235` |
| `ObjectLost` | **`spatial.object_lost`** | `226` |
| `ObjectMoved` | **`spatial.object_moved`** | `226` |
| `ObjectReleased` | **`robot.object_released`** | `235` |
| `ObstacleDetected` | **`robot.obstacle_detected`** | `235` |
| `OccupancyChanged` | **`presence.occupancy_changed`** | `226` |
| `OilPriceChanged` | **`world.oil_price_changed`** | `247` |
| `PersonDetected` | **`perception.person_detected`** | `174` |
| `PersonEntered` | **`presence.person_entered`** | `226` |
| `PersonExited` | **`presence.person_exited`** | `226` |
| `PolicyChanged` | **`world.policy_changed`** | `247` · `273` |
| `ProductLaunched` | **`world.product_launched`** | `247` |
| `RecommendationAccepted` | **`recommendation.accepted`** | `201` |
| `RecommendationRejected` | **`recommendation.rejected`** | `201` |
| `RecoveryChanged` | **`health.recovery_changed`** | `244` |
| `RecoveryStarted` | **`emergency.recovery_started`** | `235` |
| `ResearchPublished` | **`knowledge.research_published`** | `247` |
| `RobotArrived` | **`robot.arrived`** | `235` |
| `RobotMoved` | **`robot.moved`** | `235` |
| `RobotStarted` | **`robot.started`** | `235` |
| `RobotStopped` | **`robot.stopped`** | `235` |
| `RoomScanned` | **`spatial.room_scanned`** | `226` |
| `SceneChanged` | **`perception.scene_changed`** | `174` |
| `ScientificDiscoveryPublished` | **`knowledge.scientific_discovery_published`** | `273` |
| `SensorReadingReceived` | **`perception.sensor_reading_received`** | `174` |
| `SleepEnded` | **`sleep.completed`** ⚠️ | `201` · `244` |
| `SleepQualityChanged` | **`sleep.quality_changed`** | `244` |
| `SleepStarted` | **`sleep.started`** | `16` · `201` · `244` |
| `SpatialMapUpdated` | **`spatial.map_updated`** | `174` |
| `SpeechDetected` | **`perception.speech_detected`** | `174` |
| `StormFormed` | **`world.storm_formed`** | `247` |
| `StressIndicatorChanged` | **`health.stress_indicator_changed`** | `244` |
| `SupplyChainDisrupted` | **`world.supply_chain_disrupted`** | `247` |
| `SupplyChainDisruption` | **`world.supply_chain_disrupted`** ⚠️ | `273` |
| `TaskCompleted` | **`agent.task_completed`** ⚠️ | `201` |
| `TechnologyBreakthroughDetected` | **`world.technology_breakthrough_detected`** | `273` |
| `TechnologyReleased` | **`world.technology_released`** | `247` |
| `TrafficChanged` | **`world.traffic_changed`** | `247` |
| `VideoCaptured` | **`perception.video_captured`** | `174` |
| `WearableReadingReceived` | **`perception.wearable_reading_received`** | `174` |
| `WiFiMotionDetected` | **`presence.wifi_motion_detected`** | `226` |
| `WorkoutCompleted` | **`workout.completed`** | `16` · `201` · `244` |
| `WorkoutStarted` | **`workout.started`** | `244` |
| `WorldStateChanged` | **`world.state_changed`** | `273` |

---

---

## 🔧 Nama control-plane yang DICADANGKAN — bukan V0

> Ditambahkan 11 September 2026. Ditemukan
> [`../tools/periksa_dokumen.py`](../tools/README.md) **E-4**.

[`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §6 menuntut kembaran kegagalan
dan pemulihan untuk setiap kata kerja kendali. Sebagian namanya **bukan nama
naskah** — tidak ada `AgentRetired` maupun `ToolCalled` di dua puluh empat
naskah — jadi tabel padanan di atas bukan tempatnya. Ia juga bukan V0.

🔑 **Kenapa dicadangkan sekarang, padahal implementasinya jauh:** aturan
[§5](#versi--dan-satu-aturan-yang-lebih-penting-daripada-nomornya) berbunyi
*nama event tidak pernah diganti sekali diterbitkan*. Mencadangkan nama hari
ini berbiaya **nol**; membiarkannya kosong berarti Phase 11 akan mengarang
namanya sendiri, dan nama karangan itu **tidak bisa diganti lagi** begitu
baris pertamanya terbit.

| `event_type` | Pasangannya | Fase |
|---|---|---|
| `agent.retired` | `agent.restored` | 11 · 14 |
| `agent.throttled` | `agent.unthrottled` | 14 |
| `emergency.recovery_completed` | melengkapi `emergency.recovery_started` | 16 |
| `tool.called` | `tool.failed` | 11 |

⚠️ **Nol di antaranya masuk V0.** V0 tetap **23 event domain** (E-178); aturan yang
dipakai: *yang boleh ditambahkan ke V0 hanyalah hal yang **tidak bisa**
ditambahkan nanti* — dan sebuah event selalu bisa mulai diterbitkan kemudian.

🛑 **`agent.restored` bukan kerapian.** §14.29 menjadikan `RESTORE` **setara**
`RETIRE`; tanpa kembarannya, jejak audit hanya merekam sisi yang mematikan
agent dan tidak pernah sisi yang menghidupkannya kembali.

---

## 🔧 Security event memakai amplop yang sama (K-10)

> Ditambahkan 9 September 2026 — **keputusan didelegasikan K-10**, menutup
> **E-69/E-70** / [#63](../../issues/63).

§8.26 memasukkan security event ke **bus yang sama**, tetapi §8.41 memberinya
bentuk yang berbeda sama sekali (`action` + `resource` + `timestamp`, tanpa
`schema_version`, `idempotency_key`, maupun `user_id`).

**Keputusan: ada satu amplop, yaitu amplop di berkas ini.** Security event
memakainya dengan `event_type: security.*`:

```
security.permission_denied · security.consent_revoked · security.auth_failed
security.injection_detected · security.policy_violated · security.tool_abused
security.data_accessed · security.agent_flagged
```

Medan `action` dan `resource` turun menjadi isi **`payload`**, bukan bentuk
amplop tersendiri.

> 🛑 **Alasannya membalik arah keberatan yang biasa.** Empat medan yang hilang
> dari `SecurityEvent` — `schema_version`, `idempotency_key`, `user_id`, dan
> pemisahan `occurred_at`/`recorded_at` — justru **medan yang membuat sebuah
> event bisa diaudit**. Dan security event adalah jenis yang **paling mungkin
> diaudit**. Bentuk khusus itu menghapus tepat kemampuan yang paling
> dibutuhkannya.

⚠️ Kedelapan nama di atas **tidak** menambah event V0 — V0 tetap **23 event**;
security event lahir di Phase 8.

