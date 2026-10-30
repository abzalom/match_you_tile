"""Musik, efek, jadwal bunyi, dan pengaturan bisu yang tersimpan lokal."""

import json
from pathlib import Path
import pygame


class AudioPermainan:
    berkas_musik = {
        "menu": "ai generated musik/Paths_Through_Silver_Leaves.wav",
        "game": "ai generated musik/Paths_Through_Silver_Leaves.wav",
    }
    daftar_efek = ("klik", "kartu", "cocok", "kembali", "acak", "peringatan",
                   "menang", "kalah", "intro", "batal")

    def __init__(self, folder, pengaturan):
        self.folder = Path(folder)
        self.pengaturan = Path(pengaturan)
        self.dibisukan = False
        self.volume = {"game": 0.55, "system": 0.55, "background": 0.28}
        self.gagal_simpan = False
        self.tersedia = False
        self.musik = None
        self.efek = {}
        self.jadwal = []
        try:
            isi = json.loads(self.pengaturan.read_text(encoding="utf-8"))
            self.dibisukan = isi.get("bisu") is True
            nilai = isi.get("volume", {})
            if isinstance(nilai, dict):
                for kategori in self.volume:
                    angka = nilai.get(kategori)
                    if type(angka) in (int, float) and 0 <= angka <= 1:
                        self.volume[kategori] = float(angka)
        except (OSError, ValueError, AttributeError):
            pass
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1, 512)
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(2)  # Hasil dan peringatan mendapat kanal khusus.
            self.efek = {nama: pygame.mixer.Sound(str(self.folder / f"{nama}.wav"))
                         for nama in self.daftar_efek}
            self.tersedia = True
            self.terapkan_volume()
        except (pygame.error, OSError):
            # Perangkat tanpa audio tetap dapat menjalankan seluruh permainan.
            self.tersedia = False

    def putar_musik(self, nama):
        if not self.tersedia or self.musik == nama:
            return
        if nama and self.musik and self.berkas_musik[nama] == self.berkas_musik[self.musik]:
            self.musik = nama
            return  # Lagu yang sama terus berjalan, tanpa dimulai ulang saat pindah halaman.
        pygame.mixer.music.stop()
        self.musik = nama
        if nama:
            pygame.mixer.music.load(str(self.folder / self.berkas_musik[nama]))
            pygame.mixer.music.set_volume(0 if self.dibisukan else self.volume["background"])
            pygame.mixer.music.play(-1, fade_ms=350)

    def mainkan(self, nama):
        if not self.tersedia or self.dibisukan or nama in ("cocok", "peringatan"):
            return
        if nama in ("menang", "kalah"):
            pygame.mixer.Channel(0).play(self.efek[nama])
        elif nama == "peringatan":
            pygame.mixer.Channel(1).play(self.efek[nama])
        else:
            self.efek[nama].play()

    def jadwalkan(self, nama, waktu):
        self.jadwal.append((waktu, nama))

    def perbarui(self, waktu):
        siap = sorted(isi for isi in self.jadwal if isi[0] <= waktu)
        self.jadwal = [isi for isi in self.jadwal if isi[0] > waktu]
        for _, nama in siap:
            self.mainkan(nama)

    def bersihkan(self):
        self.jadwal.clear()
        if self.tersedia:
            pygame.mixer.stop()

    def ganti_bisu(self):
        self.dibisukan = not self.dibisukan
        self.terapkan_volume()
        self.simpan()

    @staticmethod
    def kategori_efek(nama):
        return "game" if nama in ("kartu", "cocok", "kembali", "acak", "peringatan") else "system"

    def terapkan_volume(self):
        if self.tersedia:
            pygame.mixer.music.set_volume(0 if self.dibisukan else self.volume["background"])
            for nama, suara in self.efek.items():
                suara.set_volume(0 if self.dibisukan else self.volume[self.kategori_efek(nama)])
            if self.dibisukan:
                pygame.mixer.stop()

    def atur_volume(self, kategori, nilai, simpan=True):
        if kategori not in self.volume:
            return
        self.volume[kategori] = max(0.0, min(1.0, nilai))
        self.terapkan_volume()
        if simpan:
            self.simpan()

    def simpan(self):
        try:
            self.pengaturan.parent.mkdir(parents=True, exist_ok=True)
            self.pengaturan.write_text(json.dumps({"bisu": self.dibisukan, "volume": self.volume}),
                                        encoding="utf-8")
            self.gagal_simpan = False
        except OSError:
            self.gagal_simpan = True
