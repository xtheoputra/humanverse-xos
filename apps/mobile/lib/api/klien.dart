import 'dart:convert';

import 'package:http/http.dart' as http;

import 'model.dart';

/// Galat beramplop spec/04: `{"error": {"code", "message", "details"?}}`.
class GalatApi implements Exception {
  const GalatApi(this.status, this.kode, this.pesan);

  final int status;
  final String kode;
  final String pesan;

  @override
  String toString() => 'GalatApi($status $kode): $pesan';
}

/// Sesi tidak bisa dipulihkan — token segar ditolak; pengguna harus masuk lagi.
class SesiBerakhir implements Exception {
  const SesiBerakhir();
}

/// Yang dibutuhkan layar dari API — layar bergantung pada antarmuka ini, bukan
/// pada HTTP, supaya uji widget tidak butuh server.
abstract interface class LayananHabit {
  bool get sudahMasuk;

  Future<Pengguna> masuk({required String email, required String sandi});

  Future<Pengguna> daftar({
    required String email,
    required String sandi,
    required String namaTampilan,
    required String zonaWaktu,
    required String versiKebijakan,
    required bool izinkanPelatihanModel,
  });

  Future<void> keluar();

  Future<List<Habit>> habitPada(String tanggal);

  /// `id` dibuat PEMANGGIL sekali per tindakan (`idBaru()`) dan dipakai ulang
  /// di tiap percobaannya — lihat `KlienApi`.
  Future<Habit> buatHabit({
    required String id,
    required String judul,
    required String periode,
    required int target,
    List<Tier> tier,
  });

  Future<Penyelesaian> tandaiSelesai(
    String habitId,
    String tanggal, {
    int? tier,
  });

  Future<void> batalkanSelesai(String habitId, String tanggal);

  Future<Checkin?> checkinPada(String tanggal);

  Future<Checkin> simpanEnergi(String tanggal, int energi, {Checkin? lama});

  Future<Dasbor> dasbor();
}

/// Klien HTTP untuk API V0 (`/v1`, spec/04).
///
/// * Token hanya di MEMORI: halaman yang dimuat ulang meminta masuk lagi.
///   Menyimpan token segar di penyimpanan web (localStorage) membuatnya bisa
///   dibaca skrip mana pun di asal yang sama — penyimpanan lokal datang bersama
///   mode luring (spec/07 6.6), dengan penyimpanan yang aman per platform.
/// * Token akses kedaluwarsa (401) disegarkan SEKALI lalu permintaannya
///   diulang; token segar berotasi (K-21) — pasangan baru menggantikan yang lama.
///   Permintaan SERENTAK yang sama-sama menerima 401 menunggu SATU penyegaran
///   yang sama. 🔴 Versi pertama menyegarkan per permintaan: yang kedua memakai
///   token segar yang sudah dirotasi yang pertama — server membacanya sebagai
///   pencurian token (`session.refresh_reused`) dan mencabut seluruh sesi
///   (tinjauan keamanan Sprint 2).
/// * Membuat habit memakai id buatan klien yang SAMA di tiap percobaan satu
///   tindakan, dan id itu juga `Idempotency-Key`-nya: percobaan ulang sesudah
///   jaringan putus diputar ulang server, bukan membuat habit kedua; sesudah 24
///   jam id yang sama menjadi `409 already_exists`, bukan baris kedua.
///   🔴 Versi pertama mengklaim ini dengan kunci acak BARU per ketukan — yang
///   tidak melindungi apa pun (tinjauan kontrak Sprint 2, F19).
/// * Penyelesaian tidak butuh kunci: `(habit, tanggal)` unik di server, dan
///   kirim ulang tanggal yang sama menjawab `200` dengan baris lama (spec/04).
class KlienApi implements LayananHabit {
  KlienApi({required this.dasar, http.Client? klien})
    : _http = klien ?? http.Client();

  /// Akar API, mis. `http://127.0.0.1:8000`.
  final Uri dasar;
  final http.Client _http;
  String? _akses;
  String? _segar;
  Future<void>? _penyegaran;

