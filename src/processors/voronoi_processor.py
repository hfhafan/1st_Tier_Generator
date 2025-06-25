"""
Voronoi Processor - Site Level Analysis

Modul untuk analisis 1st tier menggunakan metode Voronoi diagram.
Analisis dilakukan pada level site, bukan sektor individual.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
from geopy.distance import geodesic


class VoronoiProcessor:
    """Processor untuk analisis Voronoi (Site Level)"""
    
    def __init__(self):
        self.results = []
    
    def run_process(self, target_site_ids, all_points, max_radius_km=10.0):
        """
        Algoritma Voronoi untuk identifikasi 1st tier sites:
        
        1. Ekstrak koordinat unik per site dari all_points
        2. Buat Voronoi diagram dari koordinat site
        3. Untuk setiap target site:
           a. Identifikasi tetangga dari Voronoi regions
           b. Hitung jarak ke tetangga
           c. Filter berdasarkan max_radius
           d. Return list 1st tier dengan jarak
        
        Args:
            target_site_ids: List site ID yang ingin dianalisis
            all_points: DataFrame dengan kolom [site_id, sector, lat, lon, azimuth]
            max_radius_km: Radius maksimum pencarian (km)
            
        Returns:
            List dictionary dengan format:
            [
                {
                    "Site ID": "SITE001",
                    "1st_Tier": "SITE002,SITE003",
                    "Average of Distance": 2.45,
                    "Distance_Unit": "km"
                }
            ]
        """
        results = []
        
        try:
            # Step 1: Ekstrak koordinat unik per site
            site_coords = self._extract_unique_site_coordinates(all_points)
            
            # Step 2: Buat Voronoi diagram
            voronoi_diagram = self._create_voronoi_diagram(site_coords)
            
            # Step 3: Analisis untuk setiap target site
            for site_id in target_site_ids:
                site_result = self._analyze_site_voronoi(
                    site_id, site_coords, voronoi_diagram, max_radius_km
                )
                if site_result:
                    results.append(site_result)
            
            return results
            
        except Exception as e:
            print(f"Error dalam Voronoi processing: {e}")
            return []
    
    def _extract_unique_site_coordinates(self, all_points):
        """
        Ekstrak koordinat unik per site:
        1. Group by site_id
        2. Ambil koordinat pertama per site (asumsi semua sektor di site sama)
        3. Return DataFrame dengan [site_id, lat, lon]
        """
        # Implementasi ekstraksi koordinat site
        pass
    
    def _create_voronoi_diagram(self, site_coords):
        """
        Membuat Voronoi diagram:
        1. Convert koordinat ke format numpy array
        2. Buat Voronoi diagram menggunakan scipy.spatial.Voronoi
        3. Return objek Voronoi
        """
        # Konversi koordinat ke array untuk Voronoi
        points = site_coords[['lat', 'lon']].values
        
        # Buat Voronoi diagram
        voronoi = Voronoi(points)
        
        return voronoi
    
    def _analyze_site_voronoi(self, target_site_id, site_coords, voronoi, max_radius_km):
        """
        Analisis Voronoi untuk satu site:
        1. Temukan index site di voronoi diagram
        2. Identifikasi tetangga dari voronoi.regions dan voronoi.ridge_points
        3. Hitung jarak geografis ke tetangga
        4. Filter berdasarkan max_radius
        5. Return hasil dengan format yang sesuai
        """
        try:
            # Step 1: Temukan index target site
            site_index = self._find_site_index(target_site_id, site_coords)
            if site_index is None:
                return None
            
            # Step 2: Identifikasi tetangga Voronoi
            neighbor_indices = self._find_voronoi_neighbors(site_index, voronoi)
            
            # Step 3: Konversi index ke site_id dan hitung jarak
            neighbor_sites = []
            distances = []
            
            target_coord = self._get_site_coordinate(target_site_id, site_coords)
            
            for neighbor_idx in neighbor_indices:
                neighbor_site_id = self._get_site_id_by_index(neighbor_idx, site_coords)
                neighbor_coord = self._get_site_coordinate(neighbor_site_id, site_coords)
                
                # Hitung jarak geografis
                distance_km = self._calculate_geographic_distance(target_coord, neighbor_coord)
                
                # Filter berdasarkan radius
                if distance_km <= max_radius_km:
                    neighbor_sites.append(neighbor_site_id)
                    distances.append(distance_km)
            
            # Step 4: Format hasil
            if neighbor_sites:
                return {
                    "Site ID": target_site_id,
                    "1st_Tier": ",".join(neighbor_sites),
                    "Average of Distance": round(np.mean(distances), 2),
                    "Distance_Unit": "km"
                }
            
            return None
            
        except Exception as e:
            print(f"Error analyzing site {target_site_id}: {e}")
            return None
    
    def _find_site_index(self, site_id, site_coords):
        """Temukan index site dalam DataFrame site_coords"""
        # Implementasi pencarian index
        pass
    
    def _find_voronoi_neighbors(self, site_index, voronoi):
        """
        Identifikasi tetangga Voronoi:
        1. Cari ridge_points yang mengandung site_index
        2. Ambil site lain dalam setiap ridge_point
        3. Return list index tetangga
        """
        neighbors = set()
        
        # Cari ridge points yang melibatkan site ini
        for ridge in voronoi.ridge_points:
            if site_index in ridge:
                # Ambil tetangga (site lain dalam ridge)
                neighbor = ridge[0] if ridge[1] == site_index else ridge[1]
                neighbors.add(neighbor)
        
        return list(neighbors)
    
    def _get_site_coordinate(self, site_id, site_coords):
        """Ambil koordinat (lat, lon) untuk site_id"""
        # Implementasi pengambilan koordinat
        pass
    
    def _get_site_id_by_index(self, index, site_coords):
        """Ambil site_id berdasarkan index dalam DataFrame"""
        # Implementasi pengambilan site_id
        pass
    
    def _calculate_geographic_distance(self, coord1, coord2):
        """
        Hitung jarak geografis antara dua koordinat:
        1. Gunakan geopy.distance.geodesic untuk akurasi tinggi
        2. Return jarak dalam kilometer
        """
        distance = geodesic(coord1, coord2).kilometers
        return distance
    
    def visualize_voronoi(self, site_coords, output_path=None):
        """
        Visualisasi Voronoi diagram (opsional):
        1. Buat Voronoi diagram
        2. Plot menggunakan matplotlib
        3. Simpan ke file jika output_path diberikan
        """
        # Implementasi visualisasi
        pass 