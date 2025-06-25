"""
GUI Components for 1st Tier Generator HD

This module provides GUI component utilities for the DearPyGUI-based interface.
Handles window creation, layout management, and user interaction elements.

Components include:
- File dialogs and input handlers
- Tab layouts for different analysis methods
- Progress indicators and status messages
- Theme and font management

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import os
import sys
import threading
import datetime
import webbrowser
import tempfile
import requests
import subprocess
from PIL import Image
import dearpygui.dearpygui as dpg

class GUIComponents:
    """
    GUI component utilities for 1st Tier Generator HD
    
    This class manages GUI components, layouts, and user interactions
    for the DearPyGUI-based application interface.
    """
    
    def __init__(self):
        self.app_title = "1st Tier Generator HD - Multi Method"
        self.app_version = "1.0.0"
        self.logo_loaded = False
    
    def setup_fonts_and_themes(self):
        """
        Setup fonts and themes for the application
        
        Loads system fonts if available and applies custom themes
        for better visual appearance.
        """
        with dpg.font_registry():
            default_font = None
            title_font = None
            
            # Try to load system fonts (Windows)
            font_path = "C:/Windows/Fonts/segoeui.ttf"
            title_font_path = "C:/Windows/Fonts/segoeuib.ttf"
            
            try:
                if os.path.exists(font_path):
                    default_font = dpg.add_font(font_path, 16)
                
                if os.path.exists(title_font_path):
                    title_font = dpg.add_font(title_font_path, 24)
            except Exception as e:
                print(f"Failed to load fonts: {e}")
        
        # Apply global theme
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
        
        dpg.bind_theme(global_theme)
        
        return default_font, title_font
    
    def download_and_load_logo(self):
        """
        Download and load application logo from remote URL
        
        Downloads logo image to temporary directory and loads it
        into DearPyGUI texture registry for display.
        """
        try:
            image_url = "https://drive.google.com/uc?export=download&id=1RxiEZ-JqJNcQFXCtKWjIKazykqikXx6t"
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, "logo.png")
            
            # Download image
            self._download_image(image_url, image_path)

            # Process and load image
            logo_image = Image.open(image_path)
            width, height = logo_image.size
            logo_image.save(image_path)
            
            # Load into DearPyGUI texture registry
            width, height, channels, data = dpg.load_image(image_path)

            with dpg.texture_registry(show=False):
                dpg.add_static_texture(width, height, data, tag="logo_image")
            
            self.logo_loaded = True
            
        except Exception as e:
            print(f"Error processing logo: {e}")
            self.logo_loaded = False
    
    def _download_image(self, url, save_path):
        """
        Download image from URL to local path
        
        Args:
            url (str): URL of image to download
            save_path (str): Local path to save image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"Downloading image from {url}")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print(f"Image successfully saved to {save_path}")
                return True
            else:
                print(f"Failed to download image: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False
    
    def create_file_dialog(self):
        """
        Create file dialog for input file selection
        
        Sets up DearPyGUI file dialog with appropriate file filters
        for CSV and Excel files.
        """
        with dpg.file_dialog(
            directory_selector=False, 
            show=False,
            callback=self._file_dialog_callback,
            tag="file_dialog",
            width=700,
            height=400,
            default_path=os.path.expanduser("~"),
            cancel_callback=lambda: None,
            id="file_dialog_id"
        ):
            dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")
            dpg.add_file_extension(".xlsx", color=(0, 255, 255, 255), custom_text="[Excel]")
            dpg.add_file_extension(".*", color=(255, 255, 255, 255), custom_text="[All Files]")
    
    def _file_dialog_callback(self, sender, app_data):
        """
        Callback for file dialog selection
        
        Args:
            sender: DearPyGUI sender object
            app_data: Dialog data containing selected files
        """
        if not app_data["selections"]:
            return
            
        selected_files = app_data["selections"]
        if selected_files:
            selected_file = next(iter(selected_files.values()))
            dpg.set_value("file_path", selected_file)
    
    def browse_for_file(self):
        """
        Open file browser dialog
        
        Uses system file dialog as fallback if DearPyGUI dialog fails.
        """
        try:
            # Try system file dialog first
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()  # Hide main window
            file_path = filedialog.askopenfilename(
                title="Select input file",
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
            # Fallback to DearPyGUI dialog
            dpg.show_item("file_dialog")
    
    def create_header(self):
        """
        Create application header with logo and title
        
        Displays logo (if loaded) and application title/subtitle
        in a horizontal layout.
        """
        with dpg.group(horizontal=True):
            if self.logo_loaded:
                try:
                    dpg.add_image("logo_image", width=120, height=120)
                    dpg.add_spacer(width=10)
                except Exception as e:
                    print(f"Failed to display logo: {e}")
                    
            with dpg.group():
                dpg.add_spacer(height=10)
                dpg.add_text(self.app_title, tag="title")
                dpg.add_text("Multi-Method 1st Tier Generator", tag="subtitle")
                dpg.add_spacer(height=5)
    
    def create_file_input_section(self):
        """
        Create file input section with browse button
        
        Provides input field for file path and browse button
        for file selection.
        """
        with dpg.collapsing_header(label="Input File", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Input file (.csv / .xlsx):")
                dpg.add_input_text(tag="file_path", width=-200)
                dpg.add_button(label="Browse", callback=self.browse_for_file)
    
    def create_voronoi_tab(self, process_callback):
        """
        Create Voronoi analysis tab
        
        Args:
            process_callback: Callback function for process button
        """
        with dpg.tab(label="Site Level - Voronoi"):
            with dpg.group():
                dpg.add_text("Site IDs (comma-separated):")
                dpg.add_input_text(tag="site_ids_voronoi", width=-1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Maximum radius (km):")
                    dpg.add_input_float(tag="max_radius_voronoi", default_value=10.0, 
                                      min_value=1.0, max_value=20.0, width=100, step=1.0)
                
                dpg.add_separator()
                dpg.add_text("This method finds sites around target sites based on distance.")
                dpg.add_text("Only considers distance, not individual sectors.")
                dpg.add_separator()
                
                dpg.add_button(label="Process", callback=process_callback, 
                             width=120, height=40)
                dpg.add_text("", tag="status_voronoi")
    
    def create_balltree_tab(self, process_callback):
        """
        Create BallTree analysis tab
        
        Args:
            process_callback: Callback function for process button
        """
        with dpg.tab(label="Sector Level - BallTree"):
            with dpg.group():
                dpg.add_text("Site IDs (comma-separated):")
                dpg.add_input_text(tag="site_ids_balltree", width=-1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Candidates per sector:")
                    dpg.add_input_int(tag="candidate_per_sector", default_value=1, 
                                    min_value=1, max_value=10, width=100)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Maximum radius (km):")
                    dpg.add_input_float(tag="max_radius_balltree", default_value=7.0, 
                                      min_value=1.0, max_value=20.0, width=100, step=1)
                
                dpg.add_separator()
                dpg.add_text("BallTree method uses kNN to find candidates, "
                          "then filters by bearing.")
                dpg.add_separator()
                
                dpg.add_button(label="Process", callback=process_callback, 
                             width=120, height=40)
                dpg.add_text("", tag="status_balltree")
    
    def create_facing_tab(self, process_callback):
        """
        Create Facing/H2H analysis tab
        
        Args:
            process_callback: Callback function for process button
        """
        with dpg.tab(label="Sector Level - H2H"):
            with dpg.group():
                dpg.add_text("Site IDs (comma-separated):")
                dpg.add_input_text(tag="site_ids_facing", width=-1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Search radius (km):")
                    dpg.add_input_float(tag="max_radius_facing", default_value=10.0, 
                                      min_value=1.0, max_value=25.0, width=100, step=1)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Beam width filter (degrees):")
                    dpg.add_input_float(tag="beam_width", default_value=120.0, 
                                      min_value=30.0, max_value=180.0, width=100, step=5)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("H2H threshold (degrees):")
                    dpg.add_input_float(tag="h2h_threshold", default_value=30.0, 
                                      min_value=10.0, max_value=60.0, width=100, step=5)
                
                dpg.add_separator()
                dpg.add_text("This method uses optimized approach:")
                dpg.add_text("1. Find 1st tier candidates within radius using BallTree")
                dpg.add_text("2. Filter based on sector direction (beam width)")
                dpg.add_text("3. Determine Head-to-Head (H2H) status with criteria:")
                dpg.add_text("   - Source sector Dir within beam width of bearing to target")
                dpg.add_text("   - Target sector Dir within beam width of bearing to source")
                dpg.add_text("   - Distance between them < 1.5 km")
                dpg.add_separator()
                
                dpg.add_button(label="Process", callback=process_callback, 
                             width=120, height=40)
                dpg.add_text("", tag="status_facing")
    
    def create_about_tab(self, is_trial_mode=False):
        """
        Create About tab with application information
        
        Args:
            is_trial_mode (bool): Whether application is in trial mode
        """
        with dpg.tab(label="About"):
            with dpg.group():
                dpg.add_spacer(height=10)
                dpg.add_text("1st Tier Generator HD - Multi Method", tag="about_title")
                
                dpg.add_separator()
                dpg.add_spacer(height=5)
                
                dpg.add_text("This application is developed to identify 1st tier sites in telecommunications networks")
                dpg.add_text("using various methods: Voronoi (Site Level), BallTree, and Facing Sector (H2H).")
                
                # Button to open README.md
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text("For complete information: ")
                    dpg.add_button(label="Open README.md", callback=self._open_readme)
                
                # Required input file headers
                dpg.add_spacer(height=10)
                dpg.add_text("Required Input File Headers:", tag="header_title", color=[0, 200, 0, 255])
                
                dpg.add_text("Input file should be sector-level data, where each row represents one sector.")
                
                dpg.add_text("- Site ID    : Unique site identifier (string)")
                dpg.add_text("- Sector     : Sector ID within site (string)")
                dpg.add_text("- Latitude   : Latitude coordinate (float)")
                dpg.add_text("- Longitude  : Longitude coordinate (float)")
                dpg.add_text("- Dir        : Sector azimuth direction in degrees (float)")
                dpg.add_text("- [opt] tilt : Antenna tilt angle (float, optional)")
                
                # Analysis methods information
                dpg.add_spacer(height=10)
                dpg.add_text("Analysis Methods:", tag="method_title")
                
                dpg.add_text("1. Site Level - Voronoi:")
                dpg.add_text("   - Creates Voronoi diagram based on sites (not sectors)")
                dpg.add_text("   - Identifies sites sharing Voronoi cell boundaries")
                dpg.add_text("   - Sites are considered indoor if all sectors have Dir 0° or 360°")
                dpg.add_text("   - Output: 1st tier site IDs & distance (km)")
                
                dpg.add_spacer(height=5)
                dpg.add_text("2. Sector Level - BallTree:")
                dpg.add_text("   - Finds 1st tier for each sector using BallTree algorithm")
                dpg.add_text("   - Filters based on sector Dir direction")
                dpg.add_text("   - Ensures different 1st tier for each sector")
                dpg.add_text("   - Output: 1st tier site ID & distance (km) per sector")
                
                dpg.add_spacer(height=5)
                dpg.add_text("3. Sector Level - H2H:")
                dpg.add_text("   - Finds 1st tier candidates for each sector based on bearing")
                dpg.add_text("   - Determines Head-to-Head (H2H) status with criteria:")
                dpg.add_text("     - Source sector Dir within beam width of bearing to target")
                dpg.add_text("     - Target sector Dir within beam width of bearing to source")
                dpg.add_text("     - Distance between them < 1.5 km")
                dpg.add_text("   - Output: 1st tier site ID & sector, H2H status, distance (km)")
                
                # Author information
                dpg.add_spacer(height=20)
                dpg.add_text("Author:", tag="author_title")
                
                dpg.add_text("Hadi Fauzan Hanif")
                dpg.add_text("Email: hadifauzanhanif@gmail.com")
                
                # WhatsApp with clickable link
                with dpg.group(horizontal=True):
                    dpg.add_text("WhatsApp: +62 813-5719-8294")
                    dpg.add_button(label="Open WhatsApp", 
                                 callback=lambda: webbrowser.open("https://wa.me/6281357198294"))
                
                # LinkedIn with clickable link
                with dpg.group(horizontal=True):
                    dpg.add_text("LinkedIn:")
                    dpg.add_button(label="Visit Profile", 
                                 callback=lambda: webbrowser.open("https://www.linkedin.com/in/hadi-fauzan-hanif-0b407b174/"))
                
                # Version and license information
                dpg.add_spacer(height=20)
                dpg.add_text(f"Version: {self.app_version}")
                dpg.add_text("© " + datetime.datetime.now().strftime("%Y"))
                
                # Trial mode information
                if is_trial_mode:
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    dpg.add_text("License Status:", tag="license_title")
                    dpg.add_text("Trial Mode - Experimental", color=[0, 200, 0, 255])
                    dpg.add_text("Contact author for login credentials.")
                else:
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    dpg.add_text("License Status:", tag="license_title")
                    dpg.add_text("Full License", color=[0, 200, 0, 255])
    
    def create_footer(self, is_trial_mode=False):
        """
        Create application footer with version and license info
        
        Args:
            is_trial_mode (bool): Whether application is in trial mode
        """
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text(f"v{self.app_version} © " + datetime.datetime.now().strftime("%Y"))
            if is_trial_mode:
                expiry_date = datetime.date(2025, 6, 30).strftime("%d-%m-%Y")
                dpg.add_text(f" | Trial Mode - Experimental", color=[0, 200, 0, 255])
    
    def _open_readme(self):
        """
        Open README.md file in default application
        """
        try:
            readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
            if os.path.exists(readme_path):
                if sys.platform.startswith('win'):
                    os.startfile(readme_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.call(['open', readme_path])
                else:
                    subprocess.call(['xdg-open', readme_path])
            else:
                self.show_message("Error", "README.md file not found.", is_error=True)
        except Exception as e:
            self.show_message("Error", f"Failed to open README.md: {str(e)}", is_error=True)
    
    def show_message(self, title, message, is_error=False):
        """
        Show modal message dialog
        
        Args:
            title (str): Dialog title
            message (str): Message text
            is_error (bool): Whether this is an error message
        """
        with dpg.window(label=title, modal=True, autosize=True, tag="modal_window"):
            dpg.add_text(message)
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("modal_window"), width=75)
    
    def show_loading_window(self, tab_id):
        """
        Show loading window for active process
        
        Args:
            tab_id (str): ID of the tab requesting loading window
        """
        with dpg.window(label="Processing...", modal=True, no_close=True, 
                       width=300, height=100, tag=f"loading_{tab_id}", pos=(250, 250)):
            dpg.add_text("Processing, please wait...")
            dpg.add_loading_indicator(style=1, radius=10.0)
    
    def process_complete_callback(self, tab_id, success, message):
        """
        Callback for process completion
        
        Args:
            tab_id (str): ID of the tab that completed processing
            success (bool): Whether process was successful
            message (str): Result message
        """
        # Close loading window
        if dpg.does_item_exist(f"loading_{tab_id}"):
            dpg.delete_item(f"loading_{tab_id}")
        
        # Show result
        if success:
            color = [0, 200, 0, 255]
            dpg.configure_item(f"status_{tab_id}", default_value=message, color=color)
            
            # Open output folder if successful
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "1st_tier_generator_HD")
            try:
                webbrowser.open(output_dir)
            except Exception:
                pass
        else:
            color = [255, 0, 0, 255]
            dpg.configure_item(f"status_{tab_id}", default_value=message, color=color) 