  @override
  bool get sudahMasuk => _akses != null;

  /// Token akses yang sedang dipakai — untuk `tool/ujung_ke_ujung.dart`, yang
  /// membuktikan SERVER mencabutnya saat keluar (klien sendiri melupakannya).
  String? get tokenAksesSaatIni => _akses;

  Uri _uri(String jalur, [Map<String, String>? kueri]) => dasar.replace(
    path: '${dasar.path.replaceAll(RegExp(r'/$'), '')}$jalur',
    queryParameters: kueri,
  );

  Future<http.Response> _kirim(
    String metode,
    String jalur, {
    Object? badan,
    Map<String, String>? kueri,
    String? kunciIdempotensi,
    bool bersesi = true,
  }) async {
    Future<http.Response> sekali(String? akses) {
      final kepala = <String, String>{
        'Accept': 'application/json',
        if (badan != null) 'Content-Type': 'application/json',
        if (bersesi && akses != null) 'Authorization': 'Bearer $akses',
        'Idempotency-Key': ?kunciIdempotensi,
      };
      final permintaan = http.Request(metode, _uri(jalur, kueri))
        ..headers.addAll(kepala);
      if (badan != null) permintaan.body = jsonEncode(badan);
      return _http.send(permintaan).then(http.Response.fromStream);
    }

    final dipakai = _akses;
    var jawaban = await sekali(dipakai);
    if (jawaban.statusCode == 401 && bersesi && _segar != null) {
      // Token yang ditolak masih token saat ini → segarkan (atau tunggu
      // penyegaran yang sedang berjalan). Sudah diganti permintaan lain →
      // langsung ulangi dengan yang baru; menyegarkan lagi tidak perlu.
      if (_akses == dipakai) await _segarkan();
      jawaban = await sekali(_akses);
    }
    if (jawaban.statusCode >= 400) {
      if (jawaban.statusCode == 401 && bersesi) {
        _lupakan();
        throw const SesiBerakhir();
      }
      throw _galat(jawaban);
    }
    return jawaban;
  }

  GalatApi _galat(http.Response jawaban) {
    try {
      final isi =
          jsonDecode(utf8.decode(jawaban.bodyBytes)) as Map<String, dynamic>;
      final galat = isi['error'] as Map<String, dynamic>;
      return GalatApi(
        jawaban.statusCode,
        galat['code'] as String,
        galat['message'] as String,
      );
    } on Object {
      return GalatApi(
        jawaban.statusCode,
        'http_${jawaban.statusCode}',
        'Galat tak terduga.',
      );
    }
  }

  dynamic _json(http.Response jawaban) =>
      jsonDecode(utf8.decode(jawaban.bodyBytes));

  void _simpanToken(Map<String, dynamic> token) {
    _akses = token['access_token'] as String;
    _segar = token['refresh_token'] as String;
  }

  void _lupakan() {
    _akses = null;
    _segar = null;
  }

  /// SATU penyegaran untuk semua permintaan yang menunggunya (lihat docstring kelas).
  Future<void> _segarkan() =>
      _penyegaran ??= _segarkanSekali().whenComplete(() => _penyegaran = null);

  Future<void> _segarkanSekali() async {
    final segar = _segar;
    if (segar == null) throw const SesiBerakhir();
    final jawaban = await _http.post(
      _uri('/v1/auth/refresh'),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({'refresh_token': segar}),
    );
    if (jawaban.statusCode != 200) {
      _lupakan();
      throw const SesiBerakhir();
    }
    _simpanToken(
      (_json(jawaban) as Map<String, dynamic>)['tokens']
          as Map<String, dynamic>,
    );
  }

  Pengguna _akun(http.Response jawaban) {
    final isi = _json(jawaban) as Map<String, dynamic>;
    _simpanToken(isi['tokens'] as Map<String, dynamic>);
    return Pengguna.dariJson(isi['user'] as Map<String, dynamic>);
  }

