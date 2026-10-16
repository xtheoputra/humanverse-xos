// Bentuk data API V0 — spec/04. Hanya medan yang dipakai layar; medan lain
// diabaikan (spec/03 aturan 3: pembaca mengabaikan medan yang tidak dikenalnya).
import 'dart:math';

/// UUID v4 buatan klien — spec/04: klien boleh membuat id sendiri (dukungan luring).
///
/// Id yang dibuat SEKALI per tindakan dan dipakai ulang di tiap percobaan
/// tindakan itu membuat "coba lagi" sesudah jaringan putus aman: server yang
/// sudah menerima percobaan pertama memutar ulang jawabannya, bukan membuat
/// habit kedua (tinjauan Sprint 2).
String idBaru([Random? acak]) {
  final r = acak ?? Random.secure();
  final b = List<int>.generate(16, (_) => r.nextInt(256));
  b[6] = (b[6] & 0x0f) | 0x40; // versi 4
  b[8] = (b[8] & 0x3f) | 0x80; // varian RFC 4122
  final hex = b.map((x) => x.toRadixString(16).padLeft(2, '0')).join();
  return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-'
      '${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
}

/// Tanggal LOKAL perangkat sebagai `YYYY-MM-DD` (spec/04: tanggal lokal pengguna).
///
/// Sengaja dari `DateTime` lokal, bukan UTC: habit yang dijalankan Senin pagi di
/// Jakarta adalah Senin, walau di UTC masih Minggu (spec/01 `for_date`).
String tanggalLokal(DateTime waktu) {
  final t = waktu.toLocal();
  String dua(int n) => n.toString().padLeft(2, '0');
  return '${t.year.toString().padLeft(4, '0')}-${dua(t.month)}-${dua(t.day)}';
}

class Pengguna {
  const Pengguna({required this.id, required this.email});

  factory Pengguna.dariJson(Map<String, dynamic> json) =>
      Pengguna(id: json['id'] as String, email: json['email'] as String);

  final String id;
  final String email;
}

class Tier {
  const Tier({required this.label, this.menit});

  factory Tier.dariJson(Map<String, dynamic> json) =>
      Tier(label: json['label'] as String, menit: json['minutes'] as int?);

  final String label;
  final int? menit;

  Map<String, dynamic> keJson() => {
    'label': label,
    if (menit != null) 'minutes': menit,
  };
}

class Penyelesaian {
  const Penyelesaian({
    required this.forDate,
    required this.status,
    this.tierDipakai,
  });

  factory Penyelesaian.dariJson(Map<String, dynamic> json) => Penyelesaian(
    forDate: json['for_date'] as String,
    status: json['status'] as String,
    tierDipakai: json['tier_used'] as int?,
  );

  final String forDate;
  final String status; // done · skipped · partial
  final int? tierDipakai;

  bool get dijalankan => status == 'done' || status == 'partial';
}

/// `day` pada `GET /v1/habits?for_date=` — keadaan habit pada tanggal itu.
class HariHabit {
  const HariHabit({
    required this.forDate,
    this.penyelesaian,
    this.energi,
    this.tierDisarankan,
  });

  factory HariHabit.dariJson(Map<String, dynamic> json) {
    final selesai = json['completion'];
    return HariHabit(
      forDate: json['for_date'] as String,
      penyelesaian: selesai == null
          ? null
          : Penyelesaian.dariJson(selesai as Map<String, dynamic>),
      energi: json['energy'] as int?,
      tierDisarankan: json['suggested_tier'] as int?,
    );
  }

  final String forDate;
  final Penyelesaian? penyelesaian;
  final int? energi;
  final int? tierDisarankan;
}

class Habit {
  const Habit({
    required this.id,
    required this.judul,
    required this.periode,
    required this.target,
    required this.tier,
    this.hari,
  });

