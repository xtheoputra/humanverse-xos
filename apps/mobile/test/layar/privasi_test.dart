// spec/07 6.4 — layar Privacy Center (naskah 5 §26): apa yang diketahui, izin per agent,
// ekspor, hapus. Tiap tindakan yang tak bisa dibatalkan meminta sandi LAGI.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hvx_app/layar/privasi.dart';

import 'palsu_privasi.dart';

Future<void> _pasang(
  WidgetTester t,
  LayananPrivasiPalsu layanan, {
  Future<bool> Function(String, List<int>)? simpan,
  VoidCallback? sesudahHapusAkun,
}) async {
  t.view.physicalSize = const Size(900, 2400);
  t.view.devicePixelRatio = 1;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  await t.pumpWidget(
    MaterialApp(
      home: LayarPrivasi(
        layanan: layanan,
        simpan: simpan ?? (nama, isi) async => true,
        sesudahHapusAkun: sesudahHapusAkun,
      ),
    ),
  );
  await t.pumpAndSettle();
}

Future<void> _isiSandi(WidgetTester t, String sandi) async {
  await t.enterText(find.byKey(const Key('sandi-ulang')), sandi);
  await t.tap(find.byKey(const Key('konfirmasi-sandi')));
  await t.pumpAndSettle();
}

void main() {
  testWidgets(
    'menampilkan jumlah per kategori, retensi, dan yang tidak dikumpulkan',
    (t) async {
      await _pasang(t, LayananPrivasiPalsu());

      expect(find.byKey(const Key('kategori-journal')), findsOneWidget);
      expect(find.textContaining('3 catatan'), findsOneWidget);
      expect(find.textContaining('Sampai kamu menghapusnya'), findsOneWidget);
      expect(find.textContaining('1 diturunkan sistem'), findsOneWidget);
      expect(find.text('Lokasi · Kalender'), findsOneWidget);
      // Yang tak bisa dihapus tidak punya tombol hapus — hanya alasannya.
      expect(find.byKey(const Key('hapus-audit')), findsNothing);
      expect(find.byKey(const Key('hapus-journal')), findsOneWidget);
    },
  );

  testWidgets('hapus kategori meminta sandi, lalu memuat ulang jumlahnya', (
    t,
  ) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan);

    await t.tap(find.byKey(const Key('hapus-journal')));
    await t.pumpAndSettle();
    expect(find.textContaining('permanen'), findsOneWidget);
    await _isiSandi(t, layanan.sandiBenar);

    expect(layanan.panggilan, contains('hapus journal'));
    expect(find.textContaining('6 baris dihapus'), findsOneWidget);
    expect(find.textContaining('0 catatan'), findsOneWidget);
  });

  testWidgets('sandi salah tidak menghapus apa pun dan pesannya tampil', (
    t,
  ) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan);

    await t.tap(find.byKey(const Key('hapus-journal')));
    await t.pumpAndSettle();
    await _isiSandi(t, 'bukan-sandinya');

    expect(find.text('Sandi salah.'), findsOneWidget);
    expect(layanan.jurnal, 3);
  });

  testWidgets('batal di dialog sandi tidak memanggil server', (t) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan);

    await t.tap(find.byKey(const Key('hapus-journal')));
    await t.pumpAndSettle();
    await t.tap(find.text('Batal'));
    await t.pumpAndSettle();

    expect(layanan.panggilan.where((p) => p.startsWith('hapus')), isEmpty);
  });

  testWidgets('ekspor: sandi → minta → unduh → simpan berkas', (t) async {
    final layanan = LayananPrivasiPalsu();
    String? namaBerkas;
    await _pasang(
      t,
      layanan,
      simpan: (nama, isi) async {
        namaBerkas = nama;
        return true;
      },
    );

    await t.tap(find.byKey(const Key('ekspor')));
    await t.pumpAndSettle();
    await _isiSandi(t, layanan.sandiBenar);

    expect(layanan.panggilan, containsAllInOrder(['ekspor', 'unduh e1']));
    expect(namaBerkas, 'humanverse-export.json');
    expect(find.byKey(const Key('pesan-ekspor')), findsOneWidget);
    expect(find.textContaining('tersimpan (2 KB)'), findsOneWidget);
  });

  testWidgets('platform tanpa simpan berkas mengatakannya, bukan diam', (
    t,
  ) async {
    final layanan = LayananPrivasiPalsu();
    await _pasang(t, layanan, simpan: (nama, isi) async => false);

    await t.tap(find.byKey(const Key('ekspor')));
    await t.pumpAndSettle();
    await _isiSandi(t, layanan.sandiBenar);

    expect(find.textContaining('belum bisa menyimpan berkas'), findsOneWidget);
  });

  testWidgets(
    'izin per agent: sensitif ditandai, perubahan dikirim dan ditampilkan',
    (t) async {
      final layanan = LayananPrivasiPalsu();
      await _pasang(t, layanan);

      await t.tap(find.byKey(const Key('agent-coach-agent')));
      await t.pumpAndSettle();
      expect(find.text('membaca mood · sensitif'), findsOneWidget);

      await t.tap(find.byKey(const Key('izin-coach-agent-mood-read')));
      await t.pumpAndSettle();
      await t.tap(find.text('Tolak').last);
      await t.pumpAndSettle();

      expect(
        layanan.panggilan,
        contains('tetapkan coach-agent mood read deny'),
      );
      final pilih = t.widget<DropdownButton<String>>(
        find.byKey(const Key('izin-coach-agent-mood-read')),
      );
      expect(pilih.value, 'deny');
    },
  );

  testWidgets(
    'hapus akun dengan sandi menutup layar dan memanggil sesudahHapusAkun',
    (t) async {
      final layanan = LayananPrivasiPalsu();
      var keluar = false;
      await _pasang(t, layanan, sesudahHapusAkun: () => keluar = true);

      await t.tap(find.byKey(const Key('hapus-akun')));
      await t.pumpAndSettle();
      expect(find.textContaining('30 hari'), findsWidgets);
      await _isiSandi(t, layanan.sandiBenar);

      expect(layanan.panggilan, contains('hapus-akun'));
      expect(keluar, isTrue);
    },
  );
}
