// Privacy Center (spec/07 6.4), notifikasi (6.3), tinjauan mingguan (6.2) — bentuk data
// spec/04 dan antarmuka layanannya. Hanya medan yang dipakai layar; medan lain diabaikan.

/// Satu baris *“What HumanVerse knows”* (naskah 5 §26) — jumlah, bukan isi.
class KategoriPrivasi {
  const KategoriPrivasi({
    required this.key,
    required this.label,
    required this.jumlah,
    required this.turunan,
    required this.bisaDihapus,
    required this.retensi,
    this.alasanTakBisaDihapus,
  });

  factory KategoriPrivasi.dariJson(Map<String, dynamic> json) =>
      KategoriPrivasi(
        key: json['key'] as String,
        label: json['label'] as String,
        jumlah: json['count'] as int,
        turunan: json['derived_count'] as int,
        bisaDihapus: json['deletable'] as bool,
        retensi: json['retention'] as String,
        alasanTakBisaDihapus: json['why_not_deletable'] as String?,
      );

  final String key;
  final String label;
  final int jumlah; // yang kamu catat
  final int turunan; // yang sistem turunkan darinya
  final bool bisaDihapus;
  final String retensi;
  final String? alasanTakBisaDihapus;
}

class RingkasanPrivasi {
  const RingkasanPrivasi({
    required this.kategori,
    required this.tidakDikumpulkan,
  });

  factory RingkasanPrivasi.dariJson(Map<String, dynamic> json) =>
      RingkasanPrivasi(
        kategori: [
          for (final k in json['categories'] as List<dynamic>)
            KategoriPrivasi.dariJson(k as Map<String, dynamic>),
        ],
        tidakDikumpulkan: [
          for (final k in json['not_collected'] as List<dynamic>)
            (k as Map<String, dynamic>)['label'] as String,
        ],
      );

  final List<KategoriPrivasi> kategori;
  final List<String> tidakDikumpulkan;
}

/// Keputusan yang BERLAKU untuk satu (agent, scope, aksi) — `sumber` `user` = yang kamu
/// simpan, `default` = bawaan gerbang risiko.
class IzinBerlaku {
  const IzinBerlaku({
    required this.scope,
    required this.aksi,
    required this.keputusan,
    required this.sumber,
    required this.sensitif,
    required this.konfirmasiTiapKali,
  });

  factory IzinBerlaku.dariJson(Map<String, dynamic> json) => IzinBerlaku(
    scope: json['scope'] as String,
    aksi: json['action'] as String,
    keputusan: json['decision'] as String,
    sumber: json['source'] as String,
    sensitif: json['sensitive'] as bool,
    konfirmasiTiapKali: json['confirm_each_time'] as bool,
  );

  final String scope;
  final String aksi; // read · write · execute
  final String keputusan; // allow · ask · deny
  final String sumber; // user · default
  final bool sensitif;
  final bool konfirmasiTiapKali;
}

class IzinAgent {
  const IzinAgent({
    required this.agent,
    required this.tujuan,
    required this.izin,
  });

  factory IzinAgent.dariJson(Map<String, dynamic> json) => IzinAgent(
    agent: json['subject_id'] as String,
    tujuan: [for (final t in json['purpose'] as List<dynamic>) t as String],
    izin: [
      for (final i in json['permissions'] as List<dynamic>)
        IzinBerlaku.dariJson(i as Map<String, dynamic>),
    ],
  );

  final String agent;
  final List<String> tujuan;
  final List<IzinBerlaku> izin;
}

class Ekspor {
  const Ekspor({required this.id, required this.status, this.jalurUnduh});

  factory Ekspor.dariJson(Map<String, dynamic> json) => Ekspor(
    id: json['export_id'] as String,
    status: json['status'] as String,
    jalurUnduh: json['download_url'] as String?,
  );

  final String id;
  final String status; // ready · downloaded
  final String? jalurUnduh;
}

class JamTenang {
  const JamTenang({required this.mulai, required this.selesai});

  factory JamTenang.dariJson(Map<String, dynamic> json) =>
      JamTenang(mulai: json['start'] as String, selesai: json['end'] as String);

  final String mulai; // HH:MM
  final String selesai;

  Map<String, dynamic> keJson() => {'start': mulai, 'end': selesai};
}

class JenisNotifikasi {
  const JenisNotifikasi({
    required this.key,
    required this.label,
    required this.nyala,
    required this.wajib,
  });

  factory JenisNotifikasi.dariJson(Map<String, dynamic> json) =>
      JenisNotifikasi(
        key: json['key'] as String,
        label: json['label'] as String,
        nyala: json['enabled'] as bool,
        wajib: json['required'] as bool,
      );

  final String key;
  final String label;
  final bool nyala;
  final bool wajib; // keamanan akun — tidak bisa dimatikan
}

class PreferensiNotifikasi {
  const PreferensiNotifikasi({
    required this.jenis,
    required this.jamTenang,
    required this.paguHarian,
    required this.dikirim,
  });

  factory PreferensiNotifikasi.dariJson(Map<String, dynamic> json) {
    final tenang = json['quiet_hours'] as Map<String, dynamic>?;
    return PreferensiNotifikasi(
      jenis: [
        for (final j in json['types'] as List<dynamic>)
          JenisNotifikasi.dariJson(j as Map<String, dynamic>),
      ],
      jamTenang: tenang == null ? null : JamTenang.dariJson(tenang),
      paguHarian: json['daily_cap'] as int,
      // V0 tidak mengirim apa pun (A-28) — layar mengatakannya, bukan menjanjikannya.
      dikirim: json['delivery'] != 'none',
    );
  }

