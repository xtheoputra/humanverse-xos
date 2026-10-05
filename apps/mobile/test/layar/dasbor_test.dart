// spec/07 6.1 — layar Dashboard: beberapa dimensi, tiap skor ber-Why (naskah 4 §28).
// Dipakai lewat ketukan, layanan palsu memberi data; layar tak boleh menampilkan
// satu angka tanpa Why, dan cold start meminta data, bukan angka kosong.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/api/model.dart';
import 'package:hvx_app/layar/dasbor.dart';

import 'palsu.dart';

Future<void> _pasang(WidgetTester t, LayananPalsu layanan) async {
  await t.pumpWidget(MaterialApp(home: LayarDasbor(layanan: layanan)));
  await t.pumpAndSettle();
}

void main() {
  testWidgets('menampilkan tiap dimensi dengan skor dan Why-nya', (t) async {
    final layanan = LayananPalsu()
      ..dasborData = const Dasbor(
        asOf: '2026-09-20',
        dimensi: [
          Dimensi(
            key: 'energy',
            nilai: 0.75,
            keyakinan: 1,
            bukti: 1,
            why: 'Energi yang kamu laporkan sendiri di check-in 2026-09-20.',
          ),
          Dimensi(
            key: 'focus',
            nilai: 0.25,
            keyakinan: 1,
            bukti: 1,
            why: 'Fokus yang kamu laporkan sendiri di check-in 2026-09-20.',
          ),
        ],
      );

    await _pasang(t, layanan);

    expect(layanan.panggilan, contains('dasbor'));
    expect(find.byKey(const Key('as-of')), findsOneWidget);
    // Dua dimensi (bukan satu angka), masing-masing dengan skor DAN Why.
    expect(find.byKey(const Key('dimensi-energy')), findsOneWidget);
    expect(find.byKey(const Key('dimensi-focus')), findsOneWidget);
    expect(find.text('Energi'), findsOneWidget);
    expect(find.text('75%'), findsOneWidget);
    expect(find.byKey(const Key('why-energy')), findsOneWidget);
    expect(
      find.text('Energi yang kamu laporkan sendiri di check-in 2026-09-20.'),
      findsOneWidget,
    );
  });

  testWidgets('tiap dimensi yang tampil membawa Why (tak ada skor telanjang)', (
    t,
  ) async {
    final layanan = LayananPalsu()
      ..dasborData = const Dasbor(
        asOf: '2026-09-20',
        dimensi: [
          Dimensi(
            key: 'energy',
            nilai: 0.5,
            keyakinan: 1,
            bukti: 1,
            why: 'Dari check-in.',
          ),
          Dimensi(
            key: 'focus',
            nilai: 0.5,
            keyakinan: 1,
            bukti: 1,
            why: 'Dari check-in.',
          ),
        ],
      );

    await _pasang(t, layanan);

    for (final key in ['energy', 'focus']) {
      final why = _whyDimensi(t, key);
      expect(why, isNotEmpty, reason: 'dimensi $key tampil tanpa Why (§28)');
    }
  });

  testWidgets('cold start meminta data, bukan menampilkan angka kosong', (
    t,
  ) async {
    await _pasang(
      t,
      LayananPalsu(),
    ); // dasborData default: as_of null, dimensi []

    expect(find.byKey(const Key('kosong')), findsOneWidget);
    expect(find.byKey(const Key('as-of')), findsNothing);
    expect(find.textContaining('check-in'), findsOneWidget);
  });
}

/// Teks Why sebuah dimensi yang sedang tampil.
String _whyDimensi(WidgetTester t, String key) {
  final w = t.widget<Text>(find.byKey(Key('why-$key')));
  return w.data ?? '';
}
