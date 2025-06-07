from flask import Blueprint, render_template, request, redirect, url_for, session

from database import connect_db
from auth_utils import login_required

petugas_bp = Blueprint('petugas', __name__, template_folder='../templates/petugas')

# AWAL CRUD petugas
# route dan fungsi petugas tampil
@petugas_bp.route('/petugas')
@login_required
def petugas_tampil():
    if 'role' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))  # Atau tampilkan pesan akses ditolak
    
    koneksi = connect_db()
    petugas = koneksi.execute("SELECT * FROM tbl_petugas").fetchall()
    koneksi.close()
    return render_template('petugas/petugas_tampil.html', petugas=petugas)


# route dan fungsi petugas tambah
@petugas_bp.route('/petugastambah', methods=['GET', 'POST'])
@login_required
def petugas_tambah():
    if 'role' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))  # Atau tampilkan pesan akses ditolak
    
    if request.method == 'POST':
        data = (
            request.form['nip'],
            request.form['nama_petugas'],
            request.form['username'],
            request.form['password'],
            request.form['role']
        )
        with connect_db() as koneksi:
            koneksi.execute("""
                INSERT INTO tbl_petugas 
                (nip, nama_petugas, username, password, role) 
                VALUES (?, ?, ?, ?, ?)""", data)
        
            koneksi.commit()
        return redirect(url_for('petugas.petugas_tampil'))
    return render_template('petugas/petugas_tambah.html')

# route dan fungsi petugas edit
@petugas_bp.route('/petugas/edit/<int:id_petugas>', methods=['GET', 'POST'])
@login_required
def petugas_edit(id_petugas):
    if 'role' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))  # Atau tampilkan pesan akses ditolak
    
    koneksi = connect_db()
    if request.method == 'POST':
        nip = request.form['nip']
        nama_petugas = request.form['nama_petugas']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        koneksi.execute("UPDATE tbl_petugas SET nip=?, nama_petugas=?, username=?, password=?, role=? WHERE id_petugas=?", (nip, nama_petugas, username, password, role, id_petugas))
        koneksi.commit()
        koneksi.close()
        return redirect(url_for('petugas.petugas_tampil'))
    petugas = koneksi.execute("SELECT * FROM tbl_petugas WHERE id_petugas=?", (id_petugas,)).fetchone()
    koneksi.close()
    return render_template('petugas/petugas_edit.html', petugas=petugas)

# route dan fungsi petugas hapus
@petugas_bp.route('/petugas/hapus/<int:id_petugas>')
@login_required
def petugas_hapus(id_petugas):
    if 'role' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))  # Atau tampilkan pesan akses ditolak
    
    with connect_db() as koneksi:
        koneksi.execute("DELETE FROM tbl_petugas WHERE id_petugas=?", (id_petugas,))
    return redirect(url_for('petugas.petugas_tampil'))

# AKHIR CRUD petugas
