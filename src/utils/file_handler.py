"""
File Handler - Input/Output Operations

Modul untuk handling operasi file input/output dalam aplikasi 1st Tier Generator.
Mendukung format CSV dan Excel dengan validasi header yang diperlukan.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile


class FileHandler:
    """Handler untuk operasi file I/O"""
    
    def __init__(self):
        self.required_headers = ["Site ID", "Sector", "Latitude", "Longitude", "Dir"]
        self.optional_headers = ["tilt"]
        self.output_base_dir = os.path.join(os.path.expanduser("~"), "Documents", "1st_tier_generator_HD")
    
    def read_file(self, filepath):
        """
        Membaca file input (CSV/Excel):
        1. Deteksi format file berdasarkan ekstensi
        2. Baca file menggunakan pandas
        3. Validasi dan normalisasi header
        4. Return DataFrame yang telah divalidasi
        
        Args:
            filepath: Path ke file input
            
        Returns:
            pandas.DataFrame: Data yang telah divalidasi
            
        Raises:
            ValueError: Jika format file tidak didukung atau header tidak valid
            FileNotFoundError: Jika file tidak ditemukan
        """
        try:
            # Step 1: Validasi file exists
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File tidak ditemukan: {filepath}")
            
            # Step 2: Deteksi format dan baca file
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(filepath)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            else:
                raise ValueError(f"Format file tidak didukung: {file_ext}")
            
            # Step 3: Validasi dan normalisasi header
            df = self._validate_and_normalize_headers(df)
            
            # Step 4: Validasi data
            df = self._validate_data_types(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error membaca file {filepath}: {str(e)}")
    
    def _validate_and_normalize_headers(self, df):
        """
        Validasi dan normalisasi header:
        1. Cek apakah semua header wajib ada
        2. Normalisasi nama header (case-insensitive)
        3. Rename header ke format standar
        4. Return DataFrame dengan header yang dinormalisasi
        """
        # Normalisasi header (case-insensitive dan trim whitespace)
        df.columns = df.columns.str.strip()
        
        # Mapping header variations ke standar
        header_mapping = {
            'site id': 'Site ID',
            'siteid': 'Site ID',
            'site_id': 'Site ID',
            'sector': 'Sector',
            'latitude': 'Latitude',
            'lat': 'Latitude',
            'longitude': 'Longitude',
            'lon': 'Longitude',
            'lng': 'Longitude',
            'dir': 'Dir',
            'direction': 'Dir',
            'azimuth': 'Dir',
            'tilt': 'tilt'
        }
        
        # Rename columns based on mapping
        df_renamed = df.rename(columns={
            col: header_mapping.get(col.lower(), col) 
            for col in df.columns
        })
        
        # Validasi header wajib
        missing_headers = [h for h in self.required_headers if h not in df_renamed.columns]
        if missing_headers:
            raise ValueError(f"Header wajib tidak ditemukan: {missing_headers}")
        
        return df_renamed
    
    def _validate_data_types(self, df):
        """
        Validasi dan konversi tipe data:
        1. Konversi Site ID dan Sector ke string
        2. Konversi Latitude, Longitude, Dir ke float
        3. Handle missing values
        4. Validasi range nilai (koordinat, azimuth)
        5. Return DataFrame dengan tipe data yang benar
        """
        try:
            # Konversi tipe data
            df['Site ID'] = df['Site ID'].astype(str)
            df['Sector'] = df['Sector'].astype(str)
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
            df['Dir'] = pd.to_numeric(df['Dir'], errors='coerce')
            
            # Handle tilt jika ada
            if 'tilt' in df.columns:
                df['tilt'] = pd.to_numeric(df['tilt'], errors='coerce')
            
            # Validasi missing values untuk kolom wajib
            required_numeric = ['Latitude', 'Longitude', 'Dir']
            for col in required_numeric:
                if df[col].isna().any():
                    raise ValueError(f"Ditemukan nilai kosong pada kolom {col}")
            
            # Validasi range nilai
            self._validate_coordinate_ranges(df)
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error validasi data: {str(e)}")
    
    def _validate_coordinate_ranges(self, df):
        """
        Validasi range koordinat dan azimuth:
        1. Latitude: -90 to 90
        2. Longitude: -180 to 180  
        3. Dir: 0 to 360
        4. Raise error jika ada nilai di luar range
        """
        # Validasi Latitude
        if not df['Latitude'].between(-90, 90).all():
            raise ValueError("Latitude harus dalam range -90 hingga 90")
        
        # Validasi Longitude
        if not df['Longitude'].between(-180, 180).all():
            raise ValueError("Longitude harus dalam range -180 hingga 180")
        
        # Validasi Dir
        if not df['Dir'].between(0, 360).all():
            raise ValueError("Dir harus dalam range 0 hingga 360")
    
    def check_headers(self, df):
        """
        Fungsi tambahan untuk cek header (backward compatibility):
        1. Validasi keberadaan header wajib
        2. Print informasi header yang ditemukan
        3. Return True jika valid
        """
        missing_headers = [h for h in self.required_headers if h not in df.columns]
        
        if missing_headers:
            print(f"Header wajib tidak ditemukan: {missing_headers}")
            print(f"Header yang tersedia: {list(df.columns)}")
            return False
        
        print(f"✓ Semua header wajib ditemukan: {self.required_headers}")
        return True
    
    def parse_data(self, df):
        """
        Parse data ke format yang digunakan processor:
        1. Rename kolom ke format internal
        2. Add computed fields jika diperlukan
        3. Return list of dictionaries atau DataFrame
        
        Args:
            df: DataFrame yang sudah divalidasi
            
        Returns:
            list: List of dictionaries dengan format standar
        """
        try:
            # Rename kolom ke format internal processor
            df_parsed = df.rename(columns={
                'Site ID': 'site_id',
                'Sector': 'sector', 
                'Latitude': 'lat',
                'Longitude': 'lon',
                'Dir': 'azimuth'
            })
            
            # Tambah computed fields jika diperlukan
            df_parsed['row_id'] = range(len(df_parsed))
            
            # Convert ke list of dictionaries
            points = df_parsed.to_dict('records')
            
            return points
            
        except Exception as e:
            raise Exception(f"Error parsing data: {str(e)}")
    
    def save_result_to_csv(self, results, method_name):
        """
        Simpan hasil analisis ke file CSV:
        1. Buat folder output jika belum ada
        2. Generate nama file dengan timestamp
        3. Convert results ke DataFrame
        4. Simpan ke CSV dengan encoding UTF-8
        5. Return path file output
        
        Args:
            results: List of dictionaries hasil analisis
            method_name: Nama metode untuk prefix filename
            
        Returns:
            str: Path ke file output yang disimpan
        """
        try:
            # Step 1: Buat folder output
            os.makedirs(self.output_base_dir, exist_ok=True)
            
            # Step 2: Generate filename dengan timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{method_name}_{timestamp}.csv"
            output_path = os.path.join(self.output_base_dir, filename)
            
            # Step 3: Convert results ke DataFrame
            if not results:
                raise ValueError("Tidak ada hasil untuk disimpan")
            
            df_results = pd.DataFrame(results)
            
            # Step 4: Simpan ke CSV
            df_results.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✓ Hasil disimpan ke: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error menyimpan hasil: {str(e)}")
    
    def create_sample_data(self, num_sites=10, sectors_per_site=3):
        """
        Buat data sample untuk testing (opsional):
        1. Generate koordinat random dalam area tertentu
        2. Buat site ID dan sektor
        3. Assign azimuth untuk setiap sektor
        4. Return DataFrame sample
        
        Args:
            num_sites: Jumlah site yang akan dibuat
            sectors_per_site: Jumlah sektor per site
            
        Returns:
            pandas.DataFrame: Sample data dengan format yang benar
        """
        # Generate sample data
        # Implementasi pembuatan data sample
        pass
    
    def validate_site_ids(self, df, site_ids_string):
        """
        Validasi Site ID yang diinput user:
        1. Parse string site IDs menjadi list
        2. Cek apakah semua site ID ada dalam data
        3. Return list site ID yang valid dan yang tidak ditemukan
        
        Args:
            df: DataFrame input data
            site_ids_string: String site IDs dipisahkan koma
            
        Returns:
            tuple: (valid_site_ids, missing_site_ids)
        """
        # Parse site IDs
        input_site_ids = [sid.strip() for sid in site_ids_string.split(",") if sid.strip()]
        
        # Get unique site IDs dari data
        available_site_ids = set(df['Site ID'].unique())
        
        # Cek yang valid dan yang missing
        valid_site_ids = [sid for sid in input_site_ids if sid in available_site_ids]
        missing_site_ids = [sid for sid in input_site_ids if sid not in available_site_ids]
        
        return valid_site_ids, missing_site_ids
    
    def get_data_summary(self, df):
        """
        Generate summary statistik data input:
        1. Jumlah site dan sektor
        2. Range koordinat
        3. Distribusi azimuth
        4. Return dictionary summary
        """
        summary = {
            'total_rows': len(df),
            'unique_sites': df['Site ID'].nunique(),
            'unique_sectors': len(df),
            'lat_range': (df['Latitude'].min(), df['Latitude'].max()),
            'lon_range': (df['Longitude'].min(), df['Longitude'].max()),
            'azimuth_stats': {
                'min': df['Dir'].min(),
                'max': df['Dir'].max(),
                'mean': df['Dir'].mean()
            }
        }
        
        return summary 