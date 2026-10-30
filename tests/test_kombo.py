import random
import unittest

from permainan.model import Kartu, Permainan


class UjiKombo(unittest.TestCase):
    def setUp(self):
        self.waktu = 0.0
        self.game = Permainan(acak=random.Random(42), jam=lambda: self.waktu)
        self.game.kartu = [Kartu(i, i // 3, i, 0) for i in range(24)]

    def cocok(self, kelompok, bantuan=False):
        for kartu in self.game.kartu[kelompok * 3:kelompok * 3 + 3]:
            self.assertTrue(self.game.pilih(kartu, bantuan=bantuan))

    def test_bonus_bertahap_dan_batas_lima(self):
        for kelompok in range(7):
            self.waktu += 1
            self.cocok(kelompok)
            self.assertEqual(self.game.kombo, min(5, kelompok + 1))
            self.assertEqual(self.game.terakhir_poin, 300 * min(5, kelompok + 1))
        self.assertEqual(self.game.kombo_tertinggi, 5)

    def test_batas_lima_detik_termasuk_tepat_batas(self):
        self.cocok(0)
        self.waktu = 5
        self.cocok(1)
        self.assertEqual(self.game.kombo, 2)
        self.waktu = 10.001
        self.game.perbarui_kombo()
        self.assertEqual(self.game.kombo, 0)
        self.cocok(2)
        self.assertEqual(self.game.terakhir_poin, 300)
        self.assertEqual(self.game.kombo, 1)

    def test_bantuan_memutus_rantai_dan_tidak_mendapat_bonus(self):
        self.cocok(0)
        self.cocok(1)
        self.cocok(2, bantuan=True)
        self.assertEqual(self.game.kombo, 0)
        self.assertEqual(self.game.terakhir_poin, 300)
        self.cocok(3)
        self.assertEqual(self.game.kombo, 1)

    def test_undo_dan_acak_berhasil_memutus_kombo(self):
        self.cocok(0)
        self.game.pilih(self.game.kartu[3])
        self.assertTrue(self.game.kembalikan())
        self.assertEqual(self.game.kombo, 0)
        self.cocok(1)
        self.assertTrue(self.game.acak_ulang())
        self.assertEqual(self.game.kombo, 0)

    def test_modal_menjeda_waktu_kombo(self):
        self.cocok(0)
        self.waktu = 2
        self.game.jeda_kombo()
        self.waktu = 102
        self.game.perbarui_kombo()
        self.assertEqual(self.game.sisa_kombo(), 3)
        self.game.lanjutkan_kombo()
        self.assertEqual(self.game.sisa_kombo(), 3)
        self.cocok(1)
        self.assertEqual(self.game.kombo, 2)
