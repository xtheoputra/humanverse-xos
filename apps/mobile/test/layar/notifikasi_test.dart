// spec/07 6.3 — notifikasi bisa dimatikan per jenis; keamanan akun tidak; layar jujur bahwa
// V0 belum mengirim apa pun (A-28).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/layar/notifikasi.dart';

import 'palsu_privasi.dart';

Future<void> _pasang(WidgetTester t, LayananPrivasiPalsu layanan) async {
  await t.pumpWidget(MaterialApp(home: LayarNotifikasi(layanan: layanan)));
  await t.pumpAndSettle();
}

bool _nyala(WidgetTester t, String key) =>
    t.widget<SwitchListTile>(find.byKey(Key('notif-$key'))).value;

void main() {
  testWidgets(
    'tiap jenis tampil; yang wajib tidak bisa disentuh; V0 tak mengirim',
    (t) async {
      await _pasang(t, LayananPrivasiPalsu());

      expect(_nyala(t, 'habit_reminder'), isFalse);
      expect(_nyala(t, 'weekly_review'), isTrue);
      final wajib = t.widget<SwitchListTile>(
        find.byKey(const Key('notif-account_security')),
      );
      expect(wajib.onChanged, isNull, reason: 'keamanan akun bisa dimatikan');
      expect(find.byKey(const Key('belum-dikirim')), findsOneWidget);
      expect(find.byKey(const Key('pagu')), findsOneWidget);
    },
  );

  testWidgets('mematikan satu jenis hanya mengubah jenis itu', (t) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan);

    await t.tap(find.byKey(const Key('notif-weekly_review')));
    await t.pumpAndSettle();

    expect(layanan.panggilan.last, 'ubah-notifikasi {weekly_review: false}');
    expect(_nyala(t, 'weekly_review'), isFalse);
    expect(_nyala(t, 'account_security'), isTrue);
  });

  testWidgets('jam tenang bisa dimatikan dan dinyalakan lagi', (t) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan);
    expect(find.byKey(const Key('jam-mulai')), findsOneWidget);

    await t.tap(find.byKey(const Key('jam-tenang')));
    await t.pumpAndSettle();
    expect(layanan.panggilan.last, endsWith('tanpa-jam'));
    expect(find.byKey(const Key('jam-mulai')), findsNothing);

    await t.tap(find.byKey(const Key('jam-tenang')));
    await t.pumpAndSettle();
    expect(layanan.panggilan.last, contains('22:00'));
    expect(find.byKey(const Key('jam-mulai')), findsOneWidget);
  });
}
