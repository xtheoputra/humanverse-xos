import 'package:flutter/material.dart';

import 'api/klien.dart';
import 'layar/habit_hari_ini.dart';
import 'layar/masuk.dart';

/// Alamat API — `flutter run --dart-define=HVX_API=http://127.0.0.1:8000`.
/// Aplikasi web di asal lain butuh asalnya di `HVX_CORS_ORIGINS` api.
const alamatApi = String.fromEnvironment(
  'HVX_API',
  defaultValue: 'http://127.0.0.1:8000',
);

void main() {
  runApp(AplikasiHvx(layanan: KlienApi(dasar: Uri.parse(alamatApi))));
}

class AplikasiHvx extends StatefulWidget {
  const AplikasiHvx({super.key, required this.layanan});

  final LayananHabit layanan;

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
              sesudahKeluar: () => setState(() => _masuk = false),
            )
          : LayarMasuk(
              layanan: widget.layanan,
              sesudahMasuk: () => setState(() => _masuk = true),
            ),
    );
  }
}
