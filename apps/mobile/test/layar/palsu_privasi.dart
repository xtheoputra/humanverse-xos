// Layanan Privacy Center · notifikasi · tinjauan palsu untuk uji widget — tanpa HTTP.
import 'package:hvx_app/api/klien.dart';
import 'package:hvx_app/api/privasi.dart';

class LayananPrivasiPalsu implements LayananPrivasi {
  final List<String> panggilan = [];
  String sandiBenar = 'sandi-benar-sekali';
  Exception? galatBerikutnya;
  int jurnal = 3;

  List<IzinAgent> izin = [
    const IzinAgent(
      agent: 'coach-agent',
      tujuan: ['percakapan coaching harian'],
      izin: [
        IzinBerlaku(
          scope: 'habits',
          aksi: 'read',
          keputusan: 'allow',
          sumber: 'default',
          sensitif: false,
          konfirmasiTiapKali: false,
        ),
        IzinBerlaku(
          scope: 'mood',
          aksi: 'read',
          keputusan: 'ask',
          sumber: 'default',
          sensitif: true,
          konfirmasiTiapKali: false,
        ),
      ],
    ),
  ];

  PreferensiNotifikasi pref = const PreferensiNotifikasi(
    jenis: [
      JenisNotifikasi(
        key: 'habit_reminder',
        label: 'Pengingat habit',
        nyala: false,
        wajib: false,
      ),
      JenisNotifikasi(
        key: 'weekly_review',
        label: 'Tinjauan mingguan siap',
        nyala: true,
        wajib: false,
      ),
      JenisNotifikasi(
        key: 'account_security',
        label: 'Keamanan akun',
        nyala: true,
        wajib: true,
      ),
    ],
    jamTenang: JamTenang(mulai: '22:00', selesai: '07:00'),
    paguHarian: 10,
    dikirim: false,
  );

  TinjauanMingguan Function(String? minggu) tinjauan = (minggu) =>
      TinjauanMingguan(
        minggu: minggu ?? '2026-W41',
        mulai: minggu == '2026-W40' ? '2026-09-28' : '2026-10-05',
        selesai: minggu == '2026-W40' ? '2026-10-04' : '2026-10-11',
        lengkap: minggu == '2026-W40',
        sumbu: const [],
        tidakDiukur: const ['Belajar', 'Keuangan'],
        pertanyaan: const [
          PertanyaanTinjauan(
            key: 'why',
            pertanyaan: 'Kenapa?',
            bertanya: true,
            butir: [],
            ajakan: 'Menurutmu, apa yang ada di baliknya?',
          ),
        ],
      );

  void _sandi(String sandi) {
    if (sandi != sandiBenar) {
      throw const GalatApi(403, 'invalid_credentials', 'Sandi salah.');
    }
  }

  void _mungkinGagal() {
    final g = galatBerikutnya;
    if (g != null) {
      galatBerikutnya = null;
      throw g;
    }
  }

  @override
  Future<RingkasanPrivasi> ringkasanPrivasi() async {
    panggilan.add('ringkasan');
    _mungkinGagal();
    return RingkasanPrivasi(
      kategori: [
        KategoriPrivasi(
          key: 'journal',
          label: 'Jurnal',
          jumlah: jurnal,
          turunan: 0,
          bisaDihapus: true,
          retensi: 'Sampai kamu menghapusnya di sini, atau menghapus akun.',
        ),
        const KategoriPrivasi(
          key: 'audit',
          label: 'Jejak audit',
          jumlah: 5,
          turunan: 1,
          bisaDihapus: false,
          retensi: 'Selama layanan berjalan.',
          alasanTakBisaDihapus: 'Bukti bahwa sesuatu terjadi.',
        ),
      ],
      tidakDikumpulkan: const ['Lokasi', 'Kalender'],
    );
  }

  @override
  Future<List<IzinAgent>> izinAgent() async {
    panggilan.add('izin');
    return izin;
  }

  @override
  Future<IzinBerlaku> tetapkanIzin(
    String agent,
    String scope,
    String aksi,
    String keputusan,
  ) async {
    panggilan.add('tetapkan $agent $scope $aksi $keputusan');
    _mungkinGagal();
    return IzinBerlaku(
      scope: scope,
      aksi: aksi,
      keputusan: keputusan,
      sumber: 'user',
      sensitif: scope == 'mood',
      konfirmasiTiapKali: false,
    );
  }

  @override
  Future<Ekspor> mintaEkspor(String sandi) async {
    panggilan.add('ekspor');
    _sandi(sandi);
    return const Ekspor(
      id: 'e1',
      status: 'ready',
      jalurUnduh: '/v1/privacy/export/e1/download',
    );
  }

  @override
  Future<List<int>> unduhEkspor(String id) async {
    panggilan.add('unduh $id');
    return List<int>.filled(2048, 32);
  }

  @override
  Future<Map<String, int>> hapusData(String kategori, String sandi) async {
    panggilan.add('hapus $kategori');
    _sandi(sandi);
    final n = jurnal;
    jurnal = 0;
    return {'journal_entries': n, 'events': n};
  }

  @override
  Future<String> hapusAkun(String sandi) async {
    panggilan.add('hapus-akun');
    _sandi(sandi);
    return '2026-11-06T00:00:00Z';
  }

  @override
  Future<PreferensiNotifikasi> notifikasi() async {
    panggilan.add('notifikasi');
    return pref;
  }

  @override
  Future<PreferensiNotifikasi> ubahNotifikasi({
    Map<String, bool>? jenis,
    JamTenang? jamTenang,
    bool hapusJamTenang = false,
  }) async {
    panggilan.add(
      'ubah-notifikasi ${jenis ?? {}} ${jamTenang?.mulai ?? ''} ${hapusJamTenang ? 'tanpa-jam' : ''}'
          .trim(),
    );
    _mungkinGagal();
    pref = PreferensiNotifikasi(
      jenis: [
        for (final j in pref.jenis)
          JenisNotifikasi(
            key: j.key,
            label: j.label,
            nyala: jenis?[j.key] ?? j.nyala,
            wajib: j.wajib,
          ),
      ],
      jamTenang: hapusJamTenang ? null : (jamTenang ?? pref.jamTenang),
      paguHarian: pref.paguHarian,
      dikirim: pref.dikirim,
    );
    return pref;
  }

  @override
  Future<TinjauanMingguan> tinjauanMingguan({String? minggu}) async {
    panggilan.add('tinjauan ${minggu ?? 'kini'}');
    _mungkinGagal();
    return tinjauan(minggu);
  }
}
