import ast
import json
from pathlib import Path
import string
import tempfile
import unittest

from permainan.bahasa import Bahasa

AKAR = Path(__file__).resolve().parent.parent


class UjiBahasa(unittest.TestCase):
    def test_delapan_bahasa_memiliki_semua_terjemahan_dan_placeholder_sama(self):
        data = json.loads((AKAR / "assets" / "bahasa.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["kode"]), 8)
        formatter = string.Formatter()
        for baris in data["teks"].values():
            self.assertEqual(len(baris), 8)
            self.assertTrue(all(baris))
            parameter = [{nama for _, nama, _, _ in formatter.parse(teks) if nama} for teks in baris]
            self.assertTrue(all(p == parameter[0] for p in parameter))

    def test_pesan_model_dan_progres_semuanya_dapat_diterjemahkan(self):
        with tempfile.TemporaryDirectory() as folder:
            bahasa = Bahasa(AKAR / "assets" / "bahasa.json", Path(folder) / "pengaturan.json")
            for nama in ("model.py", "progres.py"):
                pohon = ast.parse((AKAR / "permainan" / nama).read_text(encoding="utf-8-sig"))
                for simpul in ast.walk(pohon):
                    if isinstance(simpul, ast.Assign) and isinstance(simpul.value, ast.Constant):
                        if any(isinstance(t, ast.Attribute) and t.attr in ("pesan", "peringatan")
                               for t in simpul.targets) and simpul.value.value:
                            self.assertIn(simpul.value.value, bahasa.sumber)

    def test_pilihan_tersimpan_dan_teks_dinamis_ikut_berubah(self):
        with tempfile.TemporaryDirectory() as folder:
            pengaturan = Path(folder) / "pengaturan.json"
            bahasa = Bahasa(AKAR / "assets" / "bahasa.json", pengaturan)
            self.assertTrue(bahasa.pilih("en"))
            self.assertEqual(bahasa.terjemahkan("Level 10 / Level Gila"), "Level 10 / Insane")
            self.assertEqual(bahasa.terjemahkan("SKOR 00300"), "SCORE 00300")
            self.assertEqual(bahasa.terjemahkan("Papan bersih!"), "Board cleared!")
            self.assertEqual(Bahasa(AKAR / "assets" / "bahasa.json", pengaturan).kode, "en")
            self.assertFalse(bahasa.pilih("tidak_ada"))
