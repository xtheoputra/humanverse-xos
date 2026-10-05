import 'dart:convert';

import 'package:flutter/material.dart';

import '../api/klien.dart';
import '../api/model.dart';
import 'dasbor.dart';

/// Layar V0 pertama — spec/07 2.7: daftar habit + tandai selesai.
///
/// "Hari ini" adalah tanggal LOKAL perangkat (spec/01 `for_date`): habit yang
/// ditandai Senin pagi di Jakarta tercatat Senin. Tier yang disarankan datang
/// dari server bersama alasannya — energi check-in (naskah 4 §34, K-23).
class LayarHabitHariIni extends StatefulWidget {
  const LayarHabitHariIni({
    super.key,
    required this.layanan,
    required this.sesudahKeluar,
    this.jam = DateTime.now,
  });

  final LayananHabit layanan;
  final VoidCallback sesudahKeluar;
  final DateTime Function() jam;

  @override
  State<LayarHabitHariIni> createState() => _LayarHabitHariIniState();
}

class _LayarHabitHariIniState extends State<LayarHabitHariIni> {
  late String _tanggal;
  List<Habit> _habit = const [];
  Checkin? _checkin;
  bool _memuat = true;
  String? _galat;
  final Set<String> _sedangDiubah = {};

  @override
  void initState() {
    super.initState();
    _tanggal = tanggalLokal(widget.jam());
    _muat();
  }

  Future<void> _muat() async {
    setState(() {
      _memuat = true;
      _galat = null;
      _tanggal = tanggalLokal(widget.jam());
    });
    try {
      final hasil = await Future.wait([
        widget.layanan.habitPada(_tanggal),
        widget.layanan.checkinPada(_tanggal),
      ]);
      if (!mounted) return;
      setState(() {
        _habit = hasil[0] as List<Habit>;
        _checkin = hasil[1] as Checkin?;
      });
    } on Exception catch (e) {
      _tangani(e);
    } finally {
      if (mounted) setState(() => _memuat = false);
    }
  }

