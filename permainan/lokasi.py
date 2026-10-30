"""Lokasi aset dan data persisten saat berjalan sebagai Python atau executable."""

import os
from pathlib import Path
import sys

AKAR = Path(__file__).resolve().parent.parent


def folder_data():
    if getattr(sys, "frozen", False):
        lokal = os.environ.get("LOCALAPPDATA")
        return (Path(lokal) if lokal else Path.home() / "AppData" / "Local") / "MatchYouTile"
    return AKAR / "data"
