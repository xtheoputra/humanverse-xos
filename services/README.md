# `services/`

Letak **final** modul human-core dan domain vertikal
([`arch/03`](../arch/03-MONOREPO-FINAL.md) §3): `identity/ profile/ goals/
habits/ checkins/ journal/ activities/` dan seterusnya.

⚠️ **Kosong di V0, dengan sengaja.** V0 adalah modular monolith: ketujuh modul
itu hidup di [`apps/api/src/hvx/modules/`](../apps/api/src/hvx/modules/) dengan
**nama yang sama** ([`arch/03`](../arch/03-MONOREPO-FINAL.md) §8). Sebuah modul
pindah ke sini hanya ketika ia benar-benar dipisah menjadi proses sendiri
(tahap **D3+**, [`arch/09`](../arch/09-DEPLOYMENT-TOPOLOGY.md) §2) — dan
batas impor yang ditegakkan `import-linter` sejak Sprint 0 yang membuat
pemindahan itu pekerjaan sehari, bukan penulisan ulang.
