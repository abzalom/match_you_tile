# Perhitungan kesulitan dan 1.000 level

Game kini menyediakan level 1–1000. Papan dibangkitkan saat mulai level, sehingga
tidak perlu menyimpan 1.000 berkas layout atau menghubungi server. Progres lama
tetap terbaca. Setiap mulai/mengulang menghasilkan variasi acak dari profil level.

## Tiga bagian dan Level Gila

- Level 1–333: **Mudah**.
- Level 334–666: **Sedang**.
- Level 667–1000: **Sulit**.
- Setiap kelipatan **10** menjadi **Level Gila**, misalnya 10, 20, 30, dan 1000.

Kategori utama menunjukkan bagian progres, bukan ambang indeks. Level Gila
menggantikan kategori pada nomor tersebut dan mendapat lonjakan kesulitan relatif
terhadap level sebelumnya. Ada 900 level biasa dan 100 Level Gila dalam total
1.000 level. Interval dapat diubah melalui `INTERVAL_LEVEL_GILA` di `level.py`.
Kategori ditampilkan pada intro dan di bawah nomor level pada layar permainan.

## Kenaikan jenis kartu per kategori

| Kategori | Jumlah jenis |
| --- | --- |
| Pengenalan, level 1-3 | 3 |
| Mudah, level 4-333 kecuali Level Gila | 5-7 |
| Sedang, level 334-666 kecuali Level Gila | 8-10 |
| Sulit, level 667-1000 kecuali Level Gila | 11-13 |
| Gila, setiap kelipatan 10 | 12-18 |

Jumlah jenis meningkat secara bertahap dalam kategori yang sama. Level biasa
memakai interpolasi linier dari awal hingga akhir bagiannya, dibulatkan ke jumlah
jenis utuh. Level Gila menggunakan kemajuan ((L - 10) / 990)^0.6 antara 12 dan 18.
Sumber konfigurasi ada di RENTANG_JENIS dan jumlah_jenis_level() dalam level.py.

Level 4 mengenalkan lima jenis dengan papan masih 27 kartu dan sebaran longgar.
Mudah meningkat sampai tujuh jenis sebelum Sedang mengenalkan delapan.
Sedang berakhir pada sepuluh jenis, lalu Sulit dimulai dengan sebelas. Level Gila
memakai sedikitnya dua belas jenis; setelahnya pemain kembali ke profil biasa.
Jumlah kartu tetap 27-90, slot tetap tujuh, dan batas kartu tertutup tetap 15%.

Jumlah jenis tidak boleh melebihi jumlah kelompok tiga di papan. Generator
memastikan setiap jenis benar-benar muncul dan jumlahnya tetap kelipatan tiga.
Ini rancangan awal untuk diuji pemain; keberadaan solusi tidak berarti tingkat
kesulitan sudah terkalibrasi terhadap pemain manusia.

## Faktor kesulitan

| Faktor | Awal → akhir | Pengaruh |
| --- | --- | --- |
| Jumlah kartu | 27 → 90 | Menambah panjang permainan dan jumlah keputusan |
| Jenis gambar | 3 sampai 18 | Menambah risiko kelompok berbeda memenuhi tujuh slot |
| Lebar/tinggi sebaran | 100% → 78% | Memadatkan kartu, meningkatkan tumpang tindih |
| Bentuk | Delapan bentuk bergantian | Memberi variasi struktur penutup |

Slot tetap tujuh dan ambang kartu tertutup tetap 15%. Ukuran kartu tidak mengecil.
Jumlah lapisan tetap tiga dan tumpukan dibatasi 9–30 agar layar tidak sesak oleh
ribuan kartu. Semua jenis gambar yang ditentukan profil dijamin muncul, masing-
masing dalam kelipatan tiga. Koleksi 24 SVG mencukupi kebutuhan maksimum 18 jenis.

`permainan/level.py` menjadi sumber konfigurasi. Untuk nomor level L:

```text
dasar = ((L - 1) / 999) ^ 0.55
fase = (L - 1) mod 10
tekanan_dasar = dasar × (0.94 + 0.012 × fase)
level biasa: tekanan = min(0.90, tekanan_dasar)
Level Gila: tekanan = min(1, tekanan_dasar + 0.16 + 0.12 × dasar)
kolom = 3 + round(7 × tekanan)
jumlah kartu = kolom × 9
jenis = lihat rentang per kategori; meningkat seiring kemajuan di kategori itu
sebaran = 1 - 0.22 × tekanan
```

