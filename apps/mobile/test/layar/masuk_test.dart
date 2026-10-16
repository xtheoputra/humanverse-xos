// Layar masuk & daftar — pintu ke layar V0 pertama (spec/07 2.7).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/layar/masuk.dart';
import 'package:hvx_app/main.dart';

import 'palsu.dart';

Future<void> _pasang(
  WidgetTester t,
  LayananPalsu layanan,
  VoidCallback sesudah,
) async {
  await t.pumpWidget(
    MaterialApp(
      home: LayarMasuk(layanan: layanan, sesudahMasuk: sesudah),
    ),
  );
}

void main() {
  testWidgets('masuk dengan email & sandi', (t) async {
    final layanan = LayananPalsu();
    var masuk = 0;
    await _pasang(t, layanan, () => masuk++);

    await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
    await t.enterText(find.byKey(const Key('sandi')), 'rahasia');
    await t.tap(find.byKey(const Key('kirim')));
    await t.pumpAndSettle();

    expect(layanan.panggilan, ['masuk ana@uji.id']);
    expect(masuk, 1);
  });

  testWidgets('daftar menolak sandi di bawah 15 karakter sebelum dikirim', (
    t,
  ) async {
    final layanan = LayananPalsu();
    await _pasang(t, layanan, () {});

    await t.tap(find.text('Daftar').first);
    await t.pumpAndSettle();
    await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
    await t.enterText(find.byKey(const Key('sandi')), 'pendek');
    await t.enterText(find.byKey(const Key('nama')), 'Ana');
    await t.ensureVisible(find.byKey(const Key('kirim')));
    await t.tap(find.byKey(const Key('kirim')));
    await t.pumpAndSettle();

    expect(find.text('Sandi paling sedikit 15 karakter.'), findsOneWidget);
    expect(layanan.panggilan, isEmpty);
  });

  testWidgets('daftar tanpa menyetujui syarat tidak dikirim', (t) async {
    final layanan = LayananPalsu();
    await _pasang(t, layanan, () {});

    await t.tap(find.text('Daftar').first);
    await t.pumpAndSettle();
    await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
    await t.enterText(
      find.byKey(const Key('sandi')),
      'kuda-laut-berjalan-pelan',
    );
    await t.enterText(find.byKey(const Key('nama')), 'Ana');
    await t.ensureVisible(find.byKey(const Key('kirim')));
    await t.tap(find.byKey(const Key('kirim')));
    await t.pumpAndSettle();

    expect(find.byKey(const Key('galat')), findsOneWidget);
    expect(layanan.panggilan, isEmpty);
  });

  testWidgets(
    'daftar: pelatihan model TIDAK disetujui kecuali dicentang sendiri',
    (t) async {
      final layanan = LayananPalsu();
      var masuk = 0;
      await _pasang(t, layanan, () => masuk++);

      await t.tap(find.text('Daftar').first);
      await t.pumpAndSettle();
      await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
      await t.enterText(
        find.byKey(const Key('sandi')),
        'kuda-laut-berjalan-pelan',
      );
      await t.enterText(find.byKey(const Key('nama')), 'Ana');
      await t.ensureVisible(find.byKey(const Key('setuju')));
      await t.tap(find.byKey(const Key('setuju')));
      await t.pumpAndSettle();
      await t.ensureVisible(find.byKey(const Key('kirim')));
      await t.tap(find.byKey(const Key('kirim')));
      await t.pumpAndSettle();

      expect(layanan.daftarDengan, {
        'nama': 'Ana',
        'zona': 'Asia/Jakarta',
        'versi': versiKebijakanV0,
        'pelatihan': false,
      });
      expect(masuk, 1);
    },
  );

  testWidgets('centang pelatihan model sampai ke layanan', (t) async {
    // Tinjauan penegak buta Sprint 2: hanya arah "tidak disetujui" yang diuji —
    // layar yang mengabaikan centangnya lolos (arah gagal-aman, tetapi salah).
    final layanan = LayananPalsu();
    await _pasang(t, layanan, () {});

    await t.tap(find.text('Daftar').first);
    await t.pumpAndSettle();
    await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
    await t.enterText(
      find.byKey(const Key('sandi')),
      'kuda-laut-berjalan-pelan',
    );
    await t.enterText(find.byKey(const Key('nama')), 'Ana');
    for (final k in ['setuju', 'pelatihan']) {
      await t.ensureVisible(find.byKey(Key(k)));
      await t.tap(find.byKey(Key(k)));
      await t.pumpAndSettle();
    }
    await t.ensureVisible(find.byKey(const Key('kirim')));
    await t.tap(find.byKey(const Key('kirim')));
    await t.pumpAndSettle();

    expect(layanan.daftarDengan?['pelatihan'], isTrue);
  });

  testWidgets('galat server (sandi ditolak) tampil apa adanya', (t) async {
    final layanan = LayananPalsu()
      ..galatBerikutnya = const GalatApi(
        401,
        'invalid_credentials',
        'Email atau sandi salah.',
      );
    await _pasang(t, layanan, () {});

    await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
    await t.enterText(find.byKey(const Key('sandi')), 'salah');
    await t.tap(find.byKey(const Key('kirim')));
    await t.pumpAndSettle();

    expect(find.text('Email atau sandi salah.'), findsOneWidget);
  });

  testWidgets('aplikasi: masuk lalu tiba di habit hari ini, keluar kembali', (
    t,
  ) async {
    final layanan = LayananPalsu();
    await t.pumpWidget(AplikasiHvx(layanan: layanan));

    await t.enterText(find.byKey(const Key('email')), 'ana@uji.id');
    await t.enterText(find.byKey(const Key('sandi')), 'rahasia');
    await t.tap(find.byKey(const Key('kirim')));
    await t.pumpAndSettle();
    expect(find.text('Habit hari ini'), findsOneWidget);

    await t.tap(find.byKey(const Key('keluar')));
    await t.pumpAndSettle();
    expect(find.byKey(const Key('kirim')), findsOneWidget);
  });
}
