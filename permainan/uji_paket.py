"""Pemeriksaan executable tersembunyi tanpa mengubah progres pengguna."""

import json
import os
from pathlib import Path
import tempfile
import traceback


def jalankan(laporan):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    hasil = {"berhasil": False}
    try:
        import pygame
        from .antarmuka import Aplikasi
        with tempfile.TemporaryDirectory() as direktori:
            a = Aplikasi(Path(direktori) / "progres.json")
            a.gambar()
            assert a.audio.tersedia
            assert len(a.gambar_aset) == 24
            a.aksi("pengaturan")
            a.aksi("modal_bahasa")
            for kode in a.bahasa.pilihan:
                a.bahasa.pilih(kode)
                a.gambar()
            a.aksi("pilih_bahasa:id")
            a.aksi("modal_volume")
            a.gambar()
            a.aksi("modal_tutup")
            a.aksi("modal_tutup")
            a.progres.level_terbuka = 1000
            assert a.mulai(1000)
            a.perbarui(a.intro["mulai"] + a.intro["durasi"])
            a.gambar()
            assert len(a.permainan.kartu) == 90
            assert a.audio.musik == "game"
            a.aksi("menu")
            a.gambar()
            assert a.konfirmasi_menu
            a.aksi("konfirmasi_keluar")
            a.perbarui(a.transisi[1] + a.transisi[2])
            a.gambar()
            hasil = {"berhasil": True, "ikon": True, "aset_svg": len(a.gambar_aset),
                     "bahasa": len(a.bahasa.pilihan), "audio": a.audio.tersedia,
                     "level_1000": True, "modal": True, "konfirmasi_keluar": True}
            a.audio.bersihkan()
            pygame.quit()
    except Exception:
        hasil["galat"] = traceback.format_exc()
    tujuan = Path(laporan)
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    tujuan.write_text(json.dumps(hasil, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if hasil["berhasil"] else 1
