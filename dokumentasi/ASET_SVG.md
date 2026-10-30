# Koleksi kartu SVG

24 ilustrasi vektor asli, latar transparan, viewBox 128 ? 128, garis membulat.

| Folder di assets/svg | Enam gambar |
| --- | --- |
| buah | Apel, pisang, jeruk, anggur, semangka, nanas |
| sayuran | Wortel, brokoli, terong, tomat, jagung, kubis |
| bumbu | Cabai, bawang putih, bawang merah, jahe, kunyit, kayu manis |
| makanan | Nasi goreng, sate, telur goreng, donat, roti, mi |

Pratinjau: [semua ikon](pratinjau_kartu.png).

Game memakai SVG melalui `permainan/aset.py`; tidak memerlukan library tambahan.
SVG diraster sekali saat startup oleh Pygame-CE, lalu disimpan di memori.
Aset GIF/PNG lama tetap disimpan tetapi tidak dipakai sebagai gambar kartu.

`assets/svg/katalog.json` berisi nama, kategori, dan berkas relatif setiap ikon.
Kategori diselang-seling supaya rentang jenis kartu mencakup berbagai kelompok.
Setiap jenis di satu level memiliki gambar unik. Level berikutnya menggeser
pilihan ikon; aturan pencocokan tetap tiga kartu dengan gambar sama.

Edit SVG memakai editor teks atau vektor. Pertahankan kanvas 128 ? 128, latar
transparan, dan siluet jelas pada ukuran kecil. Untuk menambah ikon, letakkan SVG
di folder kategori dan tambahkan entri katalog. Jalankan ulang game setelah edit.

Pengujian: `python -m unittest discover -s tests -v`.
