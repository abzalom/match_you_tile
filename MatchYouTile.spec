# Build satu file Windows; tidak menyertakan progres, pengaturan, atau MP3 sumber.
from pathlib import Path

akar = Path(SPECPATH)
ekstensi = {".png", ".jpg", ".jpeg", ".svg", ".json", ".wav"}
aset = [(str(p), str(p.parent.relative_to(akar)))
        for p in (akar / "assets").rglob("*") if p.is_file() and p.suffix.lower() in ekstensi]

a = Analysis(
    [str(akar / "main.py")],
    pathex=[str(akar)],
    binaries=[],
    datas=aset,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["numpy", "PIL", "tkinter", "matplotlib", "scipy", "pandas", "IPython"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="MatchYouTile",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(akar / "assets" / "logo.ico"),
)
