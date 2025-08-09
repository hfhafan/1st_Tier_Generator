# 🎯 1st Tier Generator HD - Multi Method
<img src="https://github.com/user-attachments/assets/1640827f-0a8e-4e78-8812-8fdc455173ca" alt="Logo" width="150"/>
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/GUI-DearPyGUI-green.svg" alt="GUI Framework"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</div>

## ☕ Traktir Kopi

Bantu aku tetap semangat bikin fitur & update baru. Satu cangkir kopi dari kamu = satu langkah fitur berikutnya. 🙌

[![Traktir Kopi di Saweria](https://img.shields.io/badge/click_Untuk_Traktir%20Kopi-Saweria-orange?logo=buymeacoffee&logoColor=white)](https://saweria.co/HDfauzan)


## 📋 Description

**1st Tier Generator HD** is a desktop application developed for identifying 1st tier sites in telecommunications networks using various spatial analysis methods. This application is specifically designed for telecommunications engineers who need fast and accurate analysis for network optimization.

## ✨ Key Features

# Preview Apps
- Site-Level Voronoi method:

  ![image](https://github.com/user-attachments/assets/8219394e-b578-4a93-aa1b-38d224e28db1)


- Sector-Level BallTree method:

  ![image](https://github.com/user-attachments/assets/1b1818f5-89e5-4a65-94be-d5ebc4a9416a)

- Sector-Level Head to Head Sector method:

  ![image](https://github.com/user-attachments/assets/401c88e7-2bc8-4ec7-97e1-5404d0d808f0)



### 🔄 Multi-Method Analysis
- **Site Level - Voronoi**: Analysis based on Voronoi diagrams for neighboring site identification
- **Sector Level - BallTree**: BallTree algorithm with bearing-based filtering
- **Sector Level - H2H**: Head-to-Head analysis with facing sector detection

### 🖥️ User Interface
- Modern GUI with DearPyGUI
- User-friendly and intuitive interface
- Multi-tab for various analysis methods
- Real-time status and progress indicators

### 📊 Input/Output
- Supports Excel (.xlsx) and CSV (.csv) file formats
- Outputs analysis results in CSV format
- Auto-opens output folder after processing

## 📥 Download

Download the latest executable version at: **[Download 1st Tier Generator HD](http://bit.ly/4k9elX1)**

> **Note**: The executable file is pre-compiled and ready to use without Python installation

## 🎯 Analysis Methods

### 1. Site Level - Voronoi
```python
# Main logic
def process_voronoi(sites, max_radius):
    # 1. Create Voronoi diagram from site coordinates
    # 2. Identify sites sharing boundaries
    # 3. Check if site is indoor (all sectors Dir 0°/360°)
    # 4. Return list of 1st tier sites with distances
```

**Advantages:**
- Site-level analysis (not individual sectors)
- Automatic indoor site identification
- Results based on geographical proximity

### 2. Sector Level - BallTree
```python
# Main logic  
def process_balltree(sectors, candidates_per_sector, max_radius):
    # 1. Build BallTree from sector coordinates
    # 2. Query k-nearest neighbors for each sector
    # 3. Filter based on bearing and sector direction
    # 4. Ensure different 1st tier for each sector
    # 5. Return results per sector with distances
```

**Advantages:**
- High-precision sector-level analysis
- Fast BallTree algorithm for searching
- Filtering based on sector direction

### 3. Sector Level - H2H (Head-to-Head)
```python
# Main logic
def process_facing(sectors, max_radius, beam_width, h2h_threshold):
    # 1. Find candidates within radius using BallTree
    # 2. Filter based on sector beam_width
    # 3. Calculate bearing between sectors
    # 4. Detect Head-to-Head conditions:
    #    - Sector A Dir within beam_width of bearing to B
    #    - Sector B Dir within beam_width of bearing to A  
    #    - Distance < 1.5 km
    # 5. Return results with H2H status
```

**Advantages:**
- Automatic facing sector detection
- Head-to-Head analysis with customizable criteria
- Detailed output including H2H status

## 📋 Input Data Format

Input file must be in CSV or Excel format with required headers:

| Header | Type | Description |
|--------|------|-------------|
| Site ID | String | Unique site identifier |
| Sector | String | Sector ID within site |
| Latitude | Float | Latitude coordinate |
| Longitude | Float | Longitude coordinate |
| Dir | Float | Sector azimuth direction (degrees) |
| tilt | Float | Antenna tilt angle (optional) |

**Example data:**
```csv
Site ID,Sector,Latitude,Longitude,Dir,tilt
SITE001,A,-6.2088,106.8456,0,5
SITE001,B,-6.2088,106.8456,120,5
SITE001,C,-6.2088,106.8456,240,5
```

## 🛠️ Technology Stack

- **Python 3.8+**: Main programming language
- **DearPyGUI**: Modern GUI framework
- **NumPy & Pandas**: Data manipulation and analysis
- **SciPy**: Spatial algorithms (Voronoi, BallTree)
- **Pillow**: Image processing for logo
- **Requests**: HTTP requests for downloading assets

## 📁 Project Structure

```
1st-tier-generator-hd/
├── src/
│   ├── main.py              # Application entry point
│   ├── auth.py              # Authentication system
│   ├── processors/
│   │   ├── voronoi_processor.py    # Voronoi logic
│   │   ├── balltree_processor.py   # BallTree logic  
│   │   └── facing_processor.py     # H2H logic
│   └── utils/
│       ├── file_handler.py         # File I/O handler
│       └── gui_components.py       # GUI components
├── assets/
│   └── logo.png             # Application logo
├── docs/
│   └── user_manual.pdf      # User manual
└── README.md
```

## 🚀 Usage

1. **Download executable** from the link above
2. **Run application** - no Python installation required
3. **Select input file** (CSV/Excel) with proper format
4. **Enter Site IDs** to analyze (comma-separated)
5. **Adjust parameters** as needed (radius, beam width, etc.)
6. **Choose analysis method** from available tabs
7. **Click Process** and wait for completion
8. **Results automatically** saved in Documents folder

## 📊 Sample Output

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
SITE001,A,SITE002,A,Yes,1.23,km
SITE001,B,SITE003,C,No,2.45,km
```

## 🤝 Contributing

This project is developed for the telecommunications engineering community. Contributions and improvement suggestions are welcome.

## 📞 Support

If you encounter any issues or have questions:
- 📧 Email: hadifauzanhanif@gmail.com
- 💬 WhatsApp: [+62 813-5719-8294](https://wa.me/6281357198294)
- 💼 LinkedIn: [Hadi Fauzan Hanif](https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/)

## 👨‍💻 Author

**Hadi Fauzan Hanif**
- Email: hadifauzanhanif@gmail.com
- LinkedIn: [Hadi Fauzan Hanif](https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/)
- WhatsApp: [+62 813-5719-8294](https://wa.me/6281357198294)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <b>⭐ If this project helps you, please give it a star! ⭐</b>
</div> 
