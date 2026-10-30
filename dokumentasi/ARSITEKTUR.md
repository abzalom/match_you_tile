# Struktur, variabel, fungsi, dan alur kerja

## Susunan proyek

```text
main.py                  titik masuk aplikasi
audit_level.py           validasi 1.000 papan dan ekspor profil CSV
permainan/
  model.py               aturan permainan dan sebaran kartu
  level.py               ProfilLevel dan rumus kesulitan level 1–1000
  antarmuka.py           tampilan potret, animasi, dan kendali
  animasi.py             interpolasi gerakan per kartu
  latar.py               muat JPEG dan undi latar level tanpa pengulangan langsung
  aset.py                baca katalog dan muat SVG ke memori
  audio.py               musik, efek suara, jadwal bunyi, dan preferensi bisu
  bahasa.py              katalog terjemahan dan preferensi bahasa
  pengaturan.py          modal bertingkat, pilihan bahasa, dan slider volume
                         serta cache ikon dan latar tombol melalui AsetTombol
  progres.py             baca/tulis level yang sudah terbuka
assets/                  gambar asli yang dipertahankan
  audio/                 dua musik dan sepuluh efek WAV
  svg/                   24 ikon SVG dan katalog.json
tests/                   pengujian model, tampilan, dan progres
dokumentasi/             panduan penggunaan dan arsitektur ini
data/progres.json        dibuat saat kemenangan; tidak dilacak Git
data/pengaturan.json     pilihan bahasa, terpisah dari progres
data/audio.json          volume tiga kategori dan bisu
requirements.txt         dependensi runtime
peralatan/buat_audio.py  sintesis WAV orisinal, tanpa library tambahan
instruksi.md             instruksi kerja proyek
konsep_game.txt          konsep dari pemilik proyek
```

## Data utama

`Kartu` menyimpan `nomor` unik sekaligus urutan gambar, `jenis` sebagai indeks
buah, `tumpukan` sebagai identitas tumpukan, `lapisan` sebagai tinggi asal,
`lokasi` (`papan`, `slot`, `musnah`), serta posisi `x` dan `y` pada kanvas.
Ukuran kartu papan adalah 80 × 90, ditetapkan oleh `LEBAR_KARTU` dan
`TINGGI_KARTU` di model; tampilan dan pemeriksaan irisan memakai konstanta sama.
Kartu yang lebih besar nomornya tampil di depan. Sisi bawah visual bertingkat
setinggi delapan piksel tidak menambah hitbox kartu.

`Permainan` menyimpan `level`, `kolom` (parameter jumlah tumpukan, bukan layout),
`jumlah_jenis`, `kartu`, `slot` (indeks nol di kiri), `riwayat`, `skor`, `status`,
`pesan`, `bentuk` (salah satu dari delapan siluet), penghitung `peringatan`, dan
`terakhir_musnah`. `kapasitas` bernilai tujuh, dengan peringatan pada kapasitas
dikurangi tiga. `acak` dapat menerima
`random.Random` berbenih untuk mereproduksi papan.

`Progres` menyimpan `berkas`, `level_terbuka`, dan `peringatan`. Penyimpanan memakai
berkas sementara pada folder yang sama lalu mengganti JSON tujuan. Nilai progres
dibatasi 1–1000. Berkas rusak dipulihkan menjadi level 1; kegagalan tulis tidak
menghentikan permainan. `level_terbuka` berarti level aktif yang belum dilewati;
`selesaikan(level)` hanya menerima level aktif tersebut. Nama kunci JSON tetap
dipertahankan agar progres versi lama masih terbaca.

