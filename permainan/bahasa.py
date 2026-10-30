"""Terjemahan lokal lengkap dan pilihan bahasa yang tersimpan."""

import json
from pathlib import Path
import re


class Bahasa:
    def __init__(self, katalog, pengaturan):
        self.pengaturan = Path(pengaturan)
        data = json.loads(Path(katalog).read_text(encoding="utf-8"))
        self.pilihan = dict(zip(data["kode"], data["nama"]))
        self.kamus = {kode: {k: v[i] for k, v in data["teks"].items()}
                      for i, kode in enumerate(data["kode"])}
        self.sumber = {v: k for k, v in self.kamus["id"].items() if "{" not in v}
        for k in ("mudah", "sedang", "sulit", "gila"):
            self.sumber[self.kamus["id"][k].upper()] = k
        self.kode = "id"
        self.gagal_simpan = False
        try:
            kode = json.loads(self.pengaturan.read_text(encoding="utf-8")).get("bahasa")
            if kode in self.pilihan:
                self.kode = kode
        except (OSError, ValueError, AttributeError, TypeError):
            pass

    def t(self, kunci, **isi):
        return self.kamus[self.kode][kunci].format(**isi)

    def pilih(self, kode):
        if kode not in self.pilihan:
            return False
        self.kode = kode
        try:
            self.pengaturan.parent.mkdir(parents=True, exist_ok=True)
            self.pengaturan.write_text(json.dumps({"bahasa": kode}), encoding="utf-8")
            self.gagal_simpan = False
        except OSError:
            self.gagal_simpan = True
        return True

    def terjemahkan(self, teks):
        if teks in self.sumber:
            return self.t(self.sumber[teks])
        pola = ((r"LEVEL (\d+)", "level", ("nomor",)),
                (r"\+(\d+)! Kombo x(\d+)\.", "pesan_kombo", ("nilai", "jumlah")),
                (r"SKOR (\d+)", "skor", ("nilai",)),
                (r"(\d+) kartu di papan", "sisa", ("jumlah",)),
                (r"Level (\d+) / Skor (\d+)", "hasil_skor", ("nomor", "nilai")))
        for ekspresi, kunci, nama in pola:
            hasil = re.fullmatch(ekspresi, teks)
            if hasil:
                return self.t(kunci, **dict(zip(nama, hasil.groups())))
        hasil = re.fullmatch(r"Level (\d+) / (.+)", teks)
        if hasil:
            return self.t("play", nomor=hasil[1], kategori=self.terjemahkan(hasil[2]))
        return teks