  void _tangani(Exception e) {
    if (!mounted) return;
    if (e is SesiBerakhir) {
      widget.sesudahKeluar();
      return;
    }
    final pesan = e is GalatApi
        ? e.pesan
        : 'Server tidak terjangkau. Coba lagi.';
    setState(() => _galat = pesan);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(pesan)));
  }

  Future<void> _ubah(String habitId, Future<void> Function() kerja) async {
    setState(() => _sedangDiubah.add(habitId));
    try {
      await kerja();
      await _muat();
    } on Exception catch (e) {
      _tangani(e);
    } finally {
      if (mounted) setState(() => _sedangDiubah.remove(habitId));
    }
  }

  Future<void> _ketuk(Habit h) async {
    // Catatan APA PUN — termasuk `skipped` dari perangkat lain — dibatalkan
    // dulu: POST ke tanggal yang sudah tercatat mengembalikan baris lama, dan
    // layar yang mengirim "done" untuk habit yang dilewati tidak berubah apa-apa
    // (tinjauan kontrak Sprint 2, D5).
    if (h.tercatatHariItu) {
      return _ubah(h.id, () => widget.layanan.batalkanSelesai(h.id, _tanggal));
    }
    int? tier;
    if (h.tier.isNotEmpty) {
      tier = await _pilihTier(h);
      if (tier == null) return; // dibatalkan
    }
    return _ubah(
      h.id,
      () => widget.layanan.tandaiSelesai(h.id, _tanggal, tier: tier),
    );
  }

  Future<int?> _pilihTier(Habit h) {
    final disarankan = h.hari?.tierDisarankan ?? 0;
    return showModalBottomSheet<int>(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: Text(h.judul),
              subtitle: const Text(
                'Versi mana yang kamu jalankan? Semuanya tetap dihitung.',
              ),
            ),
            for (var i = 0; i < h.tier.length; i++)
              ListTile(
                key: Key('tier-$i'),
                leading: Icon(
                  i == disarankan ? Icons.star : Icons.circle_outlined,
                ),
                title: Text(h.tier[i].label),
                subtitle: i == disarankan
                    ? const Text('Disarankan hari ini')
                    : null,
                onTap: () => Navigator.of(context).pop(i),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _simpanEnergi(int energi) async {
    try {
      final baru = await widget.layanan.simpanEnergi(
        _tanggal,
        energi,
        lama: _checkin,
      );
      if (!mounted) return;
      setState(() => _checkin = baru);
      await _muat(); // tier yang disarankan mengikuti energi baru
    } on Exception catch (e) {
      _tangani(e);
    }
  }

  Future<void> _keluar() async {
    await widget.layanan.keluar();
    widget.sesudahKeluar();
  }

  Future<void> _tambah() async {
    final dibuat = await showDialog<bool>(
      context: context,
      builder: (_) => _DialogTambahHabit(layanan: widget.layanan),
    );
    if (dibuat ?? false) await _muat();
  }

  String? _keterangan(Habit h) {
    final hari = h.hari;
    final selesai = hari?.penyelesaian;
    if (h.dilewatiHariItu) return 'Dilewati hari ini — ketuk untuk membatalkan';
    if (selesai != null && selesai.dijalankan) {
      final t = selesai.tierDipakai;
      return t != null && t < h.tier.length
          ? 'Selesai — ${h.tier[t].label}'
          : 'Selesai';
    }
    final saran = hari?.tierDisarankan;
    if (saran == null || saran >= h.tier.length) return _periode(h);
    final alasan = hari?.energi == null ? '' : ' (energi ${hari!.energi})';
    return 'Disarankan: ${h.tier[saran].label}$alasan';
  }

  String _periode(Habit h) => switch (h.periode) {
    'day' => 'Setiap hari',
    'week' => '${h.target}× seminggu',
    _ => '${h.target}× sebulan',
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Habit hari ini'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(20),
          child: Text(_tanggal, key: const Key('tanggal')),
        ),
        actions: [
          IconButton(
            key: const Key('buka-dasbor'),
            tooltip: 'Dashboard',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => LayarDasbor(layanan: widget.layanan),
              ),
            ),
            icon: const Icon(Icons.insights),
          ),
          IconButton(
            tooltip: 'Muat ulang',
            onPressed: _memuat ? null : _muat,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            key: const Key('keluar'),
            tooltip: 'Keluar',
            onPressed: _keluar,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        key: const Key('tambah'),
        tooltip: 'Tambah habit',
        onPressed: _tambah,
        child: const Icon(Icons.add),
      ),
      body: RefreshIndicator(
        onRefresh: _muat,
        child: ListView(
          padding: const EdgeInsets.only(bottom: 88),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
              child: Text(
                'Energi hari ini',
                style: Theme.of(context).textTheme.titleSmall,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Wrap(
                spacing: 8,
                children: [
                  for (var e = 1; e <= 5; e++)
                    ChoiceChip(
                      key: Key('energi-$e'),
                      label: Text('$e'),
                      selected: _checkin?.energi == e,
                      onSelected: (_) => _simpanEnergi(e),
                    ),
                ],
              ),
            ),
            const Divider(),
            if (_memuat && _habit.isEmpty)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_habit.isEmpty)
              Padding(
                padding: const EdgeInsets.all(32),
                child: Text(
                  _galat ?? 'Belum ada habit. Tambahkan dengan tombol +.',
                  key: const Key('kosong'),
                  textAlign: TextAlign.center,
                ),
              )
            else
              for (final h in _habit)
                CheckboxListTile(
                  key: Key('habit-${h.id}'),
                  // `skipped` bukan selesai dan bukan belum: tanda setrip.
                  tristate: true,
                  value: h.dilewatiHariItu ? null : h.selesaiHariItu,
                  onChanged: _sedangDiubah.contains(h.id)
                      ? null
                      : (_) => _ketuk(h),
                  title: Text(h.judul),
                  subtitle: Text(_keterangan(h) ?? ''),
                  controlAffinity: ListTileControlAffinity.leading,
                ),
          ],
        ),
      ),
    );
  }
}

