// Luring dasar (spec/07 6.6) lawan kontrak spec/04 — tanpa server sungguhan:
// `ServerPalsu` menegakkan ATURAN yang membuat antrean aman diulang
// (`(habit, tanggal)` unik: `POST` ulang → 200 dengan baris lama, `DELETE` ulang
// → 204) dan bisa memutus jaringan, menghilangkan jawaban, atau menolak habit.
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/luring.dart';

const _hari = '2026-09-24';
const _besok = '2026-09-25';

http.Response _json(Object isi, [int status = 200]) => http.Response(
  jsonEncode(isi),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

class ServerPalsu {
  /// Tidak ada permintaan yang sampai — seperti mode pesawat.
  bool putus = false;

  /// Permintaan berikutnya DITERAPKAN, lalu jaringan putus sebelum jawabannya
  /// kembali — klien tidak bisa tahu apakah catatannya sampai.
  bool hilangkanJawabanBerikutnya = false;

  /// Sesi ditolak: penyelesaian dan penyegaran token menjawab 401.
  bool tolakSesi = false;

  /// Status galat untuk habit tertentu pada rute penyelesaian (mis. 404, 503).
  final Map<String, int> galatUntuk = {};

  /// Baris yang benar-benar ada di server: `'$habit|$tanggal'` → penyelesaian.
  final Map<String, Map<String, dynamic>> baris = {};

  /// Semua percobaan, termasuk yang putus.
  final List<String> percobaan = [];

  /// Hanya penyelesaian yang SAMPAI ke server: `POST h1 2026-09-24`.
  final List<String> diterima = [];

  late final http.Client klien = MockClient(_tangani);

  Map<String, dynamic> _habit(String id, String tanggal) => {
    'id': id,
    'title': 'Habit $id',
    'period': 'day',
    'target_count': 1,
    'adaptive_tiers': <Object?>[],
    'day': {
      'for_date': tanggal,
      'completion': baris['$id|$tanggal'],
      'energy': null,
      'suggested_tier': null,
    },
  };

  Future<http.Response> _tangani(http.Request r) async {
    final path = r.url.path;
    percobaan.add('${r.method} $path');
    if (putus) throw http.ClientException('tak tersambung');
    if (path == '/v1/auth/login') {
      final email =
          (jsonDecode(r.body) as Map<String, dynamic>)['email'] as String;
      return _json({
        'user': {'id': 'u-$email', 'email': email, 'status': 'active'},
        'tokens': {
          'access_token': 'hvxa_akses',
          'refresh_token': 'hvxr_segar',
          'token_type': 'bearer',
          'expires_in': 900,
        },
      });
    }
    if (path == '/v1/auth/refresh') {
      return _json({
        'error': {'code': 'invalid_token', 'message': 'ditolak'},
      }, 401);
    }
    if (path == '/v1/auth/logout') return http.Response('', 204);
    if (path == '/v1/habits') {
      final tanggal = r.url.queryParameters['for_date']!;
      return _json({
        'items': [
          for (final id in ['h1', 'h2']) _habit(id, tanggal),
        ],
      });
    }
    if (path == '/v1/checkins') return _json({'items': <Object?>[]});
    final cocok = RegExp(r'^/v1/habits/(\w+)/completions(?:/([\d-]+))?$')
        .firstMatch(path);
    if (cocok == null) return http.Response('', 404);
    return _penyelesaian(r, cocok.group(1)!, cocok.group(2));
  }

  http.Response _penyelesaian(
    http.Request r,
    String habit,
    String? tanggalDel,
  ) {
    if (tolakSesi) {
      return _json({
        'error': {'code': 'invalid_token', 'message': 'kedaluwarsa'},
      }, 401);
    }
    final galat = galatUntuk[habit];
    if (galat != null) {
      return _json({
        'error': {'code': 'ditolak_uji', 'message': 'ditolak'},
      }, galat);
    }
    late final http.Response jawaban;
    if (r.method == 'POST') {
      final badan = jsonDecode(r.body) as Map<String, dynamic>;
      final tanggal = badan['for_date'] as String;
      diterima.add('POST $habit $tanggal');
      final lama = baris['$habit|$tanggal'];
      // Aturan spec/04: tanggal yang sudah tercatat → 200 dengan baris LAMA.
      final isi =
          lama ??
          {
            'for_date': tanggal,
            'status': badan['status'],
            'tier_used': badan['tier_used'],
          };
      baris['$habit|$tanggal'] = isi;
      jawaban = _json(isi, lama == null ? 201 : 200);
    } else {
      diterima.add('DELETE $habit $tanggalDel');
      baris.remove('$habit|$tanggalDel');
      jawaban = http.Response('', 204);
    }
    if (hilangkanJawabanBerikutnya) {
      hilangkanJawabanBerikutnya = false;
      throw http.ClientException('jawaban hilang di jalan');
    }
    return jawaban;
  }
}

/// Masuk, lalu muat daftar SEKALI selagi tersambung — tampilan luring bergantung
/// pada jawaban server terakhir.
Future<LayananLuring> _siap(
  ServerPalsu s, {
  String email = 'a@uji.id',
  bool muat = true,
}) async {
  final luring = LayananLuring(
    KlienApi(dasar: Uri.parse('http://api.uji'), klien: s.klien),
  );
  await luring.masuk(email: email, sandi: 'x');
  if (muat) await luring.habitPada(_hari);
  return luring;
}

void main() {
  test('tanpa jaringan: tandai selesai menunggu di antrean, daftar menampilkannya, server belum menerima apa pun', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;

    final p = await luring.tandaiSelesai('h1', _hari, tier: 1);

    expect(p.status, 'done');
    expect(p.tierDipakai, 1);
    expect(
      luring.status.value.menunggu,
      1,
      reason: 'catatan harus menunggu saat jaringan putus',
    );
    expect(luring.status.value.luring, isTrue);
    expect(s.baris, isEmpty);
    final daftar = await luring.habitPada(_hari);
    expect(
      daftar.firstWhere((h) => h.id == 'h1').selesaiHariItu,
      isTrue,
      reason: 'daftar luring harus menampilkan catatan yang menunggu',
    );
    expect(
      daftar.firstWhere((h) => h.id == 'h1').hari!.penyelesaian!.tierDipakai,
      1,
    );
    expect(daftar.firstWhere((h) => h.id == 'h2').selesaiHariItu, isFalse);
  });

  test('jaringan kembali: sinkron mengirim catatan TEPAT SEKALI dan mengosongkan antrean', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari, tier: 1);
    s.putus = false;

    await luring.sinkron();
    await luring.sinkron(); // antrean kosong: tak ada yang dikirim lagi

    expect(s.diterima, ['POST h1 $_hari']);
    expect(s.baris, hasLength(1));
    expect(s.baris['h1|$_hari']!['tier_used'], 1);
    expect(luring.status.value.menunggu, 0);
    expect(luring.status.value.luring, isFalse);
  });

  test('jawaban yang hilang di jalan: catatan dikirim LAGI, tetap SATU baris di server', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.hilangkanJawabanBerikutnya = true;

    await luring.tandaiSelesai('h1', _hari, tier: 0);

    // Server sudah menerimanya, klien tidak tahu → masih menunggu.
    expect(s.baris, hasLength(1));
    expect(
      luring.status.value.menunggu,
      1,
      reason: 'catatan yang jawabannya hilang harus tetap menunggu',
    );

    await luring.sinkron();

    expect(s.diterima, ['POST h1 $_hari', 'POST h1 $_hari']);
    expect(s.baris, hasLength(1), reason: 'kirim ulang bukan baris kedua');
    expect(luring.status.value.menunggu, 0);
  });

  test('urutan dijaga: batal lalu selesai pada tanggal yang sama dikirim DELETE dulu, baru POST', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.batalkanSelesai('h1', _hari);
    await luring.tandaiSelesai('h1', _hari);
    expect(
      (await luring.habitPada(_hari))
          .firstWhere((h) => h.id == 'h1')
          .selesaiHariItu,
      isTrue,
      reason: 'yang terakhir menang di tampilan luring',
    );
    s.putus = false;

    await luring.sinkron();

    expect(s.diterima, [
      'DELETE h1 $_hari',
      'POST h1 $_hari',
    ], reason: 'urutan antrean harus dijaga');
    expect(s.baris, hasLength(1));
  });

  test('batal membuang catatan selesai yang belum terkirim pada (habit, tanggal) yang sama', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    await luring.batalkanSelesai('h1', _hari);
    expect(
      luring.status.value.menunggu,
      1,
      reason: 'batal harus membuang selesai yang belum terkirim',
    );
    s.putus = false;

    await luring.sinkron();

    expect(s.diterima, ['DELETE h1 $_hari']);
    expect(s.baris, isEmpty);
  });

  test('batal hanya membuang catatan (habit, tanggal) yang sama — habit dan tanggal lain tetap', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    await luring.tandaiSelesai('h2', _hari);
    await luring.tandaiSelesai('h1', _besok);
    await luring.batalkanSelesai('h1', _hari);
    s.putus = false;

    await luring.sinkron();

    expect(s.diterima, [
      'POST h2 $_hari',
      'POST h1 $_besok',
      'DELETE h1 $_hari',
    ], reason: 'batal hanya boleh membuang catatan (habit, tanggal) yang sama');
  });

  test('ditolak 4xx: catatan itu dibuang dan DIHITUNG, yang di belakangnya tetap terkirim', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    await luring.tandaiSelesai('h2', _hari);
    s.putus = false;
    s.galatUntuk['h1'] = 404; // habit-nya sudah dihapus di perangkat lain

    await luring.sinkron();

    expect(s.diterima, [
      'POST h2 $_hari',
    ], reason: 'catatan yang ditolak tidak boleh menahan yang di belakangnya');
    expect(luring.status.value.menunggu, 0);
    expect(
      luring.status.value.ditolak,
      1,
      reason: 'penolakan harus terlihat di status',
    );
    luring.akuiDitolak();
    expect(
      luring.status.value.ditolak,
      0,
      reason: 'pengakuan harus mengosongkan penolakan di status',
    );
  });

  test('server sakit (5xx): seluruh antrean ditahan tanpa dibuang, dicoba lagi sesudahnya dengan urutan sama', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    await luring.tandaiSelesai('h2', _hari);
    s.putus = false;
    s.galatUntuk['h1'] = 503;

    await luring.sinkron();

    expect(
      luring.status.value.menunggu,
      2,
      reason: 'server sakit harus menahan antrean, bukan membuangnya',
    );
    expect(luring.status.value.ditolak, 0);
    expect(s.diterima, isEmpty);

    s.galatUntuk.clear();
    await luring.sinkron();

    expect(s.diterima, ['POST h1 $_hari', 'POST h2 $_hari']);
    expect(luring.status.value.menunggu, 0);
  });

  test('masuk sebagai akun LAIN membuang antrean; masuk lagi sebagai akun yang sama mempertahankannya', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    s.putus = false;

    await luring.masuk(email: 'a@uji.id', sandi: 'x');
    expect(
      luring.status.value.menunggu,
      1,
      reason: 'akun yang sama harus mempertahankan antreannya',
    );

    await luring.masuk(email: 'b@uji.id', sandi: 'x');
    expect(
      luring.status.value.menunggu,
      0,
      reason: 'catatan akun lain tidak boleh diwarisi',
    );
    await luring.sinkron();
    expect(s.diterima, isEmpty, reason: 'catatan akun A tak boleh sampai di B');
  });

  test('keluar membuang antrean dan tampilan akun itu', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    s.putus = false;

    await luring.keluar();

    expect(
      luring.status.value,
      const StatusAntrean(),
      reason: 'keluar harus membuang antrean',
    );
    await luring.masuk(email: 'a@uji.id', sandi: 'x');
    await luring.sinkron();
    expect(s.diterima, isEmpty);
  });

  test('sinkron serentak: tiap catatan terbang SEKALI', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    await luring.tandaiSelesai('h2', _hari);
    s.putus = false;

    await Future.wait([luring.sinkron(), luring.sinkron(), luring.sinkron()]);

    expect(s.diterima, [
      'POST h1 $_hari',
      'POST h2 $_hari',
    ], reason: 'satu catatan terbang sekali walau sinkron dipanggil serentak');
    expect(luring.status.value.menunggu, 0);
  });

  test(
    'catatan yang masuk selagi putaran kirim berjalan ikut terkirim',
    () async {
      final s = ServerPalsu();
      final luring = await _siap(s);
      s.putus = true;
      await luring.tandaiSelesai('h1', _hari);
      s.putus = false;

      final pertama = luring.sinkron();
      await luring.tandaiSelesai('h2', _hari); // masuk di tengah putaran
      await pertama;

      expect(s.diterima, [
        'POST h1 $_hari',
        'POST h2 $_hari',
      ], reason: 'catatan yang masuk di tengah putaran harus ikut terkirim');
      expect(luring.status.value.menunggu, 0);
    },
  );

  test(
    'tanpa jawaban server sebelumnya, daftar luring gagal jujur (bukan kosong)',
    () async {
      final s = ServerPalsu();
      final luring = await _siap(s, muat: false);
      s.putus = true;

      await expectLater(luring.habitPada(_hari), throwsA(isA<JaringanPutus>()));
      await expectLater(
        luring.checkinPada(_hari),
        throwsA(isA<JaringanPutus>()),
      );
    },
  );

  test('sinkron baru saja gagal karena jaringan: daftar luring TIDAK menunggu server sekali lagi', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.putus = true;
    await luring.tandaiSelesai('h1', _hari);
    s.percobaan.clear();

    await luring.habitPada(_hari);

    expect(
      s.percobaan,
      ['POST /v1/habits/h1/completions'],
      reason: 'jangan menunggu server sekali lagi sesudah sinkron gagal karena jaringan',
    );
  });

  test('check-in luring: jawaban terakhir server dipakai', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    await luring.checkinPada(_hari);
    s.putus = true;

    expect(await luring.checkinPada(_hari), isNull);
    expect(luring.status.value.luring, isTrue);
  });

  test(
    'habit baru dan energi TIDAK diantre: gagal sebagai JaringanPutus',
    () async {
      final s = ServerPalsu();
      final luring = await _siap(s);
      s.putus = true;

      await expectLater(
        luring.buatHabit(id: 'x', judul: 'Baru', periode: 'day', target: 1),
        throwsA(isA<JaringanPutus>()),
      );
      await expectLater(
        luring.simpanEnergi(_hari, 3),
        throwsA(isA<JaringanPutus>()),
      );
      expect(luring.status.value.menunggu, 0);
      expect(
        luring.status.value.luring,
        isTrue,
        reason: 'galat jaringan harus menandai keadaan luring',
      );
    },
  );

  test('sesi berakhir saat mengirim: SesiBerakhir diteruskan, catatan TETAP menunggu', () async {
    final s = ServerPalsu();
    final luring = await _siap(s);
    s.tolakSesi = true;

    await expectLater(
      luring.tandaiSelesai('h1', _hari),
      throwsA(isA<SesiBerakhir>()),
    );
    expect(luring.status.value.menunggu, 1);

    // Masuk lagi sebagai akun yang SAMA: catatan itu masih milik pengguna ini.
    s.tolakSesi = false;
    await luring.masuk(email: 'a@uji.id', sandi: 'x');
    await luring.sinkron();

    expect(s.diterima, ['POST h1 $_hari']);
    expect(luring.status.value.menunggu, 0);
  });
}
