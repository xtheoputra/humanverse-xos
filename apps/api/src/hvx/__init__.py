"""HumanVerse XOS — API V0.

Satu proses, dua belas modul di `hvx.modules` (spec/06). Titik rakit
aplikasinya `hvx.main.create_app`.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hvx-api")
except PackageNotFoundError:  # pragma: no cover - hanya terjadi di luar instalasi
    __version__ = "0.0.0+tidak-terpasang"

__all__ = ["__version__"]
