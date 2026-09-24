import 'package:flutter/material.dart';

import '../api/klien.dart';

/// Zona yang ditawarkan saat mendaftar — nama IANA persis (spec/07 1.3 menolak
/// `WIB` dan `asia/jakarta`). Zona lain bisa diganti kemudian lewat profil.
const zonaWaktuPilihan = <String>[
  'Asia/Jakarta',
  'Asia/Makassar',
  'Asia/Jayapura',
  'UTC',
];

/// Versi kebijakan yang disetujui saat mendaftar. ⚠️ Teks syarat & kebijakan
/// privasi final milik pemilik (#59 butir 2, C-11) — belum ada; versi ini
/// menandai persetujuan atas DRAF V0, supaya riwayatnya bisa dibedakan nanti.
const versiKebijakanV0 = 'draf-v0';

/// Layar masuk & daftar — pintu ke layar V0 pertama (spec/07 2.7).
class LayarMasuk extends StatefulWidget {
  const LayarMasuk({
    super.key,
    required this.layanan,
    required this.sesudahMasuk,
  });

  final LayananHabit layanan;
  final VoidCallback sesudahMasuk;

  @override
  State<LayarMasuk> createState() => _LayarMasukState();
}

class _LayarMasukState extends State<LayarMasuk> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _sandi = TextEditingController();
  final _nama = TextEditingController();
  bool _daftar = false;
  bool _setujuSyarat = false;
  bool _izinkanPelatihan = false;
  String _zona = zonaWaktuPilihan.first;
  bool _sibuk = false;
  String? _galat;

  @override
  void dispose() {
    _email.dispose();
    _sandi.dispose();
    _nama.dispose();
    super.dispose();
  }

  Future<void> _kirim() async {
    if (!_form.currentState!.validate()) return;
    if (_daftar && !_setujuSyarat) {
      setState(
        () => _galat = 'Syarat layanan dan kebijakan privasi wajib disetujui.',
      );
      return;
    }
    setState(() {
      _sibuk = true;
      _galat = null;
    });
    try {
      if (_daftar) {
        await widget.layanan.daftar(
          email: _email.text.trim(),
          sandi: _sandi.text,
          namaTampilan: _nama.text.trim(),
          zonaWaktu: _zona,
          versiKebijakan: versiKebijakanV0,
          izinkanPelatihanModel: _izinkanPelatihan,
        );
      } else {
        await widget.layanan.masuk(
          email: _email.text.trim(),
          sandi: _sandi.text,
        );
      }
      if (mounted) widget.sesudahMasuk();
    } on GalatApi catch (g) {
      setState(() => _galat = g.pesan);
    } on Exception {
      setState(() => _galat = 'Server tidak terjangkau. Coba lagi.');
    } finally {
      if (mounted) setState(() => _sibuk = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('HumanVerse XOS')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Form(
            key: _form,
            // SingleChildScrollView + Column, BUKAN ListView: ListView membangun
            // anak secara malas, dan Form hanya memvalidasi medan yang sudah
            // dibangun — medan di bawah layar lolos tanpa diperiksa.
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SegmentedButton<bool>(
                    segments: const [
                      ButtonSegment(value: false, label: Text('Masuk')),
                      ButtonSegment(value: true, label: Text('Daftar')),
                    ],
                    selected: {_daftar},
                    onSelectionChanged: (pilih) => setState(() {
                      _daftar = pilih.first;
                      _galat = null;
                    }),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    key: const Key('email'),
                    controller: _email,
                    decoration: const InputDecoration(labelText: 'Email'),
                    keyboardType: TextInputType.emailAddress,
                    autofillHints: const [AutofillHints.email],
                    validator: (v) =>
                        (v ?? '').contains('@') ? null : 'Email tidak sah.',
                  ),
                  TextFormField(
                    key: const Key('sandi'),
                    controller: _sandi,
                    decoration: InputDecoration(
                      labelText: 'Sandi',
                      helperText: _daftar
                          ? 'Paling sedikit 15 karakter.'
                          : null,
                    ),
                    obscureText: true,
                    autofillHints: const [AutofillHints.password],
                    validator: (v) {
                      final panjang = (v ?? '').length;
                      if (panjang == 0) return 'Sandi wajib diisi.';
                      if (_daftar && panjang < 15) {
                        return 'Sandi paling sedikit 15 karakter.';
                      }
                      return null;
                    },
                  ),
                  if (_daftar) ...[
                    TextFormField(
                      key: const Key('nama'),
                      controller: _nama,
                      decoration: const InputDecoration(
                        labelText: 'Nama tampilan',
                      ),
                      validator: (v) =>
                          (v ?? '').trim().isEmpty ? 'Nama wajib diisi.' : null,
                    ),
                    DropdownButtonFormField<String>(
                      key: const Key('zona'),
                      initialValue: _zona,
                      decoration: const InputDecoration(
                        labelText: 'Zona waktu',
                      ),
                      items: [
                        for (final z in zonaWaktuPilihan)
                          DropdownMenuItem(value: z, child: Text(z)),
                      ],
                      onChanged: (z) => setState(() => _zona = z ?? _zona),
                    ),
                    CheckboxListTile(
                      key: const Key('setuju'),
                      value: _setujuSyarat,
                      onChanged: (v) =>
                          setState(() => _setujuSyarat = v ?? false),
                      title: const Text(
                        'Saya menyetujui syarat layanan & kebijakan privasi',
                      ),
                      subtitle: const Text(
                        'Draf V0 — teks final disusun pemilik.',
                      ),
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                    CheckboxListTile(
                      key: const Key('pelatihan'),
                      value: _izinkanPelatihan,
                      onChanged: (v) =>
                          setState(() => _izinkanPelatihan = v ?? false),
                      title: const Text(
                        'Izinkan data habit & check-in dipakai melatih model',
                      ),
                      subtitle: const Text(
                        'Opsional. Menolaknya tidak mengurangi layanan.',
                      ),
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                  ],
                  if (_galat != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: Text(
                        _galat!,
                        key: const Key('galat'),
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                    ),
                  const SizedBox(height: 16),
                  FilledButton(
                    key: const Key('kirim'),
                    onPressed: _sibuk ? null : _kirim,
                    child: Text(_daftar ? 'Daftar' : 'Masuk'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
