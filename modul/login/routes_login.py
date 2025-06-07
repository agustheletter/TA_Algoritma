from flask import Blueprint, render_template
from database import connect_db
import sqlite3
from auth_utils import login_required
from datetime import datetime
import locale

# Set locale ke Indonesia (gunakan 'id_ID' atau 'indonesian' tergantung OS)
try:
    locale.setlocale(locale.LC_TIME, 'id_ID.utf8')  # Linux/macOS
except:
    try:
        locale.setlocale(locale.LC_TIME, 'indonesian')  # Windows
    except:
        pass  # fallback jika gagal

login_bp = Blueprint('login', __name__, template_folder='../templates/login')

@login_bp.route('/history_login')
@login_required
def login_tampil():
    with connect_db() as koneksi:
        koneksi.row_factory = sqlite3.Row
        hasil = koneksi.execute("""
            SELECT l.id_login, l.id_petugas, l.waktu_login, p.nama_petugas
            FROM tbl_login l
            JOIN tbl_petugas p ON l.id_petugas = p.id_petugas
            ORDER BY l.waktu_login DESC
        """).fetchall()

        # Format waktu ke format Indonesia
        history_login = []
        for row in hasil:
            waktu_obj = datetime.fromisoformat(row['waktu_login'])
            waktu_format = waktu_obj.strftime('%d %B %Y %H:%M:%S')  # Contoh: 26 Mei 2025 14:30:55
            history_login.append({
                'id_login': row['id_login'],
                'nama_petugas': row['nama_petugas'],
                'waktu_login': waktu_format
            })

    return render_template('login/history_login.html', history_login=history_login)
