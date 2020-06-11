# tesis-23218030
Parallel Fuzzing

Proses fuzzing secara paralel menggunakan fuzzer AFL. Terdiri dari host sebagai master node dan satu atau lebih container sebagai slave node.

- Master node: aplikasi master, database, AFL dan sync agent untuk path coverage
- Slave node: AFL dan sync agent untuk seed
