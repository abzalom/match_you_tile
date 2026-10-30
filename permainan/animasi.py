"""Gerakan per kartu yang dapat ditargetkan ulang tanpa melompat posisi."""

from dataclasses import dataclass
import pygame


@dataclass
class GerakanKartu:
    awal: pygame.Rect
    akhir: pygame.Rect
    jenis: int
    tertutup: bool
    mulai: int
    musnah: bool = False
    durasi: int = 420
    sebelumnya: "GerakanKartu | None" = None

    def potret(self, sekarang):
        if sekarang < self.mulai and self.sebelumnya is not None:
            return self.sebelumnya.potret(sekarang)
        t = min(1, max(0, (sekarang - self.mulai) / self.durasi))
        gerak = min(1, t / 0.7) if self.musnah else t
        halus = gerak * gerak * (3 - 2 * gerak)
        kotak = pygame.Rect(*(round(a + (b - a) * halus)
                              for a, b in zip(self.awal, self.akhir)))
        if self.musnah and t > 0.7:
            skala = max(0, (1 - t) / 0.3)
            pusat = kotak.center
            kotak.size = (round(kotak.width * skala), round(kotak.height * skala))
            kotak.center = pusat
        return kotak, self.jenis, self.tertutup

    def selesai(self, sekarang):
        return sekarang >= self.mulai + self.durasi
