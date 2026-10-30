"""Aturan permainan tanpa ketergantungan pada tampilan Pygame."""

from collections import Counter
from dataclasses import dataclass
import random
import math
import time
from .level import LEVEL_MAKSIMUM, profil_level

LEBAR_KARTU = 80
TINGGI_KARTU = 90


@dataclass
class Kartu:
    nomor: int
    jenis: int
    tumpukan: int
    lapisan: int
    lokasi: str = "papan"
    x: float | None = None
    y: float | None = None


class Permainan:
    kapasitas = 7
    level_maksimum = LEVEL_MAKSIMUM
    durasi_kombo = 5.0
    batas_kombo = 5
    bobot_bentuk = {"plus": 1, "silang": 1, "gunung": 3, "lingkaran": 3,
                   "spiral": 3, "gelombang": 3, "pulau": 3, "acak": 2}

    def __init__(self, level=1, acak=None, bentuk_sebelumnya=None, jam=None):
        self.jam = jam if jam is not None else time.monotonic
        self.kombo = 0
        self.kombo_tertinggi = 0
        self.batas_waktu_kombo = None
        self.waktu_jeda = None
        self.terakhir_poin = 0
        self.acak = acak if acak is not None else random.Random()
        self.level = max(1, min(level, self.level_maksimum))
        self.profil = profil_level(self.level)
        self.kolom = self.profil.kolom
        self.jumlah_jenis = self.profil.jumlah_jenis
        self.kartu = []
        self.slot = []  # Indeks nol selalu digambar pada slot paling kiri.
        self.riwayat = []
        self.skor = 0
        self.status = "bermain"
        self.pesan = "Pilih kartu teratas. Cocokkan tiga gambar yang sama!"
        self.peringatan = 0
        self.terakhir_musnah = []
        self.bentuk_sebelumnya = bentuk_sebelumnya
        self._buat_papan()
        self._acak_posisi()

    def _acak_posisi(self):
        """Pilih siluet acak dan sebar tumpukan mengikuti bentuknya."""
        pilihan = [nama for nama in self.bobot_bentuk if nama != self.bentuk_sebelumnya]
        self.bentuk = self.acak.choices(pilihan, weights=[self.bobot_bentuk[n] for n in pilihan])[0]
        pusat = []
        for _ in range(self.kolom * 3):
            kandidat = []
            for _ in range(100):
                if self.bentuk == "plus":
                    x, y = self.acak.uniform(-1, 1), self.acak.uniform(-0.26, 0.26)
                    if self.acak.random() < 0.5:
                        x, y = y, x
                elif self.bentuk == "silang":
                    x = self.acak.uniform(-1, 1)
                    y = self.acak.choice((-1, 1)) * x + self.acak.uniform(-0.15, 0.15)
                elif self.bentuk == "gunung":
                    # Luas segitiga melebar ke bawah seperti lereng gunung.
                    y = self.acak.uniform(-1, 1)
                    x = self.acak.uniform(-1, 1) * (y + 1) / 2
                elif self.bentuk in ("lingkaran", "spiral"):
                    sudut = self.acak.uniform(0, math.tau * (2 if self.bentuk == "spiral" else 1))
                    radius = (0.12 + 0.88 * sudut / (math.tau * 2) if self.bentuk == "spiral"
                              else self.acak.uniform(0.65, 1))
                    x, y = radius * math.cos(sudut), radius * math.sin(sudut)
                elif self.bentuk == "gelombang":
                    x = self.acak.uniform(-1, 1)
                    y = 0.6 * math.sin(math.pi * x) + self.acak.uniform(-0.2, 0.2)
                elif self.bentuk == "pulau":
                    pusat_x, pusat_y = self.acak.choice(((-0.6, -0.5), (0.5, -0.25), (0, 0.6)))
                    x = pusat_x + self.acak.uniform(-0.28, 0.28)
                    y = pusat_y + self.acak.uniform(-0.28, 0.28)
                else:
                    x, y = self.acak.uniform(-1, 1), self.acak.uniform(-1, 1)
                kandidat.append((216 + 184 * x * self.profil.sebaran,
                                 466 + 207 * max(-1, min(1, y)) * self.profil.sebaran))
            # Kandidat berjauhan menjaga bentuk tetap terbaca tanpa menjadi grid.
            titik = max(kandidat, key=lambda p: min(
                ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for q in pusat),
                default=1))
            pusat.append(titik)
        for kartu in self.kartu:
            x, y = pusat[kartu.tumpukan]
            # Setiap lapisan bergeser berbeda; sudut buah bawah tetap tersingkap.
            kartu.x = x + kartu.lapisan * 14 + self.acak.uniform(-3, 3)
            kartu.y = y + kartu.lapisan * 22 + self.acak.uniform(-3, 3)

    def _buat_papan(self):
        tinggi = [0] * (self.kolom * 3)
        kelompok = list(range(self.jumlah_jenis))
        kelompok.extend(self.acak.randrange(self.jumlah_jenis)
                        for _ in range(self.kolom * 3 - self.jumlah_jenis))
        self.acak.shuffle(kelompok)
        # Isi dalam kelompok tiga. Urutan kelompok terbalik adalah salah satu
        # solusi sah karena setiap kartu kelompok terakhir selalu berada di atas.
        for jenis in kelompok:
            tersedia = [i for i, nilai in enumerate(tinggi) if nilai < 3]
            for _ in range(3):
                tumpukan = self.acak.choice(tersedia)
                self.kartu.append(Kartu(len(self.kartu), jenis, tumpukan, tinggi[tumpukan]))
                tinggi[tumpukan] += 1
                if tinggi[tumpukan] == 3:
                    tersedia.remove(tumpukan)

    def teratas(self, kartu):
        if kartu.x is not None and kartu.y is not None:
            return kartu.lokasi == "papan" and self.bagian_tertutup(kartu) <= 0.15
        return kartu.lokasi == "papan" and not any(
            lain.lokasi == "papan" and lain.tumpukan == kartu.tumpukan
            and lain.lapisan > kartu.lapisan for lain in self.kartu
        )

    def bagian_tertutup(self, kartu):
        """Fraksi luas muka kartu yang ditutup gabungan kartu di depannya."""
        if kartu.x is None or kartu.y is None:
            return 0.0
        x, y = round(kartu.x), round(kartu.y)
        irisan = []
        for lain in self.kartu:
            if lain.lokasi != "papan" or lain.nomor <= kartu.nomor or lain.x is None or lain.y is None:
                continue
            kiri, atas = max(x, round(lain.x)), max(y, round(lain.y))
            kanan = min(x + LEBAR_KARTU, round(lain.x) + LEBAR_KARTU)
            bawah = min(y + TINGGI_KARTU, round(lain.y) + TINGGI_KARTU)
            if kiri < kanan and atas < bawah:
                irisan.append((kiri, atas, kanan, bawah))
        # Sapu pita vertikal dan gabungkan interval Y agar penutup yang saling
        # bertumpuk tidak menghitung area yang sama dua kali.
        batas = sorted({nilai for kiri, _, kanan, _ in irisan for nilai in (kiri, kanan)})
        luas = 0
        for kiri, kanan in zip(batas, batas[1:]):
            interval = sorted((atas, bawah) for a, atas, b, bawah in irisan
                              if a < kanan and b > kiri)
            ujung = -math.inf
            panjang = 0
            for atas, bawah in interval:
                panjang += max(0, bawah - max(atas, ujung))
                ujung = max(ujung, bawah)
            luas += (kanan - kiri) * panjang
        return luas / (LEBAR_KARTU * TINGGI_KARTU)

    def pilih(self, kartu, bantuan=False):
        self.terakhir_musnah = []
        if self.status != "bermain" or kartu.lokasi != "papan":
            return False
        if not bantuan and not self.teratas(kartu):
            self.pesan = "Tertutup lebih dari 15%. Ambil kartu di atasnya."
            return False
        if len(self.slot) >= self.kapasitas:
            return False
        self.perbarui_kombo()
        if bantuan:
            self.putus_kombo()
        # Sisipkan sesudah kelompok sejenis agar kelompok tetap bersebelahan.
        posisi = max((i + 1 for i, isi in enumerate(self.slot)
                      if isi.jenis == kartu.jenis), default=len(self.slot))
        self.slot.insert(posisi, kartu)
        kartu.lokasi = "slot"
        self.riwayat.append(kartu)
        cocok = [isi for isi in self.slot if isi.jenis == kartu.jenis]
        if len(cocok) == 3:
            self.terakhir_musnah = cocok
            for isi in cocok:
                isi.lokasi = "musnah"
                self.slot.remove(isi)
            self.riwayat = [isi for isi in self.riwayat if isi.lokasi == "slot"]
            if not bantuan:
                self.kombo = min(self.batas_kombo, self.kombo + 1)
                self.kombo_tertinggi = max(self.kombo_tertinggi, self.kombo)
                self.batas_waktu_kombo = self.sekarang_kombo() + self.durasi_kombo
            self.terakhir_poin = 100 * len(cocok) * max(1, self.kombo)
            self.skor += self.terakhir_poin
            self.pesan = (f"+{self.terakhir_poin}! Kombo x{self.kombo}." if self.kombo > 1
                          else "+300! Tiga kartu berhasil dicocokkan.")
        else:
            self.pesan = "Cari gambar yang sama untuk mengosongkan slot."
        if len(self.slot) >= self.kapasitas - 3:
            self.peringatan += 1
        if all(isi.lokasi == "musnah" for isi in self.kartu):
            self.status = "menang"
        elif len(self.slot) == self.kapasitas:
            self.status = "kalah"
            self.putus_kombo()
        return True

    def sekarang_kombo(self):
        return self.waktu_jeda if self.waktu_jeda is not None else self.jam()

    def putus_kombo(self):
        self.kombo = 0
        self.batas_waktu_kombo = None

    def perbarui_kombo(self):
        if self.batas_waktu_kombo is not None and self.sekarang_kombo() > self.batas_waktu_kombo:
            self.putus_kombo()

    def sisa_kombo(self):
        if self.batas_waktu_kombo is None:
            return 0.0
        return max(0.0, self.batas_waktu_kombo - self.sekarang_kombo())

    def jeda_kombo(self):
        if self.waktu_jeda is None:
            self.waktu_jeda = self.jam()

    def lanjutkan_kombo(self):
        if self.waktu_jeda is not None:
            if self.batas_waktu_kombo is not None:
                self.batas_waktu_kombo += self.jam() - self.waktu_jeda
            self.waktu_jeda = None

    def kembalikan(self):
        if self.status != "bermain":
            return False
        if not self.riwayat:
            self.pesan = "Belum ada kartu di slot yang bisa dikembalikan."
            return False
        kartu = self.riwayat.pop()
        self.putus_kombo()
        self.slot.remove(kartu)
        kartu.lokasi = "papan"
        self.pesan = "Kartu terakhir dikembalikan ke posisi semula."
        return True

    def rencana_otomatis(self):
        if self.status != "bermain":
            return []
        if not self.slot:
            self.pesan = "Isi slot terlebih dahulu untuk memakai Cocok Otomatis."
            return []
        jumlah = Counter(kartu.jenis for kartu in self.slot)
        darurat = len(self.slot) == self.kapasitas - 1 and max(jumlah.values()) == 1
        # Satu ruang dengan semua jenis berbeda diselamatkan dari sisi kanan.
        # Pada kondisi lainnya tetap prioritaskan jumlah terbanyak lalu sisi kiri.
        jenis = self.slot[-1].jenis if darurat else max(jumlah, key=jumlah.get)
        butuh = 3 - jumlah[jenis]
        tersedia = [kartu for kartu in self.kartu
                    if kartu.lokasi == "papan" and kartu.jenis == jenis]
        if len(tersedia) < butuh:
            self.pesan = "Kartu pelengkap belum tersedia di papan."
            return []
        return tersedia[:butuh]

    def cocok_otomatis(self):
        pelengkap = self.rencana_otomatis()
        if not pelengkap:
            return False
        jenis = pelengkap[0].jenis
        kelompok = [k for k in self.slot if k.jenis == jenis] + pelengkap
        # Selesaikan bantuan sebagai satu transaksi. Tidak pernah menyimpan
        # delapan kartu atau memicu kalah ketika pelengkap pertama diambil.
        self.putus_kombo()
        for kartu in kelompok:
            kartu.lokasi = "musnah"
        self.slot = [k for k in self.slot if k.lokasi == "slot"]
        self.riwayat = [k for k in self.riwayat if k.lokasi == "slot"]
        self.terakhir_musnah = kelompok
        self.terakhir_poin = 300
        self.skor += self.terakhir_poin
        self.pesan = "+300! Tiga kartu berhasil dicocokkan."
        if all(k.lokasi == "musnah" for k in self.kartu):
            self.status = "menang"
        return True

    def acak_ulang(self):
        if self.status != "bermain":
            return False
        self.putus_kombo()
        papan = [kartu for kartu in self.kartu if kartu.lokasi == "papan"]
        jenis = [kartu.jenis for kartu in papan]
        self.acak.shuffle(jenis)
        for kartu, nilai in zip(papan, jenis):
            kartu.jenis = nilai
        # Cabang berbias berpeluang 65%; cabang biasa pun mungkin cocok secara
        # alami. Pertukaran menjaga jumlah total setiap jenis tetap sama.
        if self.slot and self.acak.random() < 0.65:
            sasaran = {kartu.jenis for kartu in self.slot}
            atas = [kartu for kartu in papan if self.teratas(kartu)]
            if not any(kartu.jenis in sasaran for kartu in atas):
                cocok = [kartu for kartu in papan if kartu.jenis in sasaran]
                if cocok and atas:
                    sumber = self.acak.choice(cocok)
                    tujuan = self.acak.choice(atas)
                    sumber.jenis, tujuan.jenis = tujuan.jenis, sumber.jenis
        self.pesan = "Kartu di papan sudah diacak."
        return True
