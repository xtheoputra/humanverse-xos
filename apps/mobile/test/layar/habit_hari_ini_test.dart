// spec/07 2.7 — layar V0 pertama: daftar habit + tandai selesai, dipakai lewat
// ketukan (bukan curl). Layanan palsu mencatat apa yang layar KIRIM.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/model.dart';
import 'package:hvx_app/layar/habit_hari_ini.dart';

import 'palsu.dart';

const tigaTier = [
  Tier(label: 'Workout 60 menit', menit: 60),
  Tier(label: 'Workout 30 menit', menit: 30),
  Tier(label: 'Mobility 10 menit', menit: 10),
];

Habit _habit(
  String id,
  String judul, {
  List<Tier> tier = const [],
  int? saran,
  int? energi,
}) => Habit(
  id: id,
  judul: judul,
  periode: 'day',
  target: 1,
  tier: tier,
  hari: HariHabit(forDate: '2026-09-21', energi: energi, tierDisarankan: saran),
);

Future<void> _pasang(
  WidgetTester t,
  LayananPalsu layanan, {
  VoidCallback? keluar,
}) async {
  await t.pumpWidget(
    MaterialApp(
      home: LayarHabitHariIni(
        layanan: layanan,
        sesudahKeluar: keluar ?? () {},
        // Senin 06:30 waktu LOKAL — di UTC+7 itu masih Minggu di UTC.
        jam: () => DateTime(2026, 9, 21, 6, 30),
      ),
    ),
  );
  await t.pumpAndSettle();
}

