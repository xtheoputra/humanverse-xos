// Luring dasar — spec/07 6.6: catat habit tanpa jaringan → sinkron tanpa duplikat.
import 'package:flutter/foundation.dart';

import 'klien.dart';
import 'model.dart';

/// Dua tindakan atas penyelesaian habit yang boleh menunggu di antrean.
enum JenisCatatan { selesai, batal }

/// Satu tindakan atas penyelesaian habit yang menunggu dikirim.
///
/// HANYA `POST …/completions` dan `DELETE …/completions/{tanggal}`: keduanya
/// aman diulang menurut spec/04 — `(habit, tanggal)` unik, jadi kirim ulang
/// `POST` menjawab `200` dengan baris lama dan `DELETE` ulang menjawab `204`.
/// Itulah yang membuat catatan yang jawabannya hilang di jalan boleh dikirim
/// lagi tanpa membuat baris kedua (spec/01: *“mencegah pencatatan ganda saat
/// aplikasi luring”*).
class Catatan {
  Catatan.selesai(this.habitId, this.tanggal, {this.tier})
    : jenis = JenisCatatan.selesai;

  Catatan.batal(this.habitId, this.tanggal)
    : jenis = JenisCatatan.batal,
      tier = null;

  final JenisCatatan jenis;
  final String habitId;
  final String tanggal;
  final int? tier;

  /// Jawaban server begitu `selesai` terkirim — dibaca pemanggil yang menunggu.
  Penyelesaian? hasil;

  bool serumpun(Catatan lain) =>
      habitId == lain.habitId && tanggal == lain.tanggal;
}

/// Keadaan antrean untuk layar.
@immutable
class StatusAntrean {
  const StatusAntrean({
    this.menunggu = 0,
    this.ditolak = 0,
    this.luring = false,
  });

  /// Catatan yang belum diterima server.
  final int menunggu;

  /// Catatan yang DITOLAK server dan dibuang (habit sudah dihapus, tier berubah, …)
  /// sejak terakhir diakui pengguna — tidak pernah dibuang diam-diam.
  final int ditolak;

  /// Permintaan terakhir gagal karena jaringan.
  final bool luring;

  @override
  bool operator ==(Object other) =>
      other is StatusAntrean &&
      other.menunggu == menunggu &&
      other.ditolak == ditolak &&
      other.luring == luring;

  @override
  int get hashCode => Object.hash(menunggu, ditolak, luring);
}

/// Yang dibutuhkan layar dari antrean — terpisah dari [LayananHabit] supaya
/// layanan lain (klien polos, palsu uji) tidak dipaksa berpura-pura punya antrean.
abstract interface class StatusLuring {
  ValueListenable<StatusAntrean> get status;

  /// Kirim antrean sekarang. Tidak melempar karena jaringan putus atau server
  /// sedang sakit (catatan tetap menunggu); [SesiBerakhir] tetap dilempar.
  Future<void> sinkron();

  /// Pengguna sudah membaca bahwa ada catatan yang ditolak.
  void akuiDitolak();
}

/// [LayananHabit] yang menahan penyelesaian habit di antrean selagi jaringan
/// putus, dan mengirimnya berurutan begitu bisa (K-40).
///
/// * **Yang diantre**: tandai selesai dan batalkan — tindakan harian, dan satu-
///   satunya yang aman diulang. Check-in energi (`PUT` = ganti; salinan lama di
///   layar bisa menimpa perubahan dari perangkat lain) dan habit baru TIDAK:
///   keduanya gagal sebagai [JaringanPutus] dengan pesan yang jujur.
/// * **Urutan terjaga**: catatan baru selalu masuk di belakang yang lama. Satu
///   perkecualian yang aman — `batal` membuang catatan lama pada `(habit,
///   tanggal)` yang sama, karena `DELETE` menghapus apa pun yang ada: akhirnya
///   sama, dikirim lebih sedikit. `selesai` setelah `batal` TIDAK dipadatkan:
///   baris lama di server (mis. `skipped` dari perangkat lain) harus dihapus
///   dulu, kalau tidak `POST` mengembalikannya apa adanya (spec/04).
/// * **Tanpa duplikat** datang dari kontrak server, bukan dari klien: catatan
///   dibuang dari antrean SESUDAH server menjawab, jadi jawaban yang hilang
///   berarti dikirim lagi — dan itu aman.
/// * **Galat server**: `5xx` · `429` · `408` menahan seluruh antrean (nanti
///   dicoba lagi); `4xx` lain tak akan pernah berhasil, jadi catatan itu dibuang,
///   DIHITUNG di `StatusAntrean.ditolak`, dan yang di belakangnya jalan terus.
/// * **Milik satu akun**: masuk sebagai akun lain, atau keluar, membuang antrean.
/// * **Di memori**: antrean mati bersama proses (K-40) — penyimpanan lokal butuh
///   keputusan pemilik soal tempat menyimpan (sama dengan token, klien.dart).
class LayananLuring implements LayananHabit, StatusLuring {
  LayananLuring(this._dalam);

