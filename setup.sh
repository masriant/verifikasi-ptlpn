#!/bin/bash

set -e

echo "🚀 Setup jupyter environment..."

# Masuk ke folder script
cd "$(dirname "$0")"

# Cek Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 belum terinstall"
    exit 1
fi

# Buat venv kalau belum ada
if [ ! -d ".venv" ]; then
    echo "📦 Membuat virtual environment..."
    python3 -m venv .venv
else
    echo "✅ .venv sudah ada"
fi

# Aktifkan venv
echo "🔌 Aktivasi virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrade pip..."
pip install --upgrade pip

# Install dependency
echo "📚 Install dependency..."
pip install -r requirements.txt

# Jalankan script
echo "▶️ Menjalankan jupyter..."
python main.py

echo "✅ Selesai"