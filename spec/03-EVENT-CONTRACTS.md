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
habit.completed   →  habit:<habit_id>:<for_date>
mood.logged       →  mood:<user_id>:<occurred_at menit>
journal.created   →  journal:<journal_id>
goal.completed    →  goal:<goal_id>
```

Kirim ulang menghasilkan `UNIQUE` violation yang **ditelan sebagai sukses**,
bukan galat. Ini yang membuat aplikasi luring aman menyinkron ulang.

**2 · Urutan.** Consumer **tidak boleh** mengandalkan urutan datang. Urutan
kebenaran adalah `occurred_at`; `recorded_at` hanya untuk memantau
keterlambatan. Event yang datang terlambat (backfill mingguan dari wearable)
harus tetap benar hasilnya.

**3 · Versi.** Consumer wajib mengabaikan field yang tidak dikenalnya.
Perubahan yang melanggar kontrak **menerbitkan `event_type` baru**
(`workout.completed.v2`), bukan menaikkan versi diam-diam.

---

## 22 event — 21 dari naskah 5 §7 + 1 usulan

Tanda ✅ = dipakai V0. Sisanya kontraknya ditulis sekarang, implementasinya
menyusul — supaya nama dan bentuknya tidak berubah nanti.

| Event | V0 | Payload |
|---|---|---|
| `habit.created` | ✅ | `{title, period, target_count}` |
| `habit.completed` | ✅ | `{status, tier_used?, note?}` |
| `habit.skipped` | ✅ | `{reason?}` |
| `mood.logged` | ✅ | `{valence, label?}` |
| `journal.created` | ✅ | `{word_count}` — **isi jurnal tidak pernah masuk event** |
| `goal.created` | ✅ | `{title, domain?, target_date?}` |
| `goal.completed` | ✅ | `{days_taken}` |
| `checkin.logged` | ✅ | `{energy?, focus?, sleep_hours?}` |
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

---

## 🔧 Padanan nama event naskah → `domain.verb` (K-3)

> Ditambahkan 9 September 2026 — **keputusan didelegasikan K-3**, lihat
> [`../docs/KEPUTUSAN-DIDELEGASIKAN.md`](../docs/KEPUTUSAN-DIDELEGASIKAN.md).

[#38](../../issues/38) memilih **dua segmen huruf kecil**. Sejak naskah 5,
naskah menamai **127 event baru** dengan `PascalCase` dan **nol** memakai
format yang dipilih ([`../docs/SENSUS-EVENT.md`](../docs/SENSUS-EVENT.md)).

**Berkas naskah tidak diubah** — aturan repo menyatakan naskah merekam kata
pemilik apa adanya. Tabel ini yang menjadi jembatannya, dan **berkas ini
adalah satu-satunya sumber nama yang sampai ke kode**.

Padanannya mekanis dan bisa diperiksa: **kata pertama → domain, sisanya →
verb `snake_case`**.

⚠️ **Tiga baris bertanda ⚠️ bukan sekadar beda bentuk — kata kerjanya berbeda
untuk kejadian yang sama**, dan diselesaikan ke arah berkas ini sebab nama itu
sudah ada di DDL.

⚠️ Tabel ini **tidak** menambahkan satu pun event ke V0. V0 tetap **22 event**
di bagian atas berkas ini; sisanya milik Phase 10–20.

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
| `AgentPolicyViolation` | **`agent.policy_violation`** | `187` |
| `AgentProposalCreated` | **`agent.proposal_created`** | `218` |
| `AgentQuarantined` | **`agent.quarantined`** | `218` |
| `AgentResumed` | **`agent.resumed`** | `187` |
| `AgentRevoked` | **`agent.revoked`** | `218` |
| `AgentSecurityViolation` | **`agent.security_violation`** | `218` |
| `AgentStarted` | **`agent.started`** | `187` |
| `AgentStopped` | **`agent.stopped`** | `187` |
| `AgentSuspended` | **`agent.suspended`** | `187` |
| `AgentTaskCompleted` | **`agent.task_completed`** | `187` |
| `AgentTaskCreated` | **`agent.task_created`** | `187` |
| `AgentTaskFailed` | **`agent.task_failed`** | `187` |
| `AgentTrustUpdated` | **`agent.trust_updated`** | `218` |
| `AgentUsageRecorded` | **`agent.usage_recorded`** | `218` |
| `AnchorCreated` | **`anchor.created`** | `226` |
| `AudioCaptured` | **`audio.captured`** | `174` |
| `BatteryLow` | **`battery.low`** | `235` |
| `CivilizationEventDetected` | **`civilization.event_detected`** | `273` |
| `CivilizationRiskChanged` | **`civilization.risk_changed`** | `273` |
| `ClimateSignalDetected` | **`climate.signal_detected`** | `273` |
| `CompanyAcquired` | **`company.acquired`** | `247` |
| `DeadlineApproaching` | **`deadline.approaching`** | `201` |
| `DiseaseOutbreakReported` | **`disease.outbreak_reported`** | `247` |
| `DocumentUploaded` | **`document.uploaded`** | `174` |
| `EarthquakeDetected` | **`earthquake.detected`** | `247` |
| `EconomicStateChanged` | **`economic.state_changed`** | `273` |
| `EmergencyStop` | **`emergency.stop`** | `235` |
| `EnergyChanged` | **`energy.changed`** | `201` |
| `FlightCancelled` | **`flight.cancelled`** | `247` |
| `GestureDetected` | **`gesture.detected`** | `174` |
| `GestureRecognized` | **`gesture.recognized`** | `226` |
| `GoalChanged` | **`goal.changed`** | `201` |
| `GoalCreated` | **`goal.created`** | `201` |
| `HabitCompleted` | **`habit.completed`** | `201` |
| `HealthAnomalyDetected` | **`health.anomaly_detected`** | `244` |
| `HealthConsentGranted` | **`health.consent_granted`** | `244` |
| `HealthConsentRevoked` | **`health.consent_revoked`** | `244` |
| `HealthInsightGenerated` | **`health.insight_generated`** | `244` |
| `HealthRecommendationCreated` | **`health.recommendation_created`** | `244` |
| `HeartRateRecorded` | **`heart.rate_recorded`** | `244` |
| `HumanDetected` | **`human.detected`** | `235` |
| `ImageCaptured` | **`image.captured`** | `174` |
| `ImpactAssessmentCompleted` | **`impact.assessment_completed`** | `273` |
| `InfrastructureFailureDetected` | **`infrastructure.failure_detected`** | `273` |
| `InterestRateChanged` | **`interest.rate_changed`** | `247` |
| `LargeScaleScenarioCreated` | **`large.scale_scenario_created`** | `273` |
| `LocationChanged` | **`location.changed`** | `174` · `201` |
| `MapUpdated` | **`map.updated`** | `226` |
| `MarketMoved` | **`market.moved`** | `247` |
| `MealDetected` | **`meal.detected`** | `244` |
| `MeetingEnded` | **`meeting.completed`** ⚠️ | `201` |
| `MeetingStarted` | **`meeting.started`** | `201` |
| `MissionCompleted` | **`mission.completed`** | `235` |
| `MissionFailed` | **`mission.failed`** | `235` |
| `MoodChanged` | **`mood.logged`** ⚠️ | `201` |
| `NavigationFinished` | **`navigation.finished`** | `226` |
| `NavigationStarted` | **`navigation.started`** | `226` |
| `NutritionLogged` | **`nutrition.logged`** | `244` |
| `ObjectDetected` | **`object.detected`** | `174` · `226` |
| `ObjectGrasped` | **`object.grasped`** | `235` |
| `ObjectLost` | **`object.lost`** | `226` |
| `ObjectMoved` | **`object.moved`** | `226` |
| `ObjectReleased` | **`object.released`** | `235` |
| `ObstacleDetected` | **`obstacle.detected`** | `235` |
| `OccupancyChanged` | **`occupancy.changed`** | `226` |
| `OilPriceChanged` | **`oil.price_changed`** | `247` |
| `PersonDetected` | **`person.detected`** | `174` |
| `PersonEntered` | **`person.entered`** | `226` |
| `PersonExited` | **`person.exited`** | `226` |
| `PolicyChanged` | **`policy.changed`** | `247` · `273` |
| `ProductLaunched` | **`product.launched`** | `247` |
| `RecommendationAccepted` | **`recommendation.accepted`** | `201` |
| `RecommendationRejected` | **`recommendation.rejected`** | `201` |
| `RecoveryChanged` | **`recovery.changed`** | `244` |
| `RecoveryStarted` | **`recovery.started`** | `235` |
| `ResearchPublished` | **`research.published`** | `247` |
| `RobotArrived` | **`robot.arrived`** | `235` |
| `RobotMoved` | **`robot.moved`** | `235` |
| `RobotStarted` | **`robot.started`** | `235` |
| `RobotStopped` | **`robot.stopped`** | `235` |
| `RoomScanned` | **`room.scanned`** | `226` |
| `SceneChanged` | **`scene.changed`** | `174` |
| `ScientificDiscoveryPublished` | **`scientific.discovery_published`** | `273` |
| `SensorReadingReceived` | **`sensor.reading_received`** | `174` |
| `SleepEnded` | **`sleep.completed`** ⚠️ | `201` · `244` |
| `SleepQualityChanged` | **`sleep.quality_changed`** | `244` |
| `SleepStarted` | **`sleep.started`** | `16` · `201` · `244` |
| `SpatialMapUpdated` | **`spatial.map_updated`** | `174` |
| `SpeechDetected` | **`speech.detected`** | `174` |
| `StormFormed` | **`storm.formed`** | `247` |
| `StressIndicatorChanged` | **`stress.indicator_changed`** | `244` |
| `SupplyChainDisrupted` | **`supply.chain_disrupted`** | `247` |
| `SupplyChainDisruption` | **`supply.chain_disruption`** | `273` |
| `TaskCompleted` | **`task.completed`** | `201` |
| `TechnologyBreakthroughDetected` | **`technology.breakthrough_detected`** | `273` |
| `TechnologyReleased` | **`technology.released`** | `247` |
| `TrafficChanged` | **`traffic.changed`** | `247` |
| `VideoCaptured` | **`video.captured`** | `174` |
| `WearableReadingReceived` | **`wearable.reading_received`** | `174` |
| `WiFiMotionDetected` | **`wifi.motion_detected`** | `226` |
| `WorkoutCompleted` | **`workout.completed`** | `16` · `201` · `244` |
| `WorkoutStarted` | **`workout.started`** | `244` |
| `WorldStateChanged` | **`world.state_changed`** | `273` |