  final LayananHabit _dalam;
  final List<Catatan> _antrean = [];
  // Daftar & check-in terakhir yang DIJAWAB server, per tanggal — bahan tampilan
  // luring. Tanpanya layar luring hanya bisa berkata "gagal".
  final Map<String, List<Habit>> _habitTerakhir = {};
  final Map<String, Checkin?> _checkinTerakhir = {};
  final ValueNotifier<StatusAntrean> _status = ValueNotifier(
    const StatusAntrean(),
  );
  String? _pemilik;
  int _ditolak = 0;
  bool _luring = false;
  // Putaran kirim terakhir berhenti sebelum antreannya kosong.
  bool _tertahan = false;
  Future<void>? _jalan;

  @override
  ValueListenable<StatusAntrean> get status => _status;

  @override
  bool get sudahMasuk => _dalam.sudahMasuk;

  void _umumkan() {
    _status.value = StatusAntrean(
      menunggu: _antrean.length,
      ditolak: _ditolak,
      luring: _luring,
    );
  }

  void _setLuring(bool nilai) {
    if (_luring == nilai) return;
    _luring = nilai;
    _umumkan();
  }

  void _buang() {
    _antrean.clear();
    _habitTerakhir.clear();
    _checkinTerakhir.clear();
    _ditolak = 0;
    _luring = false;
    _umumkan();
  }

  /// Antrean dan cache milik SATU akun: akun lain tidak mewarisinya.
  Pengguna _pegang(Pengguna pengguna) {
    if (_pemilik != pengguna.id) _buang();
    _pemilik = pengguna.id;
    return pengguna;
  }

  @override
  Future<Pengguna> masuk({
    required String email,
    required String sandi,
  }) async => _pegang(await _dalam.masuk(email: email, sandi: sandi));

  @override
  Future<Pengguna> daftar({
    required String email,
    required String sandi,
    required String namaTampilan,
    required String zonaWaktu,
    required String versiKebijakan,
    required bool izinkanPelatihanModel,
  }) async => _pegang(
    await _dalam.daftar(
      email: email,
      sandi: sandi,
      namaTampilan: namaTampilan,
      zonaWaktu: zonaWaktu,
      versiKebijakan: versiKebijakan,
      izinkanPelatihanModel: izinkanPelatihanModel,
    ),
  );

  @override
  Future<void> keluar() async {
    try {
      await _dalam.keluar();
    } finally {
      _pemilik = null;
      _buang();
    }
  }

  /// Panggilan yang butuh jaringan: gagalnya menandai keadaan luring.
  Future<T> _lewat<T>(Future<T> Function() kerja) async {
    try {
      final hasil = await kerja();
      _setLuring(false);
      return hasil;
    } on JaringanPutus {
      _setLuring(true);
      rethrow;
    }
  }

  @override
  Future<List<Habit>> habitPada(String tanggal) async {
    await sinkron();
    final simpanan = _habitTerakhir[tanggal];
    // Sinkron baru saja gagal karena jaringan: jangan menunggu satu batas waktu
    // lagi hanya untuk gagal dengan cara yang sama.
    if (_luring && _tertahan && simpanan != null) {
      return _tindih(simpanan, tanggal);
    }
    try {
      final daftar = await _dalam.habitPada(tanggal);
      _habitTerakhir[tanggal] = daftar;
      _setLuring(false);
      return _tindih(daftar, tanggal);
    } on JaringanPutus {
      _setLuring(true);
      if (simpanan == null) rethrow; // tak ada yang bisa ditampilkan jujur
      return _tindih(simpanan, tanggal);
    }
  }

  /// Tumpangkan catatan yang belum diterima server di atas daftar dari server —
  /// yang terakhir untuk `(habit, tanggal)` itulah yang dilihat pengguna.
  List<Habit> _tindih(List<Habit> daftar, String tanggal) {
    final untukHariIni = [
      for (final c in _antrean)
        if (c.tanggal == tanggal) c,
    ];
    if (untukHariIni.isEmpty) return daftar;
    return [for (final h in daftar) _tindihSatu(h, tanggal, untukHariIni)];
  }

