from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from permainan.lokasi import AKAR, folder_data


class UjiLokasi(unittest.TestCase):
    def test_python_memakai_folder_proyek(self):
        with patch("sys.frozen", False, create=True):
            self.assertEqual(folder_data(), AKAR / "data")

    def test_executable_memakai_appdata_bukan_folder_ekstraksi(self):
        with tempfile.TemporaryDirectory() as direktori:
            with patch("sys.frozen", True, create=True), patch.dict(
                    "os.environ", {"LOCALAPPDATA": direktori}):
                self.assertEqual(folder_data(), Path(direktori) / "MatchYouTile")
