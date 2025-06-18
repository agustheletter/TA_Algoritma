from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from database import init_db
from modul.siswa.routes_siswa import siswa_bp
from modul.petugas.routes_petugas import petugas_bp
from modul.buku.routes_buku import buku_bp
from modul.pinjam.routes_pinjam import pinjam_bp
from modul.kembali.routes_kembali import kembali_bp
from modul.login.routes_login import login_bp
from modul.beranda.routes_beranda import beranda_bp
import sqlite3
import os
from functools import wraps
from datetime import datetime


app = Flask(__name__)

app.secret_key = 'rahasia'  # dibutuhkan untuk session

# Init database
init_db()




# Register Blueprint
app.register_blueprint(siswa_bp)
app.register_blueprint(petugas_bp)
app.register_blueprint(buku_bp)
app.register_blueprint(pinjam_bp)
app.register_blueprint(kembali_bp)
app.register_blueprint(login_bp)
app.register_blueprint(beranda_bp)

# @app.route('/')
# def index():
#     return render_template('index.html')


def connect_db():
    return sqlite3.connect('perpustakaan_python.db')



# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'login' not in session:
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response



@app.route('/')
def index():
    if 'login' in session:
        return render_template('index.html', nama=session['nama_petugas'])
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'login' in session:
        return redirect(url_for('index'))  # <- Redirect jika sudah login

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        koneksi = connect_db()
        koneksi.row_factory = sqlite3.Row

        petugas = koneksi.execute("""
            SELECT * FROM tbl_petugas 
            WHERE username = ? AND password = ?
        """, (username, password)).fetchone()

        koneksi.close()

        if petugas:
            session['login'] = True
            session['nama_petugas'] = petugas['nama_petugas']
            session['id_petugas'] = petugas['id_petugas']
            session['role'] = petugas['role']

            # Simpan ke table login
            with connect_db() as koneksi:
                cursor = koneksi.cursor()
                cursor.execute("""
                    INSERT INTO tbl_login 
                    (id_petugas, waktu_login) 
                    VALUES (?, ?)""", (petugas['id_petugas'], datetime.now()))
                koneksi.commit()

            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!', 'danger')
            return redirect(url_for('login'))

    # return render_template('login.html')
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
