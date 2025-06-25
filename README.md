# 🎯 1st Tier Generator HD - Multi Method

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/GUI-DearPyGUI-green.svg" alt="GUI Framework"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</div>

## 📋 Deskripsi

**1st Tier Generator HD** adalah aplikasi desktop yang dikembangkan untuk mengidentifikasi site 1st tier dalam jaringan telekomunikasi menggunakan berbagai metode analisis spasial. Aplikasi ini dirancang khusus untuk engineer telekomunikasi yang membutuhkan analisis cepat dan akurat untuk optimasi jaringan.

## ✨ Fitur Utama

### 🔄 Multi-Method Analysis
- **Site Level - Voronoi**: Analisis berdasarkan diagram Voronoi untuk identifikasi site tetangga
- **Sector Level - BallTree**: Algoritma BallTree dengan filtering berbasis bearing
- **Sector Level - H2H**: Analisis Head-to-Head dengan deteksi facing sector

### 🖥️ User Interface
- GUI modern dengan DearPyGUI
- Interface yang user-friendly dan intuitif  
- Multi-tab untuk berbagai metode analisis
- Real-time status dan progress indicator

### 📊 Input/Output
- Mendukung format file Excel (.xlsx) dan CSV (.csv)
- Output hasil analisis dalam format CSV
- Auto-open folder hasil setelah processing

## 📥 Download

Unduh versi executable terbaru di: **[Download 1st Tier Generator HD](http://bit.ly/4k9elX1)**

> **Catatan**: File executable sudah dikompilasi dan siap digunakan tanpa instalasi Python

## 🎯 Metode Analisis

### 1. Site Level - Voronoi
```python
# Logika utama
def process_voronoi(sites, max_radius):
    # 1. Buat diagram Voronoi dari koordinat site
    # 2. Identifikasi site yang berbagi boundary
    # 3. Cek apakah site indoor (semua sektor Dir 0°/360°)
    # 4. Return list 1st tier sites dengan jarak
```

**Keunggulan:**
- Analisis level site (bukan sektor)
- Identifikasi otomatis site indoor
- Hasil berdasarkan kedekatan geografis

### 2. Sector Level - BallTree
```python
# Logika utama  
def process_balltree(sectors, candidates_per_sector, max_radius):
    # 1. Build BallTree dari koordinat sektor
    # 2. Query k-nearest neighbors untuk setiap sektor
    # 3. Filter berdasarkan bearing dan Dir sektor
    # 4. Pastikan 1st tier berbeda untuk setiap sektor
    # 5. Return hasil per sektor dengan jarak
```

**Keunggulan:**
- Analisis level sektor dengan presisi tinggi
- Algoritma BallTree untuk pencarian cepat
- Filtering berdasarkan arah sektor

### 3. Sector Level - H2H (Head-to-Head)
```python
# Logika utama
def process_facing(sectors, max_radius, beam_width, h2h_threshold):
    # 1. Cari kandidat dalam radius menggunakan BallTree
    # 2. Filter berdasarkan beam_width sektor
    # 3. Hitung bearing antar sektor
    # 4. Deteksi kondisi Head-to-Head:
    #    - Dir sektor A dalam beam_width bearing ke B
    #    - Dir sektor B dalam beam_width bearing ke A  
    #    - Jarak < 1.5 km
    # 5. Return hasil dengan status H2H
```

**Keunggulan:**
- Deteksi facing sector otomatis
- Analisis Head-to-Head dengan kriteria yang dapat disesuaikan
- Output detail termasuk status H2H

## 📋 Format Input Data

File input harus berformat CSV atau Excel dengan header wajib:

| Header | Tipe | Deskripsi |
|--------|------|-----------|
| Site ID | String | ID unik untuk site |
| Sector | String | ID sektor dalam site |
| Latitude | Float | Koordinat latitude |
| Longitude | Float | Koordinat longitude |
| Dir | Float | Arah azimuth sektor (derajat) |
| tilt | Float | Sudut kemiringan antena (opsional) |

**Contoh data:**
```csv
Site ID,Sector,Latitude,Longitude,Dir,tilt
SITE001,A,-6.2088,106.8456,0,5
SITE001,B,-6.2088,106.8456,120,5
SITE001,C,-6.2088,106.8456,240,5
```

## 🛠️ Teknologi

- **Python 3.8+**: Bahasa pemrograman utama
- **DearPyGUI**: Framework GUI modern
- **NumPy & Pandas**: Manipulasi dan analisis data
- **SciPy**: Algoritma spatial (Voronoi, BallTree)
- **Pillow**: Image processing untuk logo
- **Requests**: HTTP requests untuk download assets

## 📁 Struktur Project

```
1st-tier-generator-hd/
├── src/
│   ├── main.py              # Entry point aplikasi
│   ├── auth.py              # Sistem autentikasi
│   ├── processors/
│   │   ├── voronoi_processor.py    # Logika Voronoi
│   │   ├── balltree_processor.py   # Logika BallTree  
│   │   └── facing_processor.py     # Logika H2H
│   └── utils/
│       ├── file_handler.py         # Handler file I/O
│       └── gui_components.py       # Komponen GUI
├── assets/
│   └── logo.png             # Logo aplikasi
├── docs/
│   └── user_manual.pdf      # Manual pengguna
└── README.md
```

## 🚀 Penggunaan

1. **Download executable** dari link di atas
2. **Jalankan aplikasi** - tidak perlu instalasi Python
3. **Pilih file input** (CSV/Excel) dengan format yang sesuai
4. **Masukkan Site ID** yang ingin dianalisis (pisahkan dengan koma)
5. **Atur parameter** sesuai kebutuhan (radius, beam width, dll)
6. **Pilih metode** analisis di tab yang tersedia
7. **Klik Proses** dan tunggu hingga selesai
8. **Hasil otomatis** tersimpan di folder Documents

## 📊 Contoh Output

### Site Level - Voronoi
```csv
Site ID,1st_Tier,Average of Distance,Distance_Unit
SITE001,SITE002,2.45,km
SITE001,SITE003,3.12,km
```

### Sector Level - BallTree
```csv
Site ID,Sector,1st_Tier,Average of Distance,Distance_Unit
SITE001,A,SITE002,2.45,km
SITE001,B,SITE003,3.12,km
```

### Sector Level - H2H
```csv
Site ID,Sector,1st_Tier,1st_Tier_Sector,H2H_Status,Average of Distance,Distance_Unit
SITE001,A,SITE002,A,Ya,1.23,km
SITE001,B,SITE003,C,Tidak,2.45,km
```

## 🤝 Kontribusi

Proyek ini dikembangkan untuk komunitas engineer telekomunikasi. Kontribusi dan saran perbaikan sangat diterima.

## 📞 Support

Jika mengalami kendala atau memiliki pertanyaan:
- 📧 Email: hadifauzanhanif@gmail.com
- 💬 WhatsApp: [+62 813-5719-8294](https://wa.me/6281357198294)
- 💼 LinkedIn: [Hadi Fauzan Hanif](https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/)

## 👨‍💻 Author

**Hadi Fauzan Hanif**
- Email: hadifauzanhanif@gmail.com
- LinkedIn: [Hadi Fauzan Hanif](https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/)
- WhatsApp: [+62 813-5719-8294](https://wa.me/6281357198294)

## 📄 License

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

---

<div align="center">
  <b>⭐ Jika project ini membantu, jangan lupa berikan star! ⭐</b>
</div> 