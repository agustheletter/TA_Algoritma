from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

from database import connect_db

from datetime import datetime

import sqlite3



from auth_utils import login_required

kembali_bp = Blueprint('kembali', __name__, template_folder='../templates/kembali')


# AWAL CRUD kembali
from flask import request, render_template
from datetime import datetime, timedelta

@kembali_bp.route('/kembali', methods=['GET', 'POST'])
@login_required
def kembali_tampil():
    koneksi = connect_db()
    koneksi.row_factory = sqlite3.Row

    siswa = koneksi.execute("SELECT * FROM tbl_siswa").fetchall()
    daftar_buku = []
    terlambat = False
    jumlah_hari = 0
    denda = 0
    total_denda = 0  

    from datetime import datetime

    if request.method == 'POST':
        id_siswa = request.form.get('id_siswa')
        waktu_kembali = request.form.get('waktu_kembali')
        buku_terpilih = request.form.getlist('buku_terpilih[]')

        id_petugas = session.get('id_petugas')  # Harus diset saat login

        if id_siswa and buku_terpilih and id_petugas:
            cur = koneksi.cursor()

            # Simpan ke tbl_kembali
            cur.execute("""
                INSERT INTO tbl_kembali (id_siswa, id_petugas, waktu_kembali)
                VALUES (?, ?, ?)
            """, (id_siswa, id_petugas, waktu_kembali))
            id_kembali = cur.lastrowid

            total_denda = 0

            # for kode in buku_terpilih:
            for id_bukudetail in buku_terpilih:
                detail = cur.execute("""
                    SELECT * FROM tbl_pinjamdetail
                    JOIN tbl_bukudetail ON tbl_bukudetail.id_bukudetail = tbl_pinjamdetail.id_bukudetail
                    JOIN tbl_buku ON tbl_buku.id_buku = tbl_bukudetail.id_buku
                    JOIN tbl_pinjam ON tbl_pinjam.id_pinjam = tbl_pinjamdetail.id_pinjam
                    JOIN tbl_siswa ON tbl_siswa.id_siswa = tbl_pinjam.id_siswa
                    JOIN tbl_petugas ON tbl_petugas.id_petugas = tbl_pinjam.id_petugas
                    LEFT JOIN tbl_kembalidetail ON tbl_pinjamdetail.id_pinjamdetail = tbl_kembalidetail.id_pinjamdetail
                    WHERE tbl_siswa.id_siswa = ?
                    AND tbl_bukudetail.id_bukudetail = ?
                    AND tbl_bukudetail.status = 0
                    AND tbl_kembalidetail.id_kembalidetail IS NULL
                """, (id_siswa, id_bukudetail)).fetchone()



                if detail:
                    waktu_pinjam = datetime.fromisoformat(detail["waktu_pinjam"])
                    keterlambatan = max(0, (datetime.now() - waktu_pinjam).days - 7)
                    denda = keterlambatan * 1000
                    total_denda += denda

                    # Simpan ke tbl_kembalidetail
                    cur.execute("""
                        INSERT INTO tbl_kembalidetail (id_kembali, id_pinjamdetail, denda)
                        VALUES (?, ?, ?)
                    """, (id_kembali, detail["id_pinjamdetail"], denda))

                    print(f"Kembali: {id_kembali}, Pinjamdetail: {detail['id_pinjamdetail']}, Denda: {denda}")


                    # Update status buku menjadi tersedia
                    cur.execute("""
                        UPDATE tbl_bukudetail SET status = 1 WHERE id_bukudetail = ?
                    """, (id_bukudetail,))
                    

            koneksi.commit()
            koneksi.close()
            # return redirect(url_for('kembali.kembali_tampil'))
            # return redirect(url_for('kembali.cetak_nota', id_kembali=id_kembali))
        
            # ================== CETAK NOTA LANGSUNG =====================
            import win32print
            import win32ui

            printer_name = win32print.GetDefaultPrinter()
            hprinter = win32print.OpenPrinter(printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_name)
            pdc.StartDoc("Nota Pengembalian")
            pdc.StartPage()

            y = 100
            pdc.TextOut(100, y, "*** NOTA PENGEMBALIAN ***")
            y += 100
            pdc.TextOut(100, y, f"Siswa: {id_siswa}")
            y += 100
            pdc.TextOut(100, y, f"ID Kembali: {id_kembali}")
            y += 100
            pdc.TextOut(100, y, f"Total Denda: Rp {total_denda}")

            y += 200
            pdc.TextOut(100, y, "Terima kasih telah mengembalikan buku.")
            pdc.EndPage()
            pdc.EndDoc()
            pdc.DeleteDC()
            # ============================================================

            return redirect(url_for('kembali.cetak_nota', id_kembali=id_kembali))


        

    return render_template(
        'kembali/kembali_tampil.html',
        siswa=siswa,
        daftar_buku=daftar_buku,
        terlambat=terlambat,
        jumlah_hari=jumlah_hari,
        denda=denda,
        total_denda=total_denda
    )