  final List<JenisNotifikasi> jenis;
  final JamTenang? jamTenang;
  final int paguHarian;
  final bool dikirim;
}

class SumbuTinjauan {
  const SumbuTinjauan({
    required this.key,
    required this.label,
    required this.nilai,
    required this.sebelumnya,
    required this.satuan,
    required this.why,
  });

  factory SumbuTinjauan.dariJson(Map<String, dynamic> json) => SumbuTinjauan(
    key: json['key'] as String,
    label: json['label'] as String,
    nilai: (json['value'] as num).toDouble(),
    sebelumnya: (json['previous'] as num?)?.toDouble(),
    satuan: json['unit'] as String,
    why: json['why'] as String,
  );

  final String key;
  final String label;
  final double nilai;
  final double? sebelumnya;
  final String satuan; // 0-1 · 1-5 · jam
  final String why;
}

class PertanyaanTinjauan {
  const PertanyaanTinjauan({
    required this.key,
    required this.pertanyaan,
    required this.bertanya,
    required this.butir,
    required this.ajakan,
  });

  factory PertanyaanTinjauan.dariJson(Map<String, dynamic> json) =>
      PertanyaanTinjauan(
        key: json['key'] as String,
        pertanyaan: json['question'] as String,
        bertanya: json['stance'] == 'ask',
        butir: [
          for (final b in json['items'] as List<dynamic>)
            (b as Map<String, dynamic>)['text'] as String,
        ],
        ajakan: json['prompt'] as String,
      );

  final String key;
  final String pertanyaan;
  final bool
  bertanya; // Confidence Layer: tanpa bukti sistem bertanya, tidak menyatakan
  final List<String> butir;
  final String ajakan;
}

class TinjauanMingguan {
  const TinjauanMingguan({
    required this.minggu,
    required this.mulai,
    required this.selesai,
    required this.lengkap,
    required this.sumbu,
    required this.tidakDiukur,
    required this.pertanyaan,
  });

  factory TinjauanMingguan.dariJson(Map<String, dynamic> json) =>
      TinjauanMingguan(
        minggu: json['week'] as String,
        mulai: json['start'] as String,
        selesai: json['end'] as String,
        lengkap: json['complete'] as bool,
        sumbu: [
          for (final s in json['axes'] as List<dynamic>)
            SumbuTinjauan.dariJson(s as Map<String, dynamic>),
        ],
        tidakDiukur: [
          for (final s in json['not_measured'] as List<dynamic>)
            (s as Map<String, dynamic>)['label'] as String,
        ],
        pertanyaan: [
          for (final q in json['questions'] as List<dynamic>)
            PertanyaanTinjauan.dariJson(q as Map<String, dynamic>),
        ],
      );

  final String minggu; // 2026-W40
  final String mulai;
  final String selesai;
  final bool lengkap;
  final List<SumbuTinjauan> sumbu;
  final List<String> tidakDiukur;
  final List<PertanyaanTinjauan> pertanyaan;
}

/// Minggu ISO sebelum/sesudah `minggu` (`2026-W40` → `2026-W39`) — navigasi layar tinjauan.
String mingguGeser(String mulaiSenin, int langkah) {
  // UTC: tanpa pergeseran jam musim panas di tengah penjumlahan hari.
  final senin = DateTime.parse('${mulaiSenin}T00:00:00Z')
      .add(Duration(days: 7 * langkah));
  final kamis = senin.add(
    const Duration(days: 3),
  ); // minggu ISO = tahun hari Kamisnya
  final awalTahun = DateTime.utc(kamis.year);
  final minggu = (kamis.difference(awalTahun).inDays ~/ 7) + 1;
  return '${kamis.year}-W${minggu.toString().padLeft(2, '0')}';
}

/// Yang dibutuhkan layar Privacy Center, notifikasi, dan tinjauan dari API — terpisah dari
/// `LayananHabit` supaya antrean luring (6.6) tidak ikut membungkus tindakan yang tidak
/// boleh menunggu jaringan (hapus data, ekspor).
abstract interface class LayananPrivasi {
  Future<RingkasanPrivasi> ringkasanPrivasi();

  Future<List<IzinAgent>> izinAgent();

  /// `keputusan`: allow · ask · deny.
  Future<IzinBerlaku> tetapkanIzin(
    String agent,
    String scope,
    String aksi,
    String keputusan,
  );

  Future<Ekspor> mintaEkspor(String sandi);

  /// Isi ekspor — SEKALI pakai (yang kedua: `GalatApi` 410).
  Future<List<int>> unduhEkspor(String id);

  /// Tabel → baris yang dihapus, termasuk turunannya.
  Future<Map<String, int>> hapusData(String kategori, String sandi);

  /// `DELETE /me` (6.5): jadwal hapus akun — semua sesi dicabut server.
  Future<String> hapusAkun(String sandi);

  Future<PreferensiNotifikasi> notifikasi();

  Future<PreferensiNotifikasi> ubahNotifikasi({
    Map<String, bool>? jenis,
    JamTenang? jamTenang,
    bool hapusJamTenang = false,
  });

  /// `minggu` null = minggu yang sedang berjalan (zona profil).
  Future<TinjauanMingguan> tinjauanMingguan({String? minggu});
}
