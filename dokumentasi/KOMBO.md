# Kombo pencocokan

Kombo memberi bonus untuk kecocokan manual yang beruntun. Kecocokan berikutnya
harus terjadi paling lambat lima detik setelah kecocokan sebelumnya, termasuk
tepat pada batas lima detik. Timer diperbarui setiap kecocokan yang berhasil.

| Pengali | Poin untuk tiga kartu |
| --- | --- |
| x1 | 300 |
| x2 | 600 |
| x3 | 900 |
| x4 | 1200 |
| x5 dan seterusnya | 1500 |

Nilai dasar tetap 100 per kartu; pengali kombo diterapkan pada tiga kartu yang
dimusnahkan. Memilih kartu yang belum cocok tidak langsung memutus rantai,
tetapi timer tetap berjalan. Setelah waktu habis, kecocokan berikutnya mulai
dari x1. Kombo dimulai ulang ketika level baru dimainkan.

Kembalikan, Cocok Otomatis, dan Acak yang berhasil dipakai memutus kombo.
Kecocokan melalui bantuan mendapat nilai dasar 300 dan tidak membuka rantai baru.
Bantuan/klik yang ditolak tidak memutus rantai, tetapi tidak memperpanjang timer.

HUD di dekat skor menampilkan pengali dan bar waktu. Toast menampilkan tambahan
poin yang sebenarnya; kombo terbaik ditampilkan pada hasil jika mencapai x2.
Tidak ada suara baru untuk pemusnahan atau peringatan slot.

Modal Pengaturan, bahasa, volume, dan konfirmasi keluar menjeda timer. Menutup
modal melanjutkan sisa waktu yang sama. Ini mencegah pemain kehilangan rantai
hanya karena menyesuaikan pengaturan. Selama animasi kartu biasa timer tetap
berjalan; pilihan kartu cepat tetap dapat diproses.

## Kode dan pengujian

`Permainan.kombo`, `kombo_tertinggi`, `batas_waktu_kombo`, dan `terakhir_poin`
menyimpan status. `durasi_kombo` dan `batas_kombo` adalah parameter lima detik
dan x5. Model menggunakan jam monoton; pengujian dapat memasukkan jam buatan.

`perbarui_kombo()` memutus rantai yang kedaluwarsa. `jeda_kombo()` dan
`lanjutkan_kombo()` mempertahankan waktu saat modal dibuka. `putus_kombo()`
dipakai bantuan yang berhasil. Antarmuka meneruskan `bantuan=True` hanya untuk
pengambilan otomatis, sehingga pilihan manual tetap memperoleh bonus.

Katalog `assets/bahasa.json` mencakup label, kombo terbaik, dan pesan poin dinamis.
Pengujian mencakup batas waktu tepat lima detik, kedaluwarsa, pengali maksimum,
bantuan, pengembalian, pengacakan, serta jeda modal.
