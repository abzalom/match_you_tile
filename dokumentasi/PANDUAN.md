# Match You Tile — Kebun Buah

Game puzzle 2D Python/Pygame-CE berdasarkan `konsep_game.txt`. Gambar kartu memakai
24 SVG buah, sayuran, bumbu, dan makanan di `assets/svg/`. Aset lama tetap disimpan.
Panel, tombol, kartu, dan ornamen digambar dengan Pygame. Lihat `ASET_SVG.md`
untuk daftar dan cara mengedit ikon.

## Menjalankan

Gunakan Python 3.10 atau lebih baru dari folder proyek:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Tampilan memakai kanvas potret 540 × 960 seperti layar HP. Jendela dapat diubah
ukurannya; gambar dan koordinat klik disesuaikan dengan rasio kanvas. Ini aplikasi
desktop Python, belum berupa paket Android/iOS.
Ikon jendela menggunakan `assets/logo.png`, dipaskan secara proporsional pada
bidang persegi. `assets/logo.ico` juga tersedia dalam tujuh ukuran (16–256 piksel)
untuk ikon executable Windows saat proses pengemasan nantinya. PNG asli dipertahankan.

Latar menu memakai `assets/BG_menu_utama.jpeg`. Setiap mulai level, termasuk
mengulang level aktif, latar game diundi dari JPEG `BG_` lainnya. Semua latar
game digunakan sekali per putaran acak sebelum diundi ulang, dan gambar yang
sama tidak muncul berturut-turut. Gambar memenuhi layar tanpa mengubah proporsi;
kelebihan tepi dipotong di tengah. Area teks diberi pelat transparan agar terbaca.
Judul menu menggunakan `assets/Title.png`, diperkecil secara proporsional ke
lebar 480 piksel dan dimuat sekali saat aplikasi dimulai.
Menu utama menampilkan judul gambar, tombol `Level N / Kesulitan`, Pengaturan,
dan speaker, tanpa kartu dekoratif atau petunjuk tambahan. Pengaturan menyediakan
delapan bahasa serta modal volume dengan tiga slider dan tombol minus/plus.
Lihat `PENGATURAN.md` untuk panduan lengkap.

## Cara bermain

- Klik Mulai / Level untuk memainkan level aktif. Level sebelumnya tidak dapat
  dimainkan lagi setelah diselesaikan.
- Klik kartu dengan luas tertutup paling banyak 15%, termasuk tepat 15%.
  Jika lebih, ambil kartu penutup terlebih dahulu. Luas dihitung dari gabungan
  semua kartu di depan, tanpa menghitung area irisan yang sama dua kali.
- Tumpukan memakai delapan siluet: plus, X, gunung, lingkaran, spiral, gelombang,
  pulau (beberapa kelompok kecil), dan acak bebas. Plus/X memiliki peluang lebih
  kecil, dan bentuk sebelumnya tidak dipakai lagi saat mulai atau mengulang level.
- Kartu papan berukuran 80 × 90, slot 68 × 86, dan ikon hingga 60 × 60,
  dengan sisi bawah bertingkat dan
  sorotan tepi untuk kesan 2.5D.
- Kartu di bawah bergeser secara diagonal; ikon buah kecil di sudutnya membantu
  mengenali kartu berikutnya. Kartu yang tertutup lebih dari 15% digambar lebih redup.
- Tujuh slot di atas papan diisi **dari kiri ke kanan**. Buah sejenis disisipkan
  setelah kelompok sejenis, sehingga tetap bersebelahan.
- Tiga gambar sama menghilang. Nilai dasar 100 per kartu: satu kelompok +300.
  Kecocokan manual berikutnya dalam lima detik menaikkan pengali hingga x5.
  Bantuan memutus rantai. Timer dijeda saat membuka modal pengaturan atau
  konfirmasi. Lihat `KOMBO.md` untuk aturan dan tabel poin.
- Tujuh slot penuh setelah pemeriksaan kecocokan berarti kalah. Jika kartu ketujuh
  melengkapi tiga buah sama, kecocokan dihitung dahulu sehingga tidak kalah.
- Semua kartu habis berarti menang dan membuka level berikutnya.
- Slot berkedip setiap penambahan yang menyisakan tiga slot atau kurang
  (mulai empat kartu yang masih berada di slot).
- Tombol **Menu** di kiri atas atau **Esc** membuka konfirmasi saat masih bermain.
  Pilih **Lanjut bermain** atau tekan Esc untuk membatalkan. **Ya, keluar**
  menghitung permainan sebagai kalah dan kembali ke menu; level aktif tidak berubah.
  Setelah menang/kalah, kembali ke menu tidak memerlukan konfirmasi tambahan.

## Bantuan

Bantuan bebas dipakai selama permainan berlangsung:

| Tombol | Pintasan | Perilaku |
| --- | --- | --- |
| Kembali | Z | Mengembalikan kartu terakhir yang masih ada di slot ke posisi semula |
| Cocok | C | Melengkapi kelompok terbanyak di slot; jika seri, kelompok paling kiri |
| Acak | R | Mengacak buah yang masih di papan, tanpa mengubah jumlah masing-masing buah |

