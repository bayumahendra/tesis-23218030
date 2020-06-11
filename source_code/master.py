import os
import sqlite3
import datetime
import random
import string
import time

# Define global variable
# [host]
direktori_proyek = '/home/bayu/Documents/Tesis/Fuzzgoat/'
direktori_cmin = '/home/bayu/Documents/Tesis/Fuzzgoat/seed-cmin/'
nama_database = 'fuzzgoat.db'
# [container]
nama_container = ['fuzzer0', 'fuzzer1']
direktori_afl = '/home/afl/'

class Masukan:
    def __init__(self, nama):
        self.nama = nama

    def copy(self, path_sumber, path_tujuan):
        perintah = "cp " + path_sumber + self.nama + " " + path_tujuan
        os.system(perintah)

class Container:
    def __init__(self, nama):
        self.nama = nama

    def jalan(self):
        perintah = "docker start " + self.nama
        os.system(perintah)

    def berhenti(self):
        print('\n> Stop Container')
        perintah = "docker stop " + self.nama
        #print(perintah)
        os.system(perintah)

class Fuzzer:
    def __init__(self, nama):
        self.nama = nama
        self.direktori_out = direktori_proyek + self.nama + "/out/"

    def jalan(self, nama_target):
        perintah = "gnome-terminal --geometry=80x26 -- bash -c 'docker exec -t -w " + direktori_afl + " " + self.nama + " afl-fuzz -i in -o out -T " + nama_target + "-" + self.nama + " ./" + nama_target + " @@; exec bash'"
        #print(perintah)
        os.system(perintah)
        time.sleep(3)

    def berhenti(self):
        perintah = "docker exec " + self.nama + " kill afl-fuzz"
        #print(perintah)
        os.system(perintah)
        print("Terminate", self.nama)
        time.sleep(1.5)    

    def resume(self, nama_target):
        print('\n> Resume Fuzzing dengan', self.nama)
        perintah = "gnome-terminal --geometry=80x26 -- bash -c 'docker exec -t -w " + direktori_afl + " " + self.nama + " afl-fuzz -i- -o out -T " + nama_target + "-" + self.nama + " ./" + nama_target + " @@; exec bash'"
        #print(perintah)
        os.system(perintah)
        time.sleep(3)

    def baca_plot_data(self):
        plot_data = self.direktori_out + 'plot_data'
        file = open(plot_data, 'r')
        isi_file = file.readlines()
        for i in range(1, len(isi_file)):
            cycles_done = isi_file[i].split(",")
            cd = int(cycles_done[1])
            unique_crashes = isi_file[i].split(",")
            uc = int(unique_crashes[7])
        if cd>=1 or uc>=len(nama_container)-1:
            terminate = 1
            return terminate
        else:
            terminate = 0
            return terminate

    def rename_file_stats(self):
        src = self.direktori_out + 'fuzzer_stats'
        dst = self.direktori_out + 'fuzzer_stats_init'
        os.rename(src, dst)
        src = self.direktori_out + 'plot_data'
        dst = self.direktori_out + 'plot_data_init'  
        os.rename(src, dst)
        print("\n> Rename file fuzzer_stats dan plot_data", self.nama)

    def simpan_stats(self):
        file_stats = direktori_proyek + self.nama + '/out/' + 'fuzzer_stats'
        f = open(file_stats, 'r')
        baris = f.readlines()
        start_time = baris[0].split(":")
        last_update = baris[1].split(":")
        cycles_done = baris[3].split(":")
        execs_per_sec = baris[5].split(":")
        paths_total = baris[6].split(":")
        paths_found = baris[8].split(":")
        cur_path = baris[11].split(":")
        unique_crashes = baris[17].split(":")
        unique_hangs = baris[18].split(":")
        command_line = baris[27].split(":")
        st = datetime.datetime.fromtimestamp(int(start_time[1].strip()))
        lu = datetime.datetime.fromtimestamp(int(last_update[1].strip()))
        rt = lu - st
        cd = cycles_done[1].strip()
        es = execs_per_sec[1].strip()
        pt = paths_total[1].strip()
        pf = paths_found[1].strip()
        cp = cur_path[1].strip()
        uc = unique_crashes[1].strip()
        uh = unique_hangs[1].strip()
        cl = command_line[1].strip()
        parameter = (str(rt), cd, es, pt, pf, cp, uc, uh, cl, self.nama)
        con = sqlite3.connect(nama_database)
        cur = con.cursor()
        cur.execute("INSERT INTO stats(run_time, cycles_done, execs_per_sec, paths_total, paths_found, cur_path, uniq_crashes, uniq_hangs, command_line, fuzzer) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", parameter)
        con.commit()
        con.close()

