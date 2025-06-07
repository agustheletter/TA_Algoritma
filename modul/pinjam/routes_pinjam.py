from flask import Blueprint, render_template, request, redirect, url_for, session

from database import connect_db

import sqlite3

from auth_utils import login_required

pinjam_bp = Blueprint('pinjam', __name__, template_folder='../templates/pinjam')


# AWAL CRUD pinjam
# route dan fungsi pinjam tampil
@pinjam_bp.route('/pinjam')
@login_required
def pinjam_tampil():
    koneksi = connect_db()

    # untuk akses pakai nama kolom database
    koneksi.row_factory = sqlite3.Row  

    pinjam = koneksi.execute("""
        SELECT 
            tp.id_pinjam, 
            tp.waktu_pinjam, 
            tp.waktu_kembali,
            ts.nis, 
            ts.nama_siswa, 
            tpe.nama_petugas,
            GROUP_CONCAT(
                tpd.id_pinjamdetail || '|' || 
                tbd.kode_bukudetail || '|' || 
                tb.judul || '|' ||
                CASE 
                    WHEN tkd.id_kembalidetail IS NOT NULL THEN 'Sudah Dikembalikan'
                    ELSE 'Masih Dipinjam'
                END, 
            ', ') AS daftar_buku
        FROM tbl_pinjam tp
        JOIN tbl_siswa ts ON tp.id_siswa = ts.id_siswa
        JOIN tbl_petugas tpe ON tp.id_petugas = tpe.id_petugas
        JOIN tbl_pinjamdetail tpd ON tp.id_pinjam = tpd.id_pinjam
        JOIN tbl_bukudetail tbd ON tpd.id_bukudetail = tbd.id_bukudetail
        JOIN tbl_buku tb ON tbd.id_buku = tb.id_buku
        LEFT JOIN tbl_kembalidetail tkd ON tpd.id_pinjamdetail = tkd.id_pinjamdetail  -- LEFT JOIN ke tbl_kembalidetail
        GROUP BY tp.id_pinjam
        ORDER BY tp.waktu_pinjam DESC
    """).fetchall()
    
    koneksi.close()
    return render_template('pinjam/pinjam_tampil.html', pinjam=pinjam)

# route dan fungsi pinjam tambah
@pinjam_bp.route('/pinjamtambah', methods=['GET', 'POST'])
@login_required
def pinjam_tambah():
    if request.method == 'POST':
        id_siswa = request.form['id_siswa']
        # id_petugas = request.form['id_petugas']
        waktu_pinjam = request.form['waktu_pinjam']
        waktu_kembali = request.form['waktu_kembali']

        # Ambil id_petugas dari session
        id_petugas = session.get('id_petugas')

        # Ambil daftar ID buku dari checkbox atau multiselect
        id_bukudetail_list = request.form.getlist('id_bukudetail')

        with connect_db() as koneksi:
            # Inisialisasi cursor
            cursor = koneksi.cursor()  
            cursor.execute(
                "INSERT INTO tbl_pinjam (id_siswa, id_petugas, waktu_pinjam, waktu_kembali) VALUES (?, ?, ?, ?)",
                (id_siswa, id_petugas, waktu_pinjam, waktu_kembali)
            )

            # Dapatkan id dari pinjam yang baru
            id_pinjam_baru = cursor.lastrowid 
            
            # Simpan ke tbl_pinjamdetail untuk setiap buku
            for id_bukudetail in id_bukudetail_list:
                cursor.execute(
                    "INSERT INTO tbl_pinjamdetail (id_pinjam, id_bukudetail) VALUES (?, ?)",
                    (id_pinjam_baru, id_bukudetail))
                
                # Mengubah status Tersedia menjadi Dipinjam
                cursor.execute(
                    "UPDATE tbl_bukudetail SET status=? WHERE id_bukudetail=?",
                    (0, id_bukudetail))

            koneksi.commit()

        return redirect(url_for('pinjam.pinjam_tampil'))

    # Jika GET, ambil data siswa dan petugas untuk ditampilkan di form
    koneksi = connect_db()
    siswa = koneksi.execute("SELECT * FROM tbl_siswa").fetchall()
    petugas = koneksi.execute("SELECT * FROM tbl_petugas").fetchall()
    bukudetail = koneksi.execute("SELECT * FROM tbl_bukudetail JOIN tbl_buku ON tbl_buku.id_buku=tbl_bukudetail.id_buku WHERE status=?",(True,)).fetchall()
    koneksi.close()

    return render_template('pinjam/pinjam_tambah.html', siswa=siswa, petugas=petugas, bukudetail=bukudetail)


# route dan fungsi pinjam edit
@pinjam_bp.route('/pinjam/edit/<int:id_pinjam>', methods=['GET', 'POST'])
@login_required
def pinjam_edit(id_pinjam):
    koneksi = connect_db()
    if request.method == 'POST':
        id_siswa = request.form['nis']
        id_petugas = request.form['nama_pinjam']
        waktu_pinjam = request.form['kelas']
        waktu_kembali = request.form['alamat']
        id_buku = request.form['hp_pinjam']
        koneksi.execute("UPDATE tbl_pinjam SET nis=?, nama_pinjam=?, kelas=?, alamat=?, hp_pinjam=? WHERE id_pinjam=?", (nis, nama_pinjam, kelas, alamat, hp_pinjam, id_pinjam))
        koneksi.commit()
        koneksi.close()
        return redirect(url_for('pinjam.pinjam_tampil'))
    pinjam = koneksi.execute("SELECT * FROM tbl_pinjam WHERE id_pinjam=?", (id_pinjam,)).fetchone()
    koneksi.close()
    return render_template('pinjam/pinjam_edit.html', pinjam=pinjam)

# route dan fungsi pinjam hapus
# @pinjam_bp.route('/pinjam/hapus/<int:id_pinjam>')
# def pinjam_hapus(id_pinjam):
#     with connect_db() as koneksi:
#         koneksi.execute("DELETE FROM tbl_pinjam WHERE id_pinjam=?", (id_pinjam,))
#     return redirect(url_for('pinjam.pinjam_tampil'))

@pinjam_bp.route('/pinjam/hapus/<int:id_pinjamdetail>')
@login_required
def pinjam_hapus(id_pinjamdetail):


    with connect_db() as koneksi:
        # ambil id_bukudetail yang dihapus dari tabel tbl_pinjamdetail
        pinjamdetail=koneksi.execute("SELECT id_bukudetail FROM tbl_pinjamdetail WHERE id_pinjamdetail=?",(id_pinjamdetail,)).fetchone()
        id_bukudetail=pinjamdetail[0]

        koneksi.execute("DELETE FROM tbl_pinjamdetail WHERE id_pinjamdetail=?", (id_pinjamdetail,))

        koneksi.execute("UPDATE tbl_bukudetail SET status=? WHERE id_bukudetail=?", (1,id_bukudetail,))
    return redirect(url_for('pinjam.pinjam_tampil'))

# AKHIR CRUD pinjam