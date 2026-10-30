# Executable Windows

Hasil build adalah **`dist/MatchYouTile.exe`**, satu file untuk Windows 64-bit.
Python, library Pygame, aset, SVG, terjemahan, musik WAV, dan ikon Windows
dikemas dalam executable. Komputer pemain tidak perlu memasang Python.

Klik dua kali executable untuk bermain. Ekstraksi internal saat startup dapat
membuat pembukaan pertama lebih lambat daripada menjalankan sumber Python.

## Data pemain

Versi `.exe` menyimpan progres, bahasa, dan volume di:

```text
%LOCALAPPDATA%\MatchYouTile\
  progres.json
  pengaturan.json
  audio.json
```

Berkas data dibuat ketika dibutuhkan, bukan di folder ekstraksi sementara.
Data pribadi dari folder `data/` proyek tidak disertakan dalam paket. Karena itu
versi `.exe` baru dimulai dari level 1 bila belum memiliki progres tersendiri.
Sumber Python tetap memakai folder `data/` proyek seperti sebelumnya.

Logo `assets/logo.ico` tertanam sebagai ikon executable dan `logo.png` dipakai
untuk ikon jendela. Nama game pada `Title.png` tetap berupa gambar asli.
Mandarin/Jepang memakai font CJK sistem sebagaimana dijelaskan di PENGATURAN.md;
font Microsoft Windows tidak disalin ke paket.

## Membuat ulang

Pada Windows 64-bit dengan Python dan dependensi proyek:

```powershell
python -m pip install -r requirements.txt
python -m pip install --target .build_tools -r requirements-build.txt
python peralatan/buat_exe.py
```

`MatchYouTile.spec` menentukan build satu file tanpa jendela konsol, aset runtime,
ikon, dan pengecualian library yang tidak digunakan. `peralatan/buat_exe.py`
menempatkan cache build di proyek. Berkas sementara ada di `build/`, hasil di
`dist/`. Hanya kirim `MatchYouTile.exe` ke pemain; folder build tidak diperlukan.

## Pemeriksaan paket

```powershell
python -m unittest discover -s tests -q
.\dist\MatchYouTile.exe --uji-paket .\dist\hasil_uji_paket.json
```

Mode uji memakai driver video/audio dummy dan data sementara. Laporan JSON
memeriksa ikon, 24 kartu SVG, delapan bahasa, modal bahasa/volume, audio, level
1000, dan konfirmasi keluar. Mode ini tidak membuka jendela atau mengubah progres
pemain. Pada PowerShell, tunggu proses selesai sebelum membaca JSON jika shell
langsung kembali karena executable menggunakan mode GUI.
