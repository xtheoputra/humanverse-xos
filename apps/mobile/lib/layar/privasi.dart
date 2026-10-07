import 'dart:async';

import 'package:flutter/material.dart';

import '../api/klien.dart';
import '../api/privasi.dart';
import '../api/simpan_berkas.dart';

/// Layar Privacy Center — spec/07 6.4, naskah 5 §26: *apa yang diketahui HumanVerse*, izin per
/// agent, ekspor, hapus (K-41 · K-42 · K-43).
///
/// Jumlah, bukan isi: layar ini menjawab *“apa yang kamu tahu tentang saya”* tanpa
/// menumpahkan seluruh data ke layar. Tiap tindakan yang tidak bisa dibatalkan — hapus satu
/// kategori, ekspor, hapus akun — meminta sandi LAGI: token yang dicuri tidak cukup.
class LayarPrivasi extends StatefulWidget {
  const LayarPrivasi({
    super.key,
    required this.layanan,
    this.simpan = simpanBerkas,
    this.sesudahHapusAkun,
  });

  final LayananPrivasi layanan;

  /// Menyimpan berkas ekspor di perangkat — `false` bila platform belum mendukungnya.
  final Future<bool> Function(String nama, List<int> isi) simpan;

  /// Dipanggil sesudah akun dijadwalkan hapus — semua sesi sudah dicabut server.
  final VoidCallback? sesudahHapusAkun;

  @override
  State<LayarPrivasi> createState() => _LayarPrivasiState();
}

const _labelKeputusan = {
  'allow': 'Izinkan',
  'ask': 'Tanya dulu',
  'deny': 'Tolak',
};
const _labelAksi = {
  'read': 'membaca',
  'write': 'menulis',
  'execute': 'menjalankan',
};

class _LayarPrivasiState extends State<LayarPrivasi> {
  RingkasanPrivasi? _ringkasan;
  List<IzinAgent> _izin = const [];
  bool _memuat = true;
  bool _sibuk = false;
  String? _galat;
  String? _pesanEkspor;

  @override
  void initState() {
    super.initState();
    _muat();
  }

  String _pesan(Object e) => switch (e) {
    GalatApi(:final pesan) => pesan,
    JaringanPutus() => 'Server tidak terjangkau. Coba lagi.',
    _ => 'Terjadi galat. Coba lagi.',
  };

