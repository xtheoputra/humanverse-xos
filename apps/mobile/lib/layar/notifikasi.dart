import 'package:flutter/material.dart';

import '../api/klien.dart';
import '../api/privasi.dart';

/// Layar notifikasi — spec/07 6.3: *bisa dimatikan per jenis* (K-44).
///
/// Jujur soal V0: belum ada notifikasi yang dikirim (A-28 — V0 reaktif). Pilihan di sini
/// disimpan, dan gerbang yang wajib dilewati pengirim mana pun kelak membacanya: jenis yang
/// dimatikan diam, jam tenang menunda, pagu harian berhenti. Keamanan akun tidak bisa
/// dimatikan — itu perlindungan, bukan promosi.
class LayarNotifikasi extends StatefulWidget {
  const LayarNotifikasi({super.key, required this.layanan});

  final LayananPrivasi layanan;

  @override
  State<LayarNotifikasi> createState() => _LayarNotifikasiState();
}

const _jamTenangBawaan = JamTenang(mulai: '22:00', selesai: '07:00');

class _LayarNotifikasiState extends State<LayarNotifikasi> {
  PreferensiNotifikasi? _pref;
  bool _sibuk = false;
  String? _galat;

  @override
  void initState() {
    super.initState();
    _jalankan(widget.layanan.notifikasi);
  }

  Future<void> _jalankan(Future<PreferensiNotifikasi> Function() kerja) async {
    setState(() {
      _sibuk = true;
      _galat = null;
    });
    try {
      final pref = await kerja();
      if (mounted) setState(() => _pref = pref);
    } on SesiBerakhir {
      if (mounted) Navigator.of(context).pop();
    } on Exception catch (e) {
      final pesan = switch (e) {
        GalatApi(:final pesan) => pesan,
        _ => 'Server tidak terjangkau. Coba lagi.',
      };
      if (!mounted) return;
      setState(() => _galat = pesan);
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(pesan)));
    } finally {
      if (mounted) setState(() => _sibuk = false);
    }
  }

  TimeOfDay _waktu(String hhmm) => TimeOfDay(
    hour: int.parse(hhmm.substring(0, 2)),
    minute: int.parse(hhmm.substring(3)),
  );

  String _hhmm(TimeOfDay t) =>
      '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}';

  Future<void> _pilihJam(JamTenang lama, {required bool mulai}) async {
    final dipilih = await showTimePicker(
      context: context,
      initialTime: _waktu(mulai ? lama.mulai : lama.selesai),
    );
    if (dipilih == null) return;
    final baru = mulai
        ? JamTenang(mulai: _hhmm(dipilih), selesai: lama.selesai)
        : JamTenang(mulai: lama.mulai, selesai: _hhmm(dipilih));
    await _jalankan(() => widget.layanan.ubahNotifikasi(jamTenang: baru));
  }

  @override
  Widget build(BuildContext context) {
    final pref = _pref;
    return Scaffold(
      appBar: AppBar(title: const Text('Notifikasi')),
      body: pref == null
          ? Center(
              child: _sibuk
                  ? const CircularProgressIndicator()
                  : Text(_galat ?? 'Gagal memuat.', key: const Key('galat')),
            )
          : AbsorbPointer(
              absorbing: _sibuk,
              child: ListView(
                children: [
                  if (!pref.dikirim)
                    const Card(
                      key: Key('belum-dikirim'),
                      margin: EdgeInsets.all(16),
                      child: Padding(
                        padding: EdgeInsets.all(12),
                        child: Text(
                          'Versi ini belum mengirim notifikasi apa pun. Pilihanmu disimpan '
                          'dan akan dipatuhi begitu pengiriman tersedia.',
                        ),
                      ),
                    ),
                  for (final j in pref.jenis)
                    SwitchListTile(
                      key: Key('notif-${j.key}'),
                      title: Text(j.label),
                      subtitle: j.wajib
                          ? const Text('Tidak bisa dimatikan')
                          : null,
                      value: j.nyala,
                      onChanged: j.wajib
                          ? null
                          : (v) => _jalankan(
                              () => widget.layanan.ubahNotifikasi(
                                jenis: {j.key: v},
                              ),
                            ),
                    ),
                  const Divider(),
                  SwitchListTile(
                    key: const Key('jam-tenang'),
                    title: const Text('Jam tenang'),
                    subtitle: const Text(
                      'Notifikasi ditunda, kecuali keamanan akun.',
                    ),
                    value: pref.jamTenang != null,
                    onChanged: (v) => _jalankan(
                      () => v
                          ? widget.layanan.ubahNotifikasi(
                              jamTenang: _jamTenangBawaan,
                            )
                          : widget.layanan.ubahNotifikasi(hapusJamTenang: true),
                    ),
                  ),
                  if (pref.jamTenang case final jam?) ...[
                    ListTile(
                      key: const Key('jam-mulai'),
                      title: const Text('Mulai'),
                      trailing: Text(jam.mulai),
                      onTap: () => _pilihJam(jam, mulai: true),
                    ),
                    ListTile(
                      key: const Key('jam-selesai'),
                      title: const Text('Selesai'),
                      trailing: Text(jam.selesai),
                      onTap: () => _pilihJam(jam, mulai: false),
                    ),
                  ],
                  ListTile(
                    title: const Text('Paling banyak per hari'),
                    trailing: Text(
                      '${pref.paguHarian}',
                      key: const Key('pagu'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
