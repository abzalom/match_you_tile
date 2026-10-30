# Riwayat pengembangan dan keputusan

Catatan sesi sampai 30 Oktober 2026. Ini rangkuman menyeluruh keputusan teknis,
permintaan, perubahan, dan hasil; bukan ekspor transkrip percakapan kata per kata.
Kode dan aset tersimpan langsung di folder proyek. Titik lanjut singkat ada di
`../LANJUTKAN.md`.

## Awal proyek

Pengguna meminta pembacaan lingkungan kerja dan menetapkan `instruksi.md` sebagai
instruksi proyek. Konsep yang benar bernama `konsep_game.txt`; penulisan
`konser_game.txt`/`koosep` dalam chat mengacu pada berkas tersebut. Proyek berupa
game puzzle 2D pencocokan tiga kartu, terinspirasi Tap Tile/mahjong.

Implementasi menggunakan Python 3.14.2 dan Pygame-CE 2.5.8 pada Windows 64-bit.
Kode modular/OOP, penamaan Indonesia, komentar pada logika kompleks, dan
dokumentasi terpisah mengikuti permintaan pengguna.

## Perjalanan perubahan konsep

1. Versi pertama memakai sembilan slot dan urutan kanan ke kiri, delapan level,
   aset buah GIF/PNG, menu, skor, menang/kalah, serta tiga bantuan.
2. Revisi konsep mengubah urutan ke kiri ke kanan, posisi tumpukan menjadi acak,
   tampilan potret, pratinjau buah bawah, animasi, dan pembukaan level berurutan.
3. Revisi berikutnya mengurangi kapasitas menjadi **tujuh slot**, memperbolehkan
   klik cepat selama animasi, memperbesar kartu, menambah sisi bawah timbul 2.5D,
   serta pola plus/X/gunung.
4. Pengguna melarang kembali ke level sebelumnya. Pemilih level dihapus, tombol
   Play selalu membuka level aktif; level aktif dapat diulang ketika kalah.
5. Kemudian pengguna meminta SVG buah/sayur/bumbu/makanan, tombol lucu, latar JPEG,
   judul PNG, pengaturan, audio, kombo, dan executable seperti rincian di bawah.

Keputusan terbaru menggantikan keputusan awal yang bertentangan. Jangan kembali
ke sembilan slot, kanan ke kiri, atau pemilih level lama.

## Aturan permainan sekarang

- Tujuh slot di atas papan, diisi **kiri ke kanan**. Kartu sejenis bersebelahan.
- Tiga kartu sejenis dimusnahkan. Nilai dasar 100 per kartu, 300 per kelompok.
- Kalah bila tujuh slot penuh setelah pemeriksaan kecocokan. Menang jika semua
  kartu dimusnahkan.
- Peringatan visual berkedip ketika penambahan menyisakan tiga slot atau kurang.
- Kartu boleh diklik jika luas tertutup **paling banyak 15%**, termasuk tepat 15%.
  Jika lebih, kartu penutup harus diambil dahulu. Luas memakai gabungan seluruh
  penutup di depan, tanpa menghitung irisan berulang.
- Papan memakai delapan bentuk: plus, silang, gunung, lingkaran, spiral,
  gelombang, pulau, dan acak bebas. Plus/silang lebih jarang. Bentuk tidak
  berulang langsung saat mulai/mengulang level.
- Kartu papan 80 x 90, slot 68 x 86, gambar hingga 60 x 60; pratinjau bawah 20 x 20.
- Kanvas potret 540 x 960, dapat diubah ukuran dengan konversi koordinat klik.

## Bantuan dan perbaikan terakhir

Tiga bantuan di bawah layar memakai **ikon saja**, dengan pintasan Z/C/R.
Bantuan bebas dipakai, tidak dibatasi jumlah atau biaya.

- **Kembalikan (Z):** kartu terakhir yang masih di slot kembali ke posisi asal.
  Kartu yang sudah musnah tidak bisa dikembalikan.
- **Cocok Otomatis (C):** utamakan jenis terbanyak di slot, lalu kelompok paling
  kiri bila seri. Boleh mengambil kartu tertutup dari seluruh papan.
- **Pengecualian terakhir:** jika hanya satu slot kosong dan keenam kartu di slot
  berbeda, prioritaskan **paling kanan**. Ambil dua pelengkap dan musnahkan
  kelompok secara atomik, tanpa kalah sementara atau slot kedelapan.
- Jika pelengkap tidak cukup, bantuan gagal tanpa memindahkan sebagian kartu.
- **Acak (R):** acak gambar di papan sambil mempertahankan jumlah tiap jenis dan
  isi slot. Cabang berbias 65% memastikan gambar sejenis slot muncul pada kartu
  yang dapat dipilih, bila ada di papan. Cabang biasa masih bisa cocok alami.

Pengguna sempat meminta perpindahan bantuan tanpa animasi, lalu meminta kembali
animasi halus untuk Cocok/Kembalikan. **Keadaan terkini memakai animasi bantuan.**
Kartu lain harus menunggu tiga kartu musnah dahulu sebelum bergeser ke kiri.
Perbaikan transaksi otomatis terakhir menyatukan aturan model dan antarmuka agar
tidak terjadi kalah sementara saat bantuan mengambil dua kartu.