class Mutator:
    def __init__(self, direktori, file):
        self.direktori = direktori
        self.file = file

    def bit_flip(self):
        file_seed = open(self.direktori + self.file, 'rb')
        nilai_seed = file_seed.read()
        list_nilai_seed = list(nilai_seed)
        index = random.randint(0, len(nilai_seed)-1)
        biner_seed = bin(ord(chr(nilai_seed[index])))
        posisi = random.randint(2, len(biner_seed)-1)
        list_biner_seed = list(biner_seed)
        if list_biner_seed[posisi]=='0':
            list_biner_seed[posisi] = '1'
        else:
            list_biner_seed[posisi] = '0'
        biner_seed_baru = ''.join(list_biner_seed)
        karakter_baru = int(biner_seed_baru, 2)
        list_nilai_seed[index] = karakter_baru 
        i = 0
        for i in range(i, len(list_nilai_seed)):
            list_nilai_seed[i] = chr(list_nilai_seed[i])
            i+=1
        nilai_seed_baru = ''.join(list_nilai_seed)
        return nilai_seed_baru

    def update_file_seed(self, nilai_seed_baru):
        file_seed_baru = open(self.direktori + self.file, 'w')
        file_seed_baru.write(nilai_seed_baru)
        file_seed_baru.close()

print("Default direktori dari project adalah", direktori_proyek)

# Pilih initial seed
while True:
    try:
        nama_seed = input("\nSilahkan pilih seed awal: ")
        if os.path.isfile(nama_seed)==True:
            seed_awal = Masukan(nama_seed)
            print('> Copy Seed')
            direktori_tujuan = direktori_proyek + nama_container[0] + "/in/"
            seed_awal.copy(direktori_proyek, direktori_tujuan)
            print('Mengcopy seed ke: ' + nama_container[0])
            break
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("File tidak ditemukan") 

# Pilih program target
while True:
    try:
        nama_target = input("\nSilahkan pilih program target: ")
        if os.path.isfile(nama_target)==True:
            target = Masukan(nama_target)
            print('> Copy Target Program')
            for i in nama_container:
                direktori_tujuan = direktori_proyek + i
                target.copy(direktori_proyek, direktori_tujuan)
                print('Mengcopy ' + nama_target + ' ke: ' + i)
            break
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("File tidak ditemukan")

# Start container
print('\n> Start Container')
for i in nama_container:
    container = Container(i)
    container.jalan()

# Start fuzzer
print('\n> Start Fuzzing dengan', nama_container[0])
fuzzer = Fuzzer(nama_container[0])
fuzzer.jalan(nama_target)

# Baca plot_data
print('\n> Monitoring Seed')
while True:
    time.sleep(1)
    terminate = fuzzer.baca_plot_data()
    if terminate==1:
        print('\n> Terminate Fuzzer')
        fuzzer.berhenti()
        fuzzer.simpan_stats()
        fuzzer.rename_file_stats()
        break

# Buat seed baru
direktori_queue = direktori_proyek + nama_container[0] + "/out/queue/"
direktori_cmin = direktori_proyek + "seed-cmin/"
files = sorted(os.listdir(direktori_queue))
for file in files:
    seed = Masukan(file)
    seed.copy(direktori_queue, direktori_cmin)
for i in range(1, len(nama_container)):
    jumlah_seed = 0
    print('\n> Buat Seed Baru untuk', nama_container[i])
    direktori_in = direktori_proyek + nama_container[i] + "/in/"
    perintah = "afl-cmin -i " + direktori_cmin + " -o " + direktori_in +  " ./" + nama_target + " @@ -C"
    os.system(perintah)
    for seed_awal in os.listdir(direktori_in):
        jumlah_seed+=1
    j = 0
    for seed_awal in sorted(os.listdir(direktori_in)):
        if j == jumlah_seed-1:
            nama_file = direktori_cmin + seed_awal
            os.remove(nama_file)
            #print("Hapus dari cmin", seed_awal)
            seed_awal_baru = seed_awal
        else:
            nama_file = direktori_in + seed_awal
            os.remove(nama_file)
            #print("Hapus dari in", seed_awal)
        j+=1
    print(f"Seed awal untuk {nama_container[i]} adalah {seed_awal_baru}")
    mutator = Mutator(direktori_in, seed_awal_baru)
    nilai_seed_baru = mutator.bit_flip()
    mutator.update_file_seed(nilai_seed_baru)

# Resume initial fuzzer
fuzzer.resume(nama_target)

# Parallel fuzzing
for i in range(1, len(nama_container)):
    fuzzer = Fuzzer(nama_container[i])
    fuzzer.jalan(nama_target)

# Sinkronisasi seed dan bitmap
time.sleep(1)
print("\n> Jalankan sinkronisasi seed dan bitmap")
for i in nama_container:
    perintah = "python3 " + direktori_proyek + i + "/sync.py &"
    os.system(perintah)
    time.sleep(1.5)
perintah = "python3 " + direktori_proyek + "sync_bitmap.py &"
os.system(perintah)

print("\n:: Proses fuzzing paralel sedang berjalan!")
while True:
    for i in nama_container:
        input(f"\nUntuk menghentikan {i}, silahkan tekan [Enter]: ")
        fuzzer = Fuzzer(i)
        container = Container(i)
        fuzzer.berhenti()
        fuzzer.simpan_stats()
        container.berhenti()
        perintah = "pkill -f " + direktori_proyek + "fuzzer0/sync.py &"
        os.system(perintah)
        perintah = "pkill -f " + direktori_proyek + "fuzzer1/sync.py &"
        os.system(perintah)
        perintah = "pkill -f " + direktori_proyek + "sync_bitmap.py &"
        os.system(perintah)
    break
print("\n:: Proses fuzzing paralel selesai.")