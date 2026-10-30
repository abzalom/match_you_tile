"""Validasi WAV, bisu, jadwal, dan perangkat audio yang tidak tersedia."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from array import array
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave
import pygame

from permainan.audio import AudioPermainan

FOLDER = Path(__file__).resolve().parent.parent / "assets" / "audio"


class UjiAudio(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.direktori = tempfile.TemporaryDirectory()
        self.pengaturan = Path(self.direktori.name) / "audio.json"

    def tearDown(self):
        pygame.quit()
        self.direktori.cleanup()

    def test_semua_wav_valid_berisi_suara_dan_tidak_clipping(self):
        berkas = list(FOLDER.glob("*.wav"))
        self.assertEqual(len(berkas), 12)
        for nama in berkas:
            with wave.open(str(nama), "rb") as suara:
                self.assertEqual(suara.getnchannels(), 1)
                self.assertEqual(suara.getsampwidth(), 2)
                self.assertEqual(suara.getframerate(), 22050)
                if nama.stem.startswith("musik_"):
                    self.assertGreater(suara.getnframes() / 22050, 15)
                data = array("h", suara.readframes(suara.getnframes()))
                self.assertGreater(max(abs(x) for x in data), 100)
                self.assertLess(max(abs(x) for x in data), 32767)

    def test_bisu_tersimpan_dan_musik_bisa_dilanjutkan(self):
        audio = AudioPermainan(FOLDER, self.pengaturan)
        self.assertTrue(audio.tersedia)
        audio.putar_musik("menu")
        self.assertEqual(audio.musik, "menu")
        audio.ganti_bisu()
        self.assertTrue(audio.dibisukan)
        self.assertEqual(pygame.mixer.music.get_volume(), 0)
        audio.mainkan("kartu")
        self.assertFalse(pygame.mixer.get_busy())
        baru = AudioPermainan(FOLDER, self.pengaturan)
        self.assertTrue(baru.dibisukan)
        baru.ganti_bisu()
        self.assertGreater(pygame.mixer.music.get_volume(), 0)

    def test_jadwal_berurutan_dan_dapat_dibatalkan(self):
        audio = AudioPermainan(FOLDER, self.pengaturan)
        with patch.object(audio, "mainkan") as bunyi:
            audio.jadwalkan("menang", 1000)
            audio.jadwalkan("cocok", 434)
            audio.perbarui(433)
            bunyi.assert_not_called()
            audio.perbarui(1000)
            self.assertEqual([isi.args[0] for isi in bunyi.call_args_list], ["cocok", "menang"])
            audio.jadwalkan("peringatan", 1100)
            audio.bersihkan()
            self.assertEqual(audio.jadwal, [])

    def test_tanpa_perangkat_audio_game_tetap_berjalan(self):
        with patch("pygame.mixer.get_init", return_value=None), patch(
                "pygame.mixer.init", side_effect=pygame.error("Tidak ada perangkat")):
            audio = AudioPermainan(FOLDER, self.pengaturan)
        self.assertFalse(audio.tersedia)
        audio.putar_musik("game")
        audio.mainkan("klik")
        audio.jadwalkan("cocok", 100)
        audio.perbarui(100)
        audio.ganti_bisu()
        audio.bersihkan()

    def test_lagu_sama_tidak_diulang_saat_masuk_game(self):
        audio = AudioPermainan(FOLDER, self.pengaturan)
        audio.putar_musik("menu")
        with patch("pygame.mixer.music.load") as muat, patch("pygame.mixer.music.stop") as berhenti:
            audio.putar_musik("game")
            audio.putar_musik("menu")
            muat.assert_not_called()
            berhenti.assert_not_called()
        audio.mainkan("cocok")
        audio.mainkan("peringatan")
        self.assertFalse(pygame.mixer.get_busy())
