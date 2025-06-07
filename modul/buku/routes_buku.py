from flask import Blueprint, render_template, request, redirect, url_for
from database import connect_db
import sqlite3
from auth_utils import login_required



import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'gambar', 'buku')  # Sesuaikan path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


buku_bp = Blueprint('buku', __name__, template_folder='../templates/buku')


# AWAL CRUD buku
# route dan fungsi buku tampil
@buku_bp.route('/buku')
@login_required
def buku_tampil():
    
    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row  
        buku = koneksi.execute("SELECT * FROM tbl_buku").fetchall()
    return render_template('buku/buku_tampil.html', buku=buku)

# route dan fungsi buku tambah
@buku_bp.route('/bukutambah', methods=['GET', 'POST'])
@login_required
def buku_tambah():
    if request.method == 'POST':

        file = request.files['cover']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        kode_buku = request.form['kode_buku']
        jumlah = int(request.form['jumlah'])

        data = (
            kode_buku,
            request.form['isbn'],
            request.form['judul'],
            request.form['pengarang'],
            request.form['penerbit'],
            request.form['tahun_terbit'],
            jumlah,
            filename
        )

        with connect_db() as koneksi:
            cursor = koneksi.cursor()  # ✅ Tambahkan baris ini

            # Simpan ke tbl_buku
            cursor.execute("""
                INSERT INTO tbl_buku 
                (kode_buku, isbn, judul, pengarang, penerbit, tahun_terbit, jumlah, cover) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", data)

            # Dapatkan ID buku terakhir
            id_buku = cursor.lastrowid

            # Tambah ke tbl_bukudetail sebanyak jumlah
            for i in range(1, jumlah + 1):
                kode_bukudetail = f"{kode_buku}-{i:03}"  # contoh: BK001-001
                cursor.execute("""
                    INSERT INTO tbl_bukudetail 
                    (id_buku, kode_bukudetail, kondisi, status) 
                    VALUES (?, ?, ?, ?)""",
                    (id_buku, kode_bukudetail, 'Baik', True)
                )

            koneksi.commit()

        return redirect(url_for('buku.buku_tampil'))

    return render_template('buku/buku_tambah.html')

# route dan fungsi buku edit
@buku_bp.route('/buku/edit/<int:id_buku>', methods=['GET', 'POST'])
@login_required
def buku_edit(id_buku):
    koneksi = connect_db()
    if request.method == 'POST':
        kode_buku = request.form['kode_buku']
        isbn = request.form['isbn']
        judul = request.form['judul']
        pengarang = request.form['pengarang']
        penerbit = request.form['penerbit']
        tahun_terbit = request.form['tahun_terbit']
        jumlah = request.form['jumlah']
    
        # ambil file cover
        cover = request.files['cover']
        if cover and cover.filename != '':
            filename = secure_filename(cover.filename)
            cover.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            # Gunakan cover lama jika tidak ada file baru
            filename = buku['cover']


        koneksi.execute("UPDATE tbl_buku SET kode_buku=?, isbn=?, judul=?, pengarang=?, penerbit=?, tahun_terbit=?, jumlah=?, cover=? WHERE id_buku=?", (kode_buku, isbn, judul, pengarang, penerbit, tahun_terbit, jumlah, filename, id_buku))
        koneksi.commit()
        koneksi.close()
        return redirect(url_for('buku.buku_tampil'))
    buku = koneksi.execute("SELECT * FROM tbl_buku WHERE id_buku=?", (id_buku,)).fetchone()
    koneksi.close()
    return render_template('buku/buku_edit.html', buku=buku)

# route dan fungsi buku hapus
@buku_bp.route('/buku/hapus/<int:id_buku>')
@login_required
def buku_hapus(id_buku):
    with connect_db() as koneksi:
        koneksi.execute("DELETE FROM tbl_buku WHERE id_buku=?", (id_buku,))
    return redirect(url_for('buku.buku_tampil'))


# route dan fungsi bukudetail tampil
@buku_bp.route('/bukudetail/<int:id_buku>')
@login_required
def bukudetail_tampil(id_buku):
    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row

        # Data buku utama
        buku = koneksi.execute("SELECT * FROM tbl_buku WHERE id_buku=?", (id_buku,)).fetchone()

        # Semua detail buku
        bukudetail = koneksi.execute("SELECT * FROM tbl_bukudetail WHERE id_buku=?", (id_buku,)).fetchall()

    return render_template('buku/bukudetail_tampil.html', buku=buku, bukudetail=bukudetail)




# route dan fungsi bukudetail edit
@buku_bp.route('/bukudetail_edit/<int:id_bukudetail>', methods=['POST'])
@login_required
def bukudetail_edit(id_bukudetail):
    kode_bukudetail = request.form['kode_bukudetail']
    kondisi = request.form['kondisi']
    status = request.form['status']

    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row
        koneksi.execute(
            "UPDATE tbl_bukudetail SET kode_bukudetail=?, kondisi=?, status=? WHERE id_bukudetail=?",
            (kode_bukudetail, kondisi, status, id_bukudetail)
        )

        # Ambil kembali data yang sudah diperbarui
        bukudetail = koneksi.execute(
            "SELECT * FROM tbl_bukudetail WHERE id_bukudetail=?", (id_bukudetail,)
        ).fetchone()

        id_buku = bukudetail['id_buku']

    # return render_template('buku/bukudetail_edit.html', bukudetail=bukudetail, id_buku=id_buku)
    return redirect(url_for('buku.bukudetail_tampil', id_buku=id_buku))





# route dan fungsi bukudetail hapus
@buku_bp.route('/bukudetail_hapus/<int:id_bukudetail>')
@login_required
def bukudetail_hapus(id_bukudetail):
    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row

        # Ambil data bukudetail
        bukudetail = koneksi.execute(
            "SELECT * FROM tbl_bukudetail WHERE id_bukudetail=?",
            (id_bukudetail,)
        ).fetchone()

        if bukudetail is None:
            return "Data detail buku tidak ditemukan", 404

        id_buku = bukudetail['id_buku']


        # Hapus data
        koneksi.execute("DELETE FROM tbl_bukudetail WHERE id_bukudetail=?", (id_bukudetail,))


        # Hitung jumlah sisa detail buku setelah penghapusan
        sisa_jumlah = koneksi.execute(
            "SELECT COUNT(*) FROM tbl_bukudetail WHERE id_buku=?",
            (id_buku,)
        ).fetchone()[0]

        # Update jumlah di tbl_buku
        koneksi.execute("UPDATE tbl_buku SET jumlah=? WHERE id_buku=?", (sisa_jumlah, id_buku))

        koneksi.commit()

        # Ambil data buku utama
        buku = koneksi.execute(
            "SELECT * FROM tbl_buku WHERE id_buku=?",
            (id_buku,)
        ).fetchone()

        # Ambil daftar detail buku lainnya untuk ditampilkan
        daftar_detail = koneksi.execute(
            "SELECT * FROM tbl_bukudetail WHERE id_buku=?",
            (id_buku,)
        ).fetchall()

    return render_template(
        'buku/bukudetail_tampil.html',
        buku=buku,
        bukudetail=daftar_detail
    )


# AKHIR CRUD buku