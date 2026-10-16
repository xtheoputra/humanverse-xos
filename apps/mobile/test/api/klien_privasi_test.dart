// KlienApi lawan kontrak spec/04 Privacy Center (6.4), notifikasi (6.3), tinjauan (6.2) —
// tanpa server: `MockClient` membaca tiap permintaan yang dikirim.
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:hvx_app/api/klien.dart';

final dasar = Uri.parse('http://api.uji');

http.Response _json(Object? isi, [int status = 200]) => http.Response(
  jsonEncode(isi),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

Map<String, dynamic> _akun() => {
  'user': {'id': 'u1', 'email': 'a@uji.id', 'status': 'active'},
  'tokens': {
    'access_token': 'hvxa_akses',
    'refresh_token': 'hvxr_segar',
    'token_type': 'bearer',
    'expires_in': 900,
  },
};

Map<String, dynamic> _pref({
  Object? jamTenang = const {'start': '22:00', 'end': '07:00'},
}) => {
  'types': [
    {
      'key': 'weekly_review',
      'label': 'Tinjauan mingguan siap',
      'enabled': true,
      'default': true,
      'required': false,
    },
  ],
  'quiet_hours': jamTenang,
  'daily_cap': 10,
  'delivery': 'none',
};

/// Klien yang sudah masuk; `jawab` menjawab tiap permintaan SESUDAH login.
Future<(KlienApi, List<http.Request>)> _klien(
  Future<http.Response> Function(http.Request) jawab,
) async {
  final dikirim = <http.Request>[];
  final klien = KlienApi(
    dasar: dasar,
    klien: MockClient((r) async {
      if (r.url.path == '/v1/auth/login') return _json(_akun());
      dikirim.add(r);
      return jawab(r);
    }),
  );
  await klien.masuk(email: 'a@uji.id', sandi: 'sandi-yang-panjang');
  return (klien, dikirim);
}

void main() {
  test(
    'ringkasan membaca kategori dan yang tidak dikumpulkan, bersesi',
    () async {
      final (klien, dikirim) = await _klien(
        (r) async => _json({
          'categories': [
            {
              'key': 'journal',
              'label': 'Jurnal',
              'count': 2,
              'derived_count': 1,
              'tables': {'journal_entries': 2},
              'deletable': true,
              'retention': 'Sampai kamu menghapusnya.',
              'why_not_deletable': null,
            },
          ],
          'not_collected': [
            {'key': 'location', 'label': 'Lokasi'},
          ],
        }),
      );

      final r = await klien.ringkasanPrivasi();

      expect(dikirim.single.url.path, '/v1/privacy/summary');
      expect(dikirim.single.headers['Authorization'], 'Bearer hvxa_akses');
      expect(r.kategori.single.jumlah, 2);
      expect(r.kategori.single.turunan, 1);
      expect(r.tidakDikumpulkan, ['Lokasi']);
    },
  );

  test(
    'ekspor: sandi di BADAN, unduhan di jalur tanpa rahasia dan bersesi',
    () async {
      final (klien, dikirim) = await _klien((r) async {
        if (r.url.path == '/v1/privacy/export') {
          return _json({
            'export_id': 'e1',
            'status': 'ready',
            'expires_at': '2026-10-07T12:00:00Z',
            'download_url': null,
          }, 202);
        }
        return http.Response('{"format":"humanverse-export"}', 200);
      });

      final e = await klien.mintaEkspor('sandi-ulang');
      final isi = await klien.unduhEkspor(e.id);

      expect(dikirim.first.method, 'POST');
      expect(jsonDecode(dikirim.first.body), {'password': 'sandi-ulang'});
      expect(dikirim.last.url.path, '/v1/privacy/export/e1/download');
      expect(
        dikirim.last.url.query,
        isEmpty,
        reason: 'rahasia di URL (ASVS V8.3.1)',
      );
      expect(dikirim.last.headers['Authorization'], 'Bearer hvxa_akses');
      expect(utf8.decode(isi), contains('humanverse-export'));
    },
  );

  test('hapus kategori: DELETE berbadan sandi, jawaban per tabel', () async {
    final (klien, dikirim) = await _klien(
      (r) async => _json({
        'category': 'journal',
        'deleted': {'journal_entries': 2, 'events': 2},
      }, 202),
    );

    final terhapus = await klien.hapusData('journal', 'sandi-ulang');

    expect(dikirim.single.method, 'DELETE');
    expect(dikirim.single.url.path, '/v1/privacy/data/journal');
    expect(jsonDecode(dikirim.single.body), {'password': 'sandi-ulang'});
    expect(terhapus, {'journal_entries': 2, 'events': 2});
  });

  test('sandi salah menjadi GalatApi 403, sesi TIDAK dilupakan', () async {
    final (klien, _) = await _klien(
      (r) async => _json({
        'error': {'code': 'invalid_credentials', 'message': 'Sandi salah.'},
      }, 403),
    );

    await expectLater(
      klien.hapusData('journal', 'salah'),
      throwsA(
        isA<GalatApi>().having((g) => g.kode, 'kode', 'invalid_credentials'),
      ),
    );
    expect(klien.sudahMasuk, isTrue);
  });

  test(
    'hapus akun melupakan token — server sudah mencabut semua sesi',
    () async {
      final (klien, dikirim) = await _klien(
        (r) async =>
            _json({'deletion_scheduled_at': '2026-11-06T00:00:00Z'}, 202),
      );

      final jadwal = await klien.hapusAkun('sandi-ulang');

      expect(dikirim.single.url.path, '/v1/me');
      expect(dikirim.single.method, 'DELETE');
      expect(jadwal, '2026-11-06T00:00:00Z');
      expect(klien.sudahMasuk, isFalse);
    },
  );

  test(
    'izin per agent: PUT ke jalur agent/scope dengan aksi & keputusan',
    () async {
      final (klien, dikirim) = await _klien(
        (r) async => _json({
          'scope': 'mood',
          'action': 'read',
          'decision': 'deny',
          'source': 'user',
          'expires_at': null,
          'sensitive': true,
          'confirm_each_time': false,
        }),
      );

      final baru = await klien.tetapkanIzin(
        'coach-agent',
        'mood',
        'read',
        'deny',
      );

      expect(dikirim.single.method, 'PUT');
      expect(
        dikirim.single.url.path,
        '/v1/privacy/permissions/agent/coach-agent/mood',
      );
      expect(jsonDecode(dikirim.single.body), {
        'action': 'read',
        'decision': 'deny',
      });
      expect(baru.keputusan, 'deny');
      expect(baru.sensitif, isTrue);
    },
  );

  test(
    'notifikasi: PATCH hanya yang diubah; jam tenang dihapus = null eksplisit',
    () async {
      final (klien, dikirim) = await _klien(
        (r) async => _json(
          _pref(jamTenang: r.method == 'PATCH' ? null : _pref()['quiet_hours']),
        ),
      );

      final awal = await klien.notifikasi();
      final tanpa = await klien.ubahNotifikasi(hapusJamTenang: true);
      await klien.ubahNotifikasi(jenis: {'weekly_review': false});

      expect(awal.dikirim, isFalse, reason: 'V0 tidak mengirim (A-28)');
      expect(awal.jamTenang?.mulai, '22:00');
      expect(jsonDecode(dikirim[1].body), {'quiet_hours': null});
      expect(tanpa.jamTenang, isNull);
      expect(jsonDecode(dikirim[2].body), {
        'types': {'weekly_review': false},
      });
    },
  );

  test(
    'tinjauan mingguan: tanpa minggu = berjalan; dengan minggu = ?week=',
    () async {
      final (klien, dikirim) = await _klien(
        (r) async => _json({
          'week': r.url.queryParameters['week'] ?? '2026-W41',
          'start': '2026-10-05',
          'end': '2026-10-11',
          'complete': false,
          'timezone': 'Asia/Jakarta',
          'axes': <Object>[],
          'not_measured': [
            {'key': 'finance', 'label': 'Keuangan'},
          ],
          'questions': [
            {
              'key': 'why',
              'question': 'Kenapa?',
              'stance': 'ask',
              'items': <Object>[],
              'prompt': 'Menurutmu?',
            },
          ],
          'review_version': 'tinjauan-mingguan@v1',
        }),
      );

      final kini = await klien.tinjauanMingguan();
      final lalu = await klien.tinjauanMingguan(minggu: '2026-W40');

      expect(dikirim.first.url.queryParameters, isEmpty);
      expect(dikirim.last.url.queryParameters, {'week': '2026-W40'});
      expect(kini.pertanyaan.single.bertanya, isTrue);
      expect(lalu.minggu, '2026-W40');
      expect(kini.tidakDiukur, ['Keuangan']);
    },
  );
}
