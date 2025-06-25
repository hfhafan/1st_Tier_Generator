"""
1st Tier Generator HD - Main Application

Entry point aplikasi GUI untuk analisis 1st tier dalam jaringan telekomunikasi.
Menggunakan DearPyGUI untuk interface dan mendukung 3 metode analisis.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import os
import sys
import threading
import datetime
import dearpygui.dearpygui as dpg

# Import modul internal
from processors.voronoi_processor import VoronoiProcessor
from processors.balltree_processor import BallTreeProcessor  
from processors.facing_processor import FacingProcessor
from utils.file_handler import FileHandler
from utils.gui_components import GUIComponents

class MainApplication:
    """Kelas utama untuk aplikasi 1st Tier Generator HD"""
    
    def __init__(self):
        self.APP_TITLE = "1st Tier Generator HD - Multi Method"
        self.APP_VERSION = "1.0.0"
        self.APP_WIDTH = 800
        self.APP_HEIGHT = 600
        
        # Initialize processors
        self.voronoi_processor = VoronoiProcessor()
        self.balltree_processor = BallTreeProcessor()
        self.facing_processor = FacingProcessor()
        
        # Initialize utilities
        self.file_handler = FileHandler()
        self.gui_components = GUIComponents()
    
    def is_indoor_site(self, df, site_id):
        """
        Logika untuk mendeteksi site indoor:
        1. Ambil semua sektor dari site_id
        2. Cek apakah semua sektor memiliki Dir = 0° atau 360°
        3. Return True jika indoor, False jika outdoor
        """
        # Implementasi logika indoor detection
        pass
    
    def process_voronoi(self, filepath, site_ids, max_radius):
        """
        Alur proses Voronoi (Site Level):
        1. Parse file input dan validasi header
        2. Extract koordinat site (bukan sektor)
        3. Cek apakah site indoor -> set "Indoor" sebagai 1st tier
        4. Untuk site outdoor -> jalankan algoritma Voronoi
        5. Identifikasi site yang berbagi boundary
        6. Simpan hasil ke CSV
        """
        try:
            # Step 1: Parse data
            df = self.file_handler.read_file(filepath)
            points = self.file_handler.parse_data(df)
            
            # Step 2: Parse site IDs
            wanted_ids = [sid.strip() for sid in site_ids.split(",")]
            
            results = []
            for site_id in wanted_ids:
                if self.is_indoor_site(df, site_id):
                    # Tambah hasil untuk site indoor
                    results.extend(self._create_indoor_results(df, site_id))
                else:
                    # Jalankan proses Voronoi
                    site_results = self.voronoi_processor.run_process(
                        [site_id], points, max_radius
                    )
                    results.extend(site_results)
            
            # Step 3: Simpan hasil
            output_path = self.file_handler.save_result_to_csv(results, "Site_Voronoi")
            return True, f"Proses selesai. File tersimpan di: {output_path}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def process_balltree(self, filepath, site_ids, candidate_per_sector, max_radius):
        """
        Alur proses BallTree (Sector Level):
        1. Parse file input dan validasi header
        2. Cek apakah site indoor -> set "Indoor" sebagai 1st tier
        3. Untuk site outdoor -> build BallTree dari koordinat sektor
        4. Query k-nearest neighbors untuk setiap sektor
        5. Filter berdasarkan bearing dan Dir sektor
        6. Pastikan 1st tier berbeda untuk setiap sektor dalam satu site
        7. Simpan hasil ke CSV
        """
        try:
            # Step 1: Parse data
            df = self.file_handler.read_file(filepath)
            points = self.file_handler.parse_data(df)
            
            # Step 2: Parse site IDs  
            wanted_ids = [sid.strip() for sid in site_ids.split(",")]
            
            results = []
            for site_id in wanted_ids:
                if self.is_indoor_site(df, site_id):
                    # Tambah hasil untuk site indoor
                    results.extend(self._create_indoor_results(df, site_id))
                else:
                    # Jalankan proses BallTree
                    site_results = self.balltree_processor.run_process(
                        df, [site_id], candidate_per_sector, max_radius
                    )
                    results.extend(site_results)
            
            # Step 3: Simpan hasil
            output_path = self.file_handler.save_result_to_csv(results, "Sector_BallTree")
            return True, f"Proses selesai. File tersimpan di: {output_path}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def process_facing(self, filepath, site_ids, max_radius, beam_width, h2h_threshold):
        """
        Alur proses Facing/H2H (Sector Level):
        1. Parse file input dan validasi header
        2. Cek apakah site indoor -> set "Indoor" sebagai 1st tier
        3. Untuk site outdoor:
           a. Cari kandidat dalam radius menggunakan BallTree
           b. Filter berdasarkan beam_width sektor
           c. Hitung bearing antar sektor
           d. Deteksi kondisi Head-to-Head:
              - Dir sektor A dalam beam_width bearing ke B
              - Dir sektor B dalam beam_width bearing ke A  
              - Jarak < threshold
        4. Simpan hasil dengan status H2H ke CSV
        """
        try:
            # Step 1: Parse data
            df = self.file_handler.read_file(filepath)
            points = self.file_handler.parse_data(df)
            
            # Step 2: Parse site IDs
            wanted_ids = [sid.strip() for sid in site_ids.split(",")]
            
            results = []
            for site_id in wanted_ids:
                if self.is_indoor_site(df, site_id):
                    # Tambah hasil untuk site indoor
                    results.extend(self._create_indoor_results(df, site_id, include_h2h=True))
                else:
                    # Jalankan proses Facing/H2H
                    site_results = self.facing_processor.run_process(
                        df, [site_id], max_radius, beam_width, h2h_threshold
                    )
                    results.extend(site_results)
            
            # Step 3: Simpan hasil
            output_path = self.file_handler.save_result_to_csv(results, "Sector_Facing_H2H")
            return True, f"Proses selesai. File tersimpan di: {output_path}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _create_indoor_results(self, df, site_id, include_h2h=False):
        """Helper method untuk membuat hasil site indoor"""
        # Implementasi pembuatan hasil untuk site indoor
        pass
    
    def run_process_in_thread(self, process_func, args, tab_id):
        """
        Menjalankan proses dalam thread terpisah:
        1. Tampilkan loading window
        2. Jalankan fungsi proses di background thread
        3. Update UI dengan hasil (success/error)
        4. Tutup loading window
        5. Buka folder output jika berhasil
        """
        self.gui_components.show_loading_window(tab_id)
        
        def thread_func():
            try:
                success, message = process_func(*args)
                # Update UI callback
                self.gui_components.process_complete_callback(tab_id, success, message)
            except Exception as e:
                self.gui_components.process_complete_callback(tab_id, False, f"Error: {str(e)}")
        
        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()
    
    def create_gui(self, is_trial_mode=False):
        """
        Membuat GUI dengan DearPyGUI:
        1. Setup context dan viewport
        2. Load font dan tema
        3. Download dan load logo
        4. Buat file dialog
        5. Buat layout dengan tabs:
           - Site Level - Voronoi
           - Sector Level - BallTree  
           - Sector Level - H2H
           - About
        6. Setup event handlers
        """
        dpg.create_context()
        dpg.create_viewport(title=self.APP_TITLE, width=self.APP_WIDTH, height=self.APP_HEIGHT)
        
        # Setup GUI components
        self.gui_components.setup_fonts_and_themes()
        self.gui_components.download_and_load_logo()
        self.gui_components.create_file_dialog()
        
        # Main window dengan tabs
        with dpg.window(tag="Primary Window", label=self.APP_TITLE):
            self.gui_components.create_header()
            self.gui_components.create_file_input_section()
            
            # Tab untuk berbagai metode
            with dpg.tab_bar():
                self.gui_components.create_voronoi_tab(self.run_voronoi_process_thread)
                self.gui_components.create_balltree_tab(self.run_balltree_process_thread)
                self.gui_components.create_facing_tab(self.run_facing_process_thread)
                self.gui_components.create_about_tab(is_trial_mode)
            
            self.gui_components.create_footer(is_trial_mode)
        
        # Start GUI
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
    
    def run_voronoi_process_thread(self):
        """Handler untuk tombol proses Voronoi"""
        filepath = dpg.get_value("file_path")
        site_ids = dpg.get_value("site_ids_voronoi")
        max_radius = dpg.get_value("max_radius_voronoi")
        
        if not filepath or not site_ids:
            self.gui_components.show_message("Peringatan", "Mohon lengkapi file input dan Site ID.", True)
            return
        
        self.run_process_in_thread(self.process_voronoi, (filepath, site_ids, max_radius), "voronoi")
    
    def run_balltree_process_thread(self):
        """Handler untuk tombol proses BallTree"""
        filepath = dpg.get_value("file_path")
        site_ids = dpg.get_value("site_ids_balltree")
        candidate_per_sector = dpg.get_value("candidate_per_sector")
        max_radius = dpg.get_value("max_radius_balltree")
        
        if not filepath or not site_ids:
            self.gui_components.show_message("Peringatan", "Mohon lengkapi file input dan Site ID.", True)
            return
        
        self.run_process_in_thread(self.process_balltree, 
                                (filepath, site_ids, candidate_per_sector, max_radius), 
                                "balltree")
    
    def run_facing_process_thread(self):
        """Handler untuk tombol proses Facing/H2H"""
        filepath = dpg.get_value("file_path")
        site_ids = dpg.get_value("site_ids_facing")
        max_radius = dpg.get_value("max_radius_facing")
        beam_width = dpg.get_value("beam_width")
        h2h_threshold = dpg.get_value("h2h_threshold")
        
        if not filepath or not site_ids:
            self.gui_components.show_message("Peringatan", "Mohon lengkapi file input dan Site ID.", True)
            return
        
        self.run_process_in_thread(self.process_facing, 
                                (filepath, site_ids, max_radius, beam_width, h2h_threshold), 
                                "facing")
    
    def main(self):
        """
        Entry point utama aplikasi:
        1. Set DPI awareness untuk Windows
        2. Cek mode trial berdasarkan tanggal
        3. Jika masih trial -> langsung jalankan GUI
        4. Jika sudah expired -> jalankan proses login
        5. Setelah login berhasil -> jalankan GUI
        """
        # Set DPI awareness (Windows)
        if sys.platform.startswith("win"):
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        
        # Cek trial mode
        current_date = datetime.datetime.now().date()
        expiry_date = datetime.date(2025, 6, 30)
        is_trial_mode = current_date <= expiry_date
        
        if is_trial_mode:
            print("Trial mode - Experimental")
            self.create_gui(is_trial_mode)
        else:
            # Login handling untuk versi penuh
            from auth import AuthManager
            auth_manager = AuthManager()
            
            if auth_manager.handle_login():
                self.create_gui(is_trial_mode)


def main():
    """Function utama untuk menjalankan aplikasi"""
    app = MainApplication()
    app.main()


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, "Click OK and Wait..", "Opening File...", 0)
    
    main() 