  factory Habit.dariJson(Map<String, dynamic> json) {
    final hari = json['day'];
    return Habit(
      id: json['id'] as String,
      judul: json['title'] as String,
      periode: json['period'] as String,
      target: json['target_count'] as int,
      tier: [
        for (final t in json['adaptive_tiers'] as List<dynamic>)
          Tier.dariJson(t as Map<String, dynamic>),
      ],
      hari: hari == null
          ? null
          : HariHabit.dariJson(hari as Map<String, dynamic>),
    );
  }

  final String id;
  final String judul;
  final String periode; // day · week · month
  final int target;
  final List<Tier> tier;
  final HariHabit? hari;

  bool get selesaiHariItu => hari?.penyelesaian?.dijalankan ?? false;

  /// Tanggal itu sudah punya catatan APA PUN — termasuk `skipped`. Mengganti
  /// status = batalkan lalu catat lagi (spec/04): `POST` ke tanggal yang sudah
  /// tercatat mengembalikan baris lama, bukan menggantinya.
  bool get tercatatHariItu => hari?.penyelesaian != null;

  bool get dilewatiHariItu => hari?.penyelesaian?.status == 'skipped';

  /// Salinan dengan catatan [tanggal] diganti `p` (`null` = tidak tercatat);
  /// energi dan tier yang disarankan dibiarkan — itu dari server, bukan dari catatan.
  Habit denganPenyelesaian(String tanggal, Penyelesaian? p) => Habit(
    id: id,
    judul: judul,
    periode: periode,
    target: target,
    tier: tier,
    hari: HariHabit(
      forDate: hari?.forDate ?? tanggal,
      penyelesaian: p,
      energi: hari?.energi,
      tierDisarankan: hari?.tierDisarankan,
    ),
  );
}

/// Satu dimensi dashboard (naskah 4 §28) — skor PLUS Why-nya.
class Dimensi {
  const Dimensi({
    required this.key,
    required this.nilai,
    required this.keyakinan,
    required this.bukti,
    required this.why,
  });

  factory Dimensi.dariJson(Map<String, dynamic> json) => Dimensi(
    key: json['key'] as String,
    nilai: (json['value'] as num).toDouble(),
    keyakinan: (json['confidence'] as num).toDouble(),
    bukti: json['evidence_count'] as int,
    why: json['why'] as String,
  );

  final String key; // 'energy' · 'focus'
  final double nilai; // 0–1
  final double keyakinan; // 0–1
  final int bukti;
  final String why;
}

/// `GET /v1/dashboard` — beberapa dimensi, tiap skor ber-Why (§28). `asOf` null =
/// belum ada check-in (cold start), `dimensi` kosong.
class Dasbor {
  const Dasbor({required this.asOf, required this.dimensi});

  factory Dasbor.dariJson(Map<String, dynamic> json) => Dasbor(
    asOf: json['as_of'] as String?,
    dimensi: [
      for (final d in json['dimensions'] as List<dynamic>)
        Dimensi.dariJson(d as Map<String, dynamic>),
    ],
  );

  final String? asOf;
  final List<Dimensi> dimensi;
}

class Checkin {
  const Checkin({
    required this.forDate,
    this.energi,
    this.fokus,
    this.jamTidur,
    this.catatan,
  });

  factory Checkin.dariJson(Map<String, dynamic> json) => Checkin(
    forDate: json['for_date'] as String,
    energi: json['energy'] as int?,
    fokus: json['focus'] as int?,
    // spec/04: angka JSON (E-170 — dulu string desimal "7.5").
    jamTidur: (json['sleep_hours'] as num?)?.toDouble(),
    catatan: json['note'] as String?,
  );

  final String forDate;
  final int? energi;
  final int? fokus;
  final double? jamTidur;
  final String? catatan;

  /// Badan `PUT` — PUT = GANTI (spec/04): medan lama ikut dikirim supaya tidak hilang.
  Map<String, dynamic> keJsonDenganEnergi(int energiBaru) => {
    'energy': energiBaru,
    if (fokus != null) 'focus': fokus,
    'sleep_hours': ?jamTidur,
    if (catatan != null) 'note': catatan,
  };
}
