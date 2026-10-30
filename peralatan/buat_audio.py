"""Buat musik dan efek orisinal dengan sintesis nada; hanya pustaka standar."""

from array import array
import math
from pathlib import Path
import wave

LAJU = 22050
TUJUAN = Path(__file__).resolve().parent.parent / "assets" / "audio"


def nada(buffer, mulai, durasi, midi, volume=0.25, warna="petik"):
    frekuensi = 440 * 2 ** ((midi - 69) / 12)
    awal = round(mulai * LAJU)
    jumlah = round(durasi * LAJU)
    for i in range(min(jumlah, len(buffer) - awal)):
        waktu = i / LAJU
        # Attack/release pendek mencegah bunyi klik pada ujung setiap nada.
        tepi = min(1, waktu / 0.008, (durasi - waktu) / 0.04)
        fase = math.tau * frekuensi * waktu
        if warna == "bas":
            sinyal = math.sin(fase) + 0.15 * math.sin(2 * fase)
            amplop = math.exp(-2 * waktu)
        else:
            sinyal = (math.sin(fase) + 0.28 * math.sin(2 * fase)
                      + 0.10 * math.sin(3 * fase))
            amplop = math.exp(-(5 if warna == "petik" else 3) * waktu)
        buffer[awal + i] += sinyal * amplop * max(0, tepi) * volume


def simpan(nama, buffer):
    puncak = max((abs(x) for x in buffer), default=1)
    pengali = 0.85 / max(1, puncak)
    pcm = array("h", (round(max(-1, min(1, x * pengali)) * 32767) for x in buffer))
    import sys
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(TUJUAN / f"{nama}.wav"), "wb") as berkas:
        berkas.setparams((1, 2, LAJU, 0, "NONE", "not compressed"))
        berkas.writeframes(pcm.tobytes())


def musik(nama, bpm, melodi):
    ketuk = 60 / bpm
    buffer = [0.0] * round(32 * ketuk * LAJU)
    akor = ((48, 52, 55), (53, 57, 60), (45, 48, 52), (55, 59, 62))
    for birama in range(8):
        akar, tengah, atas = akor[birama % 4]
        for langkah in range(8):
            waktu = (birama * 4 + langkah / 2) * ketuk
            midi = (akar + 12, tengah + 12, atas + 12, tengah + 12)[langkah % 4]
            nada(buffer, waktu, ketuk * 0.7, midi, 0.10)
        for ketukan in (0, 2):
            nada(buffer, (birama * 4 + ketukan) * ketuk, ketuk * 1.4, akar - 12, 0.14, "bas")
        for langkah, midi in enumerate(melodi[birama % len(melodi)]):
            if midi:
                nada(buffer, (birama * 4 + langkah) * ketuk, ketuk * 0.85, midi, 0.19, "lonceng")
    # Jeda mikro di batas loop menghindari diskontinuitas PCM; frase kembali ke C.
    tepi = round(LAJU * 0.035)
    for i in range(tepi):
        buffer[i] *= i / tepi
        buffer[-1 - i] *= i / tepi
    simpan(nama, buffer)


def efek(nama, notasi, sela=0.10, durasi=0.22):
    buffer = [0.0] * round((max(0, len(notasi) - 1) * sela + durasi + 0.05) * LAJU)
    for i, midi in enumerate(notasi):
        nada(buffer, i * sela, durasi, midi, 0.35)
    simpan(nama, buffer)


def buat():
    TUJUAN.mkdir(parents=True, exist_ok=True)
    musik("musik_menu", 92, ((72, 76, 79, 76), (77, 76, 72, 0),
                              (76, 79, 81, 79), (74, 71, 72, 0)))
    musik("musik_game", 108, ((76, 79, 84, 79), (81, 79, 77, 76),
                               (76, 72, 76, 81), (79, 74, 71, 72)))
    efek("klik", (81,), durasi=0.10)
    efek("kartu", (67, 74), sela=0.035, durasi=0.13)
    efek("cocok", (76, 79, 84), sela=0.09, durasi=0.30)
    efek("kembali", (76, 69), sela=0.07)
    efek("acak", (67, 72, 76, 79, 72), sela=0.055, durasi=0.17)
    efek("peringatan", (79, 79), sela=0.18, durasi=0.13)
    efek("menang", (72, 76, 79, 84, 88), sela=0.14, durasi=0.65)
    efek("kalah", (67, 64, 60, 55), sela=0.19, durasi=0.45)
    efek("intro", (72, 79, 84), sela=0.12, durasi=0.32)
    efek("batal", (57,), durasi=0.12)
    print(f"Dibuat 2 musik dan 10 efek WAV di {TUJUAN}")


if __name__ == "__main__":
    buat()