`Aplikasi` menyimpan jendela `layar`, bidang potret `kanvas`, pembatas FPS `jam`,
`huruf`, `katalog_aset`, `gambar_aset`, `permainan`, `progres`, `halaman`, `level`, `tombol`, dan
`area_kartu`. `kilat_sampai` dan `efek_sampai` adalah batas waktu efek.
`animasi` adalah dictionary nomor kartu ke `GerakanKartu`. Setiap gerakan
menyimpan kotak `awal`/`akhir`, `jenis`, `tertutup`, waktu `mulai`, `durasi`, dan
penanda `musnah`, dan `sebelumnya` untuk melanjutkan tahap gerakan sebelumnya
selama tahap baru belum dimulai. `potret(waktu)` menghasilkan posisi interpolasi dengan
smoothstep; `selesai(waktu)` menentukan kapan gerakan dibersihkan.
`transisi` berisi gambar halaman lama, waktu mulai, durasi, dan arah pergeseran.
`intro` menyimpan waktu mulai dan durasi banner pembuka level. `konfirmasi_menu`
menandai dialog keluar yang menahan input papan dan bantuan. Membatalkan dialog
mempertahankan permainan; menyetujui mengubah status menjadi kalah tanpa membuka
level berikutnya. `kembali_menu()` membersihkan gerakan dan mengganti halaman.
`slot_siap` adalah waktu slot siap menerima gerakan berikutnya. Saat cocok,
kartu lain menuju susunan sebelum pemusnahan terlebih dahulu. Perapatan ke kiri
dimulai setelah 620 ms pemusnahan selesai, lalu berlangsung 420 ms. Klik baru
langsung mengubah model, sedangkan gerakan slotnya dijadwalkan setelah tahap yang
sedang berjalan. Rantai `sebelumnya` menjaga lintasan lama tetap terlihat selama
menunggu, termasuk saat klik cepat menargetkan ulang kartu yang belum merapat.
Kombo memakai jam monoton yang dapat diganti pada pengujian. Model menghitung
pengali, kedaluwarsa, dan bonus; antarmuka menampilkan timer/poin serta menjeda
timer saat modal aktif. Bantuan otomatis secara eksplisit ditandai agar tidak
mendapat kombo. Rincian variabel dan aturan ada di `KOMBO.md`.

## Fungsi model dan progres

| Fungsi | Tujuan |
| --- | --- |
| `_buat_papan()` | Mengisi dalam kelompok tiga; urutan nomor terbalik menjadi salah satu solusi |
| `_acak_posisi()` | Pilih dari delapan siluet berbobot, hindari bentuk sebelumnya, lalu sebar dan geser lapisan |
| `teratas(kartu)` | Izinkan kartu papan jika total bagian tertutup tidak lebih dari 15% |
| `bagian_tertutup(kartu)` | Hitung gabungan luas irisan kartu depan dengan sapuan pita vertikal |
| `pilih(kartu, bantuan=False)` | Validasi, sisipkan kelompok, musnahkan tiga buah, hitung skor, periksa menang/kalah |
| `kembalikan()` | Pulihkan pilihan terakhir yang belum musnah ke posisi asal |
| `rencana_otomatis()` | Tentukan pelengkap; kondisi darurat enam kartu unik memprioritaskan kanan |
| `cocok_otomatis()` | Selesaikan kelompok secara atomik tanpa keadaan slot penuh sementara |
| `acak_ulang()` | Acak jenis buah di papan dan terapkan cabang bias 65% |
| `Progres.selesaikan(level)` | Buka level berikutnya dan simpan JSON secara lokal |

Posisi acak dihasilkan dengan memilih kandidat pada siluet yang paling jauh dari
pusat sebelumnya. Plus menggabungkan dua pita bersilangan, X mengikuti dua
diagonal, dan gunung memakai segitiga melebar ke bawah. Variasi lain memakai
lingkaran, spiral dua putaran, gelombang sinus, tiga pulau kecil, atau sebaran bebas.
Bobot plus/silang lebih kecil daripada pola lainnya. `mulai()` meneruskan
`bentuk_sebelumnya` agar pola tidak terulang langsung. Pergeseran lapisan juga
diberi variasi kecil. Ini menghasilkan persebaran tanpa grid, dengan irisan yang
masih mungkin terjadi. Irisan antartumpukan ikut dihitung dalam luas tertutup.
`bagian_tertutup()` menggabungkan interval Y di setiap pita X agar area penutup
yang bertumpuk tidak dijumlahkan berulang. Batas klik adalah paling banyak 15%
dari luas muka 80 x 90, memakai koordinat bulat yang sama dengan renderer.
Fixture pengujian tanpa posisi `x/y` memakai aturan tinggi tumpukan sederhana.

## Fungsi antarmuka

