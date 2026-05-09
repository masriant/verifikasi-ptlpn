from flask import Flask, render_template, request, redirect
import sqlite3
import qrcode
import os

app = Flask(__name__)

def connect_db():
    return sqlite3.connect("database.db")

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

def generate_qr(nomor_seri):
    url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"
    img = qrcode.make(url)

    path = f"static/qr/{nomor_seri}.png"
    img.save(path)

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
        nomor_seri = request.form["nomor_seri"]
        nama = request.form["nama"]
        jenis = request.form["jenis"]
        kegiatan = request.form["kegiatan"]
        tanggal = request.form["tanggal"]
        status = "VALID"

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO sertifikat
        (nomor_seri, nama, jenis, kegiatan, tanggal, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nomor_seri, nama, jenis, kegiatan, tanggal, status))
        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("admin.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)