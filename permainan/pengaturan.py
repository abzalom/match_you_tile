"""Modal bertingkat untuk bahasa dan tiga pengatur volume independen."""

import pygame


class ModalPengaturan:
    def __init__(self, aplikasi):
        self.a = aplikasi
        self.lapisan = []
        self.slider = {}
        self.digeser = None
        self.tombol = []

    @property
    def aktif(self):
        return bool(self.lapisan)

    def buka(self, nama):
        self.lapisan.append(nama)
        self.tombol = []
        self.slider = {}

    def tutup(self):
        if self.digeser:
            self.a.audio.simpan()
        self.digeser = None
        if self.lapisan:
            self.lapisan.pop()
        self.tombol = []
        self.slider = {}

    def tombol_baru(self, label, kotak, aksi, ikon="pengaturan", utama=False):
        self.a.tombol_baru(label, kotak, aksi, utama=utama, ikon_aksi=ikon)

    def gambar(self):
        a = self.a
        t = a.bahasa.t
        penutup = pygame.Surface((540, 960), pygame.SRCALPHA)
        penutup.fill((8, 20, 27, 210))
        a.kanvas.blit(penutup, (0, 0))
        a.tombol = []
        self.slider = {}
        halaman = self.lapisan[-1]
        if halaman == "pengaturan":
            a.panel((30, 265, 480, 445), (31, 53, 60), 24, garis=(185, 227, 115))
            a.teks(t("pengaturan"), (270, 315), 36, tengah=True)
            self.tombol_baru(t("bahasa") + " / " + a.bahasa.pilihan[a.bahasa.kode],
                              (60, 365, 420, 66), "modal_bahasa", "bahasa")
            self.tombol_baru(t("volume"), (60, 455, 420, 66), "modal_volume", "suara_aktif")
            self.tombol_baru(t("tutup"), (60, 565, 420, 58), "modal_tutup", "menu")
            gagal = a.bahasa.gagal_simpan or a.audio.gagal_simpan
            a.teks(t("gagal_simpan" if gagal else "tersimpan"), (270, 665), 18, tengah=True)
        elif halaman == "bahasa":
            a.panel((25, 185, 490, 600), (31, 53, 60), 24, garis=(185, 227, 115))
            a.teks(t("bahasa"), (270, 235), 36, tengah=True)
            for i, (kode, nama) in enumerate(a.bahasa.pilihan.items()):
                x, y = 45 + (i % 2) * 235, 290 + (i // 2) * 86
                self.tombol_baru(nama, (x, y, 215, 65), "pilih_bahasa:" + kode,
                                  "bahasa", utama=kode == a.bahasa.kode)
            self.tombol_baru(t("kembali_pengaturan"), (60, 680, 420, 58), "modal_tutup", "menu")
        else:
            a.panel((25, 170, 490, 680), (31, 53, 60), 24, garis=(185, 227, 115))
            a.teks(t("volume"), (270, 220), 36, tengah=True)
            for i, kategori in enumerate(("game", "system", "background")):
                y = 300 + i * 120
                nilai = a.audio.volume[kategori]
                kunci = {"game": "suara_game", "system": "suara_sistem", "background": "suara_latar"}[kategori]
                a.teks(t(kunci), (55, y), 24)
                a.teks(f"{round(nilai * 100)}%", (465, y + 12), 22, tengah=True)
                rel = pygame.Rect(117, y + 53, 306, 10)
                self.slider[kategori] = rel
                a.panel(rel, (15, 30, 36), 5)
                if nilai:
                    a.panel((rel.x, rel.y, round(rel.width * nilai), rel.height), (185, 227, 115), 5)
                pusat = (round(rel.x + rel.width * nilai), rel.centery)
                pygame.draw.circle(a.kanvas, (245, 239, 211), pusat, 15)
                pygame.draw.circle(a.kanvas, (131, 167, 104), pusat, 15, width=3)
                for tanda, x, aksi in (("-", 52, "minus:"), ("+", 444, "plus:")):
                    kotak = pygame.Rect(x, y + 32, 44, 48)
                    a.panel(kotak, (245, 239, 211), 12)
                    a.teks(tanda, kotak.center, 30, (67, 59, 52), True)
                    a.tombol.append((kotak, aksi + kategori))
            self.tombol_baru(t("aktifkan" if a.audio.dibisukan else "bisu"),
                              (55, 672, 430, 54), "modal_bisu", "suara_mati" if a.audio.dibisukan else "suara_aktif")
            self.tombol_baru(t("kembali_pengaturan" if len(self.lapisan) > 1 else "tutup"),
                              (55, 746, 430, 54), "modal_tutup", "menu")
            a.teks(t("gagal_simpan" if a.audio.gagal_simpan else "tersimpan"),
                   (270, 824), 18, tengah=True)
        self.tombol = list(a.tombol)

    def aksi(self, nama):
        a = self.a
        if nama == "modal_tutup":
            self.tutup()
        elif nama == "modal_bahasa":
            self.buka("bahasa")
        elif nama == "modal_volume":
            self.buka("volume")
        elif nama.startswith("pilih_bahasa:"):
            a.bahasa.pilih(nama.split(":", 1)[1])
            pygame.display.set_caption(a.bahasa.t("judul_jendela"))
            self.tutup()
        elif nama == "modal_bisu":
            a.audio.ganti_bisu()
        elif nama.startswith(("plus:", "minus:")):
            arah, kategori = nama.split(":", 1)
            a.audio.atur_volume(kategori, round(a.audio.volume[kategori] + (0.05 if arah == "plus" else -0.05), 4))
            self.pratinjau(kategori)
        a.audio.mainkan("klik")

    def pratinjau(self, kategori):
        if kategori != "background":
            self.a.audio.mainkan("kartu" if kategori == "game" else "klik")

    def geser(self, posisi):
        rel = self.slider[self.digeser]
        self.a.audio.atur_volume(self.digeser, (posisi[0] - rel.left) / rel.width, simpan=False)

    def tangani(self, kejadian):
        # Posisi mouse selalu memakai koordinat kanvas, termasuk setelah resize.
        if kejadian.type == pygame.WINDOWFOCUSLOST and self.digeser:
            self.a.audio.simpan()
            self.digeser = None
        elif kejadian.type == pygame.KEYDOWN and kejadian.key == pygame.K_ESCAPE:
            self.tutup()
        elif kejadian.type == pygame.MOUSEMOTION and self.digeser:
            self.geser(self.a.posisi_mouse(kejadian.pos))
        elif kejadian.type == pygame.MOUSEBUTTONUP and kejadian.button == 1 and self.digeser:
            self.geser(self.a.posisi_mouse(kejadian.pos))
            self.a.audio.simpan()
            self.pratinjau(self.digeser)
            self.digeser = None
        elif kejadian.type == pygame.MOUSEBUTTONDOWN and kejadian.button == 1:
            posisi = self.a.posisi_mouse(kejadian.pos)
            for kategori, rel in self.slider.items():
                if rel.inflate(30, 36).collidepoint(posisi):
                    self.digeser = kategori
                    self.geser(posisi)
                    return
            for kotak, nama in self.tombol:
                if kotak.collidepoint(posisi):
                    self.aksi(nama)
                    return