## Animasi, intro, dan keluar ke menu

- Pergeseran halaman sekitar 360 ms; kartu berpindah halus sekitar 420 ms.
- Kelompok cocok mencapai slot lalu mengecil hingga hilang, total sekitar 620 ms.
  Perapatan slot dimulai sesudah pemusnahan, sekitar 420 ms.
- Klik kartu cepat tetap diproses. Gerakan per kartu dapat diarahkan ulang dari
  posisi visual sekarang; gerakan slot dapat menunggu ruang visual yang tersedia.
- Saat mulai, ulang, atau lanjut level tampil intro sekitar 1,4 detik. Latar
  dan panel splash **70% transparan**, teks/ikon solid.
- Tombol Menu dan Esc saat bermain membuka konfirmasi: keluar dihitung kalah.
  Batal/Lanjut bermain mempertahankan papan; setuju kembali ke menu, level aktif
  tidak naik. Setelah menang/kalah tidak memerlukan konfirmasi tambahan.

## Level dan kesulitan: keadaan akhir

Awalnya hanya delapan level. Pengguna meminta diperluas menjadi 1.000, dibagi
tiga kategori dan diselingi Level Gila. Formula berada di `permainan/level.py`.

| Rentang | Kategori | Jenis gambar terkini |
| --- | --- | --- |
| 1–3 | Pengenalan dalam Mudah | 3 |
| 4–333, kecuali kelipatan 10 | Mudah | 5–7 |
| 334–666, kecuali kelipatan 10 | Sedang | 8–10 |
| 667–1000, kecuali kelipatan 10 | Sulit | 11–13 |
| Setiap kelipatan 10 | Gila | 12–18 |

Sebelumnya pengguna meminta jumlah tetap Mudah 4/Sedang 6/Sulit 8/Gila 10,
kemudian meminta jumlah jenis dinaikkan dan kerumitan disesuaikan. Rentang
bertahap pada tabel adalah keputusan **terbaru**, bukan jumlah tetap lama.

Jumlah kartu 27–90, tumpukan 9–30 dengan tiga lapis; tidak naik tanpa batas
mengikuti nomor level. Kepadatan meningkat, kesulitan berombak per sepuluh level,
Level Gila lebih berat dan sesudahnya kembali ke profil biasa. Kategori tampil
pada tombol Play, intro, dan HUD. Semua jenis profil dijamin muncul, dalam
kelipatan tiga.

Indeks kesulitan adalah perkiraan desain, bukan peluang kalah. Karena bantuan
bebas, tantangan terutama terasa tanpa bantuan. Audit 1.000 papan berbenih
tetap lulus: muat di layar dan memiliki solusi awal. Laporan
`dokumentasi/profil_level.csv`, skrip `audit_level.py`, penjelasan
`dokumentasi/KESULITAN_LEVEL.md`. Belum ada telemetry pemain atau kalibrasi manusia.

Pengguna bertanya mengenai agen pembuat level setelah publikasi. Generator lokal
sudah membuat level otomatis offline. Agen AI/backend/unduhan konfigurasi belum
diimplementasikan. Tidak ada sub-agen yang digunakan untuk mengerjakan proyek.

## Aset gambar

- `assets/svg/` berisi 24 ilustrasi SVG asli: enam buah, enam sayuran, enam bumbu,
  enam makanan. `katalog.json` menyelang-seling kategori.
- Buah: apel, pisang, jeruk, anggur, semangka, nanas.
- Sayur: wortel, brokoli, terong, tomat, jagung, kubis.
- Bumbu: cabai, bawang putih, bawang merah, jahe, kunyit, kayu manis.
- Makanan: nasi goreng, sate, telur goreng, donat, roti, mi.
- SVG dimuat oleh SDL_image/Pygame, tanpa library tambahan. Ikon dan latar tombol
  pastel bergaya lucu/tersenyum ada di `assets/svg/tombol/`, termasuk gear/bahasa/audio.
- Latar menu **`BG_menu_utama.jpeg`**. Lima JPEG `BG_` lainnya dipilih dengan
  undian acak untuk tiap mulai/ulang level. Semua dipakai per putaran, tanpa
  pengulangan langsung. Gambar memakai cover proporsional dan pelat kontras teks.
- Judul menu memakai **`Title.png`**, bukan tulisan biasa.
- Semua kartu dekoratif menu telah dihapus. Menu kini berisi judul gambar,
  Play dengan level/kesulitan, Pengaturan, dan pintasan speaker.
- Ikon aplikasi berasal dari **`logo.png`**; `logo.ico` tujuh ukuran 16–256 px
  dibuat untuk Windows. PNG asli dipertahankan.

## Pengaturan dan bahasa

Pengaturan tersedia di **menu utama dan layar permainan**. Modal bertingkat:
Pengaturan → Bahasa atau Volume, Kembali/Esc menutup satu lapisan. Klik tidak
menembus modal. Menutup Pengaturan saat bermain tidak mengulang papan/skor.

