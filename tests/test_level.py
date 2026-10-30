import unittest

from permainan.level import profil_level, RENTANG_JENIS


class UjiLevel(unittest.TestCase):
    def test_seribu_profil_memiliki_batas_aman(self):
        for nomor in range(1, 1001):
            profil = profil_level(nomor)
            self.assertEqual(profil.nomor, nomor)
            self.assertTrue(27 <= profil.jumlah_kartu <= 90)
            self.assertEqual(profil.jumlah_kartu % 3, 0)
            self.assertTrue(3 <= profil.jumlah_jenis <= 18)
            if nomor <= 3:
                self.assertEqual(profil.jumlah_jenis, 3)
            else:
                awal, akhir = RENTANG_JENIS[profil.kategori]
                self.assertTrue(awal <= profil.jumlah_jenis <= akhir)
            self.assertLessEqual(profil.jumlah_jenis * 3, profil.jumlah_kartu)
            self.assertTrue(0.78 <= profil.sebaran <= 1)
            self.assertTrue(1 <= profil.indeks <= 100)

    def test_awal_akhir_dan_jeda_siklus(self):
        awal, akhir = profil_level(1), profil_level(1000)
        self.assertEqual((awal.jumlah_kartu, awal.jumlah_jenis), (27, 3))
        self.assertEqual((akhir.jumlah_kartu, akhir.jumlah_jenis), (90, 18))
        self.assertLess(profil_level(501).indeks, profil_level(500).indeks)

    def test_tiga_bagian_dan_seratus_level_gila(self):
        for nomor, kategori in ((1, "Mudah"), (333, "Mudah"), (334, "Sedang"),
                                (666, "Sedang"), (667, "Sulit"), (999, "Sulit")):
            self.assertEqual(profil_level(nomor).kategori, kategori)
        self.assertEqual(sum(profil_level(n).kategori == "Gila" for n in range(1, 1001)), 100)
        for nomor in range(10, 1001, 10):
            gila, biasa = profil_level(nomor), profil_level(nomor - 1)
            self.assertEqual(gila.kategori, "Gila")
            self.assertGreater(gila.indeks, biasa.indeks)
            self.assertLess(gila.sebaran, biasa.sebaran)

    def test_jenis_naik_bertahap_di_dalam_setiap_kategori(self):
        kelompok = {nama: [] for nama in RENTANG_JENIS}
        for nomor in range(4, 1001):
            profil = profil_level(nomor)
            kelompok[profil.kategori].append(profil.jumlah_jenis)
        for kategori, nilai in kelompok.items():
            self.assertEqual(nilai, sorted(nilai))
            self.assertEqual((min(nilai), max(nilai)), RENTANG_JENIS[kategori])

    def test_contoh_level_saat_memperkenalkan_jenis_baru(self):
        for nomor, jenis in ((3, 3), (4, 5), (99, 6), (299, 7), (334, 8),
                             (500, 16), (666, 10), (667, 11), (999, 13), (1000, 18)):
            self.assertEqual(profil_level(nomor).jumlah_jenis, jenis)
