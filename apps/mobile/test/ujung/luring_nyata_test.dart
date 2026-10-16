// spec/07 6.6 — luring dasar lawan api SUNGGUHAN: habit ditandai tanpa jaringan,
// jawaban server hilang di tengah jalan, catatan dikirim LAGI — dan server tetap
// memegang SATU penyelesaian. Buktinya dari sisi server (sesi saksi lain), bukan
// dari keadaan antrean.
//
// `luring.dart` memakai `package:flutter/foundation.dart`, jadi uji ini berjalan
// di bawah `flutter test` (bukan `dart run tool/ujung_ke_ujung.dart`); tahap smoke
// `tools/ci_lokal.py` menjalankan seluruh `test/ujung`:
//
//   flutter test test/ujung --dart-define=HVX_API_UJI=http://127.0.0.1:8000
//
// Tanpa `HVX_API_UJI` uji ini DILEWATI dengan alasan tertulis, bukan lulus diam.
import 'dart:io';
import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/luring.dart';
import 'package:hvx_app/api/model.dart';

const _api = String.fromEnvironment('HVX_API_UJI');

/// Jaringan nyata yang bisa diputus atau dibuat kehilangan satu jawaban.
class _JaringanBisaPutus extends http.BaseClient {
  _JaringanBisaPutus(this._dalam);

  final http.Client _dalam;

  /// Tak ada permintaan yang sampai.
  bool putus = false;

  /// Permintaan berikutnya SAMPAI dan diproses server, tetapi jawabannya hilang.
  bool hilangkanJawabanBerikutnya = false;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    if (putus) throw http.ClientException('tak tersambung');
    final jawaban = await _dalam.send(request);
    if (hilangkanJawabanBerikutnya) {
      hilangkanJawabanBerikutnya = false;
      await jawaban.stream.drain<void>();
      throw http.ClientException('jawaban hilang di jalan');
    }
    return jawaban;
  }
}

void main() {
  test(
    'tandai selesai tanpa jaringan → jawaban hilang → kirim ulang: SATU penyelesaian di server',
    () async {
      // flutter_test mengganti HttpClient dengan tiruan yang menjawab 400.
      HttpOverrides.global = null;
      final acak = Random.secure();
      String hex(int n) =>
          List.generate(n, (_) => acak.nextInt(16).toRadixString(16)).join();
      final email = 'luring-${hex(12)}@uji.id';
      final sandi = 'kopi-malam-${hex(20)}';
      final dasar = Uri.parse(_api);

      final saksi = KlienApi(dasar: dasar);
      await saksi.daftar(
        email: email,
        sandi: sandi,
        namaTampilan: 'Uji Luring',
        zonaWaktu: 'Asia/Jakarta',
        versiKebijakan: 'draf-v0',
        izinkanPelatihanModel: false,
      );
      final hariIni = tanggalLokal(DateTime.now());
      final habit = await saksi.buatHabit(
        id: idBaru(),
        judul: 'Workout',
        periode: 'day',
        target: 1,
        tier: const [
          Tier(label: 'Workout 60 menit', menit: 60),
          Tier(label: 'Mobility 10 menit', menit: 10),
        ],
      );
      Future<Habit> dariServer() async =>
          (await saksi.habitPada(hariIni)).singleWhere((h) => h.id == habit.id);

      final jaringan = _JaringanBisaPutus(http.Client());
      addTearDown(jaringan.close);
      final luring = LayananLuring(KlienApi(dasar: dasar, klien: jaringan));
      await luring.masuk(email: email, sandi: sandi);
      await luring.habitPada(
        hariIni,
      ); // jawaban server terakhir = bahan tampilan luring

      jaringan.putus = true;
      await luring.tandaiSelesai(habit.id, hariIni, tier: 1);
      expect(luring.status.value.menunggu, 1);
      expect(luring.status.value.luring, isTrue);
      final tampil = (await luring.habitPada(hariIni))
          .singleWhere((h) => h.id == habit.id);
      expect(
        tampil.selesaiHariItu && tampil.hari?.penyelesaian?.tierDipakai == 1,
        isTrue,
        reason: 'tanpa jaringan layar tetap menunjukkan habit selesai (tier 1)',
      );
      expect(
        (await dariServer()).selesaiHariItu,
        isFalse,
        reason: 'server belum menerima apa pun selagi jaringan putus',
      );

      jaringan
        ..putus = false
        ..hilangkanJawabanBerikutnya = true;
      await luring.sinkron();
      expect(
        luring.status.value.menunggu,
        1,
        reason: 'jawaban hilang: klien belum tahu, catatan tetap menunggu',
      );
      expect(
        (await dariServer()).selesaiHariItu,
        isTrue,
        reason: 'server SUDAH menerimanya walau jawabannya tak sampai',
      );

      await luring.sinkron();
      final akhir = await dariServer();
      expect(luring.status.value.menunggu, 0);
      expect(akhir.selesaiHariItu, isTrue);
      expect(
        akhir.hari?.penyelesaian?.tierDipakai,
        1,
        reason: 'kirim ulang tidak menimpa dan tidak menggandakan',
      );

      await luring.keluar();
      await saksi.keluar();
    },
    // Dilewati tanpa api hidup: --dart-define=HVX_API_UJI=http://127.0.0.1:<port>
    // (tools/ci_lokal.py tahap smoke menjalankannya terhadap compose).
    skip: _api.isEmpty,
  );
}
