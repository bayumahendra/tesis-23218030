import os
import hashlib
import time

nama_fuzzer = ['fuzzer0', 'fuzzer1']

class AgenSync:
    def __init__(self, fuzzer):
        self.fuzzer = fuzzer
        self.direktori = '/home/bayu/Documents/Tesis/Fuzzgoat/'
        self.file_bitmap = self.direktori + self.fuzzer + '/out/fuzz_bitmap'

    def generate_hash(self):
        file = open(self.file_bitmap, 'rb')
        isi_file = file.read()
        md5_hash = hashlib.md5()
        md5_hash.update(isi_file)
        digest = md5_hash.hexdigest()
        return digest
    
    def baca_bitmap(self):
        dec_bitmap = list()
        file = open(self.file_bitmap, 'rb')
        isi_file = file.read()
        for karakter in isi_file:
            dec_bitmap.append(karakter)
        return dec_bitmap

    def gabung_bitmap(self, dec_karakter, dec_karakter1):
        dec_karakter_baru = dec_karakter & dec_karakter1
        karakter_baru = chr(int(dec_karakter_baru))
        list_bitmap_baru.append(karakter_baru)
        return list_bitmap_baru

    def update_bitmap(self, bitmap_baru):
        bitmap = open(self.file_bitmap, 'wb')
        bitmap.write(bitmap_baru)
        bitmap.close()

while True:
    # Baca bitmap
    list_dec_bitmap = list()
    list_digest = list()
    for fuzzer in nama_fuzzer:
        agen = AgenSync(fuzzer)
        dec_bitmap = agen.baca_bitmap()
        list_dec_bitmap.append(dec_bitmap)
        digest = agen.generate_hash()
        list_digest.append(digest)
    if list_digest[0] != list_digest[1]:
        # Merge bitmap
        list_bitmap_baru = list()
        for i in range(1, len(nama_fuzzer)):
            for j in range(0, 65536):
                dec_karakter = list_dec_bitmap[i-1][j]
                dec_karakter1 = list_dec_bitmap[i][j]
                if i == 1:
                    tmp_bitmap = agen.gabung_bitmap(dec_karakter, dec_karakter1)
                else:
                    mrg_bitmap = agen.gabung_bitmap(tmp_bitmap[j], dec_karakter1)
                    tmp_bitmap = mrg_bitmap
        list_bitmap_baru = tmp_bitmap
        bitmap_baru = bytes("".join(list_bitmap_baru), 'iso8859-1')
        # Update bitmap
        for fuzzer in nama_fuzzer:
            agen = AgenSync(fuzzer)
            agen.update_bitmap(bitmap_baru)
        merge_bitmap = open(agen.direktori + 'bitmap', 'wb')
        merge_bitmap.write(bitmap_baru)
        merge_bitmap.close()
    time.sleep(1)