# Setup Guide - 1st Tier Generator HD

Panduan lengkap untuk setup development environment dan menjalankan aplikasi.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 atau lebih tinggi
- **Operating System**: Windows 10/11, Linux, atau macOS
- **Memory**: Minimum 4GB RAM
- **Storage**: 500MB free space

### Required Software
- Git (untuk clone repository)
- Python interpreter
- pip (package manager)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/1st-tier-generator-hd.git
cd 1st-tier-generator-hd
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python src/main.py
```

## 🔧 Development Setup

### Code Structure
```
src/
├── main.py                    # Entry point aplikasi
├── processors/               # Core processing algorithms
│   ├── voronoi_processor.py  # Voronoi analysis
│   ├── balltree_processor.py # BallTree analysis
│   └── facing_processor.py   # H2H analysis
└── utils/                   # Utility modules
    ├── file_handler.py      # File I/O operations
    └── gui_components.py    # GUI components
```

### Key Dependencies

#### Core Libraries
- **pandas**: Data manipulation dan analysis
- **numpy**: Numerical computations
- **scipy**: Scientific computing (Voronoi diagrams)
- **scikit-learn**: Machine learning (BallTree)
- **geopy**: Geographic distance calculations

#### GUI Framework
- **dearpygui**: Modern GUI framework
- **Pillow**: Image processing untuk logo

#### File Support
- **openpyxl**: Excel file reading/writing
- **requests**: HTTP requests untuk download assets

## 🏗️ Building Executable

### Using PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed src/main.py
```

### Build Options
```bash
# With icon and additional files
pyinstaller --onefile --windowed --icon=icon.ico src/main.py
```

## 🧪 Testing

### Sample Data
Gunakan file `assets/sample_data.csv` untuk testing:
```bash
# Copy sample data ke lokasi test
cp assets/sample_data.csv test_data.csv
```

### Test Scenarios
1. **Voronoi Analysis**: Test dengan SITE001,SITE002,SITE003
2. **BallTree Analysis**: Test dengan berbagai parameter
3. **H2H Analysis**: Test deteksi facing sectors
4. **Indoor Detection**: Test dengan INDOOR001

## 🔍 Debugging

### Common Issues

#### 1. Import Errors
```bash
# Pastikan semua dependencies terinstall
pip install -r requirements.txt

# Check Python version
python --version
```

#### 2. GUI Issues
```bash
# Install tkinter jika belum ada (Linux)
sudo apt-get install python3-tk

# Check DearPyGUI installation
pip show dearpygui
```

#### 3. File Access Issues
- Pastikan file input accessible dan format benar
- Check permission folder output

### Debug Mode
Tambahkan logging untuk debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Configuration

### File Locations
- **Input Files**: CSV/Excel dengan header yang sesuai
- **Output Folder**: `~/Documents/1st_tier_generator_HD/`
- **Temp Files**: System temporary directory

### Header Requirements
File input harus memiliki header:
- `Site ID`: ID unik site
- `Sector`: ID sektor 
- `Latitude`: Koordinat latitude
- `Longitude`: Koordinat longitude
- `Dir`: Azimuth sektor (0-360°)
- `tilt`: Tilt antena (opsional)

## 🚢 Deployment

### Creating Distribution
```bash
# Build dengan semua dependencies
pyinstaller --onefile --collect-all dearpygui src/main.py

# Test executable
./dist/main.exe
```

### Distribution Checklist
- [ ] Test di clean environment
- [ ] Verify semua features berfungsi
- [ ] Check file size reasonable
- [ ] Test dengan sample data
- [ ] Verify output format benar

## 🤝 Contributing

### Development Workflow
1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write unit tests

## 📞 Support

Jika mengalami kesulitan dalam setup:

- 📧 Email: hadifauzanhanif@gmail.com
- 💬 WhatsApp: [+62 813-5719-8294](https://wa.me/6281357198294)
- 💼 LinkedIn: [Hadi Fauzan Hanif](https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/)

## 📝 Notes

- Virtual environment sangat direkomendasikan
- Test dengan data kecil terlebih dahulu
- Backup data penting sebelum processing
- Monitor memory usage untuk dataset besar 