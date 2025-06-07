import sqlite3
from datetime import datetime

def connect_db():
    return sqlite3.connect('perpustakaan_python.db')

def init_db():
    with connect_db() as koneksi:
        cursor = koneksi.cursor()

        # Pembuatan tabel-tabel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_login (
                id_login INTEGER PRIMARY KEY AUTOINCREMENT,
                id_petugas INTEGER NOT NULL,
                waktu_login DATETIME
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_siswa (
                id_siswa INTEGER PRIMARY KEY AUTOINCREMENT,
                nis TEXT UNIQUE NOT NULL,
                nama_siswa TEXT NOT NULL,
                kelas TEXT NOT NULL,
                alamat TEXT,
                hp_siswa TEXT,
                photo TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_buku (
                id_buku INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_buku TEXT UNIQUE NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                judul TEXT NOT NULL,
                pengarang TEXT NOT NULL,
                penerbit TEXT NOT NULL,
                tahun_terbit TEXT NOT NULL,
                kota_terbit TEXT NOT NULL,
                edisi TEXT NOT NULL,
                jumlah_halaman INTEGER NOT NULL
                kategori TEXT NOT NULL,
                nomor_ddc INTEGER NOT NULL,
                bahasa TEXT NOT NULL,
                sinopsis TEXT,
                jumlah INTEGER NOT NULL,
                cover TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_bukudetail (
                id_bukudetail INTEGER PRIMARY KEY AUTOINCREMENT,
                id_buku INTEGER NOT NULL,
                kode_bukudetail TEXT UNIQUE NOT NULL,
                kondisi TEXT CHECK(kondisi IN ('Baik', 'Rusak', 'Hilang')),
                status BOOLEAN
            )
        ''')

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_petugas(
                id_petugas INTEGER PRIMARY KEY AUTOINCREMENT,
                nip TEXT UNIQUE NOT NULL,
                nama_petugas TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('Admin', 'Operator'))
            )
        """)

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_pinjam(
                id_pinjam INTEGER PRIMARY KEY AUTOINCREMENT,
                id_siswa INTEGER,
                id_petugas INTEGER NOT NULL,
                waktu_pinjam DATETIME,
                waktu_kembali DATETIME
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_pinjamdetail(
                id_pinjamdetail INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pinjam INTEGER NOT NULL,
                id_bukudetail INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_kembali(
                id_kembali INTEGER PRIMARY KEY AUTOINCREMENT,
                id_siswa INTEGER,
                id_petugas INTEGER,
                waktu_kembali DATETIME
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_kembalidetail(
                id_kembalidetail INTEGER PRIMARY KEY AUTOINCREMENT,
                id_kembali INTEGER,
                id_pinjamdetail INTEGER,
                denda INTEGER
            )
        ''')

        # Insert data
        try:
            # Petugas
            petugas_data = [
                ('10001', 'Budi', 'budi', 'pass123', 'Admin'),
                ('10002', 'Ani', 'ani', 'pass123', 'Operator'),
                ('10003', 'Sari', 'sari', 'pass123', 'Operator'),
                ('10004', 'Joko', 'joko', 'pass123', 'Admin'),
                ('10005', 'Rina', 'rina', 'pass123', 'Operator')
            ]
            cursor.executemany("INSERT OR IGNORE INTO tbl_petugas (nip, nama_petugas, username, password, role) VALUES (?, ?, ?, ?, ?)", petugas_data)

            # Siswa
            siswa_data = [
                ('220001', 'Andi', 'X IPA 1', 'Jl. Mawar', '0811111111','1.jpg'),
                ('220002', 'Bela', 'X IPA 2', 'Jl. Melati', '0822222222','2.jpg'),
                ('220003', 'Citra', 'XI IPS 1', 'Jl. Kenanga', '0833333333','3.jpg'),
                ('220004', 'Dodi', 'XI IPA 3', 'Jl. Dahlia', '0844444444','4.jpg'),
                ('220005', 'Eka', 'XII IPA 1', 'Jl. Anggrek', '0855555555','5.jpg')
            ]
            cursor.executemany("INSERT OR IGNORE INTO tbl_siswa (nis, nama_siswa, kelas, alamat, hp_siswa, photo) VALUES (?, ?, ?, ?, ?, ?)", siswa_data)

            # Buku
            buku_data = [
                ('BK001', '9781234567001', 'Python Dasar', 'Slamet', 'Gramedia', '2020', 10, '1.jpg'),
                ('BK002', '9781234567002', 'Algoritma', 'Dewi', 'Erlangga', '2019', 5, '2.jpg'),
                ('BK003', '9781234567003', 'Struktur Data', 'Agus', 'Andi', '2021', 7, '3.jpg'),
                ('BK004', '9781234567004', 'Jaringan Komputer', 'Rudi', 'Salemba', '2022', 4, '4.jpg'),
                ('BK005', '9781234567005', 'Database', 'Sinta', 'Informatika', '2020', 6, '5.jpg')
            ]
            cursor.executemany("INSERT OR IGNORE INTO tbl_buku (kode_buku, isbn, judul, pengarang, penerbit, tahun_terbit, jumlah, cover) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", buku_data)

            # Ambil id_buku setelah insert
            cursor.execute("SELECT id_buku FROM tbl_buku ORDER BY id_buku")
            id_buku_list = [row[0] for row in cursor.fetchall()]

            # Buku detail: 5 detail per buku
            bukudetail_data = []
            counter = 1
            for id_buku in id_buku_list:
                for i in range(5):
                    kode = f"BKD{counter:04d}"
                    kondisi = 'Baik'
                    status = True
                    bukudetail_data.append((id_buku, kode, kondisi, status))
                    counter += 1
            cursor.executemany("INSERT OR IGNORE INTO tbl_bukudetail (id_buku, kode_bukudetail, kondisi, status) VALUES (?, ?, ?, ?)", bukudetail_data)

            # # Login
            # for i in range(1, 6):
            #     cursor.execute("INSERT OR IGNORE INTO tbl_login (id_petugas, waktu_login) VALUES (?, ?)", (i, datetime.now()))

            # # Peminjaman
            # for i in range(1, 6):
            #     cursor.execute("INSERT OR IGNORE INTO tbl_pinjam (id_siswa, id_petugas, waktu_pinjam, waktu_kembali) VALUES (?, ?, ?, ?)",
            #                 (i, i, datetime.now(), None))

            # # Ambil ulang id_pinjam
            # cursor.execute("SELECT id_pinjam FROM tbl_pinjam ORDER BY id_pinjam")
            # id_pinjam_list = [row[0] for row in cursor.fetchall()]

            # # Ambil daftar id_bukudetail dan id_buku
            # cursor.execute("SELECT id_bukudetail, id_buku FROM tbl_bukudetail WHERE status = 1 ORDER BY id_bukudetail")
            # bukudetail_available = cursor.fetchall()

            # # Atur agar setiap peminjaman terdiri dari 3 judul berbeda
            # pinjamdetail_data = []
            # used_bukudetail_ids = set()
            # per_pinjam = 3
            # detail_index = 0

            # for id_pinjam in id_pinjam_list:
            #     judul_terpakai = set()
            #     jumlah_ditambahkan = 0
            #     while jumlah_ditambahkan < per_pinjam and detail_index < len(bukudetail_available):
            #         id_bukudetail, id_buku = bukudetail_available[detail_index]
            #         detail_index += 1
            #         if id_bukudetail in used_bukudetail_ids:
            #             continue
            #         if id_buku in judul_terpakai:
            #             continue
            #         pinjamdetail_data.append((id_pinjam, id_bukudetail))
            #         used_bukudetail_ids.add(id_bukudetail)
            #         judul_terpakai.add(id_buku)
            #         jumlah_ditambahkan += 1

            # cursor.executemany("INSERT OR IGNORE INTO tbl_pinjamdetail (id_pinjam, id_bukudetail) VALUES (?, ?)", pinjamdetail_data)

            # # Update status buku detail menjadi 0 (dipinjam)
            # if used_bukudetail_ids:
            #     cursor.executemany("UPDATE tbl_bukudetail SET status = 0 WHERE id_bukudetail = ?", [(i,) for i in used_bukudetail_ids])

            # # Pengembalian
            # for i in range(1, 6):
            #     cursor.execute("INSERT OR IGNORE INTO tbl_kembali (id_siswa, id_petugas, waktu_kembali) VALUES (?, ?, ?)", (i, i, datetime.now()))

            # # Ambil id_kembali dan id_pinjamdetail
            # cursor.execute("SELECT id_kembali FROM tbl_kembali ORDER BY id_kembali")
            # id_kembali_list = [row[0] for row in cursor.fetchall()]

            # cursor.execute("SELECT id_pinjamdetail FROM tbl_pinjamdetail ORDER BY id_pinjamdetail")
            # id_pinjamdetail_list = [row[0] for row in cursor.fetchall()]

            # # Kembali detail: 5 per kembali
            # kembalidetail_data = []
            # detail_index = 0
            # for id_kembali in id_kembali_list:
            #     for _ in range(5):
            #         denda = 0 if detail_index % 2 == 0 else 1000
            #         kembalidetail_data.append((id_kembali, id_pinjamdetail_list[detail_index], denda))
            #         detail_index += 1
            # cursor.executemany("INSERT OR IGNORE INTO tbl_kembalidetail (id_kembali, id_pinjamdetail, denda) VALUES (?, ?, ?)", kembalidetail_data)

            koneksi.commit()

        except Exception as e:
            print("Terjadi kesalahan saat mengisi data:", e)

# Jalankan inisialisasi
init_db()
