import json
from pathlib import Path
import tempfile
import unittest

from permainan.progres import Progres


class UjiProgres(unittest.TestCase):
    def test_harus_berurutan_dan_tersimpan_setelah_dibuka_ulang(self):
        with tempfile.TemporaryDirectory() as direktori:
            berkas = Path(direktori) / "data" / "progres.json"
            progres = Progres(berkas)
            self.assertEqual(progres.level_terbuka, 1)
            self.assertFalse(progres.selesaikan(3))
            self.assertTrue(progres.selesaikan(1))
            self.assertEqual(Progres(berkas).level_terbuka, 2)
            self.assertFalse(progres.selesaikan(1))
            self.assertEqual(progres.level_terbuka, 2)

    def test_berkas_rusak_dan_nilai_tidak_valid(self):
        with tempfile.TemporaryDirectory() as direktori:
            berkas = Path(direktori) / "progres.json"
            for isi in ("rusak", "null", "[]", '{"level_terbuka": "8"}',
                        '{"level_terbuka": true}'):
                berkas.write_text(isi, encoding="utf-8")
                self.assertEqual(Progres(berkas).level_terbuka, 1)
            berkas.write_text(json.dumps({"level_terbuka": 1500}), encoding="utf-8")
            self.assertEqual(Progres(berkas).level_terbuka, 1000)
            berkas.write_text(json.dumps({"level_terbuka": 90}), encoding="utf-8")
            self.assertEqual(Progres(berkas).level_terbuka, 90)

    def test_gagal_simpan_tetap_mempertahankan_progres_sesi(self):
        with tempfile.TemporaryDirectory() as direktori:
            penghalang = Path(direktori) / "berkas"
            penghalang.write_text("bukan folder", encoding="utf-8")
            progres = Progres(penghalang / "progres.json")
            self.assertTrue(progres.selesaikan(1))
            self.assertEqual(progres.level_terbuka, 2)
            self.assertTrue(progres.peringatan)
