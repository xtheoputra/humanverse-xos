// spec/07 2.7 — ujung ke ujung: klien aplikasi yang SAMA dengan layar, lawan
// api yang SUNGGUH berjalan (compose), tanpa tiruan apa pun.
//
//   dart run tool/ujung_ke_ujung.dart http://127.0.0.1:8000
//
// Uji widget membuktikan layar mengirim yang benar ke layanan palsu; berkas ini
// membuktikan bahwa yang dikirim itu DITERIMA api nyata dan hasilnya kembali
// seperti yang layar harapkan — kontrak spec/04 dari dua sisi sekaligus.
// Dijalankan gerbang `tools/ci_lokal.py` (tahap build) terhadap tumpukan compose.
import 'dart:io';
import 'dart:math';

import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/model.dart';

void _pastikan(bool benar, String pesan) {
  if (!benar) {
    stderr.writeln('🛑 $pesan');
    exit(1);
  }
  stdout.writeln('  ✅ $pesan');
}

Future<void> main(List<String> argumen) async {
  final dasar = Uri.parse(
    argumen.isEmpty ? 'http://127.0.0.1:8000' : argumen.first,
  );
  final acak = Random.secure();
  String hex(int n) =>
      List.generate(n, (_) => acak.nextInt(16).toRadixString(16)).join();
  final klien = KlienApi(dasar: dasar);

  stdout.writeln('ujung ke ujung → $dasar');
  await klien.daftar(
    email: 'uji-${hex(12)}@uji.id',
    sandi: 'kopi-pagi-${hex(20)}',
    namaTampilan: 'Uji Ujung',
    zonaWaktu: 'Asia/Jakarta',
    versiKebijakan: 'draf-v0',
    izinkanPelatihanModel: false,
  );
  _pastikan(klien.sudahMasuk, 'daftar → sesi terbit');

  final hariIni = tanggalLokal(DateTime.now());
  await klien.simpanEnergi(hariIni, 2);
  final checkin = await klien.checkinPada(hariIni);
  _pastikan(checkin?.energi == 2, 'check-in energi 2 tersimpan untuk $hariIni');

  final habit = await klien.buatHabit(
    id: idBaru(),
    judul: 'Workout',
    periode: 'day',
    target: 1,
    tier: const [
      Tier(label: 'Workout 60 menit', menit: 60),
      Tier(label: 'Workout 30 menit', menit: 30),
      Tier(label: 'Mobility 10 menit', menit: 10),
    ],
  );

  var daftar = await klien.habitPada(hariIni);
  final awal = daftar.singleWhere((h) => h.id == habit.id);
  _pastikan(!awal.selesaiHariItu, 'habit baru belum selesai hari ini');
  _pastikan(
    awal.hari?.tierDisarankan == 1 && awal.hari?.energi == 2,
    'energi rendah → tier disarankan turun ke "Workout 30 menit" (naskah 4 §34)',
  );

  await klien.tandaiSelesai(habit.id, hariIni, tier: 1);
  await klien.tandaiSelesai(
    habit.id,
    hariIni,
    tier: 1,
  ); // ulangan luring: 200, bukan ganda
  daftar = await klien.habitPada(hariIni);
  final selesai = daftar.singleWhere((h) => h.id == habit.id);
  _pastikan(
    selesai.selesaiHariItu && selesai.hari?.penyelesaian?.tierDipakai == 1,
    'tandai selesai (dua kali) → satu penyelesaian bertier 1',
  );

  await klien.batalkanSelesai(habit.id, hariIni);
  daftar = await klien.habitPada(hariIni);
  _pastikan(
    !daftar.singleWhere((h) => h.id == habit.id).selesaiHariItu,
    'batalkan → belum selesai lagi',
  );

  await klien.keluar();
  _pastikan(!klien.sudahMasuk, 'keluar → sesi dicabut');
  try {
    await klien.habitPada(hariIni);
    _pastikan(false, 'sesudah keluar, api menolak');
  } on SesiBerakhir {
    _pastikan(true, 'sesudah keluar, api menolak');
  } on GalatApi catch (g) {
    _pastikan(g.status == 401, 'sesudah keluar, api menolak (${g.status})');
  }
  stdout.writeln('✅ layar V0 pertama bekerja lawan api nyata');
  exit(0);
}
