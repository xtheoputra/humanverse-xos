import 'package:flutter/material.dart';

import '../api/klien.dart';
import '../api/model.dart';

/// Layar Dashboard — spec/07 6.1, naskah 4 §28: *beberapa dimensi, tiap skor ber-Why*.
///
/// Pemilik menolak satu angka Life Score; layar ini menampilkan tiap dimensi yang
/// V0 ukur (energi, fokus) sebagai batang terpisah, dan Why-nya di bawah skor —
/// supaya angka tidak pernah berdiri tanpa alasannya (§29 Explainable AI). Sumbu
/// yang belum punya ukuran disepakati tidak dikarang di sini: kalau server tidak
/// mengirimnya, layar tidak menampilkannya.
class LayarDasbor extends StatefulWidget {
  const LayarDasbor({super.key, required this.layanan});

  final LayananHabit layanan;

  @override
  State<LayarDasbor> createState() => _LayarDasborState();
}

class _LayarDasborState extends State<LayarDasbor> {
  Dasbor? _dasbor;
  bool _memuat = true;
  String? _galat;

  @override
  void initState() {
    super.initState();
    _muat();
  }

  Future<void> _muat() async {
    setState(() {
      _memuat = true;
      _galat = null;
    });
    try {
      final d = await widget.layanan.dasbor();
      if (!mounted) return;
      setState(() => _dasbor = d);
    } on SesiBerakhir {
      if (mounted) Navigator.of(context).pop();
    } on Exception catch (e) {
      if (!mounted) return;
      final pesan = e is GalatApi
          ? e.pesan
          : 'Server tidak terjangkau. Coba lagi.';
      setState(() => _galat = pesan);
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(pesan)));
    } finally {
      if (mounted) setState(() => _memuat = false);
    }
  }

  // Label manusiawi tiap dimensi V0; yang tak dikenal tampil apa adanya.
  static const _label = {'energy': 'Energi', 'focus': 'Fokus'};

  String _namaDimensi(String key) => _label[key] ?? key;

  @override
  Widget build(BuildContext context) {
    final dasbor = _dasbor;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        bottom: dasbor?.asOf == null
            ? null
            : PreferredSize(
                preferredSize: const Size.fromHeight(20),
                child: Text(dasbor!.asOf!, key: const Key('as-of')),
              ),
        actions: [
          IconButton(
            tooltip: 'Muat ulang',
            onPressed: _memuat ? null : _muat,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: RefreshIndicator(onRefresh: _muat, child: _isi(context, dasbor)),
    );
  }

  Widget _isi(BuildContext context, Dasbor? dasbor) {
    if (_memuat && dasbor == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (dasbor == null || dasbor.dimensi.isEmpty) {
      // Cold start, bukan "semua nol": sistem belum punya dasar, jadi ia meminta,
      // bukan menampilkan angka kosong (sejalan Confidence Layer, spec/07 5.4).
      return ListView(
        children: [
          Padding(
            padding: const EdgeInsets.all(32),
            child: Text(
              _galat ??
                  'Belum ada yang bisa ditampilkan. Isi check-in energi dulu, '
                      'lalu dashboard mengisi sendiri.',
              key: const Key('kosong'),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      );
    }
    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 8),
      children: [
        for (final d in dasbor.dimensi)
          Padding(
            key: Key('dimensi-${d.key}'),
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      _namaDimensi(d.key),
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Text(
                      '${(d.nilai * 100).round()}%',
                      key: Key('nilai-${d.key}'),
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: d.nilai.clamp(0.0, 1.0),
                    minHeight: 10,
                  ),
                ),
                const SizedBox(height: 6),
                // Why — tiap skor membawa alasannya (§29). Tanpa ini angka
                // terbaca seperti fakta; dengan ini pengguna bisa membantahnya.
                Text(
                  d.why,
                  key: Key('why-${d.key}'),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
      ],
    );
  }
}
