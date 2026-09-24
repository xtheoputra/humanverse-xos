// spec/07 2.7 — "bisa dipakai manusia, bukan hanya curl": LAYAR yang sungguh
// dirakit `main.dart`, diketuk seperti manusia, terhadap api SUNGGUHAN.
//
// Uji widget lain memakai layanan palsu (cepat, tanpa server), dan
// `tool/ujung_ke_ujung.dart` memakai klien asli TANPA layar. Tinjauan kontrak
// Sprint 2 mencatat celah di antara keduanya: tidak ada yang menjalankan layar
// terhadap api nyata. Uji ini menutupnya — dijalankan `tools/ci_lokal.py` di
// tahap smoke, sesudah compose hidup:
//
//   flutter test test/ujung --dart-define=HVX_API_UJI=http://127.0.0.1:8000
//
// Tanpa `HVX_API_UJI` uji ini DILEWATI dengan alasan tertulis, bukan lulus diam.
import 'dart:io';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/model.dart';
import 'package:hvx_app/main.dart';

const _api = String.fromEnvironment('HVX_API_UJI');

/// Jaringan sungguhan berjalan di luar jam palsu uji widget: beri waktu nyata,
/// lalu gambar ulang, sampai `syarat` terpenuhi.
Future<void> _tunggu(WidgetTester t, bool Function() syarat, String apa) async {
  final akhir = DateTime.now().add(const Duration(seconds: 30));
  while (!syarat()) {
    if (DateTime.now().isAfter(akhir)) {
      throw TestFailure('menunggu terlalu lama: $apa');
    }
    await t.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 50)),
    );
    await t.pump();
  }
  await t.pump();
}

bool _ada(Finder f) => f.evaluate().isNotEmpty;

void main() {
  testWidgets(
    'daftar → tambah habit → tandai selesai → keluar, lewat ketukan, terhadap api nyata',
    (t) async {
      // flutter_test mengganti HttpClient dengan tiruan yang menjawab 400.
      HttpOverrides.global = null;
      // Layar ponsel (1080×2400 @ 2,5), bukan 800×600 bawaan uji: tombol di
      // bawah formulir harus terlihat untuk bisa diketuk — seperti oleh manusia.
      t.view.physicalSize = const Size(1080, 2400);
      t.view.devicePixelRatio = 2.5;
      addTearDown(t.view.reset);
      final acak = Random.secure();
      String hex(int n) =>
          List.generate(n, (_) => acak.nextInt(16).toRadixString(16)).join();
      final email = 'layar-${hex(12)}@uji.id';
      final sandi = 'kopi-sore-${hex(20)}';
      final jaringan = http.Client();
      final klien = KlienApi(dasar: Uri.parse(_api), klien: jaringan);

      await t.pumpWidget(AplikasiHvx(layanan: klien));
      await t.tap(find.text('Daftar').first);
      await t.pump();
      await t.enterText(find.byKey(const Key('email')), email);
      await t.enterText(find.byKey(const Key('sandi')), sandi);
      await t.enterText(find.byKey(const Key('nama')), 'Uji Layar');
      await t.ensureVisible(find.byKey(const Key('setuju')));
      await t.tap(find.byKey(const Key('setuju')));
      await t.pump();
      await t.ensureVisible(find.byKey(const Key('kirim')));
      await t.tap(find.byKey(const Key('kirim')));
      await _tunggu(
        t,
        () => _ada(find.byKey(const Key('tambah'))),
        'layar habit sesudah daftar',
      );

      // Daftar kosong dimuat dari server dulu — pemutar muatan berputar terus
      // selama jaringan belum menjawab, jadi `pumpAndSettle` tidak pernah tenang.
      await _tunggu(
        t,
        () => _ada(find.byKey(const Key('kosong'))),
        'daftar habit (masih kosong) termuat',
      );
      await t.tap(find.byKey(const Key('tambah')));
      await _tunggu(
        t,
        () => _ada(find.byKey(const Key('judul-habit'))),
        'dialog habit baru',
      );
      await t.enterText(find.byKey(const Key('judul-habit')), 'Jalan pagi');
      await t.tap(find.byKey(const Key('simpan-habit')));
      await _tunggu(
        t,
        () =>
            !_ada(find.byKey(const Key('simpan-habit'))) &&
            _ada(find.text('Jalan pagi')),
        'habit baru tampil di daftar',
      );

      await t.tap(find.text('Jalan pagi'));
      await _tunggu(t, () {
        final kotak = find.byType(CheckboxListTile);
        return _ada(kotak) && t.widget<CheckboxListTile>(kotak).value == true;
      }, 'habit tercentang sesudah diketuk');

      // Bukti dari SISI SERVER, lewat sesi lain — bukan dari keadaan layar.
      final saksi = KlienApi(dasar: Uri.parse(_api));
      await t.runAsync(() => saksi.masuk(email: email, sandi: sandi));
      final hariIni = tanggalLokal(DateTime.now());
      final habit = await t.runAsync(() => saksi.habitPada(hariIni));
      expect(habit, hasLength(1));
      expect(habit!.single.judul, 'Jalan pagi');
      expect(habit.single.selesaiHariItu, isTrue, reason: 'server: $hariIni');

      await t.tap(find.byKey(const Key('keluar')));
      await _tunggu(
        t,
        () => _ada(find.byKey(const Key('kirim'))),
        'kembali ke layar masuk',
      );
      expect(klien.sudahMasuk, isFalse);
      await t.runAsync(saksi.keluar);
      // Sambungan keep-alive HttpClient memasang pewaktu 15 dtk di jam PALSU uji;
      // tutup kliennya dan majukan jam supaya tidak ada pewaktu yang tertinggal.
      jaringan.close();
      await t.pump(const Duration(seconds: 16));
    },
    // Dilewati tanpa api hidup: --dart-define=HVX_API_UJI=http://127.0.0.1:<port>
    // (tools/ci_lokal.py tahap smoke menjalankannya terhadap compose).
    skip: _api.isEmpty,
  );
}
