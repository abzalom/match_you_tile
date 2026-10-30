# Musik dan efek suara

Menu dan permainan memakai lagu yang sama dari berkas yang disediakan pemilik
proyek: `ai generated musik/Paths_Through_Silver_Leaves.wav`. Lagu terus berjalan
tanpa dimulai ulang saat berganti halaman, masuk level, atau menampilkan hasil.
Peringatan slot dan pemusnahan kartu tidak mengeluarkan suara; animasi tetap ada.

| Berkas dalam assets/audio | Penggunaan |
| --- | --- |
| musik_menu.wav | Musik sintetis lama, disimpan tetapi tidak digunakan |
| ai generated musik/Paths_Through_Silver_Leaves.wav | Musik menu dan bermain, sekitar 145 detik, diulang |
| klik.wav | Tombol navigasi dan dialog |
| kartu.wav | Kartu dipilih dan bantuan pencocokan mengambil kartu |
| cocok.wav | Tidak digunakan; pemusnahan tanpa suara |
| kembali.wav | Bantuan mengembalikan kartu |
| acak.wav | Bantuan pengacakan |
| peringatan.wav | Tidak digunakan; peringatan slot hanya visual |
| menang.wav | Hasil menang, setelah animasi terakhir selesai |
| kalah.wav | Hasil kalah atau menyetujui keluar saat bermain |
| intro.wav | Pembukaan banner level |
| batal.wav | Memilih kartu tertutup atau bantuan yang belum bisa digunakan |

## Kontrol

Tombol speaker tanpa teks berada di kanan atas menu dan di bagian atas layar
permainan. Klik untuk membuka modal tiga pengatur volume; modal juga tersedia
melalui Pengaturan. Setiap pengatur mendukung slider dan tombol minus/plus.
Tombol Bisukan semua/Aktifkan suara tersedia di modal. Ikon speaker dicoret
saat bisu. Pilihan disimpan terpisah dari progres di `data/audio.json`.

Volume awal musik 28%, suara game 55%, dan suara sistem 55%; semuanya dapat
diubah sendiri-sendiri dari 0–100%. Layar hasil membunyikan jingle sekali
sementara musik tetap berjalan. Menyimpan pilihan dapat gagal
jika folder data tidak dapat ditulis; status sesi tetap berlaku.

Jika perangkat audio tidak tersedia, permainan tetap berjalan tanpa suara.
Pengujian otomatis menggunakan driver audio dummy sehingga tidak menghasilkan
bunyi di speaker pengguna. Validasi ini memeriksa pemuatan dan alur pemutaran;
penilaian kenyamanan suara perlu dilakukan melalui speaker/headphone pemain.

## Pembuatan ulang

```powershell
python peralatan/buat_audio.py
python main.py
```

Skrip hanya memakai pustaka standar Python: penjumlahan gelombang sinus,
harmonik, amplop attack/release, serta penulisan WAV PCM mono 16-bit/22050 Hz.
Nada akhir dirangkai menjadi frase yang berulang; kedua ujung loop diberi fade
singkat. Semua WAV sudah tersedia sehingga tidak perlu dibuat ulang saat startup.
Skrip menimpa dua belas WAV hasil generasinya bila dijalankan ulang.
`musik_game.wav` hasil skrip tetap disimpan sebagai musik sintetis lama, tetapi
tidak dipakai oleh game. Pemetaan musik aktif berada di `AudioPermainan.berkas_musik`.
Menjalankan skrip sintesis tidak menimpa lagu impor yang sedang digunakan.

## Lagu permainan impor

`assets/audio/ai generated musik/Paths_Through_Silver_Leaves.mp3` dikonversi ke
WAV PCM 16-bit stereo 44100 Hz, berdurasi sekitar 145,42 detik. MP3 asli tetap
disimpan. Pemutaran menggunakan hasil WAV pada folder yang sama. Mixer game
menyesuaikan format saat pemutaran; volume, perulangan, dan tombol bisu tetap
mengikuti pengaturan audio game.

## Kode

`AudioPermainan` di `permainan/audio.py` memuat efek sekali ke memori, menyalurkan
musik melalui `pygame.mixer.music`, dan memakai kanal khusus untuk hasil serta
peringatan. Efek singkat memakai kanal lain agar klik cepat bisa bersamaan.

`jadwalkan()` menyimpan efek beserta waktunya, dan `perbarui()` memutarnya satu
kali ketika waktu tercapai. Efek pencocokan dan peringatan slot dinonaktifkan.
Perpindahan halaman membuang
jadwal lama. Preferensi bisu dibaca saat startup dan ditulis hanya saat diubah.
