# Pengaturan bahasa dan volume

Menu utama tidak lagi menggambar kartu dekoratif. Menu berisi gambar judul,
tombol level/kesulitan, tombol Pengaturan, dan pintasan speaker.
Tombol roda gigi Pengaturan juga tersedia di kanan atas layar permainan.
Menutup modal melanjutkan papan yang sama, tanpa mengulang level atau mengubah skor.

## Bahasa

Klik **Pengaturan → Bahasa**, lalu pilih salah satu dari delapan bahasa:
Indonesia, Inggris, Spanyol, Prancis, Jerman, Portugis, Mandarin, atau Jepang.
Nama bahasa ditulis dalam bahasa aslinya agar tetap mudah ditemukan.

Perubahan langsung berlaku pada tombol, pengaturan, kategori kesulitan, label
level/skor, jumlah kartu, intro, hasil, konfirmasi keluar, pesan permainan,
peringatan penyimpanan, dan judul jendela. Logo Title.png adalah nama merek game
sehingga tetap berupa gambar asli dan tidak diterjemahkan.

Pilihan tersimpan dalam `data/pengaturan.json`. Katalog terjemahan lokal adalah
`assets/bahasa.json`; tidak ada permintaan ke layanan penerjemahan atau internet.
Untuk menambah bahasa, tambahkan kode/nama serta satu terjemahan pada setiap baris
teks dengan urutan yang sama. Pertahankan placeholder seperti `{nomor}` dan `{nilai}`.

`permainan/bahasa.py` menerjemahkan label tetap serta pola teks dinamis. Pesan
model tetap menggunakan sumber Indonesia secara internal agar aturan permainan
tidak bergantung pada bahasa; renderer menerjemahkannya saat digambar.

Teks Mandarin/Jepang dan nama bahasa tersebut menggunakan font CJK sistem:
Microsoft YaHei di Windows, atau Noto Sans CJK pada lokasi standar Linux.
Pada mesin publikasi lain, sediakan font CJK sistem yang sesuai atau tambahkan
font berlisensi distribusi beserta jalurnya. Font tersebut tersedia pada lingkungan
Windows pengembangan saat ini. Teks panjang diperkecil atau dibagi baris agar muat.

## Volume

Klik **Pengaturan → Volume**, atau klik speaker untuk langsung membuka modal volume.

| Pengatur | Mengendalikan |
| --- | --- |
| Suara game | Kartu dipilih, kembalikan, dan acak; pemusnahan/peringatan slot tanpa suara |
| Suara sistem | Klik tombol, intro, aksi tidak tersedia, menang, dan kalah |
| Musik latar | Lagu yang sama dan berkelanjutan di menu serta permainan |

Setiap pengatur memiliki slider yang dapat diseret, tombol **-** di kiri, tombol
**+** di kanan, dan persentase 0–100%. Tombol mengubah volume sebesar 5% dan
berhenti pada batas 0/100%. Ketiga kategori bekerja independen. Efek dan musik
langsung mengikuti nilai baru. Efek contoh diputar setelah perubahan volume efek.

Saat menyeret, nilai diterapkan langsung tetapi berkas disimpan setelah mouse
dilepas; perubahan tombol disimpan langsung. Kehilangan fokus atau menutup
jendela saat menyeret juga menyimpan nilai terakhir. Preferensi disimpan pada
`data/audio.json`, bersama status bisu. Format lama yang hanya berisi `bisu`
tetap terbaca dengan volume awal game/sistem 55% dan musik 28%.

**Bisukan semua** mematikan keluaran tanpa menghapus nilai slider. Pilih
**Aktifkan suara** untuk memulihkan volume yang sudah disesuaikan.

## Modal bertingkat

Bahasa dan volume terbuka di atas Pengaturan. Tombol Kembali atau Esc menutup
satu lapisan dan kembali ke Pengaturan. Tutup/Esc pada Pengaturan kembali ke
layar utama. Klik di luar modal tidak menjalankan tombol atau kartu di belakangnya.
Jika penyimpanan gagal, perubahan tetap berlaku selama sesi dan modal menampilkan
pesan kegagalan; progres level tidak diubah oleh pengaturan.
