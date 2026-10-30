"""Build executable Windows menggunakan PyInstaller lokal atau virtualenv."""

import os
from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    akar = Path(__file__).resolve().parent.parent
    lingkungan = os.environ.copy()
    alat = akar / ".build_tools"
    lingkungan["PYINSTALLER_CONFIG_DIR"] = str(akar / ".build_tools" / "cache")
    if alat.exists():
        lingkungan["PYTHONPATH"] = str(alat) + os.pathsep + lingkungan.get("PYTHONPATH", "")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm",
                    str(akar / "MatchYouTile.spec")], cwd=akar, env=lingkungan, check=True)
