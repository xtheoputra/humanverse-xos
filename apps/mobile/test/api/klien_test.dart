// KlienApi lawan kontrak spec/04 — tanpa server: `MockClient` membaca tiap
// permintaan yang dikirim dan menjawab seperti api V0.
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/model.dart';

final dasar = Uri.parse('http://api.uji');

Map<String, dynamic> _token(String n) => {
  'access_token': 'hvxa_akses$n',
  'refresh_token': 'hvxr_segar$n',
  'token_type': 'bearer',
  'expires_in': 900,
};

http.Response _json(Object isi, [int status = 200]) => http.Response(
  jsonEncode(isi),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

Map<String, dynamic> _akun(String n) => {
  'user': {'id': 'u1', 'email': 'a@uji.id', 'status': 'active'},
  'tokens': _token(n),
};

Map<String, dynamic> _habit({Map<String, dynamic>? hari}) => {
  'id': 'h1',
  'goal_id': null,
  'title': 'Workout',
  'period': 'day',
  'target_count': 1,
  'schedule': <String, dynamic>{},
  'adaptive_tiers': [
    {'label': 'Workout 60 menit', 'minutes': 60},
    {'label': 'Mobility 10 menit', 'minutes': 10},
  ],
  'status': 'active',
  'created_at': '2026-09-24T00:00:00Z',
  'updated_at': '2026-09-24T00:00:00Z',
  'day': hari,
};

void main() {
  test(
    'daftar mengirim persetujuan terms, privacy, dan model_training TERSENDIRI',
    () async {
      late Map<String, dynamic> badan;
      final klien = KlienApi(
        dasar: dasar,
        klien: MockClient((r) async {
          expect(r.url.path, '/v1/auth/register');
          badan = jsonDecode(r.body) as Map<String, dynamic>;
          return _json(_akun('1'), 201);
        }),
      );

      await klien.daftar(
        email: 'a@uji.id',
        sandi: 'kuda-laut-berjalan-pelan',
        namaTampilan: 'Ana',
        zonaWaktu: 'Asia/Jakarta',
        versiKebijakan: 'draf-v0',
        izinkanPelatihanModel: false,
      );

      final setuju = badan['consents'] as Map<String, dynamic>;
      expect(setuju['terms'], isTrue);
      expect(setuju['privacy'], isTrue);
      expect(setuju['model_training'], {'granted': false});
      expect(badan['timezone'], 'Asia/Jakarta');
      expect(klien.sudahMasuk, isTrue);
    },
  );

  test(
    'habit hari ini: for_date lokal, token bearer, dan day terbaca',
    () async {
      final klien = KlienApi(
        dasar: dasar,
        klien: MockClient((r) async {
          if (r.url.path == '/v1/auth/login') return _json(_akun('1'));
          expect(r.url.path, '/v1/habits');
          expect(r.url.queryParameters, {
            'status': 'active',
            'for_date': '2026-09-24',
          });
          expect(r.headers['Authorization'], 'Bearer hvxa_akses1');
          return _json({
            'items': [
              _habit(
                hari: {
                  'for_date': '2026-09-24',
                  'completion': null,
                  'energy': 1,
                  'suggested_tier': 1,
                },
              ),
            ],
          });
        }),
      );
      await klien.masuk(email: 'a@uji.id', sandi: 'x');

      final habit = await klien.habitPada('2026-09-24');

      expect(habit.single.hari!.tierDisarankan, 1);
      expect(habit.single.hari!.energi, 1);
      expect(habit.single.tier.last.label, 'Mobility 10 menit');
      expect(habit.single.selesaiHariItu, isFalse);
    },
  );

  test('membuat habit: id buatan pemanggil = id badan = Idempotency-Key, SAMA di tiap percobaan', () async {
    final dikirim = <(String?, Object?)>[];
    final klien = KlienApi(
      dasar: dasar,
      klien: MockClient((r) async {
        if (r.url.path == '/v1/auth/login') return _json(_akun('1'));
        final badan = jsonDecode(r.body) as Map<String, dynamic>;
        dikirim.add((r.headers['Idempotency-Key'], badan['id']));
        return _json({..._habit(), 'id': badan['id']}, 201);
      }),
    );
    await klien.masuk(email: 'a@uji.id', sandi: 'x');
    final id = idBaru();

    // Percobaan kedua satu tindakan (jawaban pertama hilang di jaringan).
    await klien.buatHabit(id: id, judul: 'Lari', periode: 'day', target: 1);
    await klien.buatHabit(id: id, judul: 'Lari', periode: 'day', target: 1);

    expect(dikirim, [(id, id), (id, id)]);
  });

  test('idBaru: UUID v4 yang berbeda tiap tindakan', () {
    final a = idBaru();
    final b = idBaru();
    final pola = RegExp(
      r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    );

    expect(pola.hasMatch(a), isTrue, reason: a);
    expect(a, isNot(b));
  });

  test(
    'penyelesaian tanpa Idempotency-Key — (habit, tanggal) unik di server',
    () async {
      final kunci = <String?>[];
      final klien = KlienApi(
        dasar: dasar,
        klien: MockClient((r) async {
          if (r.url.path == '/v1/auth/login') return _json(_akun('1'));
          kunci.add(r.headers['Idempotency-Key']);
          expect(jsonDecode(r.body), {
            'for_date': '2026-09-24',
            'status': 'done',
            'tier_used': 1,
          });
          return _json({
            'for_date': '2026-09-24',
            'status': 'done',
            'tier_used': 1,
          }, 201);
        }),
      );
      await klien.masuk(email: 'a@uji.id', sandi: 'x');

      await klien.tandaiSelesai('h1', '2026-09-24', tier: 1);

      expect(kunci, [null]);
    },
  );

  test('401 SERENTAK → SATU penyegaran; token segar yang sudah dirotasi tidak dipakai ulang', () async {
    final segarDipakai = <Object?>[];
    final klien = KlienApi(
      dasar: dasar,
      klien: MockClient((r) async {
        switch (r.url.path) {
          case '/v1/auth/login':
            return _json(_akun('1'));
          case '/v1/auth/refresh':
            final badan = jsonDecode(r.body) as Map<String, dynamic>;
            segarDipakai.add(badan['refresh_token']);
            // Penyegaran lambat: permintaan kedua menerima 401 SEBELUM selesai.
            await Future<void>.delayed(const Duration(milliseconds: 20));
            return _json({'tokens': _token('${segarDipakai.length + 1}')});
        }
        if (r.headers['Authorization'] == 'Bearer hvxa_akses1') {
          return _json({
            'error': {'code': 'unauthenticated', 'message': 'x'},
          }, 401);
        }
        expect(r.headers['Authorization'], 'Bearer hvxa_akses2');
        return _json({'items': <Object>[]});
      }),
    );
    await klien.masuk(email: 'a@uji.id', sandi: 'x');

    final hasil = await Future.wait([
      klien.habitPada('2026-09-24'),
      klien.checkinPada('2026-09-24'),
      klien.habitPada('2026-09-25'),
    ]);

    expect(segarDipakai, [
      'hvxr_segar1',
    ], reason: 'token segar dipakai dua kali');
    expect(hasil, hasLength(3));
    expect(klien.sudahMasuk, isTrue);
  });

  test(
    '401 → token segar dipakai SEKALI, permintaan diulang dengan token baru',
    () async {
      var segar = 0;
      final klien = KlienApi(
        dasar: dasar,
        klien: MockClient((r) async {
          switch (r.url.path) {
            case '/v1/auth/login':
              return _json(_akun('1'));
            case '/v1/auth/refresh':
              segar++;
              expect(jsonDecode(r.body), {'refresh_token': 'hvxr_segar1'});
              return _json({'tokens': _token('2')});
          }
          if (r.headers['Authorization'] == 'Bearer hvxa_akses1') {
            return _json({
              'error': {'code': 'unauthenticated', 'message': 'x'},
            }, 401);
          }
          return _json({'items': <Object>[]});
        }),
      );
      await klien.masuk(email: 'a@uji.id', sandi: 'x');

      expect(await klien.habitPada('2026-09-24'), isEmpty);
      expect(segar, 1);
    },
  );

  test('token segar ditolak → SesiBerakhir, dan token dilupakan', () async {
    final klien = KlienApi(
      dasar: dasar,
      klien: MockClient((r) async {
        if (r.url.path == '/v1/auth/login') return _json(_akun('1'));
        return _json({
          'error': {'code': 'unauthenticated', 'message': 'x'},
        }, 401);
      }),
    );
    await klien.masuk(email: 'a@uji.id', sandi: 'x');

    await expectLater(
      klien.habitPada('2026-09-24'),
      throwsA(isA<SesiBerakhir>()),
    );
    expect(klien.sudahMasuk, isFalse);
  });

  test('galat beramplop spec/04 menjadi GalatApi berkode', () async {
    final klien = KlienApi(
      dasar: dasar,
      klien: MockClient(
        (r) async => _json({
          'error': {
            'code': 'invalid_credentials',
            'message': 'Email atau sandi salah.',
          },
        }, 401),
      ),
    );

    await expectLater(
      klien.masuk(email: 'a@uji.id', sandi: 'salah'),
      throwsA(
        isA<GalatApi>()
            .having((g) => g.kode, 'kode', 'invalid_credentials')
            .having((g) => g.pesan, 'pesan', 'Email atau sandi salah.'),
      ),
    );
  });

  test(
    'simpan energi mengirim check-in UTUH — PUT mengganti, medan lama ikut',
    () async {
      late Map<String, dynamic> badan;
      final klien = KlienApi(
        dasar: dasar,
        klien: MockClient((r) async {
          if (r.url.path == '/v1/auth/login') return _json(_akun('1'));
          expect(r.method, 'PUT');
          expect(r.url.path, '/v1/checkins/2026-09-24');
          badan = jsonDecode(r.body) as Map<String, dynamic>;
          return _json({'for_date': '2026-09-24', ...badan});
        }),
      );
      await klien.masuk(email: 'a@uji.id', sandi: 'x');
      const lama = Checkin(
        forDate: '2026-09-24',
        energi: 4,
        fokus: 3,
        jamTidur: 6.5,
      );

      await klien.simpanEnergi('2026-09-24', 2, lama: lama);

      expect(badan, {'energy': 2, 'focus': 3, 'sleep_hours': 6.5});
    },
  );

  test('sleep_hours dibaca sebagai angka JSON (spec/04, E-170)', () {
    final c = Checkin.dariJson({
      'for_date': '2026-09-24',
      'energy': 3,
      'sleep_hours': 7.5,
    });
    final bulat = Checkin.dariJson({
      'for_date': '2026-09-24',
      'sleep_hours': 8,
    });

    expect(c.jamTidur, 7.5);
    expect(bulat.jamTidur, 8.0);
    expect(c.keJsonDenganEnergi(2), {'energy': 2, 'sleep_hours': 7.5});
  });

  test('tanggal lokal perangkat, bukan tanggal UTC', () {
    final senin = DateTime(2026, 9, 21, 6, 30); // waktu LOKAL
    expect(tanggalLokal(senin), '2026-09-21');
  });
}
