// spec/07 6.2 — tinjauan mingguan: lima pertanyaan §31; "Kenapa?" tampil sebagai ajakan,
// bukan jawaban sistem; navigasi minggu tidak melewati minggu yang sedang berjalan.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/api/privasi.dart';
import 'package:hvx_app/layar/tinjauan.dart';

import 'palsu_privasi.dart';

Future<void> _pasang(WidgetTester t, LayananPrivasiPalsu layanan) async {
  await t.pumpWidget(
    MaterialApp(home: LayarTinjauanMingguan(layanan: layanan)),
  );
  await t.pumpAndSettle();
}

void main() {
  testWidgets('minggu berjalan: tanpa sumbu, pertanyaan menjadi ajakan', (
    t,
  ) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan);

    expect(layanan.panggilan, ['tinjauan kini']);
    expect(find.textContaining('(berjalan)'), findsOneWidget);
    expect(find.byKey(const Key('tanpa-sumbu')), findsOneWidget);
    expect(find.byKey(const Key('tanya-why')), findsOneWidget);
    expect(find.byKey(const Key('ajakan-why')), findsOneWidget);
    expect(
      find.textContaining('Belum diukur: Belajar, Keuangan'),
      findsOneWidget,
    );
    final depan = t.widget<IconButton>(find.byKey(const Key('minggu-depan')));
    expect(
      depan.onPressed,
      isNull,
      reason: 'bisa melompat ke minggu yang belum dimulai',
    );
  });

  testWidgets(
    'minggu lalu dimuat lewat navigasi, sumbu tampil dengan pembandingnya',
    (t) async {
      final layanan = LayananPrivasiPalsu();
      layanan.tinjauan = (minggu) => TinjauanMingguan(
        minggu: minggu ?? '2026-W41',
        mulai: minggu == null ? '2026-10-05' : '2026-09-28',
        selesai: minggu == null ? '2026-10-11' : '2026-10-04',
        lengkap: minggu != null,
        sumbu: [
          if (minggu != null)
            const SumbuTinjauan(
              key: 'habits',
              label: 'Habit',
              nilai: 0.5,
              sebelumnya: 0.25,
              satuan: '0-1',
              why: '3 dari 6 periode terjadwal terpenuhi.',
            ),
        ],
        tidakDiukur: const [],
        pertanyaan: const [],
      );
      await _pasang(t, layanan);

      await t.tap(find.byKey(const Key('minggu-lalu')));
      await t.pumpAndSettle();

      expect(layanan.panggilan.last, 'tinjauan 2026-W40');
      expect(find.byKey(const Key('sumbu-habits')), findsOneWidget);
      expect(find.text('50%'), findsOneWidget);
      expect(find.text('minggu lalu 25%'), findsOneWidget);
    },
  );

  test('mingguGeser mengikuti minggu ISO, termasuk pergantian tahun', () {
    expect(mingguGeser('2026-09-28', -1), '2026-W39');
    expect(mingguGeser('2026-09-28', 1), '2026-W41');
    expect(mingguGeser('2026-12-28', 1), '2027-W01'); // 2026 punya W53
    expect(mingguGeser('2027-01-04', -1), '2026-W53');
  });
}
