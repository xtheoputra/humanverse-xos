// Layanan palsu untuk uji widget — mencatat tiap panggilan, tanpa HTTP.
import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/model.dart';

class LayananPalsu implements LayananHabit {
  LayananPalsu({List<Habit>? habit, this.checkin}) : habit = habit ?? [];

  List<Habit> habit;
  Checkin? checkin;
  bool masukDipanggil = false;
  Map<String, Object?>? daftarDengan;
  final List<String> panggilan = [];
  Exception? galatBerikutnya;

  @override
  bool sudahMasuk = false;

  void _mungkinGagal() {
    final g = galatBerikutnya;
    if (g != null) {
      galatBerikutnya = null;
      throw g;
    }
  }

  @override
  Future<Pengguna> masuk({required String email, required String sandi}) async {
    panggilan.add('masuk $email');
    _mungkinGagal();
    sudahMasuk = true;
    return Pengguna(id: 'u1', email: email);
  }

  @override
  Future<Pengguna> daftar({
    required String email,
    required String sandi,
    required String namaTampilan,
    required String zonaWaktu,
    required String versiKebijakan,
    required bool izinkanPelatihanModel,
  }) async {
    panggilan.add('daftar $email');
    daftarDengan = {
      'nama': namaTampilan,
      'zona': zonaWaktu,
      'versi': versiKebijakan,
      'pelatihan': izinkanPelatihanModel,
    };
    _mungkinGagal();
    sudahMasuk = true;
    return Pengguna(id: 'u1', email: email);
  }

  @override
  Future<void> keluar() async {
    panggilan.add('keluar');
    sudahMasuk = false;
  }

  @override
  Future<List<Habit>> habitPada(String tanggal) async {
    panggilan.add('habit $tanggal');
    _mungkinGagal();
    return habit;
  }

  @override
  Future<Habit> buatHabit({
    required String judul,
    required String periode,
    required int target,
    List<Tier> tier = const [],
  }) async {
    panggilan.add(
      'buat $judul $periode $target ${tier.map((t) => t.label).join('|')}',
    );
    final baru = Habit(
      id: 'h${habit.length + 1}',
      judul: judul,
      periode: periode,
      target: target,
      tier: tier,
    );
    habit = [...habit, baru];
    return baru;
  }

  @override
  Future<Penyelesaian> tandaiSelesai(
    String habitId,
    String tanggal, {
    int? tier,
  }) async {
    panggilan.add('selesai $habitId $tanggal ${tier ?? '-'}');
    _mungkinGagal();
    final p = Penyelesaian(forDate: tanggal, status: 'done', tierDipakai: tier);
    habit = [
      for (final h in habit)
        h.id == habitId
            ? Habit(
                id: h.id,
                judul: h.judul,
                periode: h.periode,
                target: h.target,
                tier: h.tier,
                hari: HariHabit(
                  forDate: tanggal,
                  penyelesaian: p,
                  energi: h.hari?.energi,
                  tierDisarankan: h.hari?.tierDisarankan,
                ),
              )
            : h,
    ];
    return p;
  }

  @override
  Future<void> batalkanSelesai(String habitId, String tanggal) async {
    panggilan.add('batal $habitId $tanggal');
    habit = [
      for (final h in habit)
        h.id == habitId
            ? Habit(
                id: h.id,
                judul: h.judul,
                periode: h.periode,
                target: h.target,
                tier: h.tier,
                hari: HariHabit(
                  forDate: tanggal,
                  energi: h.hari?.energi,
                  tierDisarankan: h.hari?.tierDisarankan,
                ),
              )
            : h,
    ];
  }

  @override
  Future<Checkin?> checkinPada(String tanggal) async {
    panggilan.add('checkin $tanggal');
    return checkin;
  }

  @override
  Future<Checkin> simpanEnergi(
    String tanggal,
    int energi, {
    Checkin? lama,
  }) async {
    panggilan.add('energi $tanggal $energi');
    checkin = Checkin(forDate: tanggal, energi: energi);
    return checkin!;
  }
}
