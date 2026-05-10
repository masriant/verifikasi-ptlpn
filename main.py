from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import qrcode
import os
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.colors import HexColor

app = Flask(__name__)

# =====================
# DATABASE
# =====================
def connect_db():
    return sqlite3.connect("database.db")

# =====================
# NOMOR SERI & QR CODE
# =====================
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

# =====================
# SERTIFIKAT DUOLOGO
# =====================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os


def generate_pdf_sertifikat_duo(
    nomor_seri,
    nama,
    jenis,
    kegiatan,
    tanggal
):
    file_path = f"static/sertifikat-duo/{nomor_seri}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    emas = HexColor("#C9A227")
    abu = HexColor("#444444")

    # =====================
    # BORDER EMAS
    # =====================
    c.setStrokeColor(emas)

    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    c.setLineWidth(1.5)
    c.rect(45, 45, width - 90, height - 90)

    # =====================
    # LOGO KIRI (KOP)
    # =====================
    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        c.drawImage(
        logo_path,
        60,                 # kiri aman dari border
        height - 170,       # aman dari border atas
        width=70,
        height=70,
        mask='auto'
    )

    # =====================
    # JUDUL (TENGAH)
    # =====================
    c.setFillColor(emas)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 145, "SERTIFIKAT")

    c.setFillColor(abu)
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 175,
        "PT Lembaga Persada Nusantara"
    )

    # =====================
    # OPSIONAL: TEKS KANAN ATAS (JIKA MAU)
    # =====================
    c.setFont("Helvetica", 9)
    c.drawRightString(
        width - 60,
        height - 140,
        "Dokumen Resmi"
    )

    # =====================
    # JUDUL
    # =====================
    # c.setFillColor(emas)

    # c.setFont("Helvetica-Bold", 28)

    # c.drawCentredString(
    #     width / 2,
    #     height - 200,
    #     "SERTIFIKAT"
    # )

    # =====================
    # TEKS PEMBUKA
    # =====================
    c.setFillColor(abu)

    c.setFont("Helvetica", 13)

    c.drawCentredString(
        width / 2,
        height - 220,
        "Diberikan kepada:"
   )

    # =====================
    # NAMA
    # =====================
    c.setFont("Helvetica-Bold", 20)

    c.drawCentredString(
        width / 2,
        height - 245,
        nama
   )

    # =====================
    # KETERANGAN
    # =====================
    c.setFont("Helvetica", 12)

    c.drawCentredString(
        width / 2,
        height - 330,
        f"Sebagai {jenis} pada kegiatan"
   )

    c.setFont("Helvetica-Bold", 13)

    c.drawCentredString(
        width / 2,
        height - 355,
        kegiatan
    )

    c.setFont("Helvetica", 11)

    c.drawCentredString(
        width / 2,
        height - 385,
           f"Tanggal: {tanggal}"
        )

    c.setFont("Helvetica-Bold", 11)

    c.drawCentredString(
        width / 2,
        height - 410,
            "di Jakarta Pusat"
        )

    # =====================
    # NOMOR SERI
    # =====================
    c.setFont("Helvetica", 8)

    c.drawString(
        60,
        60,
            f"Nomor Seri: {nomor_seri}"
        )

    # =====================
    # QR CODE
    # =====================
    qr_path = f"static/qr/{nomor_seri}.png"

    if os.path.exists(qr_path):
        c.drawImage(
        qr_path,
            width - 150,
            70,
            width=90,
            height=90
        )

    # =====================
    # TANDA TANGAN
    # =====================
    ttd_path = "static/ttd-direktur.png"
    if os.path.exists(ttd_path):
        c.drawImage(
            ttd_path,
            width / 2 - 100,
            90,
            width=150,
            height=65,
            mask='auto'
        )

        # Nama & Jabatan
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width / 2 - 50, 90, "Direktur")

        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2 - 50, 75, "PT Lembaga Persada Nusantara")

        # =====================
        # STEMPEL
        # =====================
        stempel_path = "static/stempel.png"
        if os.path.exists(stempel_path):
            c.drawImage(
                stempel_path,
                width / 2,
                85,
                width=120,
                height=120,
                mask='auto'
            )

        # =====================
        # FOOTER
        # =====================
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(
            width / 2,
            50,
            "Sertifikat ini diterbitkan secara elektronik dan dapat diverifikasi melalui QR Code"
        )

        c.save()


# =====================
# SERTIFIKAT LOGO
# =====================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os

