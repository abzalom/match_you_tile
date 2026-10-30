"""Latar JPEG menu dan undian latar level tanpa pengulangan langsung."""

import math
from pathlib import Path
import random
import pygame


class LatarPermainan:
    def __init__(self, folder, ukuran, acak=None):
        self.ukuran = ukuran
        self.acak = acak if acak is not None else random.Random()
        berkas = sorted(p for p in Path(folder).iterdir()
                        if p.is_file() and p.suffix.lower() in (".jpeg", ".jpg")
                        and p.stem.lower().startswith("bg_"))
        self.menu = next(p for p in berkas if p.stem.lower() == "bg_menu_utama")
        self.pilihan = [p for p in berkas if p != self.menu]
        if not self.pilihan:
            raise ValueError("Tambahkan JPEG BG_ selain BG_menu_utama untuk latar game.")
        self.aktif = None
        self.antrean = []
        self.cache = {}
        self.gambar(self.menu)

    def pilih_level(self):
        if not self.antrean:
            self.antrean = list(self.pilihan)
            self.acak.shuffle(self.antrean)
            # Jaga batas dua putaran undian agar gambar terakhir tidak berulang.
            if len(self.antrean) > 1 and self.antrean[-1] == self.aktif:
                self.antrean[0], self.antrean[-1] = self.antrean[-1], self.antrean[0]
        self.aktif = self.antrean.pop()
        return self.aktif

    def gambar(self, berkas):
        if berkas not in self.cache:
            asli = pygame.image.load(str(berkas)).convert()
            lebar, tinggi = self.ukuran
            skala = max(lebar / asli.get_width(), tinggi / asli.get_height())
            # Cover menjaga proporsi; potong kelebihan di tengah tanpa meregangkan.
            besar = pygame.transform.smoothscale(asli, (
                math.ceil(asli.get_width() * skala), math.ceil(asli.get_height() * skala)))
            kotak = pygame.Rect(0, 0, lebar, tinggi)
            kotak.center = besar.get_rect().center
            self.cache[berkas] = besar.subsurface(kotak).copy()
        return self.cache[berkas]

    def untuk_halaman(self, halaman):
        return self.gambar(self.menu if halaman == "menu" else (self.aktif or self.menu))