class _DialogTambahHabit extends StatefulWidget {
  const _DialogTambahHabit({required this.layanan});

  final LayananHabit layanan;

  @override
  State<_DialogTambahHabit> createState() => _DialogTambahHabitState();
}

class _DialogTambahHabitState extends State<_DialogTambahHabit> {
  final _judul = TextEditingController();
  final _tier = TextEditingController();
  String _periode = 'day';
  int _target = 1;
  bool _sibuk = false;
  String? _galat;
  // Satu tindakan = satu id: "Simpan" yang diketuk lagi dengan isian yang SAMA
  // (sesudah jaringan putus) mengirim id yang sama; isian yang diubah adalah
  // tindakan baru → id baru.
  String? _id;
  String? _isiTerakhir;

  String _idUntuk(String isi) {
    if (isi != _isiTerakhir || _id == null) {
      _isiTerakhir = isi;
      _id = idBaru();
    }
    return _id!;
  }

  @override
  void dispose() {
    _judul.dispose();
    _tier.dispose();
    super.dispose();
  }

  Future<void> _simpan() async {
    final judul = _judul.text.trim();
    if (judul.isEmpty) {
      setState(() => _galat = 'Judul wajib diisi.');
      return;
    }
    final tier = [
      for (final baris in _tier.text.split('\n'))
        if (baris.trim().isNotEmpty) Tier(label: baris.trim()),
    ];
    setState(() {
      _sibuk = true;
      _galat = null;
    });
    try {
      final target = _periode == 'day' ? 1 : _target;
      final isi = [judul, _periode, target, ...tier.map((t) => t.label)];
      await widget.layanan.buatHabit(
        id: _idUntuk(jsonEncode(isi)),
        judul: judul,
        periode: _periode,
        target: target,
        tier: tier,
      );
      if (mounted) Navigator.of(context).pop(true);
    } on GalatApi catch (g) {
      if (g.kode == 'already_exists') {
        // Percobaan sebelumnya SAMPAI (lebih dari 24 jam lalu, atau kuncinya
        // sudah dilupakan server): habit ini sudah ada — itu berhasil.
        if (mounted) Navigator.of(context).pop(true);
        return;
      }
      setState(() => _galat = g.pesan);
    } on Exception {
      setState(() => _galat = 'Server tidak terjangkau. Coba lagi.');
    } finally {
      if (mounted) setState(() => _sibuk = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Habit baru'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              key: const Key('judul-habit'),
              controller: _judul,
              decoration: const InputDecoration(labelText: 'Judul'),
            ),
            DropdownButtonFormField<String>(
              key: const Key('periode'),
              initialValue: _periode,
              decoration: const InputDecoration(labelText: 'Seberapa sering'),
              items: const [
                DropdownMenuItem(value: 'day', child: Text('Setiap hari')),
                DropdownMenuItem(value: 'week', child: Text('Per minggu')),
              ],
              onChanged: (p) => setState(() => _periode = p ?? _periode),
            ),
            if (_periode == 'week')
              DropdownButtonFormField<int>(
                key: const Key('target'),
                initialValue: _target,
                decoration: const InputDecoration(
                  labelText: 'Berapa kali seminggu',
                ),
                items: [
                  for (var n = 1; n <= 7; n++)
                    DropdownMenuItem(value: n, child: Text('$n×')),
                ],
                onChanged: (n) => setState(() => _target = n ?? _target),
              ),
            TextField(
              key: const Key('tier-habit'),
              controller: _tier,
              decoration: const InputDecoration(
                labelText: 'Versi ringan (opsional)',
                helperText:
                    'Satu per baris, dari versi penuh ke paling ringan.',
              ),
              minLines: 2,
              maxLines: 5,
            ),
            if (_galat != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  _galat!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _sibuk ? null : () => Navigator.of(context).pop(false),
          child: const Text('Batal'),
        ),
        FilledButton(
          key: const Key('simpan-habit'),
          onPressed: _sibuk ? null : _simpan,
          child: const Text('Simpan'),
        ),
      ],
    );
  }
}
