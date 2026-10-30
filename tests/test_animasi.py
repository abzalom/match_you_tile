import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import unittest
import pygame

from permainan.animasi import GerakanKartu


class UjiAnimasi(unittest.TestCase):
    def test_pengalihan_arah_dimulai_dari_posisi_visual_saat_ini(self):
        awal = pygame.Rect(30, 400, 66, 74)
        tujuan = pygame.Rect(22, 139, 64, 74)
        pertama = GerakanKartu(awal, tujuan, 0, False, 100)
        tengah = pertama.potret(310)[0]
        kedua = GerakanKartu(tengah, tujuan.move(72, 0), 0, False, 310)
        self.assertEqual(kedua.potret(310)[0], tengah)
        self.assertEqual(kedua.potret(730)[0], tujuan.move(72, 0))

    def test_kelompok_mencapai_slot_lalu_mengecil(self):
        gerakan = GerakanKartu(pygame.Rect(30, 400, 66, 74),
                              pygame.Rect(22, 139, 64, 74), 0, False, 0,
                              musnah=True, durasi=620)
        self.assertEqual(gerakan.potret(434)[0], gerakan.akhir)
        self.assertLess(gerakan.potret(570)[0].width, gerakan.akhir.width)
        self.assertEqual(gerakan.potret(620)[0].size, (0, 0))
