# python2binary 🚀

`python2binary` adalah alat baris perintah (CLI) untuk membungkus proyek Python Anda menjadi sebuah file binary native yang mandiri (*self-contained*).

## Cara Kerja (Pipeline)

Program ini bekerja melalui tiga tahap utama:
1.  **Pack**: Membungkus semua file `.py` dalam proyek Anda menjadi arsip `.pyz` (zipapp).
2.  **Convert**: Mengubah file `.pyz` menjadi header C (`.h`) menggunakan `xxd`.
3.  **Compile**: Menghasilkan *launcher* C yang menyematkan data Python tersebut dan mengkompilasinya menggunakan `gcc` menjadi binary native.

Binary yang dihasilkan akan mengekstrak kode Python ke folder sementara saat dijalankan dan mengeksekusinya menggunakan interpreter `python3` yang ada di sistem target.

## Prasyarat Sistem

Sebelum menggunakan `python2binary`, pastikan sistem Anda telah memiliki:
- **Python 3.8+**
- **GCC**: Compiler C (untuk tahap kompilasi).
- **XXD**: Tool hexdump (untuk tahap konversi).

Di Ubuntu/Debian, Anda dapat menginstalnya dengan:
```bash
sudo apt-get update
sudo apt-get install build-essential xxd
```

## Instalasi

Gunakan mode *editable* agar Anda dapat menjalankan perintah `python2binary` secara global di dalam venv Anda:

```bash
# Aktifkan venv Anda
source .binary/bin/activate

# Instal proyek
pip install -e .
```

## Penggunaan

Setelah diinstal, Anda dapat menjalankan `python2binary` langsung dari terminal:

```bash
python2binary --project <direktori_proyek> --entry <file_utama> --output <folder_hasil> [--name <nama_binary>]
```

### Parameter:
- `--project`, `-p`: Direktori root proyek Python Anda.
- `--entry`, `-e`: Script entry-point (misal: `main.py` atau `app/run.py`), relatif terhadap direktori proyek.
- `--output`, `-o`: Direktori tujuan hasil build.
- `--name`, `-n` (Opsional): Nama file binary yang dihasilkan. Default menggunakan nama folder proyek.

### Contoh:
```bash
python2binary -p ./my_script_folder -e main.py -o ./dist -n my_application
```

## Struktur Proyek

- `main.py`: Entry point CLI.
- `pipeline.py`: Logika utama orkestrasi pembangunan binary.
- `infrastructure/`: Implementasi teknis untuk packing, konversi, dan kompilasi.
- `interfaces/`: Definisi abstraksi untuk setiap tahapan pipeline.
- `schemas/`: Struktur data untuk konfigurasi dan hasil build.

## Lisensi
MIT
