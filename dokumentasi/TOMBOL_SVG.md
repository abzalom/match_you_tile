# Tombol SVG

Folder `assets/svg/tombol/` berisi tujuh ikon transparan bergaya kartun pastel:

| Berkas | Bentuk dan fungsi |
| --- | --- |
| `mulai.svg` | Segitiga hijau tersenyum untuk Mulai |
| `menu.svg` | Rumah beratap merah muda untuk Menu |
| `kembali.svg` | Panah biru dan bintang untuk mengembalikan kartu |
| `cocok.svg` | Bintang kuning berpipi merah untuk pencocokan otomatis |
| `acak.svg` | Dua panah melingkar dengan wajah tersenyum untuk Acak |
| `lanjut.svg` | Panah hijau dan bintang untuk level berikutnya |
| `ulang.svg` | Panah melingkar merah muda dan kuning untuk Main Lagi |

Lima latar tombol SVG bernama `latar_dasar.svg`, `latar_utama.svg`,
`latar_sorot.svg`, `latar_utama_sorot.svg`, dan `latar_nonaktif.svg` menyediakan
bentuk membulat, sorotan atas, serta sisi bawah timbul. Tombol sedikit terangkat
saat mouse berada di atasnya. Status nonaktif memakai warna redup dan ikon pudar.

`AsetTombol` dalam `permainan/aset.py` memuat SVG sekali dan menyimpan hasil
penskalaan per aksi, ukuran, dan status. `tombol_baru()` menggabungkan latar,
ikon, serta label Indonesia yang tetap digambar sebagai teks agar level dan
pintasan dapat berubah tanpa mengedit SVG. Area klik tetap mengikuti kotak asli.

Ikon memakai kanvas 128 x 128, latar 320 x 80; semua berupa bentuk vektor asli.
Tombol bantuan di game hanya menampilkan ikon, tanpa label atau teks pintasan.
Label tetap dipakai untuk level, Menu, hasil, dan pilihan dialog konfirmasi.
Pratinjau: [koleksi tombol](pratinjau_tombol.png).
