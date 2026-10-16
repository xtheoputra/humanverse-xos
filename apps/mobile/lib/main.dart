import 'package:flutter/material.dart';

import 'api/klien.dart';
import 'api/luring.dart';
import 'api/privasi.dart';
import 'layar/habit_hari_ini.dart';
import 'layar/masuk.dart';

/// Alamat API — `flutter run --dart-define=HVX_API=http://127.0.0.1:8000`.
/// Aplikasi web di asal lain butuh asalnya di `HVX_CORS_ORIGINS` api.
const alamatApi = String.fromEnvironment(
  'HVX_API',
  defaultValue: 'http://127.0.0.1:8000',
);

void main() {
  // Luring dasar (spec/07 6.6): catatan habit menunggu di antrean selagi jaringan putus.
  final klien = KlienApi(dasar: Uri.parse(alamatApi));
  final luring = LayananLuring(klien);
  // Privacy Center, notifikasi, tinjauan (6.2–6.4): langsung ke klien — hapus data dan
  // ekspor tidak boleh menunggu di antrean luring.
  runApp(AplikasiHvx(layanan: luring, luring: luring, privasi: klien));
}

class AplikasiHvx extends StatefulWidget {
  const AplikasiHvx({
    super.key,
    required this.layanan,
    this.luring,
    this.privasi,
  });

  final LayananHabit layanan;

  /// Antrean luring milik [layanan], bila ada — layar habit menampilkannya.
  final StatusLuring? luring;

  /// Privacy Center · notifikasi · tinjauan mingguan (6.2–6.4), bila ada.
  final LayananPrivasi? privasi;

  @override
  State<AplikasiHvx> createState() => _AplikasiHvxState();
}

class _AplikasiHvxState extends State<AplikasiHvx> {
  late bool _masuk = widget.layanan.sudahMasuk;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HumanVerse XOS',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF3A6EA5),
        useMaterial3: true,
      ),
      home: _masuk
          ? LayarHabitHariIni(
              layanan: widget.layanan,
              luring: widget.luring,
              privasi: widget.privasi,
              sesudahKeluar: () => setState(() => _masuk = false),
            )
          : LayarMasuk(
              layanan: widget.layanan,
              sesudahMasuk: () => setState(() => _masuk = true),
            ),
    );
  }
}
