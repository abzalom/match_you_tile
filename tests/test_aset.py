"""Validasi katalog dan render ikon SVG."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
from collections import Counter
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import pygame
from permainan.aset import muat_aset

class UjiAset(unittest.TestCase):
    def test_kategori_svg_render_unik_dan_transparan(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        try:
            folder = Path(__file__).resolve().parent.parent / "assets" / "svg"
            katalog, gambar = muat_aset(folder)
            self.assertEqual(Counter(k["kategori"] for k in katalog),
                             {"buah": 6, "sayuran": 6, "bumbu": 6, "makanan": 6})
            self.assertEqual(len({k["berkas"] for k in katalog}), 24)
            self.assertEqual(len({pygame.image.tobytes(g, "RGBA") for g in gambar}), 24)
            for entri, ikon in zip(katalog, gambar):
                akar = ET.parse(folder / entri["berkas"]).getroot()
                self.assertEqual(akar.attrib["viewBox"], "0 0 128 128")
                self.assertEqual(ikon.get_size(), (60, 60))
                self.assertGreater(ikon.get_bounding_rect().width, 20)
                self.assertEqual(ikon.get_at((0, 0)).a, 0)
        finally:
            pygame.quit()
