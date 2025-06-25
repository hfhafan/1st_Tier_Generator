"""
1st Tier Generator HD - Main Application

Entry point for GUI application for 1st tier analysis in telecommunications networks.
Uses DearPyGUI for interface and supports 3 analysis methods.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import os
import sys
import threading
import datetime
import dearpygui.dearpygui as dpg

# Import internal modules
from processors.voronoi_processor import VoronoiProcessor
from processors.balltree_processor import BallTreeProcessor  
from processors.facing_processor import FacingProcessor
from utils.file_handler import FileHandler
from utils.gui_components import GUIComponents

class MainApplication:
    """Main class for 1st Tier Generator HD application"""
    
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
        Logic for detecting indoor sites:
        1. Get all sectors from site_id
        2. Check if all sectors have Dir = 0° or 360°
        3. Return True if indoor, False if outdoor
        """
        # Implementation of indoor detection logic
        pass
    
    def process_voronoi(self, filepath, site_ids, max_radius):
        """
        Voronoi process flow (Site Level):
        1. Parse input file and validate headers
        2. Extract site coordinates (not sectors)
        3. Check if site is indoor -> set "Indoor" as 1st tier
        4. For outdoor sites -> run Voronoi algorithm
        5. Identify sites sharing boundaries
        6. Save results to CSV
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
                    # Add results for indoor sites
                    results.extend(self._create_indoor_results(df, site_id))
                else:
                    # Run Voronoi process
                    site_results = self.voronoi_processor.run_process(
                        [site_id], points, max_radius
                    )
                    results.extend(site_results)
            
            # Step 3: Save results
            output_path = self.file_handler.save_result_to_csv(results, "Site_Voronoi")
            return True, f"Process completed. File saved at: {output_path}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def process_balltree(self, filepath, site_ids, candidate_per_sector, max_radius):
        """
        BallTree process flow (Sector Level):
        1. Parse input file and validate headers
        2. Check if site is indoor -> set "Indoor" as 1st tier
        3. For outdoor sites -> build BallTree from sector coordinates
        4. Query k-nearest neighbors for each sector
        5. Filter based on bearing and sector direction
        6. Ensure different 1st tier for each sector within a site
        7. Save results to CSV
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
                    # Add results for indoor sites
                    results.extend(self._create_indoor_results(df, site_id))
                else:
                    # Run BallTree process
                    site_results = self.balltree_processor.run_process(
                        df, [site_id], candidate_per_sector, max_radius
                    )
                    results.extend(site_results)
            
            # Step 3: Save results
            output_path = self.file_handler.save_result_to_csv(results, "Sector_BallTree")
            return True, f"Process completed. File saved at: {output_path}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def process_facing(self, filepath, site_ids, max_radius, beam_width, h2h_threshold):
        """
        Facing/H2H process flow (Sector Level):
        1. Parse input file and validate headers
        2. Check if site is indoor -> set "Indoor" as 1st tier
        3. For outdoor sites:
           a. Find candidates within radius using BallTree
           b. Filter based on sector beam_width
           c. Calculate bearing between sectors
           d. Detect Head-to-Head conditions:
              - Sector A Dir within beam_width of bearing to B
              - Sector B Dir within beam_width of bearing to A  
              - Distance < threshold
        4. Save results with H2H status to CSV
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
                    # Add results for indoor sites
                    results.extend(self._create_indoor_results(df, site_id, include_h2h=True))
                else:
                    # Run Facing/H2H process
                    site_results = self.facing_processor.run_process(
                        df, [site_id], max_radius, beam_width, h2h_threshold
                    )
                    results.extend(site_results)
            
            # Step 3: Save results
            output_path = self.file_handler.save_result_to_csv(results, "Sector_Facing_H2H")
            return True, f"Process completed. File saved at: {output_path}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _create_indoor_results(self, df, site_id, include_h2h=False):
        """Helper method for creating indoor site results"""
        # Implementation for indoor site result creation
        pass
    
    def run_process_in_thread(self, process_func, args, tab_id):
        """
        Run process in separate thread:
        1. Show loading window
        2. Run process function in background thread
        3. Update UI with results (success/error)
        4. Close loading window
        5. Open output folder if successful
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
        Create GUI with DearPyGUI:
        1. Setup context and viewport
        2. Load fonts and themes
        3. Download and load logo
        4. Create file dialog
        5. Create layout with tabs:
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
        
        # Main window with tabs
        with dpg.window(tag="Primary Window", label=self.APP_TITLE):
            self.gui_components.create_header()
            self.gui_components.create_file_input_section()
            
            # Tabs for different methods
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
        """Handler for Voronoi process button"""
        filepath = dpg.get_value("file_path")
        site_ids = dpg.get_value("site_ids_voronoi")
        max_radius = dpg.get_value("max_radius_voronoi")
        
        if not filepath or not site_ids:
            self.gui_components.show_message("Warning", "Please complete input file and Site ID.", True)
            return
        
        self.run_process_in_thread(self.process_voronoi, (filepath, site_ids, max_radius), "voronoi")
    
    def run_balltree_process_thread(self):
        """Handler for BallTree process button"""
        filepath = dpg.get_value("file_path")
        site_ids = dpg.get_value("site_ids_balltree")
        candidate_per_sector = dpg.get_value("candidate_per_sector")
        max_radius = dpg.get_value("max_radius_balltree")
        
        if not filepath or not site_ids:
            self.gui_components.show_message("Warning", "Please complete input file and Site ID.", True)
            return
        
        self.run_process_in_thread(self.process_balltree, 
                                (filepath, site_ids, candidate_per_sector, max_radius), 
                                "balltree")
    
    def run_facing_process_thread(self):
        """Handler for Facing/H2H process button"""
        filepath = dpg.get_value("file_path")
        site_ids = dpg.get_value("site_ids_facing")
        max_radius = dpg.get_value("max_radius_facing")
        beam_width = dpg.get_value("beam_width")
        h2h_threshold = dpg.get_value("h2h_threshold")
        
        if not filepath or not site_ids:
            self.gui_components.show_message("Warning", "Please complete input file and Site ID.", True)
            return
        
        self.run_process_in_thread(self.process_facing, 
                                (filepath, site_ids, max_radius, beam_width, h2h_threshold), 
                                "facing")
    
    def main(self):
        """
        Main application entry point:
        1. Set DPI awareness for Windows
        2. Check trial mode based on date
        3. If still in trial -> run GUI directly
        4. If expired -> run login process
        5. After successful login -> run GUI
        """
        # Set DPI awareness (Windows)
        if sys.platform.startswith("win"):
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        
        # Check trial mode
        current_date = datetime.datetime.now().date()
        expiry_date = datetime.date(2025, 6, 30)
        is_trial_mode = current_date <= expiry_date
        
        if is_trial_mode:
            print("Trial mode - Experimental")
            self.create_gui(is_trial_mode)
        else:
            # Login handling for full version
            from auth import AuthManager
            auth_manager = AuthManager()
            
            if auth_manager.handle_login():
                self.create_gui(is_trial_mode)


def main():
    """Main function to run the application"""
    app = MainApplication()
    app.main()


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, "Click OK and Wait..", "Opening File...", 0)
    
    main() 