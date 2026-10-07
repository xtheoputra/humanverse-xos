// spec/07 6.2–6.4 — Privacy Center, notifikasi, dan tinjauan mingguan lewat KLIEN aplikasi
// terhadap api SUNGGUHAN (tahap smoke `tools/ci_lokal.py`):
//
//   flutter test test/ujung --dart-define=HVX_API_UJI=http://127.0.0.1:8000
//
// Uji widget memakai layanan palsu; di sini yang dibuktikan kontraknya: ringkasan menghitung
// yang sungguh tersimpan, ekspor sekali pakai, hapus kategori butuh sandi dan sungguh
// menghapus, pilihan notifikasi tersimpan. Tanpa `HVX_API_UJI` uji ini DILEWATI.
import 'dart:io';
import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/model.dart';

const _api = String.fromEnvironment('HVX_API_UJI');

void main() {
  test(
    'ringkasan → notifikasi → tinjauan → ekspor sekali pakai → hapus habit dengan sandi',
    () async {
      HttpOverrides.global = null;
      final acak = Random.secure();
      String hex(int n) =>
          List.generate(n, (_) => acak.nextInt(16).toRadixString(16)).join();
      final sandi = 'teh-pagi-${hex(20)}';
      final jaringan = http.Client();
      addTearDown(jaringan.close);
      final klien = KlienApi(dasar: Uri.parse(_api), klien: jaringan);
      await klien.daftar(
        email: 'privasi-${hex(12)}@uji.id',
        sandi: sandi,
        namaTampilan: 'Uji Privasi',
        zonaWaktu: 'Asia/Jakarta',
        versiKebijakan: 'draf-v0',
        izinkanPelatihanModel: false,
      );
      final habit = await klien.buatHabit(
        id: idBaru(),
        judul: 'Jalan pagi',
        periode: 'day',
        target: 1,
      );
      await klien.tandaiSelesai(habit.id, tanggalLokal(DateTime.now()));

      final sebelum = await klien.ringkasanPrivasi();
      expect(
        sebelum.kategori.firstWhere((k) => k.key == 'habits').jumlah,
        2,
        reason: 'habit + penyelesaiannya',
      );
      expect(sebelum.tidakDikumpulkan, contains('Lokasi'));

      final pref = await klien.ubahNotifikasi(jenis: {'weekly_review': false});
      expect(
        pref.jenis.firstWhere((j) => j.key == 'weekly_review').nyala,
        isFalse,
      );
      expect(pref.dikirim, isFalse);
      expect((await klien.notifikasi()).jenis.length, 4);

      final tinjauan = await klien.tinjauanMingguan();
      expect(tinjauan.pertanyaan, hasLength(5));

      final ekspor = await klien.mintaEkspor(sandi);
      final isi = await klien.unduhEkspor(ekspor.id);
      expect(String.fromCharCodes(isi), contains('Jalan pagi'));
      await expectLater(
        klien.unduhEkspor(ekspor.id),
        throwsA(isA<GalatApi>().having((g) => g.status, 'status', 410)),
      );

      await expectLater(
        klien.hapusData('habits', 'bukan-sandinya-${hex(4)}'),
        throwsA(isA<GalatApi>().having((g) => g.status, 'status', 403)),
      );
      final terhapus = await klien.hapusData('habits', sandi);
      expect(terhapus['habits'], 1);
      final sesudah = await klien.ringkasanPrivasi();
      expect(
        sesudah.kategori.firstWhere((k) => k.key == 'habits').jumlah,
        0,
        reason: 'hapus kategori tidak menghapus',
      );
      await klien.keluar();
    },
    skip: _api.isEmpty
        ? 'tanpa api hidup: --dart-define=HVX_API_UJI=http://127.0.0.1:<port>'
        : false,
  );
}
