"""Profil kesulitan 1.000 level; level dibuat saat dimainkan, tanpa server."""

from dataclasses import dataclass

LEVEL_MAKSIMUM = 1000
JENIS_MAKSIMUM = 18
INTERVAL_LEVEL_GILA = 10
RENTANG_JENIS = {"Mudah": (5, 7), "Sedang": (8, 10), "Sulit": (11, 13), "Gila": (12, 18)}


def jumlah_jenis_level(nomor, kategori):
    if nomor <= 3:
        return 3
    awal, akhir = RENTANG_JENIS[kategori]
    if kategori == "Gila":
        kemajuan = ((nomor - 10) / (LEVEL_MAKSIMUM - 10)) ** 0.6
    else:
        batas_awal, batas_akhir = {"Mudah": (4, 333), "Sedang": (334, 666),
                                   "Sulit": (667, 1000)}[kategori]
        kemajuan = (nomor - batas_awal) / (batas_akhir - batas_awal)
    return awal + round((akhir - awal) * kemajuan)


@dataclass(frozen=True)
class ProfilLevel:
    nomor: int
    kolom: int
    jumlah_jenis: int
    sebaran: float
    indeks: int
    kategori: str

    @property
    def jumlah_kartu(self):
        return self.kolom * 9


def profil_level(nomor):
    nomor = max(1, min(nomor, LEVEL_MAKSIMUM))
    dasar = ((nomor - 1) / (LEVEL_MAKSIMUM - 1)) ** 0.55
    fase = (nomor - 1) % 10
    # Gelombang kecil: awal siklus memberi jeda, akhir siklus lebih menantang.
    gila = nomor % INTERVAL_LEVEL_GILA == 0
    kategori = ("Gila" if gila else "Mudah" if nomor <= 333
                else "Sedang" if nomor <= 666 else "Sulit")
    tekanan_dasar = dasar * (0.94 + fase * 0.012)
    # Sisakan ruang tantangan di atas level biasa, termasuk mendekati level 1000.
    tekanan = (min(1.0, tekanan_dasar + 0.16 + 0.12 * dasar) if gila
               else min(0.90, tekanan_dasar))
    kolom = 3 + round(7 * tekanan)
    jenis = jumlah_jenis_level(nomor, kategori)
    sebaran = 1 - 0.22 * tekanan
    # Indeks desain menggabungkan panjang permainan, ragam, dan kepadatan.
    nilai = (0.35 * ((kolom * 9 - 27) / 63)
             + 0.40 * ((jenis - 3) / (JENIS_MAKSIMUM - 3)) + 0.25 * tekanan)
    indeks = max(1, round(100 * nilai))
    return ProfilLevel(nomor, kolom, jenis, sebaran, indeks, kategori)