  @override
  Future<Pengguna> masuk({
    required String email,
    required String sandi,
  }) async => _akun(
    await _kirim(
      'POST',
      '/v1/auth/login',
      badan: {'email': email, 'password': sandi},
      bersesi: false,
    ),
  );

  @override
  Future<Pengguna> daftar({
    required String email,
    required String sandi,
    required String namaTampilan,
    required String zonaWaktu,
    required String versiKebijakan,
    required bool izinkanPelatihanModel,
  }) async => _akun(
    await _kirim(
      'POST',
      '/v1/auth/register',
      bersesi: false,
      badan: {
        'email': email,
        'password': sandi,
        'display_name': namaTampilan,
        'timezone': zonaWaktu,
        'consents': {
          'policy_version': versiKebijakan,
          'terms': true,
          'privacy': true,
          // Persetujuan TERSENDIRI (B-22): menolaknya tidak mengurangi layanan.
          'model_training': izinkanPelatihanModel
              ? {
                  'granted': true,
                  'data_scopes': ['habits', 'checkins'],
                }
              : {'granted': false},
        },
      },
    ),
  );

  @override
  Future<void> keluar() async {
    try {
      if (_akses != null) await _kirim('POST', '/v1/auth/logout');
    } on Exception {
      // Keluar di sisi klien tetap terjadi walau server tak terjangkau.
    } finally {
      _lupakan();
    }
  }

  @override
  Future<List<Habit>> habitPada(String tanggal) async {
    final jawaban = await _kirim(
      'GET',
      '/v1/habits',
      kueri: {'status': 'active', 'for_date': tanggal},
    );
    final isi = _json(jawaban) as Map<String, dynamic>;
    return [
      for (final h in isi['items'] as List<dynamic>)
        Habit.dariJson(h as Map<String, dynamic>),
    ];
  }

  @override
  Future<Habit> buatHabit({
    required String id,
    required String judul,
    required String periode,
    required int target,
    List<Tier> tier = const [],
  }) async {
    final jawaban = await _kirim(
      'POST',
      '/v1/habits',
      kunciIdempotensi: id,
      badan: {
        'id': id,
        'title': judul,
        'period': periode,
        'target_count': target,
        'adaptive_tiers': [for (final t in tier) t.keJson()],
      },
    );
    return Habit.dariJson(_json(jawaban) as Map<String, dynamic>);
  }

  @override
  Future<Penyelesaian> tandaiSelesai(
    String habitId,
    String tanggal, {
    int? tier,
  }) async {
    final jawaban = await _kirim(
      'POST',
      '/v1/habits/$habitId/completions',
      badan: {'for_date': tanggal, 'status': 'done', 'tier_used': ?tier},
    );
    return Penyelesaian.dariJson(_json(jawaban) as Map<String, dynamic>);
  }

  @override
  Future<void> batalkanSelesai(String habitId, String tanggal) async {
    await _kirim('DELETE', '/v1/habits/$habitId/completions/$tanggal');
  }

  @override
  Future<Checkin?> checkinPada(String tanggal) async {
    final jawaban = await _kirim(
      'GET',
      '/v1/checkins',
      kueri: {'from': tanggal, 'to': tanggal},
    );
    final items =
        (_json(jawaban) as Map<String, dynamic>)['items'] as List<dynamic>;
    return items.isEmpty
        ? null
        : Checkin.dariJson(items.first as Map<String, dynamic>);
  }

  @override
  Future<Checkin> simpanEnergi(
    String tanggal,
    int energi, {
    Checkin? lama,
  }) async {
    final badan = lama?.keJsonDenganEnergi(energi) ?? {'energy': energi};
    final jawaban = await _kirim('PUT', '/v1/checkins/$tanggal', badan: badan);
    return Checkin.dariJson(_json(jawaban) as Map<String, dynamic>);
  }

  @override
  Future<Dasbor> dasbor() async {
    final jawaban = await _kirim('GET', '/v1/dashboard');
    return Dasbor.dariJson(_json(jawaban) as Map<String, dynamic>);
  }
}
