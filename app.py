from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_data(nomor_seri):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nama, jenis, kegiatan, tanggal, status
        FROM sertifikat
        WHERE nomor_seri = ?
    """, (nomor_seri,))
    data = cursor.fetchone()
    conn.close()
    return data

@app.route("/verifikasi/<nomor_seri>")
def verifikasi(nomor_seri):
    data = get_data(nomor_seri)

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

if __name__ == "__main__":
    app.run(debug=True)