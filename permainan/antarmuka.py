"""Tampilan potret, animasi kartu, dan kendali Match You Tile."""

from pathlib import Path
import pygame

from .model import Permainan, LEBAR_KARTU, TINGGI_KARTU
from .animasi import GerakanKartu
from .progres import Progres
from .aset import muat_aset, AsetTombol
from .latar import LatarPermainan
from .level import profil_level
from .audio import AudioPermainan
from .bahasa import Bahasa
from .pengaturan import ModalPengaturan
from .lokasi import AKAR, folder_data

LEBAR, TINGGI = 540, 960
LATAR = (16, 31, 39)
PUTIH = (240, 245, 232)
HIJAU = (185, 227, 115)
REDUP = (156, 179, 181)


class Aplikasi:
    def __init__(self, berkas_progres=None):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        logo = pygame.image.load(str(AKAR / "assets" / "logo.png"))
        skala_ikon = min(128 / logo.get_width(), 128 / logo.get_height())
        ukuran_ikon = (round(logo.get_width() * skala_ikon), round(logo.get_height() * skala_ikon))
        self.ikon_aplikasi = pygame.Surface((128, 128), pygame.SRCALPHA)
        kecil = pygame.transform.smoothscale(logo, ukuran_ikon)
        self.ikon_aplikasi.blit(kecil, kecil.get_rect(center=(64, 64)))
        pygame.display.set_icon(self.ikon_aplikasi)
        self.layar = pygame.display.set_mode((LEBAR, TINGGI), pygame.RESIZABLE)
        pygame.display.set_caption("Match You Tile - Dapur Warna")
        self.kanvas = pygame.Surface((LEBAR, TINGGI))
        judul = pygame.image.load(str(AKAR / "assets" / "Title.png")).convert_alpha()
        lebar_judul = LEBAR - 60
        tinggi_judul = round(judul.get_height() * lebar_judul / judul.get_width())
        self.gambar_judul = pygame.transform.smoothscale(judul, (lebar_judul, tinggi_judul))
        self.jam = pygame.time.Clock()
        self.huruf = {ukuran: pygame.font.Font(None, ukuran)
                      for ukuran in (16, 18, 20, 22, 24, 26, 30, 36, 48, 60)}
        kandidat_font = (Path("C:/Windows/Fonts/msyh.ttc"),
                         Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"))
        self.font_cjk = next((str(p) for p in kandidat_font if p.exists()), None)
        self.huruf_cjk = {}
        self.katalog_aset, self.gambar_aset = muat_aset(AKAR / "assets" / "svg")
        self.aset_tombol = AsetTombol(AKAR / "assets" / "svg" / "tombol")
        self.latar = LatarPermainan(AKAR / "assets", (LEBAR, TINGGI))
        self.progres = Progres(berkas_progres or folder_data() / "progres.json")
        self.bahasa = Bahasa(AKAR / "assets" / "bahasa.json",
                             self.progres.berkas.with_name("pengaturan.json"))
        pygame.display.set_caption(self.bahasa.t("judul_jendela"))
        self.audio = AudioPermainan(AKAR / "assets" / "audio",
                                    self.progres.berkas.with_name("audio.json"))
        self.audio.putar_musik("menu")
        self.hasil_dibunyikan = False
        self.level = self.progres.level_terbuka
        self.permainan = Permainan(self.level)
        self.halaman = "menu"
        self.tombol = []
        self.area_kartu = []
        self.kilat_sampai = 0
        self.efek_sampai = 0
        self.poin_efek = 0
        self.kombo_efek = 0
        self.animasi = {}
        self.slot_siap = 0
        self.transisi = None
        self.intro = None
        self.konfirmasi_menu = False
        self.aktif = True
        self.modal = ModalPengaturan(self)

    def font_untuk(self, tulisan, ukuran):
        if any(ord(huruf) >= 0x2e80 for huruf in tulisan):
            if ukuran not in self.huruf_cjk:
                self.huruf_cjk[ukuran] = pygame.font.Font(self.font_cjk, ukuran)
            return self.huruf_cjk[ukuran]
        if ukuran not in self.huruf:
            self.huruf[ukuran] = pygame.font.Font(None, ukuran)
        return self.huruf[ukuran]

    def teks(self, tulisan, posisi, ukuran=24, warna=PUTIH, tengah=False):
        tulisan = self.bahasa.terjemahkan(tulisan)
        batas = 500 if tengah else max(50, LEBAR - posisi[0] - 20)
        while ukuran > 16 and self.font_untuk(tulisan, ukuran).size(tulisan)[0] > batas:
            ukuran -= 2
        font = self.font_untuk(tulisan, ukuran)
        # Pesan panjang di beberapa bahasa dibagi baris agar tidak keluar layar.
        baris = [tulisan]
        if font.size(tulisan)[0] > batas:
            baris, bagian = [], ""
            for karakter in tulisan:
                if bagian and font.size(bagian + karakter)[0] > batas:
                    baris.append(bagian)
                    bagian = ""
                bagian += karakter
            baris.append(bagian)
        for i, isi in enumerate(baris):
            gambar = font.render(isi, True, warna)
            titik = (posisi[0], posisi[1] + i * font.get_linesize())
            kotak = gambar.get_rect(center=titik) if tengah else gambar.get_rect(topleft=titik)
            self.kanvas.blit(gambar, kotak)

    def panel(self, kotak, warna=(28, 47, 55), radius=14, garis=None):
        pygame.draw.rect(self.kanvas, warna, kotak, border_radius=radius)
        if garis:
            pygame.draw.rect(self.kanvas, garis, kotak, width=2, border_radius=radius)

    def tombol_baru(self, tulisan, kotak, aksi, utama=False, tersedia=True, ikon_aksi=None):
        tulisan = self.bahasa.terjemahkan(tulisan)
        kotak = pygame.Rect(kotak)
        sorot = tersedia and kotak.collidepoint(self.posisi_mouse())
        latar, ikon = self.aset_tombol.gambar(ikon_aksi or aksi, kotak.size, utama, sorot, tersedia)
        tampilan = kotak.move(0, -2 if sorot else 0)
        self.kanvas.blit(latar, tampilan)
        warna = (67, 59, 52) if tersedia else (150, 167, 163)
        ukuran = 22
        while ukuran > 16 and self.font_untuk(tulisan, ukuran).size(tulisan)[0] + ikon.get_width() + 24 > kotak.width:
            ukuran -= 2
        label = self.font_untuk(tulisan, ukuran).render(tulisan, True, warna)
        lebar_isi = ikon.get_width() + (7 + label.get_width() if tulisan else 0)
        awal = tampilan.centerx - lebar_isi // 2
        tengah_y = tampilan.centery - 3
        self.kanvas.blit(ikon, ikon.get_rect(midleft=(awal, tengah_y)))
        self.kanvas.blit(label, label.get_rect(midleft=(awal + ikon.get_width() + 7, tengah_y)))
        if tersedia:
            self.tombol.append((kotak, aksi))

    def posisi_mouse(self, posisi=None):
        x, y = pygame.mouse.get_pos() if posisi is None else posisi
        lebar, tinggi = self.layar.get_size()
        skala = min(lebar / LEBAR, tinggi / TINGGI)
        return ((x - (lebar - LEBAR * skala) / 2) / skala,
                (y - (tinggi - TINGGI * skala) / 2) / skala)

    def pindah_halaman(self, halaman):
        if halaman == self.halaman:
            return
        self.transisi = (self.kanvas.copy(), pygame.time.get_ticks(), 360,
                         1 if halaman == "game" else -1)
        self.halaman = halaman

    def mulai(self, level=None):
        tujuan = self.progres.level_terbuka if level is None else level
        # Progres hanya maju: level yang telah diselesaikan tidak dapat dibuka lagi.
        if tujuan != self.progres.level_terbuka:
            return False
        self.level = tujuan
        self.permainan = Permainan(self.level, bentuk_sebelumnya=self.permainan.bentuk)
        self.kilat_sampai = self.efek_sampai = 0
        self.latar.pilih_level()
        self.animasi.clear()
        self.slot_siap = 0
        self.konfirmasi_menu = False
        self.pindah_halaman("game")
        self.audio.bersihkan()
        self.audio.putar_musik("game")
        self.hasil_dibunyikan = False
        self.intro = {"mulai": pygame.time.get_ticks() + (360 if self.transisi else 0),
                      "durasi": 1400}
        self.audio.jadwalkan("intro", self.intro["mulai"])
        return True

    def gambar_kartu(self, jenis):
        return self.gambar_aset[((self.level - 1) * 3 + jenis) % len(self.gambar_aset)]

    def kartu_baru(self, kotak, jenis, tertutup=False):
        self.panel(kotak.move(1, 8), (7, 18, 24), 9)
        self.panel(kotak.move(0, 5), (116, 128, 113), 9)
        self.panel(kotak.move(0, 2), (207, 211, 188), 9)
        self.panel(kotak, (183, 191, 174) if tertutup else (245, 242, 219), 9)
        pygame.draw.line(self.kanvas, (255, 253, 238),
                         (kotak.left + 9, kotak.top + 2), (kotak.right - 9, kotak.top + 2))
        ukuran = min(kotak.width - 8, kotak.height - 8, 60)
        gambar = pygame.transform.smoothscale(self.gambar_kartu(jenis), (ukuran, ukuran))
        self.kanvas.blit(gambar, gambar.get_rect(center=kotak.center))
        if tertutup:
            # Ikon kecil pada sudut yang tersingkap memperlihatkan buah berikutnya.
            kecil = pygame.transform.smoothscale(self.gambar_kartu(jenis), (20, 20))
            self.kanvas.blit(kecil, (kotak.x + 1, kotak.y + 1))

    @staticmethod
    def kotak_slot(indeks):
        return pygame.Rect(20 + indeks * 72, 139, 68, 86)

    def potret_kartu(self):
        hasil = {}
        for kartu in self.permainan.kartu:
            if kartu.lokasi == "papan":
                hasil[kartu.nomor] = (pygame.Rect(round(kartu.x), round(kartu.y),
                                                LEBAR_KARTU, TINGGI_KARTU),
                                     kartu.jenis, not self.permainan.teratas(kartu))
        for i, kartu in enumerate(self.permainan.slot):
            hasil[kartu.nomor] = (self.kotak_slot(i), kartu.jenis, False)
        return hasil

    def potret_visual(self, sekarang):
        hasil = self.potret_kartu()
        for nomor, gerakan in self.animasi.items():
            # Tetap sertakan kartu musnah berukuran nol sampai perbarui() membersihkan
            # gerakannya; waktu dapat melewati batas durasi di tengah satu frame.
            hasil[nomor] = gerakan.potret(sekarang)
        return hasil

    def gambar_menu(self):
        self.kanvas.blit(self.gambar_judul, self.gambar_judul.get_rect(midtop=(LEBAR // 2, 55)))
        profil = profil_level(self.progres.level_terbuka)
        kategori = "Level Gila" if profil.kategori == "Gila" else profil.kategori
        self.tombol_baru(f"Level {profil.nomor} / {kategori}",
                         (102, 755, 336, 62), "mulai", True)
        self.tombol_baru(self.bahasa.t("pengaturan"), (102, 835, 336, 58), "pengaturan")

    def gambar_game(self):
        game = self.permainan
        sekarang = pygame.time.get_ticks()
        self.tombol_baru("Menu", (20, 22, 104, 42), "menu")
        self.teks(f"LEVEL {game.level}", (148, 34), 24, HIJAU)
        warna_kategori = (255, 178, 119) if game.profil.kategori == "Gila" else PUTIH
        self.teks(game.profil.kategori.upper(), (148, 64), 18, warna_kategori)
        self.teks(f"SKOR {game.skor:05d}", (352, 31), 30)
        if game.kombo:
            self.teks(self.bahasa.t("kombo", jumlah=game.kombo), (352, 65), 20, (255, 211, 120))
            self.panel((352, 94, 100, 5), (65, 80, 72), 2)
            lebar = round(100 * game.sisa_kombo() / game.durasi_kombo)
            if lebar:
                self.panel((352, 94, min(100, lebar), 5), (255, 211, 120), 2)
        sisa = sum(k.lokasi == "papan" for k in game.kartu)
        self.teks(f"{sisa} kartu di papan", (270, 97), 24, REDUP, True)
        self.tombol_baru("", (474, 77, 46, 42), "pengaturan")
        kilat = sekarang < self.kilat_sampai and (sekarang // 120) % 2 == 0
        self.panel((12, 128, 516, 116), (88, 55, 43) if kilat else (28, 47, 55),
                   garis=(244, 174, 93) if kilat else None)
        for i in range(game.kapasitas):
            kotak = self.kotak_slot(i)
            self.panel(kotak, (17, 34, 43), 9)
            self.teks(str(i + 1), kotak.center, 18, (71, 96, 103), True)
        self.area_kartu = []
        potret = self.potret_visual(sekarang)
        for kartu in game.kartu:
            if kartu.lokasi == "papan":
                kotak, jenis, tertutup = potret[kartu.nomor]
                self.kartu_baru(kotak, jenis, tertutup)
                self.area_kartu.append((kotak, kartu))
                if game.teratas(kartu) and kotak.collidepoint(self.posisi_mouse()):
                    pygame.draw.rect(self.kanvas, HIJAU, kotak, 2, border_radius=9)
        # Kartu yang terbang ke slot digambar di depan papan.
        for kartu in game.slot:
            kotak, jenis, _ = potret[kartu.nomor]
            self.kartu_baru(kotak, jenis)
        for kartu in game.kartu:
            if kartu.lokasi == "musnah" and kartu.nomor in self.animasi:
                kotak, jenis, _ = potret[kartu.nomor]
                if kotak.width >= 10 and kotak.height >= 10:
                    self.kartu_baru(kotak, jenis)
        self.teks(game.pesan, (270, 835), 20, HIJAU, True)
        if sekarang < self.efek_sampai:
            kemajuan = 1 - (self.efek_sampai - sekarang) / 1100
            y = 280 - round(8 * min(1, max(0, kemajuan)))
            self.panel((105, y - 24, 330, 48), (41, 61, 54), 16, garis=(255, 211, 120))
            label = (self.bahasa.t("kombo", jumlah=self.kombo_efek) + f"  +{self.poin_efek}"
                     if self.kombo_efek > 1 else f"+{self.poin_efek}")
            self.teks(label, (270, y), 30, (255, 211, 120), True)
        tersedia = game.status == "bermain" and not self.animasi
        self.tombol_baru("", (16, 868, 160, 54), "kembali", tersedia=tersedia)
        self.tombol_baru("", (190, 868, 160, 54), "cocok", tersedia=tersedia)
        self.tombol_baru("", (364, 868, 160, 54), "acak", tersedia=tersedia)
        if game.status != "bermain" and not self.animasi:
            self.gambar_hasil()

    def gambar_hasil(self):
        penutup = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        penutup.fill((5, 15, 23, 215))
        self.kanvas.blit(penutup, (0, 0))
        self.tombol = []
        self.panel((30, 300, 480, 360), (31, 53, 60), garis=HIJAU)
        menang = self.permainan.status == "menang"
        self.teks("Papan bersih!" if menang else "Slot sudah penuh", (270, 351), 48, tengah=True)
        if self.permainan.kombo_tertinggi > 1:
            self.teks(self.bahasa.t("kombo_terbaik", jumlah=self.permainan.kombo_tertinggi),
                      (270, 380), 18, HIJAU, True)
        self.teks(f"Level {self.level} / Skor {self.permainan.skor}",
                  (270, 405), 30, HIJAU, True)
        selesai = menang and self.level == Permainan.level_maksimum
        self.teks("Semua level selesai!" if selesai else
                  ("Level berikutnya sudah terbuka!" if menang else "Coba lagi dan atur urutan pilihanmu."),
                  (270, 451), 24, REDUP, True)
        aksi = "lanjut" if menang and not selesai else "ulang"
        self.tombol_baru("Level Berikutnya" if aksi == "lanjut" else "Main Lagi",
                         (70, 500, 400, 58), aksi, True)
        self.tombol_baru("Kembali ke Menu", (70, 580, 400, 54), "menu")
        if self.progres.peringatan:
            self.teks(self.progres.peringatan, (270, 685), 18, (245, 178, 106), True)

    def jalankan_gerakan(self, nama, kartu=None, bantuan=False):
        game = self.permainan
        sekarang = pygame.time.get_ticks()
        sebelum = self.potret_visual(sekarang)
        slot_awal = list(game.slot)
        peringatan, skor = game.peringatan, game.skor
        if nama == "pilih":
            berhasil = game.pilih(kartu, bantuan=bantuan)
        elif nama == "kembali":
            berhasil = game.kembalikan()
        elif nama == "acak":
            berhasil = game.acak_ulang()
        elif nama == "cocok":
            berhasil = game.cocok_otomatis()
        else:
            return
        if not berhasil:
            self.audio.mainkan("batal")
            return
        self.audio.mainkan({"pilih": "kartu", "cocok": "kartu", "kembali": "kembali", "acak": "acak"}[nama])
        sesudah = self.potret_kartu()
        hilang = {}
        sebelum_musnah = {}
        mulai_slot = max(sekarang, self.slot_siap)
        if nama in ("pilih", "cocok") and game.terakhir_musnah:
            jenis = game.terakhir_musnah[0].jenis
            posisi = max((i + 1 for i, k in enumerate(slot_awal) if k.jenis == jenis),
                         default=len(slot_awal))
            pelengkap = [k for k in game.terakhir_musnah if k not in slot_awal]
            slot_awal[posisi:posisi] = pelengkap
            for i, isi in enumerate(slot_awal):
                # Bantuan darurat mempertemukan pelengkap di ruang terakhir;
                # animasi tidak menggambar slot kedelapan di luar bilah.
                tujuan = self.kotak_slot(min(i, game.kapasitas - 1))
                sebelum_musnah[isi.nomor] = tujuan
                if isi.lokasi == "musnah":
                    hilang[isi.nomor] = (tujuan, isi.jenis, False)
        durasi_musnah = 620
        if nama == "acak":
            # Pasangkan gambar sejenis sebelum/sesudah pengacakan sehingga buah
            # terlihat berpindah tempat, bukan berubah jenis di tengah perjalanan.
            sumber = {}
            for isi in game.kartu:
                if isi.lokasi == "papan":
                    nilai = sebelum[isi.nomor]
                    sumber.setdefault(nilai[1], []).append(nilai)
            for isi in game.kartu:
                if isi.lokasi == "papan":
                    sebelum[isi.nomor] = sumber[sesudah[isi.nomor][1]].pop()
        for nomor, akhir in (sesudah | hilang).items():
            awal = sebelum.get(nomor, akhir)
            lama = self.animasi.get(nomor)
            isi = game.kartu[nomor]
            mulai = mulai_slot if isi.lokasi in ("slot", "musnah") else sekarang
            # Aksi cepat tetap diterima, tetapi gerakan slot menunggu ruang visual
            # dari kelompok sebelumnya. Lintasan lama dilanjutkan selama menunggu.
            if lama:
                awal = lama.potret(mulai)
            if hilang and isi.lokasi == "slot":
                singgah = sebelum_musnah[nomor]
                masuk = GerakanKartu(awal[0], singgah, akhir[1], False, mulai,
                                     sebelumnya=lama)
                if singgah != akhir[0]:
                    self.animasi[nomor] = GerakanKartu(
                        singgah, akhir[0], akhir[1], False, mulai + durasi_musnah,
                        sebelumnya=masuk)
                else:
                    self.animasi[nomor] = masuk
                continue
            # Gerakan yang tujuannya tetap tidak dimulai ulang saat klik berikutnya.
            if lama and lama.akhir == akhir[0] and lama.jenis == akhir[1] and not (nomor in hilang):
                continue
            if awal[0] != akhir[0] or nomor in hilang or (nama == "acak" and awal[1] != akhir[1]):
                self.animasi[nomor] = GerakanKartu(
                    awal[0], akhir[0], akhir[1], akhir[2], mulai,
                    musnah=nomor in hilang, durasi=durasi_musnah if nomor in hilang else 420,
                    sebelumnya=lama)
        if hilang:
            geser = any(sebelum_musnah[k.nomor] != sesudah[k.nomor][0] for k in game.slot)
            self.slot_siap = mulai_slot + durasi_musnah + (420 if geser else 0)
        if game.peringatan != peringatan:
            self.kilat_sampai = pygame.time.get_ticks() + 1100
        if game.skor > skor:
            self.poin_efek = game.skor - skor
            self.kombo_efek = game.kombo
            self.efek_sampai = pygame.time.get_ticks() + 1100
        if game.status == "menang":
            self.progres.selesaikan(game.level)

    def perbarui(self, sekarang=None):
        sekarang = pygame.time.get_ticks() if sekarang is None else sekarang
        if self.modal.aktif or self.konfirmasi_menu:
            self.permainan.jeda_kombo()
        else:
            self.permainan.lanjutkan_kombo()
        if self.permainan.status == "bermain":
            self.permainan.perbarui_kombo()
        self.audio.perbarui(sekarang)
        if self.transisi and sekarang - self.transisi[1] >= self.transisi[2]:
            self.transisi = None
        if self.intro and sekarang >= self.intro["mulai"] + self.intro["durasi"]:
            self.intro = None
        self.animasi = {nomor: gerakan for nomor, gerakan in self.animasi.items()
                        if not gerakan.selesai(sekarang)}
        if (self.halaman == "game" and self.permainan.status != "bermain"
                and not self.animasi and not self.intro and not self.hasil_dibunyikan):
            self.audio.mainkan(self.permainan.status)
            self.hasil_dibunyikan = True

    def aksi(self, nama):
        if self.modal.aktif:
            self.modal.aksi(nama)
            return
        if self.transisi or self.intro:
            return
        if nama in ("suara", "pengaturan"):
            self.modal.buka("volume" if nama == "suara" else "pengaturan")
            self.audio.mainkan("klik")
            return
        if nama in ("menu", "mulai", "ulang", "lanjut", "tetap_bermain", "konfirmasi_keluar"):
            self.audio.mainkan("klik")
        if self.konfirmasi_menu:
            if nama == "tetap_bermain":
                self.konfirmasi_menu = False
            elif nama == "konfirmasi_keluar":
                self.permainan.status = "kalah"
                self.konfirmasi_menu = False
                self.kembali_menu()
                self.audio.mainkan("kalah")
            return
        if nama == "menu":
            if self.halaman == "game" and self.permainan.status == "bermain":
                self.konfirmasi_menu = True
            else:
                self.kembali_menu()
        elif nama in ("mulai", "ulang"):
            self.mulai()
        elif nama == "lanjut":
            if self.permainan.status == "menang":
                self.mulai(self.permainan.level + 1)
        elif self.halaman == "game" and self.permainan.status == "bermain":
            if self.animasi:
                return  # Hanya alat bantu menunggu; pemilihan kartu tetap aktif.
            if nama == "cocok":
                self.jalankan_gerakan("cocok")
            elif nama in ("kembali", "acak"):
                self.jalankan_gerakan(nama)

    def kembali_menu(self):
        self.audio.bersihkan()
        self.audio.putar_musik("menu")
        self.animasi.clear()
        self.slot_siap = 0
        self.intro = None
        self.level = self.progres.level_terbuka
        self.pindah_halaman("menu")

    def gambar_konfirmasi(self):
        penutup = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        penutup.fill((8, 20, 27, 205))
        self.kanvas.blit(penutup, (0, 0))
        self.panel((30, 310, 480, 330), (31, 53, 60), garis=HIJAU)
        self.teks("Kembali ke menu?", (270, 360), 36, tengah=True)
        self.teks("Keluar sekarang dihitung kalah.", (270, 410), 26, PUTIH, True)
        self.teks("Level ini harus dimulai lagi.", (270, 446), 24, REDUP, True)
        self.tombol = []
        self.tombol_baru("Lanjut bermain", (65, 492, 410, 56), "tetap_bermain",
                         utama=True, ikon_aksi="mulai")
        self.tombol_baru("Ya, keluar", (65, 564, 410, 54), "konfirmasi_keluar", ikon_aksi="menu")

    def gambar_intro(self):
        waktu = pygame.time.get_ticks() - self.intro["mulai"]
        if waktu < 0:
            return
        t = min(1, waktu / self.intro["durasi"])
        masuk = min(1, t / 0.22)
        keluar = max(0, (t - 0.73) / 0.27)
        halus = lambda nilai: nilai * nilai * (3 - 2 * nilai)
        x = round(-LEBAR * (1 - halus(masuk)) + LEBAR * halus(keluar))
        redup = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        # Transparansi 70% berarti opasitas 30% (alpha 77 dari 255).
        redup.fill((8, 20, 27, round(77 * min(masuk, 1 - keluar))))
        self.kanvas.blit(redup, (0, 0))
        panel_intro = pygame.Surface((490, 240), pygame.SRCALPHA)
        pygame.draw.rect(panel_intro, (245, 239, 211, 77), panel_intro.get_rect(), border_radius=28)
        pygame.draw.rect(panel_intro, (139, 176, 98, 77), panel_intro.get_rect(),
                         width=2, border_radius=28)
        self.kanvas.blit(panel_intro, (x + 25, 352))
        ikon = self.aset_tombol.ikon["cocok"]
        gambar = pygame.transform.smoothscale(ikon, (70, 70))
        self.kanvas.blit(gambar, (x + 235, 367))
        self.teks(f"LEVEL {self.level}", (x + 270, 471), 60, (67, 59, 52), True)
        kategori = self.permainan.profil.kategori
        warna = (156, 54, 83) if kategori == "Gila" else (67, 59, 52)
        self.teks("LEVEL GILA!" if kategori == "Gila" else kategori.upper(),
                  (x + 270, 521), 30, warna, True)
        self.teks("Cocokkan tiga gambar yang sama", (x + 270, 562), 24, (85, 104, 76), True)
        self.tombol = []

    def gambar(self):
        self.perbarui()
        self.kanvas.blit(self.latar.untuk_halaman(self.halaman), (0, 0))
        redup = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        redup.fill((10, 25, 30, 38))
        # Pelat transparan memberi kontras pada teks, sambil mempertahankan gambar.
        if self.halaman != "menu":
            pygame.draw.rect(redup, (16, 31, 39, 185), (0, 0, LEBAR, 122))
            pygame.draw.rect(redup, (16, 31, 39, 185), (0, 820, LEBAR, 140))
        self.kanvas.blit(redup, (0, 0))
        self.tombol = []
        if self.halaman == "menu":
            self.gambar_menu()
        else:
            self.gambar_game()
        if self.permainan.status == "bermain" or self.halaman == "menu":
            kotak_suara = (474, 18, 46, 42) if self.halaman == "menu" else (280, 22, 46, 42)
            self.tombol_baru("", kotak_suara, "suara",
                             ikon_aksi="suara_mati" if self.audio.dibisukan else "suara_aktif")
        if self.transisi:
            lama, mulai, durasi, arah = self.transisi
            t = min(1, max(0, (pygame.time.get_ticks() - mulai) / durasi))
            halus = t * t * (3 - 2 * t)
            baru = self.kanvas.copy()
            self.kanvas.fill(LATAR)
            self.kanvas.blit(lama, (round(-arah * LEBAR * halus), 0))
            self.kanvas.blit(baru, (round(arah * LEBAR * (1 - halus)), 0))
        if self.intro:
            self.gambar_intro()
        if self.konfirmasi_menu:
            self.gambar_konfirmasi()
        if self.modal.aktif:
            self.modal.gambar()
        lebar, tinggi = self.layar.get_size()
        skala = min(lebar / LEBAR, tinggi / TINGGI)
        ukuran = (max(1, int(LEBAR * skala)), max(1, int(TINGGI * skala)))
        self.layar.fill((8, 18, 24))
        self.layar.blit(pygame.transform.smoothscale(self.kanvas, ukuran),
                        ((lebar - ukuran[0]) // 2, (tinggi - ukuran[1]) // 2))
        pygame.display.flip()

    def tangani(self, kejadian):
        if kejadian.type == pygame.QUIT:
            if self.modal.digeser:
                self.audio.simpan()
            self.aktif = False
            return
        if self.modal.aktif:
            self.modal.tangani(kejadian)
            return
        if self.transisi or self.intro:
            return
        if self.konfirmasi_menu:
            if kejadian.type == pygame.KEYDOWN and kejadian.key == pygame.K_ESCAPE:
                self.aksi("tetap_bermain")
            elif kejadian.type == pygame.MOUSEBUTTONDOWN and kejadian.button == 1:
                posisi = self.posisi_mouse(kejadian.pos)
                for kotak, nama in self.tombol:
                    if nama in ("tetap_bermain", "konfirmasi_keluar") and kotak.collidepoint(posisi):
                        self.aksi(nama)
                        break
            return
        if kejadian.type == pygame.KEYDOWN:
            if kejadian.key == pygame.K_ESCAPE:
                self.aksi("menu")
            elif self.halaman == "game":
                self.aksi({pygame.K_z: "kembali", pygame.K_c: "cocok", pygame.K_r: "acak"}
                          .get(kejadian.key, ""))
        elif kejadian.type == pygame.MOUSEBUTTONDOWN and kejadian.button == 1:
            posisi = self.posisi_mouse(kejadian.pos)
            for kotak, aksi in self.tombol:
                if kotak.collidepoint(posisi):
                    self.aksi(aksi)
                    return
            if self.halaman == "game" and self.permainan.status == "bermain":
                # Hitbox dihitung ulang tiap event: beberapa klik pada satu frame
                # langsung melihat kartu yang baru tersingkap, bukan data frame lama.
                potret = self.potret_visual(pygame.time.get_ticks())
                for kartu in reversed(self.permainan.kartu):
                    if kartu.lokasi != "papan":
                        continue
                    kotak = potret[kartu.nomor][0]
                    if kotak.collidepoint(posisi):
                        if self.permainan.teratas(kartu):
                            self.jalankan_gerakan("pilih", kartu)
                        else:
                            self.permainan.pesan = "Tertutup lebih dari 15%. Ambil kartu di atasnya."
                            self.audio.mainkan("batal")
                        return

    def jalankan(self):
        self.gambar()
        while self.aktif:
            for kejadian in pygame.event.get():
                self.tangani(kejadian)
            self.gambar()
            self.jam.tick(60)
        self.audio.bersihkan()
        pygame.quit()
