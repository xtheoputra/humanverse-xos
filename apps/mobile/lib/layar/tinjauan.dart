import 'package:flutter/material.dart';

import '../api/klien.dart';
import '../api/privasi.dart';

/// Layar tinjauan mingguan — spec/07 6.2, naskah 4 §31: lima pertanyaan (K-45).
///
/// Sistem menyiapkan bahan — apa yang terpenuhi, yang berubah, alasan yang kamu catat
/// sendiri — tetapi tidak pernah menjawab *“Kenapa?”* untukmu: yang terlihat hanya hal yang
/// terjadi bersamaan, bukan sebabnya (naskah 4 §7). Pertanyaan tanpa bukti tampil sebagai
/// pertanyaan, bukan angka kosong (Confidence Layer 5.4).
class LayarTinjauanMingguan extends StatefulWidget {
  const LayarTinjauanMingguan({super.key, required this.layanan});

  final LayananPrivasi layanan;

  @override
  State<LayarTinjauanMingguan> createState() => _LayarTinjauanMingguanState();
}

class _LayarTinjauanMingguanState extends State<LayarTinjauanMingguan> {
  TinjauanMingguan? _tinjauan;
  bool _memuat = true;
  String? _galat;

  @override
  void initState() {
    super.initState();
    _muat(null);
  }

  Future<void> _muat(String? minggu) async {
    setState(() {
      _memuat = true;
      _galat = null;
    });
    try {
      final t = await widget.layanan.tinjauanMingguan(minggu: minggu);
      if (mounted) setState(() => _tinjauan = t);
    } on SesiBerakhir {
      if (mounted) Navigator.of(context).pop();
    } on Exception catch (e) {
      final pesan = switch (e) {
        GalatApi(:final pesan) => pesan,
        _ => 'Server tidak terjangkau. Coba lagi.',
      };
      if (mounted) setState(() => _galat = pesan);
    } finally {
      if (mounted) setState(() => _memuat = false);
    }
  }

  String _nilai(double v, String satuan) => switch (satuan) {
    '0-1' => '${(v * 100).round()}%',
    'jam' => '${v.toStringAsFixed(1)} jam',
    _ => '${v.toStringAsFixed(1)}/5',
  };

  @override
  Widget build(BuildContext context) {
    final t = _tinjauan;
    final teks = Theme.of(context).textTheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tinjauan mingguan'),
        bottom: t == null
            ? null
            : PreferredSize(
                preferredSize: const Size.fromHeight(40),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    IconButton(
                      key: const Key('minggu-lalu'),
                      tooltip: 'Minggu sebelumnya',
                      onPressed: _memuat
                          ? null
                          : () => _muat(mingguGeser(t.mulai, -1)),
                      icon: const Icon(Icons.chevron_left),
                    ),
                    Text(
                      '${t.minggu} · ${t.mulai} – ${t.selesai}'
                      '${t.lengkap ? '' : ' (berjalan)'}',
                      key: const Key('minggu'),
                    ),
                    IconButton(
                      key: const Key('minggu-depan'),
                      tooltip: 'Minggu berikutnya',
                      // Minggu yang belum selesai adalah yang terbaru — sesudahnya belum ada.
                      onPressed: _memuat || !t.lengkap
                          ? null
                          : () => _muat(mingguGeser(t.mulai, 1)),
                      icon: const Icon(Icons.chevron_right),
                    ),
                  ],
                ),
              ),
      ),
      body: t == null
          ? Center(
              child: _memuat
                  ? const CircularProgressIndicator()
                  : Text(_galat ?? 'Gagal memuat.', key: const Key('galat')),
            )
          : ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                if (t.sumbu.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'Belum ada habit, check-in, atau mood di minggu ini untuk ditinjau.',
                      key: Key('tanpa-sumbu'),
                    ),
                  ),
                for (final s in t.sumbu)
                  ListTile(
                    key: Key('sumbu-${s.key}'),
                    title: Text(s.label),
                    subtitle: Text(s.why, style: teks.bodySmall),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          _nilai(s.nilai, s.satuan),
                          style: teks.titleMedium,
                        ),
                        if (s.sebelumnya != null)
                          Text(
                            'minggu lalu ${_nilai(s.sebelumnya!, s.satuan)}',
                            style: teks.bodySmall,
                          ),
                      ],
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
                  child: Text(
                    'Belum diukur: ${t.tidakDiukur.join(', ')}.',
                    key: const Key('tak-diukur'),
                    style: teks.bodySmall,
                  ),
                ),
                for (final q in t.pertanyaan)
                  Card(
                    key: Key('tanya-${q.key}'),
                    margin: const EdgeInsets.fromLTRB(12, 6, 12, 6),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(q.pertanyaan, style: teks.titleMedium),
                          for (final b in q.butir)
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: Text('• $b'),
                            ),
                          const SizedBox(height: 8),
                          Text(
                            q.ajakan,
                            key: Key('ajakan-${q.key}'),
                            style: q.bertanya
                                ? teks.bodyMedium?.copyWith(
                                    fontStyle: FontStyle.italic,
                                  )
                                : teks.bodySmall,
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
    );
  }
}