void main() {
  testWidgets('menampilkan habit tanggal LOKAL hari ini', (t) async {
    final layanan = LayananPalsu(
      habit: [_habit('h1', 'Minum air'), _habit('h2', 'Baca')],
    );

    await _pasang(t, layanan);

    expect(find.text('2026-09-21'), findsOneWidget);
    expect(find.text('Minum air'), findsOneWidget);
    expect(find.text('Baca'), findsOneWidget);
    expect(
      layanan.panggilan,
      containsAll(['habit 2026-09-21', 'checkin 2026-09-21']),
    );
  });

  testWidgets(
    'ketuk habit tanpa tier → tercatat selesai hari ini, lalu bisa dibatalkan',
    (t) async {
      final layanan = LayananPalsu(habit: [_habit('h1', 'Minum air')]);
      await _pasang(t, layanan);

      await t.tap(find.text('Minum air'));
      await t.pumpAndSettle();

      expect(layanan.panggilan, contains('selesai h1 2026-09-21 -'));
      final kotak = t.widget<CheckboxListTile>(
        find.byKey(const Key('habit-h1')),
      );
      expect(kotak.value, isTrue);
      expect(find.text('Selesai'), findsOneWidget);

      await t.tap(find.text('Minum air'));
      await t.pumpAndSettle();

      expect(layanan.panggilan, contains('batal h1 2026-09-21'));
      expect(
        t.widget<CheckboxListTile>(find.byKey(const Key('habit-h1'))).value,
        isFalse,
      );
    },
  );

  testWidgets(
    'habit bertier: saran dari energi ditampilkan beserta alasannya, tier dipilih',
    (t) async {
      final layanan = LayananPalsu(
        habit: [_habit('h1', 'Workout', tier: tigaTier, saran: 1, energi: 2)],
      );
      await _pasang(t, layanan);

      expect(
        find.text('Disarankan: Workout 30 menit (energi 2)'),
        findsOneWidget,
      );

      await t.tap(find.text('Workout'));
      await t.pumpAndSettle();
      expect(find.text('Disarankan hari ini'), findsOneWidget);
      await t.tap(find.byKey(const Key('tier-2')));
      await t.pumpAndSettle();

      expect(layanan.panggilan, contains('selesai h1 2026-09-21 2'));
      expect(find.text('Selesai — Mobility 10 menit'), findsOneWidget);
    },
  );

  testWidgets('menutup pilihan tier tanpa memilih tidak mencatat apa pun', (
    t,
  ) async {
    final layanan = LayananPalsu(
      habit: [_habit('h1', 'Workout', tier: tigaTier, saran: 0)],
    );
    await _pasang(t, layanan);

    await t.tap(find.text('Workout'));
    await t.pumpAndSettle();
    await t.tapAt(const Offset(10, 10)); // di luar lembar bawah
    await t.pumpAndSettle();

    expect(layanan.panggilan.where((p) => p.startsWith('selesai')), isEmpty);
  });

  testWidgets('energi dipilih → check-in disimpan dan daftar dimuat ulang', (
    t,
  ) async {
    final layanan = LayananPalsu(
      habit: [_habit('h1', 'Workout', tier: tigaTier, saran: 0)],
    );
    await _pasang(t, layanan);
    layanan.panggilan.clear();

    await t.tap(find.byKey(const Key('energi-1')));
    await t.pumpAndSettle();

    expect(layanan.panggilan, [
      'energi 2026-09-21 1',
      'habit 2026-09-21',
      'checkin 2026-09-21',
    ]);
    expect(
      t.widget<ChoiceChip>(find.byKey(const Key('energi-1'))).selected,
      isTrue,
    );
  });

  testWidgets('tambah habit mingguan dengan versi ringan', (t) async {
    final layanan = LayananPalsu();
    await _pasang(t, layanan);
    expect(find.byKey(const Key('kosong')), findsOneWidget);

    await t.tap(find.byKey(const Key('tambah')));
    await t.pumpAndSettle();
    await t.enterText(find.byKey(const Key('judul-habit')), 'Lari');
    await t.tap(find.byKey(const Key('periode')));
    await t.pumpAndSettle();
    await t.tap(find.text('Per minggu').last);
    await t.pumpAndSettle();
    await t.enterText(
      find.byKey(const Key('tier-habit')),
      'Lari 5 km\nJalan 20 menit\n',
    );
    await t.tap(find.byKey(const Key('simpan-habit')));
    await t.pumpAndSettle();

    expect(
      layanan.panggilan,
      contains('buat Lari week 1 Lari 5 km|Jalan 20 menit'),
    );
    expect(find.text('Lari'), findsOneWidget);
  });

  testWidgets(
    'Simpan lagi sesudah jaringan putus mengirim id YANG SAMA; isian diubah → id baru',
    (t) async {
      final layanan = LayananPalsu();
      await _pasang(t, layanan);
      await t.tap(find.byKey(const Key('tambah')));
      await t.pumpAndSettle();
      await t.enterText(find.byKey(const Key('judul-habit')), 'Lari');

      layanan.galatBerikutnya = Exception('jaringan putus');
      await t.tap(find.byKey(const Key('simpan-habit')));
      await t.pumpAndSettle();
      expect(find.text('Server tidak terjangkau. Coba lagi.'), findsOneWidget);
      layanan.galatBerikutnya = Exception('jaringan putus lagi');
      await t.tap(find.byKey(const Key('simpan-habit')));
      await t.pumpAndSettle();
      await t.enterText(find.byKey(const Key('judul-habit')), 'Lari pagi');
      await t.tap(find.byKey(const Key('simpan-habit')));
      await t.pumpAndSettle();

      final id = layanan.idHabitDikirim;
      expect(id, hasLength(3));
      expect(id[0], id[1], reason: 'percobaan ulang tindakan yang sama');
      expect(id[2], isNot(id[1]), reason: 'isian lain = tindakan lain');
      expect(find.text('Lari pagi'), findsOneWidget);
    },
  );

  testWidgets(
    'already_exists saat menyimpan = percobaan sebelumnya sudah sampai',
    (t) async {
      final layanan = LayananPalsu();
      await _pasang(t, layanan);
      await t.tap(find.byKey(const Key('tambah')));
      await t.pumpAndSettle();
      await t.enterText(find.byKey(const Key('judul-habit')), 'Lari');
      layanan.galatBerikutnya = const GalatApi(
        409,
        'already_exists',
        'Habit dengan id ini sudah ada.',
      );

      await t.tap(find.byKey(const Key('simpan-habit')));
      await t.pumpAndSettle();

      expect(find.byKey(const Key('simpan-habit')), findsNothing);
      expect(find.text('Habit dengan id ini sudah ada.'), findsNothing);
    },
  );

  testWidgets('habit yang DILEWATI tampil lain dan ketukan membatalkannya', (
    t,
  ) async {
    final dilewati = Habit(
      id: 'h1',
      judul: 'Minum air',
      periode: 'day',
      target: 1,
      tier: const [],
      hari: const HariHabit(
        forDate: '2026-09-21',
        penyelesaian: Penyelesaian(forDate: '2026-09-21', status: 'skipped'),
      ),
    );
    final layanan = LayananPalsu(habit: [dilewati]);
    await _pasang(t, layanan);

    final kotak = t.widget<CheckboxListTile>(find.byKey(const Key('habit-h1')));
    expect(
      kotak.value,
      isNull,
      reason: 'skipped bukan selesai dan bukan belum',
    );
    expect(find.textContaining('Dilewati'), findsOneWidget);

    await t.tap(find.text('Minum air'));
    await t.pumpAndSettle();

    expect(layanan.panggilan, contains('batal h1 2026-09-21'));
    expect(
      layanan.panggilan.where((p) => p.startsWith('selesai')),
      isEmpty,
      reason:
          'POST "done" ke tanggal yang sudah tercatat tidak mengubah apa pun',
    );
  });

  testWidgets('galat server tampil sebagai pesan, bukan layar rusak', (
    t,
  ) async {
    final layanan = LayananPalsu(habit: [_habit('h1', 'Minum air')]);
    await _pasang(t, layanan);
    layanan.galatBerikutnya = const GalatApi(
      422,
      'for_date_in_future',
      'Tanggal itu belum terjadi.',
    );

    await t.tap(find.text('Minum air'));
    await t.pumpAndSettle();

    expect(find.text('Tanggal itu belum terjadi.'), findsOneWidget);
  });

  testWidgets('sesi berakhir → kembali ke layar masuk', (t) async {
    final layanan = LayananPalsu(habit: [_habit('h1', 'Minum air')]);
    var keluar = 0;
    await _pasang(t, layanan, keluar: () => keluar++);
    layanan.galatBerikutnya = const SesiBerakhir();

    await t.tap(find.text('Minum air'));
    await t.pumpAndSettle();

    expect(keluar, 1);
  });

  testWidgets('tombol keluar mencabut sesi di server', (t) async {
    final layanan = LayananPalsu();
    var keluar = 0;
    await _pasang(t, layanan, keluar: () => keluar++);

    await t.tap(find.byKey(const Key('keluar')));
    await t.pumpAndSettle();

    expect(layanan.panggilan, contains('keluar'));
    expect(keluar, 1);
  });
}
