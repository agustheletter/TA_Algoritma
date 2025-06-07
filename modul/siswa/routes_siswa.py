from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import connect_db
import sqlite3
from auth_utils import login_required


import barcode
from barcode.writer import ImageWriter
import os

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'gambar', 'siswa')  # Sesuaikan path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


siswa_bp = Blueprint('siswa', __name__, template_folder='../templates/siswa')

# AWAL CRUD SISWA
# route dan fungsi siswa tampil
@siswa_bp.route('/siswa')
@login_required
def siswa_tampil():
    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row  
        siswa = koneksi.execute("SELECT * FROM tbl_siswa").fetchall()
    return render_template('siswa/siswa_tampil.html', siswa=siswa)
    

# route dan fungsi siswa tambah
@siswa_bp.route('/siswatambah', methods=['GET', 'POST'])
@login_required
def siswa_tambah():
    if request.method == 'POST':
        nis = request.form['nis']
        nama_siswa = request.form['nama_siswa']
        kelas = request.form['kelas']
        alamat = request.form['alamat']
        hp_siswa = request.form['hp_siswa']
        
        # Pertama: simpan data tanpa file foto dulu
        with connect_db() as koneksi:
            cursor = koneksi.cursor()
            cursor.execute("""
                INSERT INTO tbl_siswa (nis, nama_siswa, kelas, alamat, hp_siswa, photo) 
                VALUES (?, ?, ?, ?, ?, NULL)
            """, (nis, nama_siswa, kelas, alamat, hp_siswa))
            id_siswa = cursor.lastrowid  # ambil ID hasil insert
            koneksi.commit()
        
        # Kedua: proses upload file jika ada
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            ext = photo.filename.rsplit('.', 1)[1].lower()  # ambil ekstensi
            safe_name = secure_filename(nama_siswa.replace(" ", "_"))  # nama tanpa spasi
            filename_photo = f"{id_siswa}_{nis}_{safe_name}.{ext}"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            photo.save(os.path.join(UPLOAD_FOLDER, filename_photo))

            # Ketiga: update kolom photo
            with connect_db() as koneksi:
                koneksi.execute("UPDATE tbl_siswa SET photo=? WHERE id_siswa=?", (filename_photo, id_siswa))
                koneksi.commit()

        return redirect(url_for('siswa.siswa_tampil'))
    
    return render_template('siswa/siswa_tambah.html')


# route dan fungsi siswa edit
@siswa_bp.route('/siswa/edit/<int:id_siswa>', methods=['GET', 'POST'])
@login_required
def siswa_edit(id_siswa):
    koneksi = connect_db()
    koneksi.row_factory = sqlite3.Row
    siswa = koneksi.execute("SELECT * FROM tbl_siswa WHERE id_siswa=?", (id_siswa,)).fetchone()

    if request.method == 'POST':
        nis = request.form['nis']
        nama_siswa = request.form['nama_siswa']
        kelas = request.form['kelas']
        alamat = request.form['alamat']
        hp_siswa = request.form['hp_siswa']

        # Update data dasar
        koneksi.execute("""
            UPDATE tbl_siswa 
            SET nis=?, nama_siswa=?, kelas=?, alamat=?, hp_siswa=? 
            WHERE id_siswa=?
        """, (nis, nama_siswa, kelas, alamat, hp_siswa, id_siswa))

        # Proses update photo jika ada
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            ext = photo.filename.rsplit('.', 1)[1].lower()
            safe_name = secure_filename(nama_siswa.replace(" ", "_"))
            filename_photo = f"{id_siswa}_{nis}_{safe_name}.{ext}"

            # Hapus file lama jika ada
            if siswa['photo']:
                old_photo_path = os.path.join(UPLOAD_FOLDER, siswa['photo'])
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            # Simpan file baru
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            photo.save(os.path.join(UPLOAD_FOLDER, filename_photo))

            # Update field photo di database
            koneksi.execute("UPDATE tbl_siswa SET photo=? WHERE id_siswa=?", (filename_photo, id_siswa))

        koneksi.commit()
        koneksi.close()
        return redirect(url_for('siswa.siswa_tampil'))

    koneksi.close()
    return render_template('siswa/siswa_edit.html', siswa=siswa)





# route dan fungsi siswa hapus
@siswa_bp.route('/siswa/hapus/<int:id_siswa>')
@login_required
def siswa_hapus(id_siswa):
    with connect_db() as koneksi:
        koneksi.execute("DELETE FROM tbl_siswa WHERE id_siswa=?", (id_siswa,))
    return redirect(url_for('siswa.siswa_tampil'))

# AKHIR CRUD SISWA




# AWAL MEMBUAT KARTU SISWA
@siswa_bp.route('/kartu_siswa/<int:id_siswa>')
@login_required
def kartu_siswa(id_siswa):
    koneksi = connect_db()
    koneksi.row_factory = sqlite3.Row
    siswa = koneksi.execute("SELECT * FROM tbl_siswa WHERE id_siswa = ?", (id_siswa,)).fetchone()
    koneksi.close()

    # Generate barcode jika belum ada
    # from your_barcode_module import buat_barcode_nis  # sesuaikan dengan file kamu
    barcode_filename = buat_barcode_nis(siswa['nis'])

    return render_template('siswa/kartu_siswa.html', siswa=siswa, barcode=barcode_filename)




def buat_barcode_nis(nis, folder='static/gambar/kartu_siswa'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    kode = barcode.get('code128', str(nis), writer=ImageWriter())
    file_path = os.path.join(folder, f"{nis}.png")
    kode.save(file_path[:-4])  # remove .png because `save()` will add it
    return f"{nis}.png"

# AKHIR MEMBUAT KARTU SISWA



# CETAK KARTU SISWA MASAL
@siswa_bp.route('/cetak_batch_kartu', methods=['POST'])
@login_required
def cetak_batch_kartu():
    ids = request.form.getlist('id_siswa[]')
    if not ids:
        flash("Tidak ada siswa yang dipilih untuk dicetak.", "warning")
        return redirect(url_for('siswa.siswa_tampil'))

    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row
        format_ids = ','.join('?' for _ in ids)
        siswa_terpilih = koneksi.execute(
            f"SELECT * FROM tbl_siswa WHERE id_siswa IN ({format_ids})", ids
        ).fetchall()

    return render_template('siswa/cetak_kartu_batch.html', siswa=siswa_terpilih)
