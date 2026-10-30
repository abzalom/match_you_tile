import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame

from permainan.antarmuka import Aplikasi
from permainan.audio import AudioPermainan


class UjiPengaturan(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.a = Aplikasi(Path(self.folder.name) / "progres.json")
        self.a.gambar()

    def tearDown(self):
        pygame.quit()
        self.folder.cleanup()

    def test_menu_tanpa_kartu_dan_modal_menahan_input_di_belakangnya(self):
        with patch.object(self.a, "kartu_baru") as kartu:
            self.a.gambar_menu()
            kartu.assert_not_called()
        self.a.aksi("pengaturan")
        self.a.gambar()
        self.a.tangani(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(270, 780)))
        self.assertEqual(self.a.halaman, "menu")
        self.assertTrue(self.a.modal.aktif)

    def test_bahasa_dan_volume_modal_bertingkat_dan_render_semua_bahasa(self):
        self.a.aksi("pengaturan")
        self.a.aksi("modal_bahasa")
        self.assertEqual(self.a.modal.lapisan, ["pengaturan", "bahasa"])
        self.a.gambar()
        for kode in self.a.bahasa.pilihan:
            self.a.bahasa.pilih(kode)
            self.a.gambar()
        self.a.aksi("pilih_bahasa:en")
        self.assertEqual(self.a.modal.lapisan, ["pengaturan"])
        self.a.aksi("modal_volume")
        self.a.gambar()
        self.a.tangani(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(self.a.modal.lapisan, ["pengaturan"])

    def test_slider_resize_drag_plus_minus_tersimpan_dan_independen(self):
        self.a.layar = pygame.display.set_mode((360, 640))
        self.a.aksi("suara")
        self.a.gambar()
        lain = (self.a.audio.volume["system"], self.a.audio.volume["background"])
        rel = self.a.modal.slider["game"]
        posisi = (round((rel.left + rel.width * 0.5) * 2 / 3), round(rel.centery * 2 / 3))
        self.a.tangani(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=posisi))
        self.a.tangani(pygame.event.Event(pygame.MOUSEMOTION, pos=(500, posisi[1])))
        self.a.tangani(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(500, posisi[1])))
        self.assertEqual(self.a.audio.volume["game"], 1)
        self.a.aksi("plus:game")
        self.assertEqual(self.a.audio.volume["game"], 1)
        self.a.aksi("minus:game")
        self.assertAlmostEqual(self.a.audio.volume["game"], 0.95)
        self.assertEqual(lain, (self.a.audio.volume["system"], self.a.audio.volume["background"]))
        baru = AudioPermainan(self.a.audio.folder, self.a.audio.pengaturan)
        self.assertAlmostEqual(baru.volume["game"], 0.95)
        self.assertAlmostEqual(baru.efek["kartu"].get_volume(), 0.95, delta=0.01)
        self.assertAlmostEqual(baru.efek["klik"].get_volume(), lain[0], delta=0.01)

    def test_volume_nol_dan_bisu_tidak_menghapus_pengaturan(self):
        self.a.audio.atur_volume("background", 0)
        self.assertEqual(pygame.mixer.music.get_volume(), 0)
        self.a.audio.atur_volume("system", 0.3)
        self.a.audio.ganti_bisu()
        self.a.audio.ganti_bisu()
        self.assertEqual(self.a.audio.volume["background"], 0)
        self.assertAlmostEqual(self.a.audio.efek["klik"].get_volume(), 0.3, delta=0.01)

    def test_pengaturan_bisa_dibuka_dalam_game_tanpa_mengulang_papan(self):
        self.a.mulai()
        self.a.perbarui(self.a.intro["mulai"] + self.a.intro["durasi"])
        self.a.gambar()
        self.assertIn("pengaturan", [nama for _, nama in self.a.tombol])
        permainan = self.a.permainan
        self.a.aksi("pengaturan")
        self.a.gambar()
        self.assertEqual(self.a.modal.lapisan, ["pengaturan"])
        self.a.aksi("modal_bahasa")
        self.a.aksi("pilih_bahasa:en")
        self.a.aksi("modal_tutup")
        self.assertFalse(self.a.modal.aktif)
        self.assertEqual(self.a.halaman, "game")
        self.assertIs(self.a.permainan, permainan)
        self.assertEqual(self.a.permainan.status, "bermain")
