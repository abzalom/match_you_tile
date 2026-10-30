"""Katalog ikon SVG yang dimuat sekali dan dipakai ulang selama permainan."""

import json
from pathlib import Path
import pygame
from .level import JENIS_MAKSIMUM


def muat_aset(folder):
    folder = Path(folder)
    katalog = json.loads((folder / "katalog.json").read_text(encoding="utf-8"))
    if len(katalog) < JENIS_MAKSIMUM:
        raise ValueError(f"Katalog memerlukan setidaknya {JENIS_MAKSIMUM} gambar kartu berbeda.")
    gambar = []
    for entri in katalog:
        # SVG diraster saat startup oleh SDL_image; tidak ada konversi per frame
        # atau dependensi tambahan. ViewBox tetap menjaga ruang ikon konsisten.
        asli = pygame.image.load(str(folder / entri["berkas"])).convert_alpha()
        gambar.append(pygame.transform.smoothscale(asli, (60, 60)))
    return katalog, gambar


class AsetTombol:
    """Ikon dan latar SVG tombol, dengan cache ukuran/status tampilan."""

    aksi = ("mulai", "menu", "kembali", "cocok", "acak", "lanjut", "ulang",
            "suara_aktif", "suara_mati", "pengaturan", "bahasa")
    gaya = ("dasar", "utama", "sorot", "utama_sorot", "nonaktif")

    def __init__(self, folder):
        folder = Path(folder)
        self.ikon = {nama: pygame.image.load(str(folder / f"{nama}.svg")).convert_alpha()
                     for nama in self.aksi}
        self.latar = {nama: pygame.image.load(str(folder / f"latar_{nama}.svg")).convert_alpha()
                      for nama in self.gaya}
        self.cache = {}

    def gambar(self, aksi, ukuran, utama=False, sorot=False, tersedia=True):
        gaya = ("utama_sorot" if sorot else "utama") if utama else ("sorot" if sorot else "dasar")
        if not tersedia:
            gaya = "nonaktif"
        kunci = (aksi, tuple(ukuran), gaya)
        if kunci not in self.cache:
            latar = pygame.transform.smoothscale(self.latar[gaya], ukuran)
            sisi = min(44, ukuran[1] - 14)
            ikon = pygame.transform.smoothscale(self.ikon[aksi], (sisi, sisi))
            if not tersedia:
                ikon.set_alpha(100)
            self.cache[kunci] = latar, ikon
        return self.cache[kunci]
