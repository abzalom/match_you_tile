"""Jalankan dengan python main.py dari direktori mana pun."""

import sys


if __name__ == "__main__":
    if "--uji-paket" in sys.argv:
        from permainan.uji_paket import jalankan
        indeks = sys.argv.index("--uji-paket")
        if len(sys.argv) <= indeks + 1:
            raise SystemExit("Sertakan lokasi JSON laporan setelah --uji-paket.")
        raise SystemExit(jalankan(sys.argv[indeks + 1]))
    from permainan.antarmuka import Aplikasi
    Aplikasi().jalankan()
