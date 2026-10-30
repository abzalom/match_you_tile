# Titik lanjut Match You Tile

Disimpan pada 30 Oktober 2026 atas permintaan pengguna sebelum mematikan komputer.

## Mulai dari sini

- Panduan kerja: `instruksi.md`.
- Konsep pengguna: `konsep_game.txt`.
- Riwayat keputusan dan perubahan: `dokumentasi/RIWAYAT_PENGEMBANGAN.md`.
- Panduan menjalankan: `dokumentasi/PANDUAN.md`.
- Game tetap Python/Pygame-CE. Kivy/Android baru dibahas, belum dimigrasikan.

## Status terakhir

Perbaikan terakhir adalah **Cocok Otomatis saat tersisa satu slot dan keenam
kartu di slot semuanya berbeda**. Bantuan mengambil dua pelengkap dari papan
untuk mencocokkan kartu **paling kanan**, termasuk kartu tertutup, tanpa kalah
di tengah proses. Bantuan diselesaikan sebagai satu transaksi; slot model tidak
pernah memuat delapan kartu. Dalam kondisi lain prioritas tetap jumlah terbanyak,
lalu kelompok paling kiri bila seri. Animasi bantuan tetap ada. Jika pelengkap
tidak tersedia, papan/slot/skor tidak diubah.

File yang diperbaiki: `permainan/model.py`, `permainan/antarmuka.py`,
`assets/bahasa.json`, pengujian model/antarmuka, dan dokumentasi.

**Validasi terakhir: 72 pengujian lulus.**

`dist/MatchYouTile.exe` sudah dibangun ulang setelah perbaikan. Build selesai,
tetapi menjalankan executable terbaru ditolak Windows dengan pesan:
`An Application Control policy has blocked this file.` Jangan menganggap versi
terbaru sudah lolos uji executable. Versi sebelum perbaikan pernah lolos uji
executable langsung; itu tidak membuktikan versi terbaru dapat dijalankan.

Pemeriksaan paket melalui sumber Python berhasil. Laporan:
`dist/hasil_uji_sumber_perbaikan.json`. Laporan lama
`dist/hasil_uji_paket.json` berasal dari build sebelumnya.

## Perintah penting

```powershell
python main.py
python -m unittest discover -s tests -q
python audit_level.py
python peralatan/buat_exe.py
python main.py --uji-paket dist/hasil_uji_sumber.json
```

Build memakai `MatchYouTile.spec`, PyInstaller lokal di `.build_tools`, dan
`requirements-build.txt`. Hasil satu file: `dist/MatchYouTile.exe` (sekitar 60 MB,
Windows 64-bit). Penjelasan: `dokumentasi/BUILD_WINDOWS.md`.

## Data yang harus dipertahankan

- Saat menjalankan Python: `data/progres.json`, `data/pengaturan.json`, `data/audio.json`.
- Saat menjalankan EXE: `%LOCALAPPDATA%\MatchYouTile\` dengan nama berkas sama.
- Build tidak menyertakan data pribadi dari folder `data/`.
- Jangan menjalankan `peralatan/buat_audio.py` tanpa alasan: skrip menimpa WAV
  sintetis yang dibuatnya. Lagu impor WAV tidak ditimpa oleh skrip tersebut.

## Pekerjaan tersisa

Tidak ada permintaan fitur baru yang tertunda. Pengguna menghentikan sesi untuk
melanjutkan nanti. Baca permintaan berikutnya sebelum memulai perubahan baru.
Hal yang belum diverifikasi: eksekusi build EXE terbaru karena Application Control.
Jangan menonaktifkan atau melewati kebijakan keamanan tersebut.
