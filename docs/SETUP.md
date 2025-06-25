# Setup Guide - 1st Tier Generator HD

Complete guide for setting up development environment and running the application.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, Linux, or macOS
- **Memory**: Minimum 4GB RAM
- **Storage**: 500MB free space

### Required Software
- Git (for cloning repository)
- Python interpreter
- pip (package manager)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/hfhafan/1st_Tier_Generator.git
cd 1st_Tier_Generator
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
├── main.py                    # Application entry point
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
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **scipy**: Scientific computing (Voronoi diagrams)
- **scikit-learn**: Machine learning (BallTree)
- **geopy**: Geographic distance calculations

#### GUI Framework
- **dearpygui**: Modern GUI framework
- **Pillow**: Image processing for logo

#### File Support
- **openpyxl**: Excel file reading/writing
- **requests**: HTTP requests for downloading assets

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
Use the file `assets/sample_data.csv` for testing:
```bash
# Copy sample data to test location
cp assets/sample_data.csv test_data.csv
```

### Test Scenarios
1. **Voronoi Analysis**: Test with SITE001,SITE002,SITE003
2. **BallTree Analysis**: Test with various parameters
3. **H2H Analysis**: Test facing sector detection
4. **Indoor Detection**: Test with INDOOR001

## 🔍 Debugging

### Common Issues

#### 1. Import Errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python version
python --version
```

#### 2. GUI Issues
```bash
# Install tkinter if not available (Linux)
sudo apt-get install python3-tk

# Check DearPyGUI installation
pip show dearpygui
```

#### 3. File Access Issues
- Ensure input files are accessible and properly formatted
- Check output folder permissions

### Debug Mode
Add logging for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Configuration

### File Locations
- **Input Files**: CSV/Excel with proper headers
- **Output Folder**: `~/Documents/1st_tier_generator_HD/`
- **Temp Files**: System temporary directory

### Header Requirements
Input file must have headers:
- `Site ID`: Unique site identifier
- `Sector`: Sector ID 
- `Latitude`: Latitude coordinate
- `Longitude`: Longitude coordinate
- `Dir`: Sector azimuth (0-360°)
- `tilt`: Antenna tilt (optional)

## 🚢 Deployment

### Creating Distribution
```bash
# Build with all dependencies
pyinstaller --onefile --collect-all dearpygui src/main.py

# Test executable
./dist/main.exe
```

### Distribution Checklist
- [ ] Test in clean environment
- [ ] Verify all features work
- [ ] Check reasonable file size
- [ ] Test with sample data
- [ ] Verify correct output format

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

If you encounter difficulties in setup:

- 📧 Email: hadifauzanhanif@gmail.com
- 💬 WhatsApp: [+62 813-5719-8294](https://wa.me/6281357198294)
- 💼 LinkedIn: [Hadi Fauzan Hanif](https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/)

## 📝 Notes

- Virtual environment is highly recommended
- Test with small data first
- Backup important data before processing
- Monitor memory usage for large datasets 