| Fungsi | Tujuan |
| --- | --- |
| `teks()`, `panel()`, `tombol_baru()` | Menggambar komponen dan mencatat tombol aktif |
| `posisi_mouse()` | Konversi koordinat jendela ke kanvas termasuk margin rasio |
| `pindah_halaman()` | Rekam halaman lama dan mulai transisi geser |
| `mulai()` | Hanya terima level aktif; tolak level sebelumnya dan level yang belum dicapai |
| `gambar_kartu()`, `kartu_baru()` | Pilih gambar, gambar kartu, dan ikon pratinjau kartu bawah |
| `kotak_slot()` | Posisi tujuh slot dari kiri ke kanan |
| `potret_kartu()` | Rekam posisi, jenis, dan status tertutup setiap kartu yang terlihat |
| `potret_visual()` | Gabungkan posisi model dengan posisi interpolasi gerakan yang masih berjalan |
| `gambar_menu()`, `gambar_game()`, `gambar_hasil()` | Render halaman dan hasil |
| `gambar_intro()`, `gambar_konfirmasi()` | Render banner pembuka dan dialog keluar |
| `jalankan_gerakan()` | Rekam aksi, ubah model, animasikan pilihan dan bantuan dengan interpolasi halus |
| `perbarui()` | Bersihkan gerakan selesai dan akhiri transisi halaman |
| `aksi()` | Jalankan tombol dan pengambilan bantuan berdasarkan prioritas model |
| `gambar()` | Render halaman, gabungkan transisi, skalakan kanvas, dan tampilkan |
| `tangani()` | Hitung ulang hitbox tiap klik, tangani kartu saat animasi berjalan, dan batasi input saat transisi halaman |
| `jalankan()` | Loop event, gambar, dan batas 60 FPS |

## Alur interaksi

Klik → konversi koordinat → hitung ulang hitbox terkini → cari kartu terdepan →
validasi irisan → ambil posisi visual sekarang → ubah model → hitung tujuan →
buat/perbarui gerakan kartu. Klik selanjutnya langsung diproses meskipun gerakan
sebelumnya belum selesai. Kelompok cocok mengecil setelah mencapai slot.

Bantuan otomatis menentukan kelompok terbanyak dari kiri, memeriksa ruang, lalu
memproses pengambilan pelengkap dengan gerakan masing-masing. Pengacakan memasangkan
sumber dan tujuan sejenis agar buah tampak bergerak sambil menjaga jumlahnya.

Model diperbarui sebelum animasi, sehingga hasil dan penyimpanan kemenangan sudah
konsisten selama gambar bergerak. Gerakan dengan tujuan tetap dilanjutkan; gerakan
dengan tujuan berubah dimulai dari posisi visual saat ini. Gerakan pemusnahan
tetap hidup meski kelompok baru dipilih. Kartu yang sudah dipindahkan tidak lagi
menjadi kandidat klik di papan. Alat bantu menunggu gerakan selesai, tetapi klik
kartu tetap aktif. Penutupan jendela selalu dapat diproses.

Model dan progres tidak mengimpor Pygame. Perubahan aturan dilakukan di `model.py`,
penyimpanan di `progres.py`, tampilan di `antarmuka.py`. Jalankan pengujian dari
panduan setelah perubahan.

## Pemuat SVG

Pengaturan menggunakan `ModalPengaturan.lapisan` sebagai tumpukan halaman modal.
Input diarahkan ke modal teratas sebelum hitbox game. `digeser` melacak slider
yang sedang dipegang hingga mouse dilepas atau fokus hilang. UI menyesuaikan
koordinat mouse dengan skala kanvas sebelum memperbarui volume. `Bahasa` membaca
terjemahan lokal dan menyimpan kode pilihan. Font CJK dipilih ketika teks
mengandung aksara Mandarin/Jepang. `AudioPermainan.atur_volume()` menerapkan
volume independen ke efek game, efek sistem, dan musik serta menyimpan preferensi.

`muat_aset(folder)` di `aset.py` membaca `katalog.json` berisi nama, kategori, dan
berkas relatif. SVG dirender oleh SDL_image bawaan Pygame-CE sekali saat startup,
lalu disimpan dalam memori pada ukuran 60 x 60. `gambar_kartu()` memilih ikon
berdasarkan jenis kartu dan level. Kategori diselang-seling di katalog.
