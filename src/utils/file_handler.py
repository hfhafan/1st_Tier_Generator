"""
File Handler Utilities for 1st Tier Generator HD

This module provides file I/O operations for the 1st tier analysis application.
Handles CSV/Excel file reading, data validation, and result export.

Supported formats:
- CSV files (.csv)
- Excel files (.xlsx, .xls)

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import pandas as pd
import numpy as np
import os
import datetime
from pathlib import Path

class FileHandler:
    """
    Handler for file I/O operations in 1st tier analysis
    
    This class manages input file reading, data validation,
    and output file generation for the application.
    """
    
    def __init__(self):
        self.required_headers = ['Site ID', 'Sector', 'Latitude', 'Longitude', 'Dir']
        self.optional_headers = ['tilt', 'height', 'technology']
        self.output_directory = self._get_output_directory()
    
    def _get_output_directory(self):
        """
        Get or create output directory for results
        
        Returns:
            str: Path to output directory
        """
        # Create output directory in user's Documents folder
        docs_folder = Path.home() / "Documents"
        output_dir = docs_folder / "1st_tier_generator_HD"
        
        # Create directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return str(output_dir)
    
    def read_file(self, filepath):
        """
        Read input file (CSV or Excel) with proper encoding handling
        
        Args:
            filepath (str): Path to input file
            
        Returns:
            DataFrame: Parsed data with standardized column names
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported or headers missing
            Exception: For other file reading errors
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Get file extension
        file_ext = Path(filepath).suffix.lower()
        
        try:
            if file_ext == '.csv':
                # Try different encodings for CSV
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    raise ValueError("Unable to read CSV file with any supported encoding")
                    
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath, engine='openpyxl' if file_ext == '.xlsx' else 'xlrd')
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            raise Exception(f"Error reading file {filepath}: {str(e)}")
        
        # Validate and standardize data
        df = self._validate_and_standardize(df)
        
        return df
    
    def _validate_and_standardize(self, df):
        """
        Validate input data and standardize column names
        
        Args:
            df (DataFrame): Raw input data
            
        Returns:
            DataFrame: Validated and standardized data
            
        Raises:
            ValueError: If required headers are missing or data is invalid
        """
        if df.empty:
            raise ValueError("Input file is empty")
        
        # Check for required headers (case-insensitive)
        df_headers = [col.strip().lower() for col in df.columns]
        required_lower = [h.lower() for h in self.required_headers]
        
        missing_headers = []
        for required in required_lower:
            if required not in df_headers:
                missing_headers.append(required)
        
        if missing_headers:
            raise ValueError(f"Missing required headers: {missing_headers}")
        
        # Standardize column names (map to expected names)
        column_mapping = {}
        for col in df.columns:
            col_lower = col.strip().lower()
            if col_lower == 'site id':
                column_mapping[col] = 'site_id'
            elif col_lower == 'sector':
                column_mapping[col] = 'sector'
            elif col_lower == 'latitude':
                column_mapping[col] = 'latitude'
            elif col_lower == 'longitude':
                column_mapping[col] = 'longitude'
            elif col_lower == 'dir':
                column_mapping[col] = 'azimuth'
            elif col_lower == 'tilt':
                column_mapping[col] = 'tilt'
        
        df = df.rename(columns=column_mapping)
        
        # Validate data types and ranges
        df = self._validate_data_types(df)
        
        return df
    
    def _validate_data_types(self, df):
        """
        Validate and convert data types
        
        Args:
            df (DataFrame): Input data
            
        Returns:
            DataFrame: Data with validated types
        """
        # Remove rows with missing critical data
        critical_cols = ['site_id', 'sector', 'latitude', 'longitude', 'azimuth']
        df = df.dropna(subset=critical_cols)
        
        if df.empty:
            raise ValueError("No valid data rows found after removing incomplete records")
        
        # Convert data types
        try:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['azimuth'] = pd.to_numeric(df['azimuth'], errors='coerce')
            
            if 'tilt' in df.columns:
                df['tilt'] = pd.to_numeric(df['tilt'], errors='coerce')
        except Exception as e:
            raise ValueError(f"Error converting numeric columns: {str(e)}")
        
        # Remove rows with invalid coordinates or azimuth
        df = df.dropna(subset=['latitude', 'longitude', 'azimuth'])
        
        # Validate coordinate ranges
        invalid_coords = (
            (df['latitude'] < -90) | (df['latitude'] > 90) |
            (df['longitude'] < -180) | (df['longitude'] > 180)
        )
        
        if invalid_coords.any():
            print(f"Warning: Removing {invalid_coords.sum()} rows with invalid coordinates")
            df = df[~invalid_coords]
        
        # Validate azimuth range
        invalid_azimuth = (df['azimuth'] < 0) | (df['azimuth'] > 360)
        if invalid_azimuth.any():
            print(f"Warning: Removing {invalid_azimuth.sum()} rows with invalid azimuth")
            df = df[~invalid_azimuth]
        
        if df.empty:
            raise ValueError("No valid data rows found after validation")
        
        return df
    
    def parse_data(self, df):
        """
        Parse DataFrame to list of dictionaries for processing
        
        Args:
            df (DataFrame): Validated input data
            
        Returns:
            list: List of sector dictionaries
        """
        return df.to_dict('records')
    
    def save_result_to_csv(self, results, method_name):
        """
        Save analysis results to CSV file with timestamp
        
        Args:
            results (list): List of result dictionaries
            method_name (str): Name of analysis method for filename
            
        Returns:
            str: Path to saved file
        """
        if not results:
            raise ValueError("No results to save")
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{method_name}_Results_{timestamp}.csv"
        filepath = os.path.join(self.output_directory, filename)
        
        # Convert results to DataFrame
        df_results = pd.DataFrame(results)
        
        # Save to CSV
        try:
            df_results.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"Results saved to: {filepath}")
            return filepath
        except Exception as e:
            raise Exception(f"Error saving results: {str(e)}")
    
    def get_file_info(self, filepath):
        """
        Get information about input file
        
        Args:
            filepath (str): Path to file
            
        Returns:
            dict: File information including size, format, etc.
        """
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        file_path = Path(filepath)
        file_size = file_path.stat().st_size
        
        # Try to read file for row count
        try:
            df = self.read_file(filepath)
            row_count = len(df)
            site_count = df['site_id'].nunique()
            sector_count = len(df)
        except Exception:
            row_count = "Unknown"
            site_count = "Unknown"  
            sector_count = "Unknown"
        
        info = {
            "filename": file_path.name,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024*1024), 2),
            "format": file_path.suffix.upper(),
            "total_sectors": sector_count,
            "unique_sites": site_count,
            "total_rows": row_count
        }
        
        return info
    
    def validate_site_ids(self, df, site_ids_string):
        """
        Validate that requested site IDs exist in data
        
        Args:
            df (DataFrame): Input data
            site_ids_string (str): Comma-separated site IDs
            
        Returns:
            tuple: (valid_sites, invalid_sites)
        """
        # Parse site IDs
        requested_sites = [sid.strip() for sid in site_ids_string.split(",") if sid.strip()]
        
        # Get available sites
        available_sites = set(df['site_id'].unique())
        
        # Check which are valid
        valid_sites = [sid for sid in requested_sites if sid in available_sites]
        invalid_sites = [sid for sid in requested_sites if sid not in available_sites]
        
        return valid_sites, invalid_sites
    
    def export_sample_template(self):
        """
        Export sample template file for user reference
        
        Returns:
            str: Path to exported template
        """
        # Create sample data
        sample_data = {
            'Site ID': ['SITE001', 'SITE001', 'SITE001', 'SITE002', 'SITE002'],
            'Sector': ['A', 'B', 'C', 'A', 'B'],
            'Latitude': [-6.2088, -6.2088, -6.2088, -6.2145, -6.2145],
            'Longitude': [106.8456, 106.8456, 106.8456, 106.8523, 106.8523],
            'Dir': [0, 120, 240, 45, 180],
            'tilt': [5, 5, 5, 3, 3]
        }
        
        df_template = pd.DataFrame(sample_data)
        
        # Save template
        template_path = os.path.join(self.output_directory, "input_template.csv")
        df_template.to_csv(template_path, index=False)
        
        return template_path
    
    def cleanup_old_files(self, days_old=30):
        """
        Clean up old result files to save disk space
        
        Args:
            days_old (int): Remove files older than this many days
        """
        try:
            output_path = Path(self.output_directory)
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            
            removed_count = 0
            for file_path in output_path.glob("*Results*.csv"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                print(f"Cleaned up {removed_count} old result files")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_output_directory(self):
        """
        Get the current output directory path
        
        Returns:
            str: Output directory path
        """
        return self.output_directory 