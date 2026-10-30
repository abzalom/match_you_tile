import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from pathlib import Path
import random
import unittest
import pygame

from permainan.latar import LatarPermainan


class UjiLatar(unittest.TestCase):
    def test_menu_tetap_dan_game_acak_tanpa_ulang_langsung(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        try:
            latar = LatarPermainan(Path(__file__).resolve().parent.parent / "assets",
                                  (540, 960), random.Random(42))
            self.assertEqual(latar.menu.stem, "BG_menu_utama")
            undian = [latar.pilih_level() for _ in range(15)]
            for i in range(0, 15, len(latar.pilihan)):
                self.assertEqual(set(undian[i:i + len(latar.pilihan)]), set(latar.pilihan))
            self.assertTrue(all(a != b for a, b in zip(undian, undian[1:])))
            self.assertNotIn(latar.menu, undian)
            for berkas in [latar.menu] + latar.pilihan:
                self.assertEqual(latar.gambar(berkas).get_size(), (540, 960))
                self.assertIs(latar.gambar(berkas), latar.gambar(berkas))
        finally:
            pygame.quit()