  void _kabari(String pesan) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(pesan)));
  }

  Future<void> _muat() async {
    setState(() {
      _memuat = true;
      _galat = null;
    });
    try {
      final ringkasan = await widget.layanan.ringkasanPrivasi();
      final izin = await widget.layanan.izinAgent();
      if (!mounted) return;
      setState(() {
        _ringkasan = ringkasan;
        _izin = izin;
      });
    } on SesiBerakhir {
      if (mounted) Navigator.of(context).pop();
    } on Exception catch (e) {
      if (mounted) setState(() => _galat = _pesan(e));
    } finally {
      if (mounted) setState(() => _memuat = false);
    }
  }

  /// Sandi ulang — `null` bila dibatalkan.
  Future<String?> _mintaSandi(String judul, String penjelasan, String tombol) =>
      showDialog<String>(
        context: context,
        builder: (_) =>
            _DialogSandi(judul: judul, penjelasan: penjelasan, tombol: tombol),
      );

  Future<void> _sambil(Future<void> Function() kerja) async {
    setState(() => _sibuk = true);
    try {
      await kerja();
    } on SesiBerakhir {
      if (mounted) Navigator.of(context).pop();
    } on Exception catch (e) {
      _kabari(_pesan(e));
    } finally {
      if (mounted) setState(() => _sibuk = false);
    }
  }

  Future<void> _hapus(KategoriPrivasi k) async {
    final sandi = await _mintaSandi(
      'Hapus ${k.label}?',
      'Semua ${k.label.toLowerCase()} (${k.jumlah} catatan) dan yang diturunkan darinya '
          'dihapus permanen. Tidak bisa dibatalkan.',
      'Hapus',
    );
    if (sandi == null || sandi.isEmpty) return;
    await _sambil(() async {
      final terhapus = await widget.layanan.hapusData(k.key, sandi);
      final total = terhapus.values.fold(0, (a, b) => a + b);
      _kabari('${k.label}: $total baris dihapus.');
      await _muat();
    });
  }

  Future<void> _ekspor() async {
    final sandi = await _mintaSandi(
      'Ekspor datamu',
      'Salinan seluruh datamu dalam berkas JSON. Tautannya sekali pakai.',
      'Ekspor',
    );
    if (sandi == null || sandi.isEmpty) return;
    await _sambil(() async {
      final ekspor = await widget.layanan.mintaEkspor(sandi);
      final isi = await widget.layanan.unduhEkspor(ekspor.id);
      final tersimpan = await widget.simpan('humanverse-export.json', isi);
      if (!mounted) return;
      setState(
        () => _pesanEkspor = tersimpan
            ? 'Berkas ekspor tersimpan (${(isi.length / 1024).ceil()} KB).'
            : 'Ekspor dibuat (${(isi.length / 1024).ceil()} KB), tetapi aplikasi ini belum '
                  'bisa menyimpan berkas di perangkat — unduh dari aplikasi web.',
      );
    });
  }

  Future<void> _hapusAkun() async {
    final sandi = await _mintaSandi(
      'Hapus akun?',
      'Akunmu dijadwalkan hapus dalam 30 hari dan semua sesi diakhiri. Selama 30 hari itu '
          'kamu masih bisa masuk dan membatalkannya.',
      'Hapus akun',
    );
    if (sandi == null || sandi.isEmpty) return;
    await _sambil(() async {
      await widget.layanan.hapusAkun(sandi);
      if (!mounted) return;
      Navigator.of(context).pop();
      widget.sesudahHapusAkun?.call();
    });
  }

  Future<void> _ubahIzin(IzinAgent a, IzinBerlaku i, String keputusan) async {
    await _sambil(() async {
      final baru = await widget.layanan.tetapkanIzin(
        a.agent,
        i.scope,
        i.aksi,
        keputusan,
      );
      if (!mounted) return;
      setState(() {
        _izin = [
          for (final x in _izin)
            if (x.agent != a.agent)
              x
            else
              IzinAgent(
                agent: x.agent,
                tujuan: x.tujuan,
                izin: [
                  for (final y in x.izin)
                    if (y.scope == i.scope && y.aksi == i.aksi) baru else y,
                ],
              ),
        ];
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final teks = Theme.of(context).textTheme;
    final ringkasan = _ringkasan;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Privasi'),
        actions: [
          IconButton(
            tooltip: 'Muat ulang',
            onPressed: _memuat || _sibuk ? null : _muat,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _memuat && ringkasan == null
          ? const Center(child: CircularProgressIndicator())
          : ringkasan == null
          ? Center(
              child: Text(_galat ?? 'Gagal memuat.', key: const Key('galat')),
            )
          : AbsorbPointer(
              absorbing: _sibuk,
              child: ListView(
                children: [
                  _judul('Apa yang diketahui HumanVerse', teks),
                  for (final k in ringkasan.kategori) _kategori(k, teks),
                  _judul('Tidak dikumpulkan', teks),
                  ListTile(
                    key: const Key('tak-dikumpulkan'),
                    leading: const Icon(Icons.radio_button_unchecked),
                    title: Text(ringkasan.tidakDikumpulkan.join(' · ')),
                  ),
                  _judul('Izin asisten', teks),
                  for (final a in _izin) _agent(a),
                  _judul('Salinan datamu', teks),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: OutlinedButton.icon(
                        key: const Key('ekspor'),
                        onPressed: _ekspor,
                        icon: const Icon(Icons.download),
                        label: const Text('Ekspor semua data (JSON)'),
                      ),
                    ),
                  ),
                  if (_pesanEkspor != null)
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                      child: Text(
                        _pesanEkspor!,
                        key: const Key('pesan-ekspor'),
                      ),
                    ),
                  _judul('Akun', teks),
                  ListTile(
                    key: const Key('hapus-akun'),
                    leading: Icon(
                      Icons.delete_forever,
                      color: Theme.of(context).colorScheme.error,
                    ),
                    title: const Text('Hapus akun'),
                    subtitle: const Text(
                      'Tenggang 30 hari — bisa dibatalkan dengan masuk lagi.',
                    ),
                    onTap: _hapusAkun,
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
    );
  }

  Widget _judul(String isi, TextTheme teks) => Padding(
    padding: const EdgeInsets.fromLTRB(16, 20, 16, 4),
    child: Text(isi, style: teks.titleMedium),
  );

  Widget _kategori(KategoriPrivasi k, TextTheme teks) {
    final turunan = k.turunan > 0 ? ' · ${k.turunan} diturunkan sistem' : '';
    return ListTile(
      key: Key('kategori-${k.key}'),
      leading: Icon(
        k.jumlah + k.turunan > 0
            ? Icons.check_circle
            : Icons.radio_button_unchecked,
      ),
      title: Text(k.label),
      subtitle: Text(
        '${k.jumlah} catatan$turunan\n${k.retensi}',
        style: teks.bodySmall,
      ),
      isThreeLine: true,
      trailing: k.bisaDihapus
          ? IconButton(
              key: Key('hapus-${k.key}'),
              tooltip: 'Hapus ${k.label}',
              onPressed: k.jumlah + k.turunan == 0 ? null : () => _hapus(k),
              icon: const Icon(Icons.delete_outline),
            )
          : Tooltip(
              message: k.alasanTakBisaDihapus ?? '',
              child: const Icon(Icons.info_outline),
            ),
    );
  }

  Widget _agent(IzinAgent a) => ExpansionTile(
    key: Key('agent-${a.agent}'),
    title: Text(a.agent),
    subtitle: Text(a.tujuan.join(' · ')),
    children: [
      for (final i in a.izin)
        ListTile(
          dense: true,
          title: Text(
            '${_labelAksi[i.aksi] ?? i.aksi} ${i.scope}'
            '${i.sensitif ? ' · sensitif' : ''}',
          ),
          subtitle: Text(
            [
              if (i.sumber == 'default') 'bawaan',
              if (i.konfirmasiTiapKali) 'selalu dikonfirmasi',
            ].join(' · '),
          ),
          trailing: DropdownButton<String>(
            key: Key('izin-${a.agent}-${i.scope}-${i.aksi}'),
            value: i.keputusan,
            onChanged: (v) {
              if (v != null && v != i.keputusan) unawaited(_ubahIzin(a, i, v));
            },
            items: [
              for (final e in _labelKeputusan.entries)
                DropdownMenuItem(value: e.key, child: Text(e.value)),
            ],
          ),
        ),
    ],
  );
}

/// Dialog sandi ulang — MEMILIKI pengendali teksnya. 🔴 Versi pertama membuang pengendali
/// begitu `showDialog` selesai, padahal dialognya masih beranimasi tutup dan membacanya:
/// *“TextEditingController was used after being disposed”* di tiap ketukan Batal/Hapus.
class _DialogSandi extends StatefulWidget {
  const _DialogSandi({
    required this.judul,
    required this.penjelasan,
    required this.tombol,
  });

  final String judul;
  final String penjelasan;
  final String tombol;

  @override
  State<_DialogSandi> createState() => _DialogSandiState();
}

class _DialogSandiState extends State<_DialogSandi> {
  final _kendali = TextEditingController();

  @override
  void dispose() {
    _kendali.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
    title: Text(widget.judul),
    content: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(widget.penjelasan),
        const SizedBox(height: 12),
        TextField(
          key: const Key('sandi-ulang'),
          controller: _kendali,
          obscureText: true,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Sandi'),
        ),
      ],
    ),
    actions: [
      TextButton(
        onPressed: () => Navigator.of(context).pop(),
        child: const Text('Batal'),
      ),
      FilledButton(
        key: const Key('konfirmasi-sandi'),
        onPressed: () => Navigator.of(context).pop(_kendali.text),
        child: Text(widget.tombol),
      ),
    ],
  );
}
