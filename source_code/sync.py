import os
import sqlite3
import time
import datetime
import random
import string

direktori_proyek = '/home/bayu/Documents/Tesis/Fuzzgoat/'
nama_database = direktori_proyek + 'fuzzgoat.db'
nama_fuzzer = 'fuzzer0'

class AgenSync:
    def __init__(self, fuzzer):
        self.fuzzer = fuzzer
        self.direktori = direktori_proyek + fuzzer + "/out/queue/"

    def cek_duplikasi(self, nilai_hex):
        con = sqlite3.connect(nama_database)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) as total FROM seed WHERE hex_value=?;", (nilai_hex, ))
        baris = cur.fetchone()
        total = baris[0]
        con.commit()
        con.close()
        return total

    def baca_file_seed(self):
        files = sorted(os.listdir(self.direktori))
        files.remove('.state')
        return files

    def simpan_seed(self, file, nilai_seed, hex_seed):
        con = sqlite3.connect(nama_database)
        cur = con.cursor()
        cur.execute("INSERT INTO seed(file_name, value, hex_value, fuzzer) VALUES(?, ?, ?, ?);", (file, nilai_seed, hex_seed, self.fuzzer))
        con.commit()
        con.close()

    def update_seed(self, nilai_seed_baru, hex_seed, hex_seed_baru):
        status='2'
        con = sqlite3.connect(nama_database)
        cur = con.cursor()
        cur.execute("UPDATE seed SET value=?, hex_value=?, status=? WHERE hex_value=? AND fuzzer=?;", (nilai_seed_baru, hex_seed_baru, status, hex_seed, self.fuzzer))
        con.commit()
        con.close()

    def generator_acak(self, nilai_seed, hex_seed):
        list_nilai_seed = list(nilai_seed)
        posisi = random.randint(0,len(list_nilai_seed))
        #jumlah_karakter_acak = random.randint(1,3)
        #karakter_acak = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(jumlah_karakter_acak))
        #for karakter in karakter_acak:
        #    list_nilai_seed.insert(posisi, ord(karakter))
        #    posisi+=1
        karakter_acak = random.choice(string.ascii_letters + string.digits + string.punctuation)
        list_nilai_seed.insert(posisi, ord(karakter_acak))
        list_nilai_seed_baru = list()
        nilai_seed_baru = ''
        for karakter_desimal in list_nilai_seed:
            karakter_ascii = chr(karakter_desimal)
            list_nilai_seed_baru.append(karakter_ascii)
        str_nilai_seed_baru = nilai_seed_baru.join(map(str, list_nilai_seed_baru))
        nilai_seed_baru = str.encode(str_nilai_seed_baru)
        hex_seed_baru = nilai_seed_baru.hex()
        seed_baru = [str_nilai_seed_baru, hex_seed_baru]
        return seed_baru

    def update_file_seed(self, file, nilai_seed_baru):
        file_seed_baru = open(self.direktori + file, 'w')
        file_seed_baru.write(nilai_seed_baru)
        file_seed_baru.close()

index = 0
agen = AgenSync(nama_fuzzer)
while(True):
    file = agen.baca_file_seed()
    if len(file)!=index:
        for i in range(index, len(file)):
            seed = open(direktori_proyek + nama_fuzzer + "/out/queue/" + file[i], 'rb')
            nilai_seed = seed.read()
            hex_seed = nilai_seed.hex()
            total = agen.cek_duplikasi(hex_seed)
            agen.simpan_seed(file[i], nilai_seed, hex_seed)
            if total>0:
                #if file[i].find('orig')==-1:
                seed_baru = agen.generator_acak(nilai_seed, hex_seed)
                nilai_seed_baru = seed_baru[0]
                hex_seed_baru = seed_baru[1]
                agen.update_seed(nilai_seed_baru, hex_seed, hex_seed_baru)
                agen.update_file_seed(file[i], nilai_seed_baru)
            i+=1
        index=len(file)
    time.sleep(1)