  Habit _tindihSatu(Habit h, String tanggal, List<Catatan> catatan) {
    Catatan? terakhir;
    for (final c in catatan) {
      if (c.habitId == h.id) terakhir = c;
    }
    if (terakhir == null) return h;
    return h.denganPenyelesaian(
      tanggal,
      terakhir.jenis == JenisCatatan.selesai
          ? Penyelesaian(
              forDate: tanggal,
              status: 'done',
              tierDipakai: terakhir.tier,
            )
          : null,
    );
  }

  @override
  Future<Checkin?> checkinPada(String tanggal) async {
    try {
      final checkin = await _dalam.checkinPada(tanggal);
      _checkinTerakhir[tanggal] = checkin;
      _setLuring(false);
      return checkin;
    } on JaringanPutus {
      _setLuring(true);
      // "Tidak tahu" bukan "kosong": tanpa jawaban sebelumnya galatnya diteruskan.
      if (!_checkinTerakhir.containsKey(tanggal)) rethrow;
      return _checkinTerakhir[tanggal];
    }
  }

  @override
  Future<Habit> buatHabit({
    required String id,
    required String judul,
    required String periode,
    required int target,
    List<Tier> tier = const [],
  }) => _lewat(
    () => _dalam.buatHabit(
      id: id,
      judul: judul,
      periode: periode,
      target: target,
      tier: tier,
    ),
  );

  @override
  Future<Checkin> simpanEnergi(String tanggal, int energi, {Checkin? lama}) =>
      _lewat(() => _dalam.simpanEnergi(tanggal, energi, lama: lama));

  @override
  Future<Dasbor> dasbor() => _lewat(_dalam.dasbor);

  @override
  Future<Penyelesaian> tandaiSelesai(
    String habitId,
    String tanggal, {
    int? tier,
  }) async {
    final catatan = Catatan.selesai(habitId, tanggal, tier: tier);
    _tambah(catatan);
    await sinkron();
    // Terkirim → jawaban server; masih menunggu → yang pengguna lihat sekarang.
    return catatan.hasil ??
        Penyelesaian(forDate: tanggal, status: 'done', tierDipakai: tier);
  }

  @override
  Future<void> batalkanSelesai(String habitId, String tanggal) async {
    _tambah(Catatan.batal(habitId, tanggal));
    await sinkron();
  }

  void _tambah(Catatan catatan) {
    if (catatan.jenis == JenisCatatan.batal) {
      // `DELETE` menghapus apa pun yang ada: catatan lama pada tanggal yang sama
      // tak lagi mengubah akhirnya. Yang sedang terbang dibiarkan selesai —
      // putaran kirim mengambil catatan dari depan, jadi `DELETE` ini baru
      // berangkat SESUDAH jawabannya.
      _antrean.removeWhere(catatan.serumpun);
    }
    _antrean.add(catatan);
    _umumkan();
  }

  @override
  void akuiDitolak() {
    _ditolak = 0;
    _umumkan();
  }

  /// SATU putaran untuk semua pemanggil serentak: catatan yang sama tidak terbang
  /// dua kali. Catatan yang masuk selagi putaran berjalan diambil putaran itu
  /// sendiri (`_kuras` memeriksa antreannya lagi sesudah tiap kiriman).
  @override
  Future<void> sinkron() =>
      _jalan ??= _kuras().whenComplete(() => _jalan = null);

  Future<void> _kuras() async {
    _tertahan = false;
    while (_antrean.isNotEmpty) {
      final catatan = _antrean.first;
      try {
        if (catatan.jenis == JenisCatatan.selesai) {
          catatan.hasil = await _dalam.tandaiSelesai(
            catatan.habitId,
            catatan.tanggal,
            tier: catatan.tier,
          );
        } else {
          await _dalam.batalkanSelesai(catatan.habitId, catatan.tanggal);
        }
        _setLuring(false);
      } on JaringanPutus {
        _tertahan = true;
        _setLuring(true);
        return;
      } on GalatApi catch (g) {
        if (_sementara(g)) {
          _tertahan = true;
          return;
        }
        // Tak akan pernah berhasil — menahannya menahan semua yang di belakangnya.
        _ditolak++;
      }
      _antrean.removeWhere((c) => identical(c, catatan));
      _umumkan();
    }
  }

  /// Server sedang sakit atau menyuruh menunggu — bukan penolakan atas catatannya.
  bool _sementara(GalatApi g) =>
      g.status >= 500 || g.status == 429 || g.status == 408;
}
