from flask import Blueprint, render_template
from database import connect_db
from auth_utils import login_required


beranda_bp = Blueprint('beranda', __name__, template_folder='../../templates/beranda')

@beranda_bp.route('/')
@login_required
def beranda():
    koneksi = connect_db()
    koneksi.row_factory = None  # kalau mau rows biasa, atau sqlite3.Row kalau mau dict-like

    # Ambil data buku (misal 5 buku dengan cover)
    buku = koneksi.execute("""
        SELECT judul, cover, jumlah, id_buku FROM tbl_buku
        WHERE cover IS NOT NULL AND cover != ''
        LIMIT 10
    """).fetchall()

    koneksi.close()

    # return render_template('beranda.html', buku=buku)

    return render_template('beranda.html', buku=buku, enumerate=enumerate)
