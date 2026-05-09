from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import qrcode
import os


app = Flask(__name__)

def connect_db():
    return sqlite3.connect("database.db")

def generate_qr(nomor_seri):
    # URL verifikasi (sementara lokal)
    url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"

    # Pastikan folder static/qr ada
    qr_folder = "static/qr"
    os.makedirs(qr_folder, exist_ok=True)

    # Generate QR
    img = qrcode.make(url)

    # Simpan file
    file_path = os.path.join(qr_folder, f"{nomor_seri}.png")
    img.save(file_path)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sertifikat (
        nomor_seri TEXT PRIMARY KEY,
        nama TEXT,
        jenis TEXT,
        kegiatan TEXT,
        tanggal TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()



def generate_nomor_seri(jenis):
    tahun = datetime.now().year

    kode = {
        "Peserta": "PST",
        "Pemateri": "PMT",
        "Panitia": "PNT"
    }.get(jenis, "UNK")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nomor_seri
        FROM sertifikat
        WHERE nomor_seri LIKE ?
        ORDER BY nomor_seri DESC
        LIMIT 1
    """, (f"PLPN-{tahun}-{kode}-%",))

    last = cursor.fetchone()
    conn.close()

    if last:
        last_number = int(last[0].split("-")[-1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"PLPN-{tahun}-{kode}-{str(next_number).zfill(4)}"
    
# =========================
# ROUTE VERIFIKASI (WAJIB)
# =========================
@app.route("/verifikasi/<nomor_seri>")
def verifikasi(nomor_seri):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT nama, jenis, kegiatan, tanggal, status
    FROM sertifikat
    WHERE nomor_seri = ?
    """, (nomor_seri,))
    data = cursor.fetchone()
    conn.close()

    if data:
        nama, jenis, kegiatan, tanggal, status = data
        return render_template(
            "verifikasi.html",
            status=status,
            nama=nama,
            jenis=jenis,
            kegiatan=kegiatan,
            tanggal=tanggal,
            nomor_seri=nomor_seri
        )
    else:
        return render_template(
            "verifikasi.html",
            status="TIDAK VALID",
            nomor_seri=nomor_seri
        )


# ======================
# PANEL ADMIN
# ======================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        nama = request.form["nama"]
        jenis = request.form["jenis"]
        kegiatan = request.form["kegiatan"]
        tanggal = request.form["tanggal"]

        nomor_seri = generate_nomor_seri(jenis)
        status = "VALID"

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sertifikat
            (nomor_seri, nama, jenis, kegiatan, tanggal, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nomor_seri, nama, jenis, kegiatan, tanggal, status))
        conn.commit()
        conn.close()

        # ✅ GENERATE QR OTOMATIS
        generate_qr(nomor_seri)

        return redirect("/admin")

    return render_template("admin.html")



if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)