Delapan bahasa: Indonesia, Inggris, Spanyol, Prancis, Jerman, Portugis,
Mandarin, Jepang. Semua teks UI/pesan dinamis diterjemahkan; logo nama merek
tetap gambar. Katalog `assets/bahasa.json`, kode `permainan/bahasa.py`.
Mandarin/Jepang memakai font CJK sistem (YaHei pada Windows pengembangan);
font Windows tidak dibundel untuk redistribusi.

Volume independen: game (kartu/bantuan), sistem (klik/intro/hasil/aksi ditolak),
latar (musik). Masing-masing 0–100%, slider drag atau -/+ 5%. Perubahan langsung
berlaku, disimpan saat lepas drag atau tekan tombol. Status bisu terpisah dari
nilai slider. Katalog modal di `permainan/pengaturan.py`.

## Audio: riwayat dan keadaan akhir

Awalnya dibuat dua musik sintetis dan sepuluh efek WAV dengan pustaka standar.
Skrip: `peralatan/buat_audio.py`; aset di `assets/audio/`. Lalu pengguna memberikan
`assets/audio/ai generated musik/Paths_Through_Silver_Leaves.mp3`.

MP3 dikonversi menjadi WAV pada folder sama: PCM 16-bit stereo 44100 Hz,
sekitar 145,42 detik, 25.652.780 byte. MP3 asli tetap disimpan.

**Keadaan akhir:** WAV `Paths_Through_Silver_Leaves` digunakan di menu dan game,
berlanjut tanpa diulang dari awal saat pindah halaman/level, termasuk layar hasil.
Musik sintetis lama tetap tersimpan tetapi tidak dipakai. Pemetaan ada pada
`AudioPermainan.berkas_musik`.

Atas permintaan pengguna, **peringatan slot dan kartu musnah tidak bersuara**.
Efek `cocok`/`peringatan` tidak dimainkan walau WAV aslinya tetap tersimpan.
Efek lain, termasuk bunyi kartu masuk, bantuan, klik, intro, menang/kalah, tetap
aktif sesuai volume. Jangan menambahkan kembali suara pemusnahan/slot.

## Kombo

- Kecocokan manual beruntun dalam lima detik menaikkan pengali sampai x5.
- Poin kelompok: 300, 600, 900, 1200, lalu maksimal 1500.
- Indikator pengali/bar waktu, toast poin, dan kombo terbaik pada hasil.
- Bantuan berhasil memutus rantai; kecocokan otomatis hanya mendapat 300 poin.
- Modal pengaturan atau konfirmasi keluar menjeda timer. Klik cepat tetap aktif.
- Aturan lengkap `dokumentasi/KOMBO.md`; jam monoton model dapat diinjeksi untuk tes.

## Android/Kivy dan EXE

Pengguna hanya bertanya tentang APK/AAB serta migrasi Pygame ke Kivy dan meminta
pertanyaan itu dijawab saja. **Tidak ada migrasi Kivy atau build Android.**

Pengguna kemudian meminta EXE Windows. PyInstaller 6.22.3 dipasang lokal di
`.build_tools`. Spec `MatchYouTile.spec`, skrip `peralatan/buat_exe.py`.
Build single-file tanpa konsol dengan ikon dan semua aset runtime. Dependensi
tidak terpakai dikecualikan. Data pemain/MP3 sumber tidak disertakan.

`dist/MatchYouTile.exe` sekitar 60 MB, Windows 64-bit, tidak perlu Python terpasang.
Saat berjalan lewat Python, data ada di `data/`; lewat EXE data di
`%LOCALAPPDATA%\MatchYouTile\`. Berkas: progres.json, pengaturan.json, audio.json.

Build EXE pertama lolos pengujian langsung `--uji-paket`. Setelah perbaikan bantuan
darurat terakhir, build ulang **berhasil**, tetapi peluncuran versi baru diblokir
Application Control Windows. Tidak dicoba melewati kebijakan itu. Pemeriksaan
paket dari kode sumber berhasil. Selalu bedakan build berhasil, tes sumber lulus,
dan tes executable yang belum lolos karena kebijakan lingkungan.

## Validasi terakhir dan melanjutkan

**72 tes lulus** setelah perbaikan bantuan otomatis. Uji paket melalui sumber
meliputi ikon, 24 SVG, 8 bahasa, audio, level 1000, modal, konfirmasi keluar.

```powershell
python main.py
python -m unittest discover -s tests -q
python audit_level.py
python peralatan/buat_exe.py
python main.py --uji-paket dist/hasil_uji_sumber.json
```

Dokumentasi tambahan: PANDUAN.md, ARSITEKTUR.md, ASET_SVG.md, TOMBOL_SVG.md,
PENGATURAN.md, AUDIO.md, KOMBO.md, KESULITAN_LEVEL.md, BUILD_WINDOWS.md.

Pengguna meminta menyimpan riwayat sebelum mematikan komputer dan melanjutkan
nanti. Tidak ada permintaan fitur aktif lain. Jangan mematikan komputer melalui
alat; pengguna hanya menyampaikan rencananya sendiri.
