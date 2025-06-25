"""
GUI Components - User Interface Elements

Modul untuk komponen-komponen GUI dalam aplikasi 1st Tier Generator.
Menggunakan DearPyGUI untuk membuat interface yang modern dan user-friendly.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import os
import sys
import tempfile
import webbrowser
import requests
import dearpygui.dearpygui as dpg
from PIL import Image


class GUIComponents:
    """Kelas untuk komponen-komponen GUI"""
    
    def __init__(self):
        self.logo_url = "https://drive.google.com/uc?export=download&id=1RxiEZ-JqJNcQFXCtKWjIKazykqikXx6t"
        self.default_font = None
        self.title_font = None
    
    def setup_fonts_and_themes(self):
        """
        Setup font dan tema untuk GUI:
        1. Load font sistem (Segoe UI untuk Windows)
        2. Buat tema dengan style modern
        3. Apply tema ke seluruh aplikasi
        4. Handle fallback jika font tidak tersedia
        """
        with dpg.font_registry():
            # Font paths untuk berbagai OS
            font_paths = {
                'windows': {
                    'regular': "C:/Windows/Fonts/segoeui.ttf",
                    'bold': "C:/Windows/Fonts/segoeuib.ttf"
                },
                'linux': {
                    'regular': "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    'bold': "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                },
                'darwin': {
                    'regular': "/System/Library/Fonts/Helvetica.ttc",
                    'bold': "/System/Library/Fonts/Helvetica.ttc"
                }
            }
            
            # Deteksi OS dan load font
            os_name = self._detect_os()
            self._load_fonts(font_paths.get(os_name, {}))
        
        # Setup tema
        self._create_modern_theme()
    
    def _detect_os(self):
        """Deteksi sistem operasi untuk pemilihan font yang tepat"""
        if sys.platform.startswith('win'):
            return 'windows'
        elif sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('darwin'):
            return 'darwin'
        else:
            return 'unknown'
    
    def _load_fonts(self, font_paths):
        """
        Load font berdasarkan sistem operasi:
        1. Coba load font regular dan bold
        2. Set sebagai default_font dan title_font
        3. Handle exception jika font tidak tersedia
        """
        try:
            regular_path = font_paths.get('regular')
            bold_path = font_paths.get('bold')
            
            if regular_path and os.path.exists(regular_path):
                self.default_font = dpg.add_font(regular_path, 16)
            
            if bold_path and os.path.exists(bold_path):
                self.title_font = dpg.add_font(bold_path, 24)
                
        except Exception as e:
            print(f"Warning: Gagal memuat font - {e}")
    
    def _create_modern_theme(self):
        """
        Buat tema modern untuk aplikasi:
        1. Set warna-warna yang konsisten
        2. Atur style seperti rounding, padding
        3. Apply ke seluruh aplikasi
        """
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Style
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 5, 5)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 16)
                
                # Colors (opsional - bisa disesuaikan)
                # dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 130, 180, 255))
        
        dpg.bind_theme(global_theme)
    
    def download_and_load_logo(self):
        """
        Download dan load logo aplikasi:
        1. Download logo dari URL ke temporary directory
        2. Resize jika diperlukan
        3. Load ke texture registry DearPyGUI
        4. Handle error jika gagal download
        """
        try:
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, "logo.png")
            
            # Download logo
            self._download_image(self.logo_url, image_path)
            
            # Load dan resize logo
            logo_image = Image.open(image_path)
            width, height = logo_image.size
            
            # Load ke DearPyGUI
            width, height, channels, data = dpg.load_image(image_path)
            
            with dpg.texture_registry(show=False):
                dpg.add_static_texture(width, height, data, tag="logo_image")
                
        except Exception as e:
            print(f"Warning: Gagal memuat logo - {e}")
    
    def _download_image(self, url, save_path):
        """
        Download gambar dari URL:
        1. Request gambar dengan stream=True
        2. Simpan ke file lokal
        3. Handle timeout dan error
        """
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                return True
        except Exception as e:
            print(f"Error downloading image: {e}")
        return False
    
    def create_file_dialog(self):
        """
        Buat file dialog untuk pemilihan file input:
        1. Setup file dialog dengan filter
        2. Set callback untuk handle file selection
        3. Configure untuk CSV dan Excel files
        """
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=self._file_dialog_callback,
            tag="file_dialog",
            width=700,
            height=400,
            default_path=os.path.expanduser("~")
        ):
            dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")
            dpg.add_file_extension(".xlsx", color=(0, 255, 255, 255), custom_text="[Excel]")
            dpg.add_file_extension(".*", color=(255, 255, 255, 255), custom_text="[All Files]")
    
    def _file_dialog_callback(self, sender, app_data):
        """
        Callback untuk file dialog:
        1. Handle file selection
        2. Update file path input
        3. Validasi file yang dipilih
        """
        if not app_data["selections"]:
            return
        
        selected_files = app_data["selections"]
        if selected_files:
            selected_file = next(iter(selected_files.values()))
            dpg.set_value("file_path", selected_file)
    
    def create_header(self):
        """
        Buat header aplikasi dengan logo dan judul:
        1. Layout horizontal dengan logo dan text
        2. Apply font yang sesuai
        3. Add spacing yang tepat
        """
        with dpg.group(horizontal=True):
            try:
                # Logo
                dpg.add_image("logo_image", width=120, height=120)
                dpg.add_spacer(width=10)
            except:
                # Fallback jika logo tidak tersedia
                dpg.add_spacer(width=130)
            
            # Title section
            with dpg.group():
                dpg.add_spacer(height=10)
                dpg.add_text("1st Tier Generator HD - Multi Method", tag="title_text")
                if self.title_font:
                    dpg.bind_item_font("title_text", self.title_font)
                
                dpg.add_text("Multi-Method 1st Tier Generator", tag="subtitle_text")
                dpg.add_spacer(height=5)
    
    def create_file_input_section(self):
        """
        Buat section untuk input file:
        1. Input text untuk file path
        2. Browse button
        3. Layout yang rapi
        """
        with dpg.collapsing_header(label="Input File", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Input file (.csv / .xlsx):")
                dpg.add_input_text(tag="file_path", width=-200)
                dpg.add_button(label="Browse", callback=self._browse_file)
    
    def _browse_file(self):
        """
        Handler untuk tombol browse:
        1. Coba gunakan system file dialog
        2. Fallback ke DearPyGUI dialog
        """
        try:
            # Coba gunakan tkinter file dialog
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            file_path = filedialog.askopenfilename(
                title="Pilih file input",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                dpg.set_value("file_path", file_path)
                
        except Exception as e:
            print(f"Error opening file dialog: {e}")
            # Fallback ke DearPyGUI dialog
            dpg.show_item("file_dialog")
    
    def create_voronoi_tab(self, process_callback):
        """
        Buat tab untuk metode Voronoi:
        1. Input fields untuk parameter
        2. Deskripsi metode
        3. Process button dengan callback
        """
        with dpg.tab(label="Site Level - Voronoi"):
            with dpg.group():
                dpg.add_text("Site IDs (pisahkan dengan koma):")
                dpg.add_input_text(tag="site_ids_voronoi", width=-1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Radius maksimum (km):")
                    dpg.add_input_float(tag="max_radius_voronoi", default_value=10.0,
                                      min_value=1.0, max_value=20.0, width=100, step=1.0)
                
                dpg.add_separator()
                dpg.add_text("Metode ini mencari site di sekitar site pusat berdasarkan jarak.")
                dpg.add_text("Hanya mempertimbangkan jarak, tanpa memperhatikan sektor.")
                dpg.add_separator()
                
                dpg.add_button(label="Proses", callback=process_callback,
                             width=120, height=40)
                dpg.add_text("", tag="status_voronoi")
    
    def create_balltree_tab(self, process_callback):
        """
        Buat tab untuk metode BallTree:
        1. Input fields untuk parameter
        2. Deskripsi metode
        3. Process button dengan callback
        """
        with dpg.tab(label="Sector Level - BallTree"):
            with dpg.group():
                dpg.add_text("Site IDs (pisahkan dengan koma):")
                dpg.add_input_text(tag="site_ids_balltree", width=-1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Kandidat per sektor:")
                    dpg.add_input_int(tag="candidate_per_sector", default_value=1,
                                    min_value=1, max_value=10, width=100)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Radius maksimum (km):")
                    dpg.add_input_float(tag="max_radius_balltree", default_value=7.0,
                                      min_value=1.0, max_value=20.0, width=100, step=1)
                
                dpg.add_separator()
                dpg.add_text("Metode BallTree menggunakan kNN untuk menemukan kandidat,")
                dpg.add_text("kemudian memfilter berdasarkan bearing.")
                dpg.add_separator()
                
                dpg.add_button(label="Proses", callback=process_callback,
                             width=120, height=40)
                dpg.add_text("", tag="status_balltree")
    
    def create_facing_tab(self, process_callback):
        """
        Buat tab untuk metode Facing/H2H:
        1. Input fields untuk parameter
        2. Deskripsi metode H2H
        3. Process button dengan callback
        """
        with dpg.tab(label="Sector Level - H2H"):
            with dpg.group():
                dpg.add_text("Site IDs (pisahkan dengan koma):")
                dpg.add_input_text(tag="site_ids_facing", width=-1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Radius Pencarian (km):")
                    dpg.add_input_float(tag="max_radius_facing", default_value=10.0,
                                      min_value=1.0, max_value=25.0, width=100, step=1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Filter Beam Width (derajat):")
                    dpg.add_input_float(tag="beam_width", default_value=120.0,
                                      min_value=30.0, max_value=180.0, width=100, step=5)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Threshold H2H (derajat):")
                    dpg.add_input_float(tag="h2h_threshold", default_value=30.0,
                                      min_value=10.0, max_value=60.0, width=100, step=5)
                
                dpg.add_separator()
                self._add_h2h_description()
                dpg.add_separator()
                
                dpg.add_button(label="Proses", callback=process_callback,
                             width=120, height=40)
                dpg.add_text("", tag="status_facing")
    
    def _add_h2h_description(self):
        """Tambahkan deskripsi detail untuk metode H2H"""
        dpg.add_text("Metode ini menggunakan pendekatan optimized:")
        dpg.add_text("1. Mencari kandidat 1st tier dalam radius tertentu berdasarkan BallTree")
        dpg.add_text("2. Filter berdasarkan Dir sektor (beam width)")
        dpg.add_text("3. Menentukan status Head-to-Head (H2H) dengan kriteria:")
        dpg.add_text("   - Dir sektor sumber berada dalam beam width dari bearing ke tujuan")
        dpg.add_text("   - Dir sektor tujuan berada dalam beam width dari bearing ke sumber")
        dpg.add_text("   - Jarak antara keduanya < 1.5 km")
    
    def create_about_tab(self, is_trial_mode=False):
        """
        Buat tab About dengan informasi aplikasi:
        1. Informasi aplikasi dan author
        2. Header requirements
        3. Metode descriptions
        4. Contact information
        """
        with dpg.tab(label="About"):
            self._add_about_content(is_trial_mode)
    
    def _add_about_content(self, is_trial_mode):
        """Tambahkan konten lengkap untuk tab About"""
        # Implementation untuk about content
        # Mencakup info aplikasi, requirements, metode, dan contact
        pass
    
    def create_footer(self, is_trial_mode=False):
        """
        Buat footer aplikasi:
        1. Informasi versi
        2. Copyright
        3. Status trial/license
        """
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text("v1.0.0 © 2025")
            if is_trial_mode:
                dpg.add_text(" | Trial Mode - Experimental", color=[0, 200, 0, 255])
            else:
                dpg.add_text(" | Licensed Version", color=[0, 200, 0, 255])
    
    def show_loading_window(self, tab_id):
        """
        Tampilkan loading window:
        1. Modal window dengan loading indicator
        2. Tidak bisa ditutup selama proses
        3. Tag berdasarkan tab_id
        """
        with dpg.window(label="Sedang Memproses...", modal=True, no_close=True,
                       width=300, height=100, tag=f"loading_{tab_id}", pos=(250, 250)):
            dpg.add_text("Sedang memproses, mohon tunggu...")
            dpg.add_loading_indicator(style=1, radius=10.0)
    
    def process_complete_callback(self, tab_id, success, message):
        """
        Callback setelah proses selesai:
        1. Tutup loading window
        2. Update status message
        3. Buka folder output jika berhasil
        """
        # Tutup loading window
        if dpg.does_item_exist(f"loading_{tab_id}"):
            dpg.delete_item(f"loading_{tab_id}")
        
        # Update status
        if success:
            color = [0, 200, 0, 255]  # Green
            dpg.configure_item(f"status_{tab_id}", default_value=message, color=color)
            
            # Buka folder output
            self._open_output_folder()
        else:
            color = [255, 0, 0, 255]  # Red
            dpg.configure_item(f"status_{tab_id}", default_value=message, color=color)
    
    def _open_output_folder(self):
        """
        Buka folder output setelah proses berhasil:
        1. Deteksi OS
        2. Gunakan command yang sesuai
        3. Handle error jika gagal
        """
        try:
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "1st_tier_generator_HD")
            webbrowser.open(output_dir)
        except Exception as e:
            print(f"Gagal membuka folder output: {e}")
    
    def show_message(self, title, message, is_error=False):
        """
        Tampilkan message dialog:
        1. Modal window dengan pesan
        2. Warna berbeda untuk error vs info
        3. OK button untuk menutup
        """
        color = [255, 0, 0, 255] if is_error else [255, 255, 255, 255]
        
        with dpg.window(label=title, modal=True, autosize=True, tag="modal_message"):
            dpg.add_text(message, color=color)
            dpg.add_button(label="OK", 
                         callback=lambda: dpg.delete_item("modal_message"), 
                         width=75) 