"""Audit 1.000 level: batas papan, ragam gambar, dan satu solusi tanpa bantuan."""

import csv
from pathlib import Path
import random

from permainan.model import Permainan, LEBAR_KARTU, TINGGI_KARTU


def audit():
    tujuan = Path(__file__).resolve().parent / "dokumentasi" / "profil_level.csv"
    with tujuan.open("w", newline="", encoding="utf-8") as berkas:
        penulis = csv.writer(berkas)
        penulis.writerow(("level", "kategori", "indeks_desain", "kartu", "tumpukan",
                          "jenis", "sebaran", "bentuk_audit", "bisa_dipilih_awal", "solusi_valid"))
        for level in range(1, Permainan.level_maksimum + 1):
            game = Permainan(level, random.Random(level))
            profil = game.profil
            assert len(game.kartu) == profil.jumlah_kartu
            assert len({k.jenis for k in game.kartu}) == profil.jumlah_jenis
            for kartu in game.kartu:
                assert 20 <= round(kartu.x) <= 520 - LEBAR_KARTU
                assert 245 <= round(kartu.y) <= 820 - TINGGI_KARTU - 8
            tersedia = sum(game.teratas(k) for k in game.kartu)
            for kartu in reversed(game.kartu):
                assert game.pilih(kartu), f"Solusi gagal pada level {level}"
            assert game.status == "menang"
            penulis.writerow((level, profil.kategori, profil.indeks, len(game.kartu),
                              game.kolom * 3, game.jumlah_jenis, round(profil.sebaran, 4),
                              game.bentuk, tersedia, "ya"))
    print(f"Lulus: {Permainan.level_maksimum} level. Laporan: {tujuan}")


if __name__ == "__main__":
    audit()