Cocok dapat mengambil kartu tertutup. Jika tersisa satu slot dan keenam kartu
di slot berbeda, kelompok kartu paling kanan diprioritaskan. Bantuan mengambil
dua pelengkap dan menyelesaikan kecocokan sebagai satu transaksi, tanpa memicu
kalah di tengah proses atau menyimpan kartu melebihi kapasitas tujuh slot.
Pada kondisi lain, prioritas tetap kelompok terbanyak lalu kelompok paling kiri.
Kartu bantuan bergerak halus dari papan ke kelompoknya di slot,
kemudian kelompok cocok dimusnahkan (620 ms total). Kartu lain baru merapat
ke kiri setelah pemusnahan selesai. Kembalikan menggerakkan kartu dari slot
ke posisi asal di papan selama 420 ms dengan percepatan dan perlambatan halus.
Tiga tombol bantuan hanya menampilkan ikon; pintasan Z/C/R tetap berfungsi.
Kartu yang sudah musnah tidak bisa dikembalikan. Bantuan nonaktif setelah kalah.

Acak menggunakan cabang bias berpeluang 65%: jika ada buah yang sesuai slot di
papan, sedikitnya satu buah yang sesuai dibuat terlihat di atas. Pengacakan biasa
pada 35% sisanya masih mungkin menghasilkan kecocokan secara alami. Jadi 65%
adalah peluang cabang bias, bukan batas persentase hasil cocok keseluruhan.

## Animasi

- Perpindahan menu ke game dan kembali menggunakan pergeseran halaman 360 ms.
- Setiap mulai, mengulang, atau melanjutkan level menampilkan intro level selama
  1,4 detik setelah transisi halaman. Banner level bergeser masuk, berhenti sejenak,
  lalu bergeser keluar. Input kartu dan bantuan aktif setelah intro selesai.
  Latar dan panel intro memakai transparansi 70% (opasitas 30%); teks dan ikon
  tetap solid agar mudah dibaca.
- Kartu pilihan biasa bergerak selama 420 ms dengan percepatan halus.
- Kelompok pilihan biasa bergerak ke slot dahulu, lalu mengecil hingga hilang (620 ms total).
- Setelah kelompok benar-benar hilang, kartu slot yang tersisa baru bergeser
  ke kiri (420 ms). Klik baru tetap diterima; gerakan menuju slot menunggu giliran
  jika ruangnya masih dipakai animasi pemusnahan atau perapatan sebelumnya.
- Pengacakan memindahkan gambar buah sejenis antara posisi asal dan tujuan.
- Pemain dapat terus mengklik kartu selama animasi. Setiap pilihan langsung
  memperbarui model dan mempunyai gerakan sendiri; kartu yang berubah posisi slot
  diarahkan ulang dari posisi visual saat ini tanpa melompat.
- Hitbox dihitung ulang setiap klik, termasuk beberapa klik dalam satu frame.
  Kartu yang sudah dipilih tidak dapat dipilih lagi saat masih terbang.
- Alat bantu menunggu gerakan kartu selesai agar pengacakan/pengembalian tidak
  berbenturan dengan pilihan baru. Menu dapat dibuka selama gerakan kartu;
  perpindahan halaman menahan input selama 360 ms. Jendela tetap dapat ditutup.

## Level dan progres

Ada 1.000 level dengan 9–30 tumpukan acak, tiga lapis, dan total 27–90 kartu.
Level 1–3 memakai 3 jenis gambar. Mulai level 4, jumlah jenis bertambah di dalam
setiap kategori: Mudah 5–7, Sedang 8–10, Sulit 11–13, dan Level Gila 12–18.
Jumlah kartu dan kepadatan ikut meningkat; setelah Level Gila ada jeda tantangan.
Kesulitan berombak per sepuluh level dengan tren meningkat. Rumus, contoh level,
hasil audit, dan opsi agen setelah publikasi tersedia di `KESULITAN_LEVEL.md`.
Syarat mencocokkan tetap tiga kartu sejenis; bantuan tetap bebas digunakan.
Pembagian level: 1–333 Mudah, 334–666 Sedang, dan 667–1000 Sulit. Setiap kelipatan
10 menjadi Level Gila dengan tantangan tambahan. Nama kategori terlihat di intro
dan di bagian atas layar selama permainan berlangsung.

Awalnya hanya level 1 yang terbuka. Menang membuka satu level selanjutnya.
Menu hanya menampilkan tombol Mulai untuk level aktif, tanpa pemilih level.
Level sebelumnya tidak dapat dibuka lagi; ketika kalah, level aktif dapat diulang.
Kembali ke menu setelah menang langsung menampilkan level berikutnya.
Level aktif disimpan otomatis ke `data/progres.json` menggunakan nama kunci lama
`level_terbuka`, sehingga progres versi sebelumnya tetap terbaca. Folder dibuat
saat kemenangan pertama. Skor direset setiap mulai level. Jika penyimpanan gagal,
progres masih berlaku selama sesi dan pesan kegagalan ditampilkan.

Papan awal selalu memiliki setidaknya satu solusi tanpa bantuan. Acak mempertahankan
jumlah setiap buah tetapi tidak menjamin urutan solusi tanpa bantuan setelahnya.
Musik latar dan sepuluh efek suara tersedia. Tombol speaker membuka modal volume
game, sistem, dan musik, beserta tombol bisu. Pilihan disimpan otomatis. Rincian aset, volume, dan
cara membuat ulang suara ada di `AUDIO.md`. GIF belum dianimasikan.

## Pengujian

```powershell
python -m unittest discover -s tests -v
```

Pengujian meliputi tujuh slot dan kecocokan pada slot terakhir, prioritas dari kiri,
irisan antartumpukan, solusi semua level, batas dan siluet posisi kartu, penyimpanan
progres, level terkunci, animasi bantuan, klik cepat tanpa menunggu, pengalihan
gerakan tanpa melompat, serta perpindahan menu. Tes tampilan memakai driver dummy dan berkas
progres sementara sehingga tidak membuka jendela atau mengubah progres pemain.
