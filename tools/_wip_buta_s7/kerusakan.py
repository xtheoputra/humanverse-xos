"""Kerusakan yang masuk akal untuk Sprint 7 — (berkas, lama, baru)."""

M = "apps/api/src/hvx/modules"
KON = f"{M}/events/kontrak.py"
PEN = f"{M}/events/penerbit.py"
PRY = f"{M}/intelligence/proyeksi.py"
ACT = f"{M}/activities/repository.py"
PRF = f"{M}/profile/repository.py"
TJW = f"{M}/intelligence/terjadwal.py"
MIG = "data/migrations/versions/0014_tugas_terjadwal.up.sql"
PRV = f"{M}/intelligence/privasi.py"
STR = f"{M}/events/stream.py"
ALT = "apps/api/src/hvx/stream_mati.py"
PKJ = "apps/api/src/hvx/pekerja.py"

U71 = ["tests/unit/test_admisi_event.py", "tests/unit/test_kontrak_event.py"]
I71 = U71 + ["tests/integration/test_event.py", "tests/integration/test_penerbitan_event.py"]
U72 = ["tests/unit/test_proyeksi_daftar.py"]
I72 = U72 + [
    "tests/integration/test_proyeksi_terdaftar.py",
    "tests/integration/test_proyektor.py",
    "tests/integration/test_human_state.py",
    "tests/integration/test_privacy_center.py",
]
I73 = [
    "tests/integration/test_tugas_terjadwal.py",
    "tests/integration/test_kepemilikan_data.py",
    "tests/unit/test_cakupan_privasi.py",
    "tests/integration/test_privacy_center.py",
]
I74 = ["tests/integration/test_stream_mati.py", "tests/integration/test_pekerja.py"]

