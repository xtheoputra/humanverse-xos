// Menyimpan berkas ekspor Privacy Center (spec/07 6.4) di perangkat pemiliknya.
//
// Web: unduhan peramban biasa (Blob + tautan `download`) — berkasnya milik pengguna, disimpan
// atas tindakannya sendiri. Platform lain: `false` — menyimpan ke penyimpanan perangkat butuh
// plugin dan keputusan penyimpanan perangkat (C-35 — milik pemilik); layar mengatakannya,
// bukan diam.
export 'simpan_berkas_lain.dart'
    if (dart.library.js_interop) 'simpan_berkas_web.dart';