def generate_pdf_sertifikat_logo(nomor_seri, nama, jenis, kegiatan, tanggal):
    file_path = f"static/sertifikat-logo/{nomor_seri}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    emas = HexColor("#C9A227")
    abu = HexColor("#444444")

    # =====================
    # BORDER EMAS
    # =====================
    c.setStrokeColor(emas)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    c.setLineWidth(1.5)
    c.rect(45, 45, width - 90, height - 90)

    # =====================
    # LOGO (ATAS TENGAH)
    # =====================
    # logo_path = "static/logo.png"
    # if os.path.exists(logo_path):
    #     c.drawImage(
    #         logo_path,
    #         (width / 2) - 50,
    #         height - 110,
    #         width=100,
    #         height=100,
    #         mask='auto'
    #     )
    # =====================
    # LOGO (ATAS TENGAH - AMAN BORDER)
    # =====================
    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        logo_width = 95
        logo_height = 95

        c.drawImage(
            logo_path,
            (width - logo_width) / 2,
            height - 170,   # ✅ DITURUNKAN (AMAN)
            width=logo_width,
            height=logo_height,
            mask='auto'
        )
    # =====================
    # JUDUL
    # =====================
    c.setFillColor(emas)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 200, "SERTIFIKAT")

    c.setFillColor(abu)
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 220, "Diberikan kepada:")

    # =====================
    # NAMA
    # =====================
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 245, nama)

    # =====================
    # KETERANGAN
    # =====================
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 330,
            f"Sebagai {jenis} pada kegiatan"
        )

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, height - 355, kegiatan)

    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 385, f"Tanggal: {tanggal}")

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 410, f"di Jakarta Pusat")

    # =====================
    # NOMOR SERI
    # =====================
    c.setFont("Helvetica", 8)
    c.drawString(60, 60, f"Nomor Seri: {nomor_seri}")

    # =====================
    # QR CODE
    # =====================
    qr_path = f"static/qr/{nomor_seri}.png"
    if os.path.exists(qr_path):
        c.drawImage(qr_path, width - 150, 70, width=90, height=90)

    # =====================
    # TANDA TANGAN
    # =====================
    ttd_path = "static/ttd-direktur.png"
    if os.path.exists(ttd_path):
        c.drawImage(
            ttd_path,
            width / 2 - 100,
            90,
            width=150,
            height=65,
            mask='auto'
        )

    # Nama & Jabatan
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2 - 50, 90, "Direktur")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2 - 50, 75, "PT Lembaga Persada Nusantara")

    # =====================
    # STEMPEL
    # =====================
    stempel_path = "static/stempel.png"
    if os.path.exists(stempel_path):
        c.drawImage(
            stempel_path,
            width / 2,
            85,
            width=120,
            height=120,
            mask='auto'
        )
    # =====================
    # FOOTER
    # =====================
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(
            width / 2,
            50,
            "Sertifikat ini diterbitkan secara elektronik dan dapat diverifikasi melalui QR Code"
        )

    c.save()

# =====================
# SERTIFIKAT
# =====================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def generate_pdf_sertifikat(nomor_seri, nama, jenis, kegiatan, tanggal):
    file_path = f"static/sertifikat/{nomor_seri}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    emas = HexColor("#C9A227")   # emas elegan
    abu = HexColor("#444444")

    # =====================
    # BORDER EMAS
    # =====================
    c.setStrokeColor(emas)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    c.setLineWidth(1.5)
    c.rect(45, 45, width - 90, height - 90)

    # =====================
    # JUDUL
    # =====================
    c.setFillColor(emas)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 120, "SERTIFIKAT")

    c.setFillColor(abu)
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 155, "Diberikan kepada:")

    # =====================
    # NAMA
    # =====================
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 200, nama)

    # =====================
    # KETERANGAN
    # =====================
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 245,
        f"Sebagai {jenis} pada kegiatan"
    )

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, height - 270, kegiatan)

    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 300, f"Tanggal: {tanggal}")

    # =====================
    # NOMOR SERI
    # =====================
    c.setFont("Helvetica", 9)
    c.drawString(60, 70, f"Nomor Seri: {nomor_seri}")

    # =====================
    # QR CODE
    # =====================
    qr_path = f"static/qr/{nomor_seri}.png"
    c.drawImage(qr_path, width - 160, 60, width=90, height=90)

    # =====================
    # FOOTER
    # =====================
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2,
        55,
        "Sertifikat ini diterbitkan secara elektronik dan dapat diverifikasi melalui QR Code"
    )

    c.save()

# =====================
# KWITANSI
# =====================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf_kwitansi(nomor_seri, nama, jenis, kegiatan, tanggal):
    file_path = f"static/kwitansi/{nomor_seri}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Judul
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 100, "KWITANSI")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 140, "Diberikan kepada:")

    # Nama
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 180, nama)

    # Keterangan
    c.setFont("Helvetica", 11)
    c.drawCentredString(
        width / 2,
        height - 220,
        f"Sebagai {jenis} pada kegiatan"
    )

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 250, kegiatan)

    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 280, f"Tanggal: {tanggal}")

    # Nomor seri
    c.setFont("Helvetica", 9)
    c.drawString(50, 80, f"Nomor Seri: {nomor_seri}")

    # QR
    qr_path = f"static/qr/{nomor_seri}.png"
    c.drawImage(qr_path, width - 150, 60, width=90, height=90)

    c.save()

# =====================
# INISIALISASI DATABASE
# =====================
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


# =====================
# NOMOR SERI OTOMATIS
# =====================
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
        
        generate_pdf_sertifikat_duo(
            nomor_seri,
            nama,
            jenis,
            kegiatan,
            tanggal
        )
        
        generate_pdf_sertifikat_logo(
            nomor_seri,
            nama,
            jenis,
            kegiatan,
            tanggal
        )
        
        generate_pdf_sertifikat(
            nomor_seri,
            nama,
            jenis,
            kegiatan,
            tanggal
        )
        
        generate_pdf_kwitansi(
            nomor_seri,
            nama,
            jenis,
            kegiatan,
            tanggal
        )

        return redirect("/admin")

    return render_template("admin.html")



if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)