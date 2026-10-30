"""Integrasi tampilan memakai driver dummy; tidak membuka jendela pengguna."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame

from permainan.antarmuka import Aplikasi, LEBAR, TINGGI


class UjiAntarmuka(unittest.TestCase):
    def setUp(self):
        self.direktori = tempfile.TemporaryDirectory()
        self.app = Aplikasi(Path(self.direktori.name) / "progres.json")
        self.app.gambar()

    def tearDown(self):
        pygame.quit()
        self.direktori.cleanup()

    def selesaikan_animasi(self):
        if self.app.animasi:
            self.app.perbarui(max(g.mulai + g.durasi for g in self.app.animasi.values()))
        self.app.gambar()

    def mulai(self):
        self.app.mulai()
        self.app.perbarui(self.app.intro["mulai"] + self.app.intro["durasi"])
        self.app.gambar()

    def test_potret_slot_kiri_dan_level_terkunci(self):
        self.assertLess(LEBAR, TINGGI)
        self.assertFalse(self.app.mulai(2))
        self.assertEqual(self.app.level, 1)
        self.assertLess(self.app.kotak_slot(0).x, self.app.kotak_slot(1).x)
        self.mulai()
        self.assertIn("menu", [aksi for _, aksi in self.app.tombol])

    def test_tombol_suara_menyimpan_pilihan_tanpa_mengubah_level(self):
        self.assertIn("suara", [nama for _, nama in self.app.tombol])
        awal = self.app.audio.dibisukan
        self.app.aksi("suara")
        self.assertEqual(self.app.modal.lapisan, ["volume"])
        self.app.aksi("modal_bisu")
        self.assertNotEqual(self.app.audio.dibisukan, awal)
        self.assertTrue(self.app.audio.pengaturan.exists())
        self.assertEqual(self.app.progres.level_terbuka, 1)

    def test_pemusnahan_dan_peringatan_slot_tanpa_suara(self):
        self.mulai()
        self.app.audio.jadwal.clear()
        with patch.object(self.app.audio, "mainkan") as bunyi:
            with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=10000):
                for kartu in list(reversed(self.app.permainan.kartu))[:3]:
                    self.app.jalankan_gerakan("pilih", kartu)
            self.app.perbarui(10433)
            self.assertNotIn("cocok", [p.args[0] for p in bunyi.call_args_list])
            self.app.perbarui(10434)
            self.app.perbarui(10435)
            for jenis, kartu in enumerate(list(reversed(self.app.permainan.kartu))[3:7]):
                kartu.jenis = jenis
                self.app.jalankan_gerakan("pilih", kartu)
            self.assertGreater(self.app.permainan.peringatan, 0)
            self.app.perbarui(99999)
            nama = [p.args[0] for p in bunyi.call_args_list]
            self.assertNotIn("cocok", nama)
            self.assertNotIn("peringatan", nama)

    def test_pilih_kembali_acak_dan_animasi_otomatis(self):
        self.mulai()
        kartu = self.app.permainan.kartu[-1]
        self.app.jalankan_gerakan("pilih", kartu)
        self.assertTrue(self.app.animasi)
        self.app.gambar()
        self.selesaikan_animasi()
        self.app.aksi("kembali")
        self.assertEqual(kartu.lokasi, "papan")
        kembali = self.app.animasi[kartu.nomor]
        self.assertEqual(kembali.awal, self.app.kotak_slot(0))
        self.assertEqual(kembali.akhir.topleft, (round(kartu.x), round(kartu.y)))
        tengah = kembali.potret(kembali.mulai + kembali.durasi // 2)[0]
        self.assertNotEqual(tengah, kembali.awal)
        self.assertNotEqual(tengah, kembali.akhir)
        self.selesaikan_animasi()
        self.app.aksi("acak")
        self.assertTrue(self.app.animasi)
        self.app.gambar()
        self.selesaikan_animasi()
        self.app.jalankan_gerakan("pilih", kartu)
        self.selesaikan_animasi()
        self.app.aksi("cocok")
        self.assertTrue(self.app.animasi)
        self.assertEqual(sum(g.musnah for g in self.app.animasi.values()), 3)
        self.assertEqual(sum(g.musnah and g.awal != g.akhir
                             for g in self.app.animasi.values()), 2)
        self.app.gambar()
        self.selesaikan_animasi()
        self.assertEqual(self.app.permainan.skor, 300)
        self.assertEqual(len(self.app.permainan.slot), 0)

    def test_bantuan_darurat_satu_slot_tetap_beranimasi_dan_tidak_kalah(self):
        self.mulai()
        game = self.app.permainan
        for jenis, kartu in enumerate(list(reversed(game.kartu))[:6]):
            kartu.jenis = jenis
            self.app.jalankan_gerakan("pilih", kartu)
        self.selesaikan_animasi()
        game.kartu[0].jenis = game.kartu[1].jenis = 5
        self.app.aksi("cocok")
        self.assertEqual(game.status, "bermain")
        self.assertEqual(len(game.slot), 5)
        self.assertEqual([k.jenis for k in game.terakhir_musnah], [5, 5, 5])
        self.assertTrue(self.app.animasi)
        for gerakan in self.app.animasi.values():
            self.assertLessEqual(gerakan.akhir.right, self.app.kotak_slot(6).right)
        self.app.gambar()
        self.selesaikan_animasi()
        self.assertEqual(game.skor, 300)

    def test_klik_setelah_resize_dan_bantuan_menunggu_animasi(self):
        self.mulai()
        self.app.layar = pygame.display.set_mode((360, 640))
        self.app.gambar()
        kartu = self.app.permainan.kartu[-1]
        kotak = next(r for r, k in self.app.area_kartu if k is kartu)
        posisi = (round(kotak.centerx * 2 / 3), round(kotak.centery * 2 / 3))
        self.app.tangani(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=posisi))
        self.assertEqual(kartu.lokasi, "slot")
        self.app.tangani(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(kartu.lokasi, "slot")
        self.selesaikan_animasi()
        self.app.tangani(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(kartu.lokasi, "papan")

    def test_menang_membuka_level_dan_menu_bertransisi(self):
        self.mulai()
        for kartu in reversed(self.app.permainan.kartu):
            self.app.jalankan_gerakan("pilih", kartu)
            self.selesaikan_animasi()
        self.assertEqual(self.app.permainan.status, "menang")
        self.assertEqual(self.app.progres.level_terbuka, 2)
        self.app.aksi("menu")
        self.assertIsNotNone(self.app.transisi)
        self.assertEqual(self.app.halaman, "menu")

    def test_klik_cepat_memproses_semua_kartu_sebelum_animasi_selesai(self):
        self.mulai()
        game = self.app.permainan
        # Klik seluruh papan pada satu frame tanpa gambar/perbarui di antaranya.
        for kartu in reversed(game.kartu):
            posisi = (round(kartu.x + 33), round(kartu.y + 37))
            self.app.tangani(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=posisi))
            self.assertNotEqual(kartu.lokasi, "papan")
        self.assertEqual(game.status, "menang")
        kelompok = len(game.kartu) // 3
        self.assertEqual(game.skor, 300 * sum(min(i, 5) for i in range(1, kelompok + 1)))
        self.assertTrue(self.app.animasi)
        self.app.gambar()
        self.selesaikan_animasi()
        self.assertEqual(self.app.animasi, {})

    def test_klik_ulang_kartu_terbang_tidak_memilih_dua_kali(self):
        self.mulai()
        kartu = self.app.permainan.kartu[-1]
        self.app.jalankan_gerakan("pilih", kartu)
        self.app.jalankan_gerakan("pilih", kartu)
        self.assertEqual(self.app.permainan.slot.count(kartu), 1)

    def test_sisipan_kelompok_mengalihkan_gerakan_dari_posisi_sekarang(self):
        self.mulai()
        pertama, kedua, ketiga = list(reversed(self.app.permainan.kartu))[:3]
        pertama.jenis, kedua.jenis, ketiga.jenis = 0, 1, 0
        with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=100):
            self.app.jalankan_gerakan("pilih", pertama)
        with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=200):
            self.app.jalankan_gerakan("pilih", kedua)
        posisi = self.app.potret_visual(300)[kedua.nomor][0]
        with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=300):
            self.app.jalankan_gerakan("pilih", ketiga)
        self.assertEqual(self.app.animasi[kedua.nomor].awal, posisi)
        self.assertEqual(self.app.animasi[kedua.nomor].akhir, self.app.kotak_slot(2))

    def test_frame_melewati_akhir_animasi_pemusnahan_tetap_bisa_digambar(self):
        self.mulai()
        for kartu in list(reversed(self.app.permainan.kartu))[:3]:
            self.app.jalankan_gerakan("pilih", kartu)
        batas = max(g.mulai + g.durasi for g in self.app.animasi.values())
        with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=batas + 1):
            self.app.gambar_game()

    def test_level_lama_diblokir_dan_mulai_selalu_level_aktif(self):
        self.app.progres.selesaikan(1)
        self.assertFalse(self.app.mulai(1))
        self.assertFalse(self.app.mulai(3))
        self.assertTrue(self.app.mulai())
        self.assertEqual(self.app.permainan.level, 2)
        self.app.perbarui(self.app.intro["mulai"] + self.app.intro["durasi"])
        self.app.aksi("menu")
        self.assertTrue(self.app.konfirmasi_menu)
        self.app.aksi("konfirmasi_keluar")
        self.app.perbarui(self.app.transisi[1] + self.app.transisi[2])
        self.app.gambar()
        self.assertEqual([aksi for _, aksi in self.app.tombol], ["mulai", "pengaturan", "suara"])
        self.app.aksi("kurang")
        self.assertEqual(self.app.level, 2)
        # Progres lama tetap berlaku setelah aplikasi dibuka kembali.
        berkas = self.app.progres.berkas
        self.app = Aplikasi(berkas)
        self.assertEqual(self.app.level, 2)
        self.assertFalse(self.app.mulai(1))

    def test_menu_setelah_menang_langsung_memulai_level_berikutnya(self):
        self.mulai()
        for kartu in reversed(self.app.permainan.kartu):
            self.app.jalankan_gerakan("pilih", kartu)
        self.app.aksi("menu")
        self.app.perbarui(self.app.transisi[1] + self.app.transisi[2])
        self.app.gambar()
        self.assertEqual(self.app.level, 2)
        self.app.aksi("mulai")
        self.assertEqual(self.app.permainan.level, 2)

    def test_kalah_bisa_mengulang_level_aktif(self):
        self.mulai()
        self.app.permainan.status = "kalah"
        self.app.gambar()
        self.app.aksi("ulang")
        self.assertEqual(self.app.permainan.level, 1)
        self.assertEqual(self.app.permainan.status, "bermain")

    def test_level_1000_dapat_dirender_dan_tidak_melanjutkan_ke_1001(self):
        self.app.progres.level_terbuka = 1000
        self.assertTrue(self.app.mulai(1000))
        self.app.perbarui(self.app.intro["mulai"] + self.app.intro["durasi"])
        self.app.permainan.status = "menang"
        self.app.gambar()
        self.assertEqual([nama for _, nama in self.app.tombol], ["ulang", "menu"])
        self.assertFalse(self.app.mulai(1001))
        self.assertEqual(self.app.permainan.level, 1000)

    def test_intro_memblokir_klik_dan_hilang_sebelum_mulai(self):
        self.app.mulai()
        self.app.perbarui(self.app.transisi[1] + self.app.transisi[2])
        self.assertIsNotNone(self.app.intro)
        kartu = self.app.permainan.kartu[-1]
        self.app.tangani(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                        pos=(round(kartu.x + 40), round(kartu.y + 45))))
        self.assertEqual(kartu.lokasi, "papan")
        with patch("permainan.antarmuka.pygame.time.get_ticks",
                   return_value=self.app.intro["mulai"] + 600):
            self.app.gambar()
        self.assertFalse(self.app.tombol)
        self.app.perbarui(self.app.intro["mulai"] + self.app.intro["durasi"])
        self.assertIsNone(self.app.intro)

    def test_konfirmasi_keluar_batal_tetap_bermain_dan_ya_dihitung_kalah(self):
        self.mulai()
        self.app.aksi("menu")
        self.app.gambar()
        self.assertTrue(self.app.konfirmasi_menu)
        self.assertEqual(self.app.halaman, "game")
        kartu = self.app.permainan.kartu[-1]
        # Posisi di belakang overlay tetapi di luar tombol dialog, agar variasi
        # papan tidak membuat tes tanpa sengaja menekan tombol Ya, keluar.
        kartu.x, kartu.y = 210, 245
        self.app.tangani(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                        pos=(round(kartu.x + 40), round(kartu.y + 45))))
        self.assertEqual(kartu.lokasi, "papan")
        self.app.tangani(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertFalse(self.app.konfirmasi_menu)
        self.assertEqual(self.app.permainan.status, "bermain")
        self.app.aksi("menu")
        self.app.aksi("konfirmasi_keluar")
        self.assertEqual(self.app.permainan.status, "kalah")
        self.assertEqual(self.app.halaman, "menu")
        self.assertEqual(self.app.progres.level_terbuka, 1)

    def test_slot_baru_merapat_setelah_kelompok_selesai_musnah(self):
        self.mulai()
        kartu = list(reversed(self.app.permainan.kartu))[:6]
        for isi, jenis in zip(kartu, (0, 0, 1, 2, 0, 1)):
            isi.jenis = jenis
        for i, isi in enumerate(kartu[:4]):
            with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=1000 + i * 500):
                self.app.jalankan_gerakan("pilih", isi)
        with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=3000):
            self.app.jalankan_gerakan("pilih", kartu[4])
        bergeser = self.app.animasi[kartu[2].nomor]
        self.assertEqual(bergeser.mulai, 3620)
        self.assertEqual(bergeser.potret(3619)[0], self.app.kotak_slot(3))
        self.assertEqual(bergeser.potret(3620)[0], self.app.kotak_slot(3))
        self.assertEqual(bergeser.potret(4040)[0], self.app.kotak_slot(0))
        for isi in (kartu[0], kartu[1], kartu[4]):
            self.assertTrue(self.app.animasi[isi.nomor].selesai(3620))
        # Klik baru tetap diterima tanpa memajukan perapatan yang sudah dijadwalkan.
        with patch("permainan.antarmuka.pygame.time.get_ticks", return_value=3300):
            self.app.jalankan_gerakan("pilih", kartu[5])
        self.assertEqual(kartu[5].lokasi, "slot")
        self.assertEqual(self.app.animasi[kartu[2].nomor].potret(3619)[0],
                         self.app.kotak_slot(3))
        self.assertGreaterEqual(self.app.animasi[kartu[5].nomor].mulai, 4040)
