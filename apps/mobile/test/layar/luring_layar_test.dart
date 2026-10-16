// spec/07 6.6 — layar habit saat jaringan putus: catatan menunggu terlihat, tidak
// dibuang diam-diam, dan terkirim begitu jaringan pulih. `LayananLuring` yang SAMA
// dengan yang dirakit `main.dart`, di atas layanan palsu yang bisa diputus.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/luring.dart';
import 'package:hvx_app/api/model.dart';
import 'package:hvx_app/layar/habit_hari_ini.dart';

import 'palsu.dart';

Habit _habit(String id, String judul) => Habit(
  id: id,
  judul: judul,
  periode: 'day',
  target: 1,
  tier: const [],
  hari: const HariHabit(forDate: '2026-09-21'),
);

Future<(LayananPalsu, LayananLuring)> _pasang(
  WidgetTester t, {
  VoidCallback? keluar,
}) async {
  final palsu = LayananPalsu(habit: [_habit('h1', 'Minum air')]);
  final luring = LayananLuring(palsu);
  await t.pumpWidget(
    MaterialApp(
      home: LayarHabitHariIni(
        layanan: luring,
        luring: luring,
        sesudahKeluar: keluar ?? () {},
        jam: () => DateTime(2026, 9, 21, 6, 30),
      ),
    ),
  );
  await t.pumpAndSettle();
  return (palsu, luring);
}

Iterable<String> _selesai(LayananPalsu palsu) =>
    palsu.panggilan.where((p) => p.startsWith('selesai'));

void main() {
  testWidgets(
    'tanpa jaringan: habit tercentang dan spanduk menyebut yang menunggu; sesudah tersambung, Sinkronkan mengirimnya',
    (t) async {
      final (palsu, _) = await _pasang(t);
      expect(find.byKey(const Key('spanduk-luring')), findsNothing);
      palsu.putus = true;

      await t.tap(find.text('Minum air'));
      await t.pumpAndSettle();

      expect(
        t.widget<CheckboxListTile>(find.byKey(const Key('habit-h1'))).value,
        isTrue,
      );
      expect(find.byKey(const Key('spanduk-luring')), findsOneWidget);
      expect(
        find.text('1 catatan menunggu sinkron'),
        findsOneWidget,
        reason: 'spanduk harus menyebut catatan yang menunggu',
      );
      expect(_selesai(palsu), isEmpty, reason: 'belum ada yang sampai');

      palsu.putus = false;
      await t.tap(find.byKey(const Key('sinkron')));
      await t.pumpAndSettle();

      expect(_selesai(palsu), ['selesai h1 2026-09-21 -']);
      expect(find.byKey(const Key('spanduk-menunggu')), findsNothing);
      expect(find.byKey(const Key('spanduk-luring')), findsNothing);
      expect(
        t.widget<CheckboxListTile>(find.byKey(const Key('habit-h1'))).value,
        isTrue,
      );
    },
  );

  testWidgets(
    'keluar dengan catatan yang tak bisa terkirim: ditanya dulu — "Tetap di sini" tidak keluar, "Keluar dan buang" keluar',
    (t) async {
      var keluar = 0;
      final (palsu, luring) = await _pasang(t, keluar: () => keluar++);
      palsu.putus = true;
      await t.tap(find.text('Minum air'));
      await t.pumpAndSettle();

      await t.tap(find.byKey(const Key('keluar')));
      await t.pumpAndSettle();

      expect(
        find.text('Keluar sekarang?'),
        findsOneWidget,
        reason: 'keluar harus bertanya dulu bila ada catatan yang tak terkirim',
      );
      expect(find.textContaining('1 catatan belum terkirim'), findsOneWidget);
      await t.tap(find.byKey(const Key('tetap-masuk')));
      await t.pumpAndSettle();
      expect(keluar, 0);
      expect(palsu.panggilan, isNot(contains('keluar')));
      expect(luring.status.value.menunggu, 1);

      await t.tap(find.byKey(const Key('keluar')));
      await t.pumpAndSettle();
      await t.tap(find.byKey(const Key('keluar-buang')));
      await t.pumpAndSettle();

      expect(keluar, 1);
      expect(palsu.panggilan, contains('keluar'));
      expect(luring.status.value.menunggu, 0);
    },
  );

  testWidgets(
    'keluar dengan catatan yang BISA terkirim: dikirim dulu, tanpa pertanyaan',
    (t) async {
      var keluar = 0;
      final (palsu, _) = await _pasang(t, keluar: () => keluar++);
      palsu.putus = true;
      await t.tap(find.text('Minum air'));
      await t.pumpAndSettle();
      palsu.putus = false; // jaringan pulih sebelum pengguna keluar

      await t.tap(find.byKey(const Key('keluar')));
      await t.pumpAndSettle();

      expect(
        find.text('Keluar sekarang?'),
        findsNothing,
        reason: 'catatan yang bisa terkirim harus dikirim dulu, tanpa bertanya',
      );
      expect(_selesai(palsu), ['selesai h1 2026-09-21 -']);
      expect(keluar, 1);
    },
  );

  testWidgets(
    'catatan yang DITOLAK server tidak hilang diam-diam: spanduk menyebutnya sampai diakui',
    (t) async {
      final (palsu, _) = await _pasang(t);
      palsu.putus = true;
      await t.tap(find.text('Minum air'));
      await t.pumpAndSettle();
      palsu.putus = false;
      palsu.galatBerikutnya = const GalatApi(
        404,
        'habit_not_found',
        'Habit tidak ditemukan.',
      );

      await t.tap(find.byKey(const Key('sinkron')));
      await t.pumpAndSettle();

      expect(
        find.byKey(const Key('spanduk-ditolak')),
        findsOneWidget,
        reason: 'catatan yang ditolak harus terlihat',
      );
      expect(find.text('1 catatan ditolak server'), findsOneWidget);
      expect(find.byKey(const Key('spanduk-menunggu')), findsNothing);

      await t.tap(find.byKey(const Key('akui-ditolak')));
      await t.pumpAndSettle();

      expect(find.byKey(const Key('spanduk-ditolak')), findsNothing);
    },
  );

  testWidgets(
    'habit baru tanpa jaringan: dialog menjelaskan dan isiannya tetap',
    (t) async {
      final (palsu, _) = await _pasang(t);
      palsu.putus = true;

      await t.tap(find.byKey(const Key('tambah')));
      await t.pumpAndSettle();
      await t.enterText(find.byKey(const Key('judul-habit')), 'Baca');
      await t.tap(find.byKey(const Key('simpan-habit')));
      await t.pumpAndSettle();

      expect(
        find.textContaining('Tidak ada jaringan'),
        findsOneWidget,
        reason: 'dialog habit baru harus menjelaskan bahwa jaringan dibutuhkan',
      );
      expect(find.byKey(const Key('judul-habit')), findsOneWidget);
      expect(palsu.panggilan.where((p) => p.startsWith('buat')), isEmpty);
    },
  );

  testWidgets(
    'energi tanpa jaringan: pesan jaringan, bukan "server tidak terjangkau"',
    (t) async {
      final (palsu, _) = await _pasang(t);
      palsu.putus = true;

      await t.tap(find.byKey(const Key('energi-3')));
      await t.pumpAndSettle();

      expect(
        find.text('Tidak ada jaringan. Coba lagi saat tersambung.'),
        findsWidgets,
        reason: 'galat jaringan harus dijelaskan sebagai jaringan',
      );
    },
  );
}