@kembali_bp.route('/kembali/get_buku/<int:id_siswa>')
@login_required
def get_buku_by_siswa(id_siswa):
    koneksi = connect_db()
    koneksi.row_factory = sqlite3.Row

    pinjam = koneksi.execute("""
        SELECT * FROM tbl_pinjamdetail
        JOIN tbl_bukudetail ON tbl_bukudetail.id_bukudetail = tbl_pinjamdetail.id_bukudetail
        JOIN tbl_buku ON tbl_buku.id_buku = tbl_bukudetail.id_buku
        JOIN tbl_pinjam ON tbl_pinjam.id_pinjam = tbl_pinjamdetail.id_pinjam
        JOIN tbl_siswa ON tbl_siswa.id_siswa = tbl_pinjam.id_siswa
        JOIN tbl_petugas ON tbl_petugas.id_petugas = tbl_pinjam.id_petugas
        LEFT JOIN tbl_kembalidetail ON tbl_pinjamdetail.id_pinjamdetail = tbl_kembalidetail.id_pinjamdetail
        WHERE tbl_siswa.id_siswa = ?
        AND tbl_bukudetail.status = 0
        AND tbl_kembalidetail.id_kembalidetail IS NULL
    """, (id_siswa,)).fetchall()

    koneksi.close()

    result = [
        {
            'id_pinjamdetail': row['id_pinjamdetail'],
            'id_bukudetail': row['id_bukudetail'],
            'kode_bukudetail': row['kode_bukudetail'],
            'judul': row['judul'],
            'petugas': row['nama_petugas'],
            'waktu_pinjam': row['waktu_pinjam'],
        } for row in pinjam
    ]

    return jsonify(result)




@kembali_bp.route('/kembali_list', methods=['GET'])
@login_required
def kembali_list():
    koneksi = connect_db()
    koneksi.row_factory = sqlite3.Row

    rows = koneksi.execute("""
        SELECT 
            tbl_kembali.id_kembali,
            tbl_kembali.waktu_kembali,
            tbl_siswa.nis,
            tbl_siswa.nama_siswa,
            tbl_petugas.nama_petugas,
            tbl_pinjam.id_pinjam,
            tbl_buku.judul,
            tbl_bukudetail.kode_bukudetail,
            tbl_kembalidetail.denda
        FROM tbl_kembalidetail
        JOIN tbl_kembali ON tbl_kembali.id_kembali = tbl_kembalidetail.id_kembali
        JOIN tbl_siswa ON tbl_kembali.id_siswa = tbl_siswa.id_siswa
        JOIN tbl_petugas ON tbl_kembali.id_petugas = tbl_petugas.id_petugas                       
        JOIN tbl_pinjamdetail ON tbl_pinjamdetail.id_pinjamdetail = tbl_kembalidetail.id_pinjamdetail
        JOIN tbl_bukudetail ON tbl_bukudetail.id_bukudetail = tbl_pinjamdetail.id_bukudetail
        JOIN tbl_buku ON tbl_bukudetail.id_buku = tbl_buku.id_buku
        JOIN tbl_pinjam ON tbl_pinjam.id_pinjam = tbl_pinjamdetail.id_pinjam
        ORDER BY tbl_kembali.id_kembali DESC
    """).fetchall()

    # Kelompokkan data berdasarkan id_kembali
    grouped = {}
    for row in rows:
        id_kembali = row['id_kembali']
        if id_kembali not in grouped:
            grouped[id_kembali] = {
                'id_pinjam': row['id_pinjam'],
                'nis': row['nis'],
                'nama_siswa': row['nama_siswa'],
                'waktu_kembali': row['waktu_kembali'],
                'nama_petugas': row['nama_petugas'],
                'details': []
            }
        grouped[id_kembali]['details'].append({
            'judul': row['judul'],
            'kode_bukudetail': row['kode_bukudetail'],
            'denda': row['denda']
        })

    return render_template(
        'kembali/kembali_list.html',
        kembali=grouped
    )


@kembali_bp.route('/nota/<int:id_kembali>')
@login_required
def cetak_nota(id_kembali):
    koneksi = connect_db()
    koneksi.row_factory = sqlite3.Row

    nota = koneksi.execute("""
        SELECT 
            tbl_kembali.id_kembali,
            tbl_kembali.waktu_kembali,
            tbl_siswa.nis,
            tbl_siswa.nama_siswa,
            tbl_petugas.nama_petugas
        FROM tbl_kembali
        JOIN tbl_siswa ON tbl_kembali.id_siswa = tbl_siswa.id_siswa
        JOIN tbl_petugas ON tbl_kembali.id_petugas = tbl_petugas.id_petugas
        WHERE tbl_kembali.id_kembali = ?
    """, (id_kembali,)).fetchone()

    detail = koneksi.execute("""
        SELECT 
            tbl_buku.judul,
            tbl_bukudetail.kode_bukudetail,
            tbl_kembalidetail.denda
        FROM tbl_kembalidetail
        JOIN tbl_pinjamdetail ON tbl_kembalidetail.id_pinjamdetail = tbl_pinjamdetail.id_pinjamdetail
        JOIN tbl_bukudetail ON tbl_pinjamdetail.id_bukudetail = tbl_bukudetail.id_bukudetail
        JOIN tbl_buku ON tbl_bukudetail.id_buku = tbl_buku.id_buku
        WHERE tbl_kembalidetail.id_kembali = ?
    """, (id_kembali,)).fetchall()

    total_denda = sum([d['denda'] for d in detail])

    return render_template(
        'kembali/nota.html',
        nota=nota,
        detail=detail,
        total_denda=total_denda
    )
