"""Penyimpanan level terbuka secara lokal, tanpa dependensi tambahan."""

import json
from pathlib import Path

from .model import Permainan


class Progres:
    def __init__(self, berkas):
        self.berkas = Path(berkas)
        self.level_terbuka = 1
        self.peringatan = ""
        try:
            nilai = json.loads(self.berkas.read_text(encoding="utf-8"))["level_terbuka"]
            if type(nilai) is int:
                self.level_terbuka = max(1, min(nilai, Permainan.level_maksimum))
        except FileNotFoundError:
            pass
        except (OSError, ValueError, KeyError, TypeError):
            self.peringatan = "Progres tidak terbaca; mulai dari level 1."

    def selesaikan(self, level):
        if level != self.level_terbuka:
            return False
        self.level_terbuka = min(Permainan.level_maksimum,
                                 max(self.level_terbuka, level + 1))
        try:
            self.berkas.parent.mkdir(parents=True, exist_ok=True)
            sementara = self.berkas.with_suffix(".tmp")
            sementara.write_text(json.dumps({"level_terbuka": self.level_terbuka}),
                                  encoding="utf-8")
            sementara.replace(self.berkas)
            self.peringatan = ""
        except OSError:
            self.peringatan = "Progres sesi ini aktif, tetapi gagal disimpan."
        return True
