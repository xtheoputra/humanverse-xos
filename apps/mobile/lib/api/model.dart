// Bentuk data API V0 — spec/04. Hanya medan yang dipakai layar; medan lain
// diabaikan (spec/03 aturan 3: pembaca mengabaikan medan yang tidak dikenalnya).

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
    // numeric → JSON sebagai string desimal (pydantic Decimal)
    jamTidur: json['sleep_hours']?.toString(),
    catatan: json['note'] as String?,
  );

  final String forDate;
  final int? energi;
  final int? fokus;
  final String? jamTidur;
  final String? catatan;

  /// Badan `PUT` — PUT = GANTI (spec/04): medan lama ikut dikirim supaya tidak hilang.
  Map<String, dynamic> keJsonDenganEnergi(int energiBaru) => {
    'energy': energiBaru,
    if (fokus != null) 'focus': fokus,
    if (jamTidur != null) 'sleep_hours': double.parse(jamTidur!),
    if (catatan != null) 'note': catatan,
  };
}
