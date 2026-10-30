"""Pengujian aturan slot, bantuan, dan penyelesaian papan."""

from collections import Counter
import random
import unittest

from permainan.model import Kartu, Permainan, LEBAR_KARTU, TINGGI_KARTU


def buat_game(jenis):
    game = Permainan(acak=random.Random(42))
    game.kartu = [Kartu(i, nilai, i, 0) for i, nilai in enumerate(jenis)]
    return game


class UjiPermainan(unittest.TestCase):
    def test_slot_berkelompok_dari_kiri(self):
        game = buat_game([0, 1, 0, 2, 1])
        for kartu in game.kartu:
            game.pilih(kartu)
        self.assertEqual([k.jenis for k in game.slot], [0, 0, 1, 1, 2])

    def test_cocok_pada_slot_terakhir_dihitung_sebelum_kalah(self):
        game = buat_game([0, 1, 2, 3, 4, 0, 0])
        for kartu in game.kartu:
            game.pilih(kartu)
        self.assertEqual(game.skor, 300)
        self.assertEqual(len(game.slot), 4)
        self.assertEqual(game.status, "bermain")

    def test_tujuh_slot_penuh_kalah(self):
        game = buat_game(list(range(8)))
        for kartu in game.kartu:
            game.pilih(kartu)
        self.assertEqual(game.status, "kalah")
        self.assertEqual(len(game.slot), 7)
        self.assertEqual(game.kartu[-1].lokasi, "papan")
        self.assertFalse(game.acak_ulang())

    def test_kembalikan_kartu_terakhir_bukan_ujung_slot(self):
        game = buat_game([0, 1, 0])
        for kartu in game.kartu:
            game.pilih(kartu)
        self.assertTrue(game.kembalikan())
        self.assertEqual(game.kartu[2].lokasi, "papan")
        self.assertEqual([k.jenis for k in game.slot], [0, 1])

    def test_kartu_tertutup_tidak_bisa_dipilih(self):
        game = buat_game([0, 1])
        game.kartu[1].tumpukan = 0
        game.kartu[1].lapisan = 1
        self.assertFalse(game.pilih(game.kartu[0]))
        self.assertTrue(game.pilih(game.kartu[1]))

    def test_otomatis_memilih_jumlah_terbanyak(self):
        game = buat_game([0, 1, 1, 0, 0, 1])
        for kartu in game.kartu[:3]:
            game.pilih(kartu)
        self.assertTrue(game.cocok_otomatis())
        self.assertEqual([k.jenis for k in game.slot], [0])
        self.assertEqual(game.skor, 300)

    def test_otomatis_seri_memilih_kelompok_kiri(self):
        game = buat_game([1, 0, 1, 1, 0, 0])
        for kartu in game.kartu[:2]:
            game.pilih(kartu)
        game.cocok_otomatis()
        self.assertEqual([k.jenis for k in game.slot], [0])

    def test_otomatis_tidak_mengisi_sebagian_jika_slot_kurang(self):
        game = buat_game(list(range(6)) + [0, 0])
        for kartu in game.kartu[:6]:
            game.pilih(kartu)
        self.assertFalse(game.cocok_otomatis())
        self.assertEqual(len(game.slot), 6)

    def test_otomatis_satu_slot_sisa_memprioritaskan_kanan_dan_tidak_kalah(self):
        game = buat_game(list(range(6)) + [0, 0, 5, 5])
        for kartu in game.kartu[:6]:
            game.pilih(kartu)
        self.assertTrue(game.cocok_otomatis())
        self.assertEqual([k.jenis for k in game.slot], [0, 1, 2, 3, 4])
        self.assertEqual([k.jenis for k in game.terakhir_musnah], [5, 5, 5])
        self.assertEqual(game.status, "bermain")
        self.assertEqual(game.skor, 300)
        self.assertEqual(len(game.riwayat), 5)

    def test_otomatis_tidak_mengubah_papan_jika_pelengkap_kanan_kurang(self):
        game = buat_game(list(range(6)) + [0, 0, 5])
        for kartu in game.kartu[:6]:
            game.pilih(kartu)
        sebelum = [(k.nomor, k.lokasi) for k in game.kartu]
        self.assertFalse(game.cocok_otomatis())
        self.assertEqual(sebelum, [(k.nomor, k.lokasi) for k in game.kartu])
        self.assertEqual(game.skor, 0)

    def test_otomatis_dapat_memenangkan_kelompok_terakhir(self):
        game = buat_game([0, 0, 0])
        game.pilih(game.kartu[0])
        self.assertTrue(game.cocok_otomatis())
        self.assertEqual(game.status, "menang")
        self.assertEqual(game.slot, [])
        self.assertEqual(game.skor, 300)
        self.assertEqual(game.kombo, 0)

    def test_acakan_mempertahankan_jumlah_dan_slot(self):
        game = Permainan(8, random.Random(5))
        game.pilih(next(k for k in game.kartu if game.teratas(k)))
        sebelum = Counter(k.jenis for k in game.kartu)
        slot = [(k.nomor, k.jenis) for k in game.slot]
        for _ in range(30):
            game.acak_ulang()
            self.assertEqual(Counter(k.jenis for k in game.kartu), sebelum)
            self.assertEqual([(k.nomor, k.jenis) for k in game.slot], slot)

    def test_peringatan_diulang_setiap_penambahan_mulai_empat(self):
        game = buat_game(list(range(7)))
        for kartu in game.kartu[:3]:
            game.pilih(kartu)
        self.assertEqual(game.peringatan, 0)
        for i, kartu in enumerate(game.kartu[3:], 1):
            game.pilih(kartu)
            self.assertEqual(game.peringatan, i)

    def test_irisan_tumpukan_berbeda_memblokir_kartu_bawah(self):
        game = buat_game([0, 1])
        game.kartu[0].x, game.kartu[0].y = 100, 300
        game.kartu[1].x, game.kartu[1].y = 140, 340
        self.assertFalse(game.pilih(game.kartu[0]))
        self.assertTrue(game.pilih(game.kartu[1]))
        self.assertTrue(game.pilih(game.kartu[0]))

    def test_posisi_acak_dalam_batas_papan(self):
        game = Permainan(1000, random.Random(5))
        for kartu in game.kartu:
            self.assertGreaterEqual(kartu.x, 20)
            self.assertLessEqual(kartu.x + LEBAR_KARTU, 520)
            self.assertGreaterEqual(kartu.y, 245)
            self.assertLessEqual(kartu.y + TINGGI_KARTU + 8, 820)
        pusat = [k for k in game.kartu if k.lapisan == 0]
        self.assertEqual(len({k.x for k in pusat}), 30)
        self.assertEqual(len({k.y for k in pusat}), 30)

    def test_semua_bentuk_muncul_dan_mengikuti_siluet(self):
        bentuk = set()
        for benih in range(80):
            game = Permainan(8, random.Random(benih))
            bentuk.add(game.bentuk)
            for kartu in game.kartu:
                if kartu.lapisan:
                    continue
                x = (kartu.x - 216) / (184 * game.profil.sebaran)
                y = (kartu.y - 466) / (207 * game.profil.sebaran)
                if game.bentuk == "plus":
                    self.assertLessEqual(min(abs(x), abs(y)), 0.28)
                elif game.bentuk == "silang":
                    self.assertLessEqual(abs(abs(x) - abs(y)), 0.19)
                elif game.bentuk == "gunung":
                    self.assertLessEqual(abs(x), (y + 1) / 2 + 0.03)
        self.assertEqual(bentuk, set(Permainan.bobot_bentuk))
        self.assertLess(Permainan.bobot_bentuk["silang"], Permainan.bobot_bentuk["gunung"])

    def test_bentuk_sebelumnya_tidak_diulang(self):
        for bentuk in Permainan.bobot_bentuk:
            game = Permainan(acak=random.Random(42), bentuk_sebelumnya=bentuk)
            self.assertNotEqual(game.bentuk, bentuk)

    def test_tertutup_tepat_15_persen_bisa_dipilih(self):
        game = buat_game([0, 1])
        bawah, atas = game.kartu
        bawah.x, bawah.y = 100, 300
        atas.x, atas.y = 168, 300
        self.assertAlmostEqual(game.bagian_tertutup(bawah), 0.15)
        self.assertTrue(game.pilih(bawah))

    def test_tertutup_lebih_dari_15_persen_harus_ambil_penutup(self):
        game = buat_game([0, 1])
        bawah, atas = game.kartu
        bawah.x, bawah.y = 100, 300
        atas.x, atas.y = 167, 300
        self.assertFalse(game.pilih(bawah))
        self.assertTrue(game.pilih(atas))
        self.assertTrue(game.pilih(bawah))

    def test_total_penutup_dari_dua_sisi_melebihi_batas(self):
        game = buat_game([0, 1, 2])
        for kartu, x in zip(game.kartu, (100, 172, 28)):
            kartu.x, kartu.y = x, 300
        self.assertAlmostEqual(game.bagian_tertutup(game.kartu[0]), 0.2)
        self.assertFalse(game.pilih(game.kartu[0]))

    def test_penutup_bertumpuk_tidak_dihitung_dua_kali(self):
        game = buat_game([0, 1, 2])
        for kartu, x in zip(game.kartu, (100, 168, 168)):
            kartu.x, kartu.y = x, 300
        self.assertAlmostEqual(game.bagian_tertutup(game.kartu[0]), 0.15)
        self.assertTrue(game.pilih(game.kartu[0]))

    def test_semua_level_memiliki_solusi_awal(self):
        for level in (1, 10, 50, 100, 250, 500, 750, 1000):
            for benih in range(20):
                game = Permainan(level, random.Random(benih), jam=lambda: 0)
                self.assertGreaterEqual(len(game.kartu), 27)
                self.assertLessEqual(len(game.kartu), 90)
                self.assertEqual(set(k.jenis for k in game.kartu), set(range(game.jumlah_jenis)))
                for kartu in reversed(game.kartu):
                    self.assertTrue(game.pilih(kartu))
                self.assertEqual(game.status, "menang")
                kelompok = len(game.kartu) // 3
                self.assertEqual(game.skor, 300 * sum(min(i, 5) for i in range(1, kelompok + 1)))


if __name__ == "__main__":
    unittest.main()
