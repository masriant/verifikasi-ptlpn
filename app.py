from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import qrcode
import os
from reportlab.lib.utils import ImageReader
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.colors import HexColor

app = Flask(__name__)

# =====================
# DATABASE
# =====================
def connect_db():
    return sqlite3.connect("database.db")

def draw_logo_scaled(c, image_path, x, y, max_w, max_h):
    if not os.path.exists(image_path):
        return

    img = ImageReader(image_path)
    iw, ih = img.getSize()

    scale = min(max_w / iw, max_h / ih)
    w = iw * scale
    h = ih * scale

    c.drawImage(
        image_path,
        x + (max_w - w) / 2,
        y + (max_h - h) / 2,
        width=w,
        height=h,
        mask='auto'
    )


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
# SERTIFIKAT DUOLOGO LANDSCAPE
# =====================
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
import os

def generate_pdf_sertifikat_landscape(nomor_seri, nama, jenis, kegiatan, tanggal):
    file_path = f"static/sertifikat/{nomor_seri}_LANDSCAPE.pdf"
    c = canvas.Canvas(file_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    emas = HexColor("#C9A227")
    abu = HexColor("#444444")

    # =====================
    # BORDER EMAS (AMAN)
    # =====================
    c.setStrokeColor(emas)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    c.setLineWidth(1.5)
    c.rect(45, 45, width - 90, height - 90)

    # =====================
    # LOGO KIRI–KANAN (AUTO-SCALE)
    # =====================
    draw_logo_scaled(c, "static/logo.png", x=60, y=height - 150, max_w=70, max_h=70)
    draw_logo_scaled(c, "static/logo.png", x=width - 130, y=height - 150, max_w=70, max_h=70)

    # =====================
    # JUDUL (TENGAH)
    # =====================
    c.setFillColor(emas)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 125, "SERTIFIKAT")

    c.setFillColor(abu)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 155, "PT Lembaga Persada Nusantara")

    # =====================
    # ISI (LEBIH LAPANG)
    # =====================
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 200, "Diberikan kepada:")

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 235, nama)

    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 275, f"Sebagai {jenis} pada kegiatan")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 305, kegiatan)

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 335, f"Tanggal: {tanggal}")

    # =====================
    # NOMOR SERI
    # =====================
    c.setFont("Helvetica", 9)
    c.drawString(60, 70, f"Nomor Seri: {nomor_seri}")

    # =====================
    # QR
    # =====================
    qr_path = f"static/qr/{nomor_seri}.png"
    if os.path.exists(qr_path):
        c.drawImage(qr_path, width - 160, 60, width=90, height=90, mask='auto')

    # =====================
    # TTD & STEMPEL
    # =====================
    ttd_path = "static/ttd-direktur.png"
    if os.path.exists(ttd_path):
        c.drawImage(ttd_path, width/2 - 140, 90, width=160, height=60, mask='auto')

    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2 - 60, 75, "Direktur")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2 - 60, 60, "PT Lembaga Persada Nusantara")

    stempel_path = "static/stempel.png"
    if os.path.exists(stempel_path):
        c.drawImage(stempel_path, width/2 + 10, 70, width=120, height=120, mask='auto')

    # =====================
    # FOOTER
    # =====================
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2, 50, # DITURUNKAN AGAR JARAK LEBIH LAPANG DENGAN LINK VERIFIKASI 45
        "Sertifikat ini diterbitkan secara elektronik dan dapat diverifikasi melalui QR Code"
    )

    # =====================
    # LINK VERIFIKASI (TEXT + CLICKABLE)
    # =====================
    verifikasi_url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"

    c.setFont("Helvetica", 9)
    c.setFillColor(abu)
    c.drawCentredString(
        width / 2,
        18, # DITURUNKAN AGAR JARAK LEBIH LAPANG DENGAN FOOTER 40
        "Verifikasi sertifikat:"
    )
    c.setFillColor(HexColor("#1f4e79"))
    c.drawCentredString(
        width / 2,
        8, # DITURUNKAN AGAR JARAK LEBIH LAPANG DENGAN FOOTER 28
        verifikasi_url
    )

    # Link aktif (bisa diklik di PDF)
    c.linkURL(
        verifikasi_url,
        (width/2 - 200, 8, width/2 + 200, 25),
        relative=0
    )

    c.save()
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
    # LOGO KIRI (PLPN)
    # =====================
    logo_plpn = "static/logo.png"
    if os.path.exists(logo_plpn):
        draw_logo_scaled(
            c,
            "static/logo.png",
            x=60,
            y=height - 170,
            max_w=70,
            max_h=70
        )

    # =====================
    # LOGO KANAN (MITRA)
    # =====================
    logo_mitra = "static/logo.png"
    if os.path.exists(logo_mitra):
        draw_logo_scaled(
            c,
            "static/logo.png",
            x=width - 130,
            y=height - 170,
            max_w=70,
            max_h=70
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

        # =====================
        # LINK VERIFIKASI (TEXT + CLICKABLE)
        # =====================
        verifikasi_url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"

        c.setFont("Helvetica", 9)
        c.setFillColor(abu)
        c.drawCentredString(
            width / 2,
            18,
            "Verifikasi sertifikat:"
        )
        c.setFillColor(HexColor("#1f4e79"))
        c.drawCentredString(
            width / 2,
            8,
            verifikasi_url
        )

        # Link aktif (bisa diklik di PDF)
        c.linkURL(
            verifikasi_url,
            (width/2 - 200, 8, width/2 + 200, 25),
            relative=0
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

    # =====================
    # LINK VERIFIKASI (TEXT + CLICKABLE)
    # =====================
    verifikasi_url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"

    c.setFont("Helvetica", 9)
    c.setFillColor(abu)
    c.drawCentredString(
        width / 2,
        18,
        "Verifikasi sertifikat:"
    )
    c.setFillColor(HexColor("#1f4e79"))
    c.drawCentredString(
        width / 2,
        8,
        verifikasi_url
    )

    # Link aktif (bisa diklik di PDF)
    c.linkURL(
        verifikasi_url,
        (width/2 - 200, 8, width/2 + 200, 25),
        relative=0
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

    # =====================
    # LINK VERIFIKASI (TEXT + CLICKABLE)
    # =====================
    verifikasi_url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"

    c.setFont("Helvetica", 9)
    c.setFillColor(abu)
    c.drawCentredString(
        width / 2,
        18,
        "Verifikasi sertifikat:"
    )
    c.setFillColor(HexColor("#1f4e79"))
    c.drawCentredString(
        width / 2,
        8,
        verifikasi_url
    )

    # Link aktif (bisa diklik di PDF)
    c.linkURL(
        verifikasi_url,
        (width/2 - 200, 8, width/2 + 200, 25),
        relative=0
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

    # =====================
    # LINK VERIFIKASI (TEXT + CLICKABLE)
    # =====================
    verifikasi_url = f"http://127.0.0.1:5000/verifikasi/{nomor_seri}"

    c.setFont("Helvetica", 9)
    c.setFillColor(abu)
    c.drawCentredString(
        width / 2,
        18,
        "Verifikasi sertifikat:"
    )
    c.setFillColor(HexColor("#1f4e79"))
    c.drawCentredString(
        width / 2,
        8,
        verifikasi_url
    )

    # Link aktif (bisa diklik di PDF)
    c.linkURL(
        verifikasi_url,
        # (width/2 - 200, 20, width/2 + 200, 45),
        (width/2 - 200, 8, width/2 + 200, 25),
        relative=0
    )

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

    prefix = f"PLPN-{tahun}-{kode}-"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nomor_seri
        FROM sertifikat
        WHERE nomor_seri LIKE ?
        ORDER BY nomor_seri DESC
        LIMIT 1
    """, (f"{prefix}%",))

    last = cursor.fetchone()
    conn.close()

    if last:
        last_number = int(last[0].split("-")[-1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{prefix}{str(next_number).zfill(4)}"
    
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
        format_sertifikat = request.form.get("format", "portrait")

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

        # Generate PDF sesuai pilihan
        if format_sertifikat == "landscape":

            pdf_file_name = f"{nomor_seri}_LANDSCAPE.pdf"

            generate_pdf_sertifikat_landscape(
                nomor_seri,
                nama,
                jenis,
                kegiatan,
                tanggal
            )

        elif format_sertifikat == "portrait":

            pdf_file_name = f"{nomor_seri}.pdf"

            generate_pdf_sertifikat(
                nomor_seri,
                nama,
                jenis,
                kegiatan,
                tanggal
            )

        elif format_sertifikat == "duo":

            pdf_file_name = f"{nomor_seri}.pdf"

            generate_pdf_sertifikat_duo(
                nomor_seri,
                nama,
                jenis,
                kegiatan,
                tanggal
            )

        elif format_sertifikat == "logo":

            pdf_file_name = f"{nomor_seri}.pdf"

            generate_pdf_sertifikat_logo(
                nomor_seri,
                nama,
                jenis,
                kegiatan,
                tanggal
            )

        elif format_sertifikat == "kwitansi":

            pdf_file_name = f"{nomor_seri}.pdf"

            generate_pdf_kwitansi(
                nomor_seri,
                nama,
                jenis,
                kegiatan,
                tanggal
            )

        else:

            pdf_file_name = f"{nomor_seri}.pdf"

            generate_pdf_sertifikat(
                nomor_seri,
                nama,
                jenis,
                kegiatan,
                tanggal
            )

        return redirect(f"/admin?file={pdf_file_name}")
            

        # generate_qr(nomor_seri)

        # generate_pdf_sertifikat_landscape(
        #     nomor_seri, nama, jenis, kegiatan, tanggal
        # )
        
        # generate_pdf_sertifikat_duo(
        #     nomor_seri,
        #     nama,
        #     jenis,
        #     kegiatan,
        #     tanggal
        # )
        
        # generate_pdf_sertifikat_logo(
        #     nomor_seri,
        #     nama,
        #     jenis,
        #     kegiatan,
        #     tanggal
        # )
        
        # generate_pdf_sertifikat(
        #     nomor_seri,
        #     nama,
        #     jenis,
        #     kegiatan,
        #     tanggal
        # )
        
        # generate_pdf_kwitansi(
        #     nomor_seri,
        #     nama,
        #     jenis,
        #     kegiatan,
        #     tanggal
        # )

        # return redirect("/admin")
        return redirect(f"/admin?file={pdf_file_name}")

    # return render_template("admin.html")
    file = request.args.get("file")
    return render_template("admin.html", file=file)

# ======================
# PANEL ADMIN LIS
# ======================
@app.route("/admin/list")
def admin_list():
    keyword = request.args.get("q", "")

    conn = connect_db()
    cursor = conn.cursor()

    if keyword:
        cursor.execute("""
            SELECT nomor_seri, nama, jenis, kegiatan, tanggal
            FROM sertifikat
            WHERE nomor_seri LIKE ?
               OR nama LIKE ?
               OR jenis LIKE ?
               OR kegiatan LIKE ?
            ORDER BY tanggal DESC
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))
    else:
        cursor.execute("""
            SELECT nomor_seri, nama, jenis, kegiatan, tanggal
            FROM sertifikat
            ORDER BY tanggal DESC
        """)

    data = cursor.fetchall()
    conn.close()

    return render_template("admin_list.html", data=data, keyword=keyword)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ======================
# PANEL ADMIN EXPORT EXCEL JENIS
# ======================
from openpyxl import Workbook

@app.route("/admin/export/excel/<int:tahun>/<jenis>")
def export_excel_jenis(tahun, jenis):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nomor_seri, nama, jenis, kegiatan, tanggal
        FROM sertifikat
        WHERE nomor_seri LIKE ? AND jenis = ?
        ORDER BY tanggal ASC
    """, (f"PLPN-{tahun}-%", jenis))
    data = cursor.fetchall()
    conn.close()

    os.makedirs("static/laporan", exist_ok=True)
    file_path = f"static/laporan/Laporan_{jenis}_{tahun}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = f"{jenis} {tahun}"

    ws.append(["No", "Nomor Seri", "Nama", "Jenis", "Kegiatan", "Tanggal"])
    for i, row in enumerate(data, start=1):
        ws.append([i, *row])

    wb.save(file_path)
    return redirect(f"/{file_path}")
# ======================
# PANEL ADMIN EXPORT PDF JENIS
# ======================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

@app.route("/admin/export/pdf/<int:tahun>/<jenis>")
def export_pdf_jenis(tahun, jenis):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nomor_seri, nama, jenis, kegiatan, tanggal
        FROM sertifikat
        WHERE nomor_seri LIKE ? AND jenis = ?
        ORDER BY tanggal ASC
    """, (f"PLPN-{tahun}-%", jenis))
    data = cursor.fetchall()
    conn.close()

    os.makedirs("static/laporan", exist_ok=True)
    file_path = f"static/laporan/Laporan_{jenis}_{tahun}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, h-50, f"LAPORAN {jenis.upper()} TAHUN {tahun}")
    c.setFont("Helvetica", 10)

    y = h - 90
    for i, row in enumerate(data, start=1):
        if y < 60:
            c.showPage()
            y = h - 60
        c.drawString(
            40, y,
            f"{i}. {row[0]} | {row[1]} | {row[3]} | {row[4]}"
        )
        y -= 14

    c.save()
    return redirect(f"/{file_path}")
# ======================
# PANEL ADMIN EXPORT PDF TAHUN
# ======================
@app.route("/admin/export/pdf/<int:tahun>")
def export_pdf_tahun(tahun):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nomor_seri, nama, jenis, kegiatan, tanggal
        FROM sertifikat
        WHERE nomor_seri LIKE ?
        ORDER BY tanggal ASC
    """, (f"PLPN-{tahun}-%",))
    data = cursor.fetchall()
    conn.close()

    file_path = f"static/laporan/Laporan_Sertifikat_{tahun}.pdf"
    os.makedirs("static/laporan", exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, h-50, f"LAPORAN SERTIFIKAT TAHUN {tahun}")
    c.setFont("Helvetica", 10)

    y = h - 90
    for i, row in enumerate(data, start=1):
        if y < 60:
            c.showPage()
            y = h - 60
        c.drawString(40, y, f"{i}. {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
        y -= 14

    c.save()
    return redirect(f"/{file_path}")

# ======================
# PANEL ADMIN EXPORT EXCEL TAHUN
# ======================
from openpyxl import Workbook

@app.route("/admin/export/excel/<int:tahun>")
def export_excel_tahun(tahun):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nomor_seri, nama, jenis, kegiatan, tanggal
        FROM sertifikat
        WHERE nomor_seri LIKE ?
        ORDER BY tanggal ASC
    """, (f"PLPN-{tahun}-%",))
    data = cursor.fetchall()
    conn.close()

    os.makedirs("static/laporan", exist_ok=True)
    file_path = f"static/laporan/Laporan_Sertifikat_{tahun}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = f"Laporan {tahun}"

    ws.append(["No", "Nomor Seri", "Nama", "Jenis", "Kegiatan", "Tanggal"])
    for i, row in enumerate(data, start=1):
        ws.append([i, *row])

    wb.save(file_path)
    return redirect(f"/{file_path}")

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)