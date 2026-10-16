import 'dart:js_interop';
import 'dart:typed_data';

import 'package:web/web.dart' as web;

/// Unduhan peramban: isi dijadikan Blob, tautan sementaranya diklik lalu DICABUT — salinan
/// data tidak tinggal sebagai URL hidup di halaman.
Future<bool> simpanBerkas(String nama, List<int> isi) async {
  final blob = web.Blob(
    [Uint8List.fromList(isi).toJS].toJS,
    web.BlobPropertyBag(type: 'application/json'),
  );
  final url = web.URL.createObjectURL(blob);
  final tautan = web.HTMLAnchorElement()
    ..href = url
    ..download = nama;
  web.document.body?.append(tautan);
  tautan.click();
  tautan.remove();
  web.URL.revokeObjectURL(url);
  return true;
}