DAFTAR = [
    # ───────────────────────────── 7.1 ─────────────────────────────
    dict(kode="7.1-a", maksud="identitas boleh kosong (+ → *)", uji=U71, sunting=[
        (KON, '_IDENTITAS = "[A-Za-z0-9:._+-]+"', '_IDENTITAS = "[A-Za-z0-9:._+-]*"')]),
    dict(kode="7.1-b", maksud="fullmatch → search", uji=U71, sunting=[
        (KON, "    if not admisi.pola.fullmatch(idempotency_key):",
         "    if not admisi.pola.search(idempotency_key):")]),
    dict(kode="7.1-c", maksud="sumber diperiksa terhadap SUMBER, bukan per jenis", uji=I71, sunting=[
        (KON, "    if source not in admisi.sumber:", "    if source not in SUMBER:")]),
    dict(kode="7.1-d", maksud="jenis tanpa admisi diloloskan", uji=I71, sunting=[
        (KON, '        raise EventTidakSah(f"event_type tanpa uji admisi spec/03: {event_type!r}")',
         "        return")]),
    dict(kode="7.1-e", maksud="pesan galat mengutip kunci (bocor id/tanggal)", uji=I71, sunting=[
        (KON, 'raise EventTidakSah(f"idempotency_key {event_type} wajib `{admisi.kunci}` (spec/03)")',
         'raise EventTidakSah(f"idempotency_key {idempotency_key!r} {event_type} wajib `{admisi.kunci}` (spec/03)")')]),
    dict(kode="7.1-f", maksud="templat tanpa re.escape bagian harfiah", uji=U71, sunting=[
        (KON, "        return re.compile(_IDENTITAS.join(re.escape(b) for b in bagian))",
         "        return re.compile(_IDENTITAS.join(b for b in bagian))")]),
    dict(kode="7.1-g", maksud="pola placeholder tanpa garis bawah", uji=U71, sunting=[
        (KON, '        bagian = re.split(r"<[a-z_]+>", self.kunci)',
         '        bagian = re.split(r"<[a-z]+>", self.kunci)')]),
    dict(kode="7.1-h", maksud="__post_init__ tidak menolak sumber di luar SUMBER", uji=U71, sunting=[
        (KON, "        if not self.sumber or not self.sumber <= SUMBER:",
         "        if not self.sumber:")]),
    dict(kode="7.1-i", maksud="__post_init__ menerima himpunan kosong", uji=U71, sunting=[
        (KON, "        if not self.sumber or not self.sumber <= SUMBER:",
         "        if not self.sumber <= SUMBER:")]),
    dict(kode="7.1-j", maksud="identitas tanpa titik dua", uji=U71, sunting=[
        (KON, '_IDENTITAS = "[A-Za-z0-9:._+-]+"', '_IDENTITAS = "[A-Za-z0-9._+-]+"')]),
    dict(kode="7.1-k", maksud="identitas apa pun (.+)", uji=U71, sunting=[
        (KON, '_IDENTITAS = "[A-Za-z0-9:._+-]+"', '_IDENTITAS = ".+"')]),
    dict(kode="7.1-l", maksud="admisi sesudah pola umum — urutan (ekuivalen?)", uji=I71, sunting=[
        (PEN, "    admisi_sah(event_type, idempotency_key, source)\n", ""),
        (PEN, '        raise EventTidakSah("idempotency_key wajib `jenis:identitas` (spec/03 aturan 1)")\n',
         '        raise EventTidakSah("idempotency_key wajib `jenis:identitas` (spec/03 aturan 1)")\n    admisi_sah(event_type, idempotency_key, source)\n')]),
    # ───────────────────────────── 7.2 ─────────────────────────────
    dict(kode="7.2-a", maksud="bangun ulang tidak menyaring jenis", uji=I72, sunting=[
        (PRY, "            e for e in await events.untuk_proyeksi(conn, user_id) if e.event_type in proyeksi.jenis\n",
         "            e for e in await events.untuk_proyeksi(conn, user_id)\n")]),
    dict(kode="7.2-b", maksud="kosongkan human_states semua versi model", uji=I72, sunting=[
        (PRF, '    "DELETE FROM human_states WHERE user_id = :user_id AND model_version = :model_version"',
         '    "DELETE FROM human_states WHERE user_id = :user_id AND :model_version = :model_version"')]),
    dict(kode="7.2-c", maksud="potret human_states tanpa metrics", uji=I72, sunting=[
        (PRF, '    "SELECT for_date, metrics FROM human_states "', '    "SELECT for_date FROM human_states "')]),
    dict(kode="7.2-d", maksud="potret activities tanpa payload", uji=I72, sunting=[
        (ACT, '    "SELECT id, kind, occurred_at, payload FROM activities "',
         '    "SELECT id, kind, occurred_at FROM activities "')]),
    dict(kode="7.2-e", maksud="potret activities termasuk baris manual", uji=I72, sunting=[
        (ACT, "    \"WHERE user_id = :user_id AND source = 'inferred' ORDER BY id\"",
         '    "WHERE user_id = :user_id ORDER BY id"')]),
    dict(kode="7.2-f", maksud="potret human_states semua versi", uji=I72, sunting=[
        (PRF, '    "WHERE user_id = :user_id AND model_version = :model_version ORDER BY for_date"',
         '    "WHERE user_id = :user_id AND :model_version = :model_version ORDER BY for_date"')]),
    dict(kode="7.2-g", maksud="kunci turunan sesudah kosongkan", uji=I72, sunting=[
        (PRY, "        await platform.kunci_turunan(conn, user_id)\n        await proyeksi.kosongkan(conn, user_id)\n",
         "        await proyeksi.kosongkan(conn, user_id)\n        await platform.kunci_turunan(conn, user_id)\n")]),
    dict(kode="7.2-h", maksud="bangun ulang mengembalikan jumlah semua event", uji=I72, sunting=[
        (PRY, "    return len(riwayat)\n\n\nasync def bangun_ulang_proyeksi",
         "    return len(riwayat) + 1\n\n\nasync def bangun_ulang_proyeksi")]),
    dict(kode="7.2-i", maksud="potret tanpa ORDER BY (activities)", uji=I72, sunting=[
        (ACT, "    \"WHERE user_id = :user_id AND source = 'inferred' ORDER BY id\"",
         "    \"WHERE user_id = :user_id AND source = 'inferred'\"")]),
    dict(kode="7.2-j", maksud="kosongkan human_states memakai versi tetap lain", uji=I72, sunting=[
        (PRY, "    return await profile.kosongkan_human_state(conn, user_id, model_version=MODEL)",
         '    return await profile.kosongkan_human_state(conn, user_id, model_version="v0")')]),
    dict(kode="7.2-k", maksud="BUKAN_PROYEKSI menelan proyeksi (human-state dipindah)", uji=U72, sunting=[
        (PRY, '    "pola": (\n', '    "human-state": "x" * 50,\n    "pola": (\n')]),
    # ───────────────────────────── 7.3 ─────────────────────────────
    dict(kode="7.3-a", maksud="NOT EXISTS tanpa r.task — tugas lain menutupi", uji=I73, sunting=[
        (MIG, "        WHERE r.user_id = u.id AND r.task = p_tugas AND r.for_date = h.for_date",
         "        WHERE r.user_id = u.id AND r.for_date = h.for_date")]),
    dict(kode="7.3-b", maksud="NOT EXISTS tanpa r.for_date — satu klaim menutup semua hari", uji=I73, sunting=[
        (MIG, "        WHERE r.user_id = u.id AND r.task = p_tugas AND r.for_date = h.for_date",
         "        WHERE r.user_id = u.id AND r.task = p_tugas")]),
    dict(kode="7.3-c", maksud="NOT EXISTS dibuang — yang sudah diklaim ikut jatuh tempo", uji=I73, sunting=[
        (MIG, "      AND NOT EXISTS (\n        SELECT 1 FROM public.scheduled_runs r\n        WHERE r.user_id = u.id AND r.task = p_tugas AND r.for_date = h.for_date\n      )\n", "")]),
    dict(kode="7.3-d", maksud="hari akun dibuat menurut tanggal UTC/sesi", uji=I73, sunting=[
        (MIG, "      AND h.for_date >= (u.created_at AT TIME ZONE z.name)::date\n",
         "      AND h.for_date >= u.created_at::date\n")]),
    dict(kode="7.3-e", maksud="ORDER BY dibalik (u.id, for_date) — kursor tak sejalan", uji=I73, sunting=[
        (MIG, "    ORDER BY h.for_date, u.id\n", "    ORDER BY u.id, h.for_date\n")]),
    dict(kode="7.3-f", maksud="kursor >= (mengulang baris kursor)", uji=I73, sunting=[
        (MIG, "           OR (h.for_date, u.id) > (p_setelah_tanggal, p_setelah_id))",
         "           OR (h.for_date, u.id) >= (p_setelah_tanggal, p_setelah_id))")]),
    dict(kode="7.3-g", maksud="ambang jam lokal > bukan >=", uji=I73, sunting=[
        (MIG, "      AND w.lokal >= h.for_date + make_interval(mins => p_menit)",
         "      AND w.lokal > h.for_date + make_interval(mins => p_menit)")]),
    dict(kode="7.3-h", maksud="GRANT UPDATE ke hvx_app", uji=I73, sunting=[
        (MIG, "GRANT SELECT, INSERT, DELETE ON scheduled_runs TO hvx_app;",
         "GRANT SELECT, INSERT, UPDATE, DELETE ON scheduled_runs TO hvx_app;")]),
    dict(kode="7.3-i", maksud="kebijakan RLS USING true", uji=I73, sunting=[
        (MIG, "CREATE POLICY scheduled_runs_own_rows ON scheduled_runs USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());",
         "CREATE POLICY scheduled_runs_own_rows ON scheduled_runs USING (true) WITH CHECK (user_id = app_current_user_id());")]),
    dict(kode="7.3-j", maksud="WITH CHECK true — tulis klaim pengguna lain", uji=I73, sunting=[
        (MIG, "CREATE POLICY scheduled_runs_own_rows ON scheduled_runs USING (user_id = app_current_user_id()) WITH CHECK (user_id = app_current_user_id());",
         "CREATE POLICY scheduled_runs_own_rows ON scheduled_runs USING (user_id = app_current_user_id()) WITH CHECK (true);")]),
    dict(kode="7.3-k", maksud="EXECUTE juga ke hvx_app", uji=I73, sunting=[
        (MIG, "  TO hvx_pekerja;", "  TO hvx_pekerja, hvx_app;")]),
    dict(kode="7.3-l", maksud="tanpa REVOKE FROM PUBLIC", uji=I73, sunting=[
        (MIG, "REVOKE ALL ON FUNCTION tugas_jatuh_tempo(text, integer, integer, date, uuid) FROM PUBLIC;\n", "")]),
    dict(kode="7.3-m", maksud="RLS tidak dinyalakan", uji=I73, sunting=[
        (MIG, "ALTER TABLE scheduled_runs ENABLE ROW LEVEL SECURITY;\n", "")]),
    dict(kode="7.3-n", maksud="tanpa ON DELETE CASCADE", uji=I73, sunting=[
        (MIG, "  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,",
         "  user_id      uuid NOT NULL REFERENCES users(id),")]),
    dict(kode="7.3-o", maksud="klaim tanpa ON CONFLICT DO NOTHING", uji=I73, sunting=[
        (TJW, '    "ON CONFLICT DO NOTHING RETURNING for_date"', '    "RETURNING for_date"')]),
    dict(kode="7.3-p", maksud="kursor dari baris PERTAMA halaman", uji=I73, sunting=[
        (TJW, "        setelah = (jatuh_tempo[-1][1], jatuh_tempo[-1][0])",
         "        setelah = (jatuh_tempo[0][1], jatuh_tempo[0][0])")]),
    dict(kode="7.3-q", maksud="halaman penuh dianggap terakhir (<=)", uji=I73, sunting=[
        (TJW, "        if len(jatuh_tempo) < halaman:\n", "        if len(jatuh_tempo) <= halaman:\n")]),
    dict(kode="7.3-r", maksud="kerja sebelum klaim", uji=I73, sunting=[
        (TJW, "            klaim = await conn.execute(\n                _KLAIM, {\"user_id\": user_id, \"tugas\": tugas.nama, \"for_date\": for_date}\n            )\n            if klaim.first() is None:  # pekerja lain lebih dulu — dan sudah commit\n                return 0\n            await tugas.kerjakan(conn, user_id, for_date)\n",
         "            await tugas.kerjakan(conn, user_id, for_date)\n            klaim = await conn.execute(\n                _KLAIM, {\"user_id\": user_id, \"tugas\": tugas.nama, \"for_date\": for_date}\n            )\n            if klaim.first() is None:  # pekerja lain lebih dulu — dan sudah commit\n                return 0\n")]),
    dict(kode="7.3-s", maksud="menit_lokal tidak diteruskan (selalu 0)", uji=I73, sunting=[
        (TJW, '                    "menit": tugas.menit_lokal,', '                    "menit": 0,')]),
    dict(kode="7.3-t", maksud="penghapus scheduled_runs dibuang dari privasi", uji=I73, sunting=[
        (PRV, '    identity.penghapus_sql(\n        _REKOMENDASI,\n        "scheduled_runs",\n        "DELETE FROM scheduled_runs WHERE user_id = :u",\n        turunan=True,\n    ),\n', "")]),
    dict(kode="7.3-u", maksud="bagian ekspor scheduled_runs dibuang", uji=I73, sunting=[
        (PRV, '    identity.bagian_sql(\n        _REKOMENDASI,\n        "scheduled_runs",\n        "SELECT count(*) FROM scheduled_runs WHERE user_id = :u",\n        "SELECT * FROM scheduled_runs WHERE user_id = :u ORDER BY for_date, task",\n        turunan=True,\n    ),\n', "")]),
    dict(kode="7.3-v", maksud="penghapus scheduled_runs bukan turunan (kategori sendiri)", uji=I73, sunting=[
        (PRV, '        "DELETE FROM scheduled_runs WHERE user_id = :u",\n        turunan=True,\n',
         '        "DELETE FROM scheduled_runs WHERE user_id = :u",\n')]),
    dict(kode="7.3-w", maksud="hanya akun active — status disaring !=deleted", uji=I73, sunting=[
        (MIG, "    WHERE u.status = 'active'", "    WHERE u.status <> 'deleted'")]),
    dict(kode="7.3-x", maksud="LIMIT tanpa pagu 500", uji=I73, sunting=[
        (MIG, "    LIMIT least(greatest(p_batas, 1), 500)", "    LIMIT greatest(p_batas, 1)")]),
    dict(kode="7.3-y", maksud="hari LOKAL dibulatkan dari now() UTC (w.lokal pakai sesi)", uji=I73, sunting=[
        (MIG, "      SELECT (w.lokal::date - k) AS for_date FROM generate_series(0, 1) AS k",
         "      SELECT (now()::date - k) AS for_date FROM generate_series(0, 1) AS k")]),
    dict(kode="7.3-z", maksud="search_path definer tidak dipatok", uji=I73, sunting=[
        (MIG, "  LANGUAGE sql STABLE SECURITY DEFINER\n  SET search_path = pg_catalog, public, pg_temp\n",
         "  LANGUAGE sql STABLE SECURITY DEFINER\n")]),
    # ───────────────────────────── 7.4 ─────────────────────────────
    dict(kode="7.4-a", maksud="putar ulang tanpa kunci turunan", uji=I74, sunting=[
        (STR, "            await platform.kunci_turunan(conn, user_id)\n            baris = (await conn.execute(_MENURUT_ID, {\"id\": UUID(isi[\"id\"])})).first()\n            if baris is None:\n                return \"event_hilang\"\n",
         "            baris = (await conn.execute(_MENURUT_ID, {\"id\": UUID(isi[\"id\"])})).first()\n            if baris is None:\n                return \"event_hilang\"\n")]),
    dict(kode="7.4-b", maksud="jenis tidak disaring saat putar ulang", uji=I74, sunting=[
        (STR, "            if baris.event_type in k.jenis:\n                await k.tangani(conn, EventMasuk(**baris._asdict()))\n",
         "            await k.tangani(conn, EventMasuk(**baris._asdict()))\n")]),
    dict(kode="7.4-c", maksud="daftar mati terbaru dulu", uji=I74, sunting=[
        (STR, "        await redis.xrange(kunci_mati(awalan), count=max(1, min(batas, 1000))),",
         "        await redis.xrevrange(kunci_mati(awalan), count=max(1, min(batas, 1000))),")]),
    dict(kode="7.4-d", maksud="daftar mati mengabaikan batas", uji=I74, sunting=[
        (STR, "        await redis.xrange(kunci_mati(awalan), count=max(1, min(batas, 1000))),",
         "        await redis.xrange(kunci_mati(awalan)),")]),
    dict(kode="7.4-e", maksud="alat operator mencetak seluruh isi entri", uji=I74, sunting=[
        (ALT, "                sys.stdout.write(f\"{id_mati}\\t{isi.get('grup')}\\t{isi.get('event_type')}\\n\")",
         "                sys.stdout.write(f\"{id_mati}\\t{isi}\\n\")")]),
    dict(kode="7.4-f", maksud="alat operator tanpa pemeriksaan peran", uji=I74, sunting=[
        (ALT, "        await platform.pastikan_peran_aplikasi(engine, pekerja=True)\n", "")]),
    dict(kode="7.4-g", maksud="gagal dianggap selesai — kode keluar 0", uji=I74, sunting=[
        (ALT, '_SELESAI = frozenset({"diputar", "event_hilang"})',
         '_SELESAI = frozenset({"diputar", "event_hilang", "gagal"})')]),
    dict(kode="7.4-h", maksud="tidak_ada dianggap selesai", uji=I74, sunting=[
        (ALT, '_SELESAI = frozenset({"diputar", "event_hilang"})',
         '_SELESAI = frozenset({"diputar", "event_hilang", "tidak_ada"})')]),
    dict(kode="7.4-i", maksud="XDEL sebelum cek grup — entri grup tak dikenal hilang", uji=I74, sunting=[
        (STR, "    k = konsumen.get(str(isi.get(\"grup\")))\n    if k is None:\n        return \"grup_tak_dikenal\"\n    if not await redis.xdel(kunci, id_mati):\n        return \"tidak_ada\"  # pemutar lain lebih dulu\n",
         "    if not await redis.xdel(kunci, id_mati):\n        return \"tidak_ada\"  # pemutar lain lebih dulu\n    k = konsumen.get(str(isi.get(\"grup\")))\n    if k is None:\n        return \"grup_tak_dikenal\"\n")]),
    dict(kode="7.4-j", maksud="xadd kembali tanpa grup", uji=I74, sunting=[
        (STR, '        await redis.xadd(kunci, cast("dict[Any, Any]", isi))\n',
         '        await redis.xadd(kunci, cast("dict[Any, Any]", {k2: v for k2, v in isi.items() if k2 != "pesan"}))\n')]),
    dict(kode="7.4-k", maksud="penangan dipanggil di luar transaksi pengguna (transaksi_sistem)", uji=I74, sunting=[
        (STR, "        async with platform.transaksi_pengguna(engine, user_id) as conn:\n            await platform.kunci_turunan(conn, user_id)\n            baris = (await conn.execute(_MENURUT_ID",
         "        async with platform.transaksi_sistem(engine) as conn:\n            await platform.kunci_turunan(conn, user_id)\n            baris = (await conn.execute(_MENURUT_ID")]),
    dict(kode="7.4-l", maksud="xrange tanpa min=max — entri lain yang diambil", uji=I74, sunting=[
        (STR, "        await redis.xrange(kunci, min=id_mati, max=id_mati, count=1),",
         "        await redis.xrange(kunci, min=id_mati, count=1),")]),
    dict(kode="7.4-m", maksud="event_hilang mengembalikan entri ke stream mati", uji=I74, sunting=[
        (STR, '            if baris is None:\n                return "event_hilang"\n',
         '            if baris is None:\n                await redis.xadd(kunci, cast("dict[Any, Any]", isi))\n                return "event_hilang"\n')]),
]
