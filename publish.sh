#!/bin/bash

# Pastikan venv aktif jika diperlukan
# source .binary/bin/activate

echo "--- Membersihkan folder build lama ---"
rm -rf dist/ build/ *.egg-info

echo "--- Menginstal alat build terbaru ---"
pip install --upgrade build twine

echo "--- Memulai proses build paket ---"
python3 -m build

echo "--- Memeriksa integritas paket ---"
python3 -m twine check dist/*

echo ""
echo "Selesai! Paket siap diunggah."
echo "Jalankan perintah berikut untuk mengunggah ke PyPI:"
echo "python3 -m twine upload dist/*"
echo ""
echo "Gunakan '__token__' sebagai username dan API Token Anda sebagai password."
