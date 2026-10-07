// spec/07 6.2–6.4 — layar habit membuka tinjauan mingguan, notifikasi, dan Privacy Center
// lewat menu *Lainnya*; tanpa layanan privasi menu itu tidak ada (bukan tombol mati).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/layar/habit_hari_ini.dart';
import 'package:hvx_app/layar/notifikasi.dart';
import 'package:hvx_app/layar/privasi.dart';
import 'package:hvx_app/layar/tinjauan.dart';

import 'palsu.dart';
import 'palsu_privasi.dart';

Future<void> _pasang(WidgetTester t, {LayananPrivasiPalsu? privasi}) async {
  await t.pumpWidget(
    MaterialApp(
      home: LayarHabitHariIni(
        layanan: LayananPalsu(),
        privasi: privasi,
        sesudahKeluar: () {},
        jam: () => DateTime(2026, 9, 21, 6, 30),
      ),
    ),
  );
  await t.pumpAndSettle();
}

void main() {
  for (final (kunci, layar) in [
    ('buka-tinjauan', LayarTinjauanMingguan),
    ('buka-notifikasi', LayarNotifikasi),
    ('buka-privasi', LayarPrivasi),
  ]) {
    testWidgets('menu Lainnya membuka $layar', (t) async {
      await _pasang(t, privasi: LayananPrivasiPalsu());

      await t.tap(find.byKey(const Key('lainnya')));
      await t.pumpAndSettle();
      await t.tap(find.byKey(Key(kunci)));
      await t.pumpAndSettle();

      expect(find.byType(layar), findsOneWidget);
    });
  }

  testWidgets('tanpa layanan privasi, menu Lainnya tidak ada', (t) async {
    await _pasang(t);

    expect(find.byKey(const Key('lainnya')), findsNothing);
  });
}