Fase awal siklus sedikit lebih ringan daripada akhir siklus sebelumnya. Jadi
kesulitan tidak naik lurus setiap level, tetapi berombak dengan tren meningkat.
Variasi acak bentuk dapat membuat papan tertentu lebih ringan atau berat daripada
level berdekatan.

## Indeks desain

```text
indeks = 100 × [
    0.35 × (jumlah kartu - 27) / 63
  + 0.40 × (jenis - 3) / 15
  + 0.25 × tekanan
]
```

Nilai dibulatkan dan dibatasi 1–100. Bobot adalah keputusan desain awal, bukan
hasil pengukuran pemain. Indeks bukan persentase kalah/menang. Kategori memakai
pembagian progres di atas. Batas tekanan level biasa menyisakan tantangan lebih
tinggi untuk Level Gila, termasuk pada bagian akhir permainan.

| Level | Kategori | Kartu | Jenis | Indeks | Sebaran |
| --- | --- | --- | --- | --- | --- |
| 1 | Mudah | 27 | 3 | 1 | 100.0% |
| 3 | Mudah | 27 | 3 | 1 | 99.3% |
| 4 | Mudah | 27 | 5 | 6 | 99.1% |
| 9 | Mudah | 36 | 5 | 12 | 98.4% |
| 10 | Gila | 45 | 12 | 40 | 94.6% |
| 99 | Mudah | 45 | 6 | 25 | 93.6% |
| 299 | Mudah | 63 | 7 | 44 | 88.3% |
| 333 | Mudah | 63 | 7 | 44 | 88.4% |
| 334 | Sedang | 63 | 8 | 47 | 88.3% |
| 499 | Sedang | 72 | 9 | 59 | 84.5% |
| 500 | Gila | 90 | 16 | 94 | 78.9% |
| 666 | Sedang | 81 | 10 | 69 | 82.4% |
| 667 | Sulit | 81 | 11 | 72 | 82.2% |
| 999 | Sulit | 81 | 13 | 79 | 80.2% |
| 1000 | Gila | 90 | 18 | 100 | 78.0% |

Bantuan tetap bebas digunakan sesuai aturan proyek. Pemain dapat menyelesaikan
papan dengan mengulang Cocok Otomatis, sehingga indeks terutama menggambarkan
tantangan tanpa bantuan. Tidak ada batas bantuan baru yang ditambahkan.

## Validasi

`python audit_level.py` membuat satu papan per level dengan benih nomor level,
memeriksa batas layar dan ragam gambar, lalu menjalankan satu solusi yang sah.
Hasil seluruh 1.000 level tercatat di `dokumentasi/profil_level.csv`, termasuk
bentuk audit dan jumlah kartu yang bisa dipilih pada awal papan.

Audit ini membuktikan solusi untuk sampel tersebut, bukan mengukur kemampuan
pemain. Konstruksi kelompok tiga juga memberikan urutan solusi awal secara
struktural. Pengacakan bantuan tetap tidak menjamin solusi tanpa bantuan sesudahnya.

Untuk kalibrasi setelah publikasi, kumpulkan statistik dengan persetujuan pemain:
rasio menang pada percobaan pertama, jumlah percobaan, waktu penyelesaian, dan
jumlah bantuan. Pisahkan penyelesaian dengan/tanpa bantuan saat mengevaluasi profil.
Pengumpulan statistik belum diimplementasikan.

## Agen setelah publikasi

Generator prosedural lokal sudah membuat level otomatis saat game dimainkan,
termasuk saat offline. Ini algoritme Python, bukan agen AI.

Agen AI juga dapat dipakai setelah publikasi melalui backend: agen mengusulkan
konfigurasi level sebagai data, validator memeriksa batas dan solusi, lalu paket
level yang lolos disalurkan ke game. Perubahan dapat dilakukan tanpa memperbarui
aplikasi jika jalur unduh konfigurasi sudah dibangun. Pendekatan ini membutuhkan
layanan backend, koneksi, biaya layanan, dan pengelolaan versi konfigurasi.

Backend, agen AI, pengiriman konfigurasi jarak jauh, dan penerbitan game belum
dibuat. Generator dan audit lokal adalah implementasi yang tersedia sekarang.
