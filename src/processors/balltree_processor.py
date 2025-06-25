"""
BallTree Processor - Sector Level Analysis

Modul untuk analisis 1st tier menggunakan algoritma BallTree.
Analisis dilakukan pada level sektor dengan filtering berdasarkan bearing.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import math


class BallTreeProcessor:
    """Processor untuk analisis BallTree (Sector Level)"""
    
    def __init__(self):
        self.results = []
        self.earth_radius_km = 6371.0
    
    def run_process(self, df_points, target_site_ids, candidates_per_sector=1, max_radius_km=7.0):
        """
        Algoritma BallTree untuk identifikasi 1st tier per sektor:
        
        1. Build BallTree dari semua koordinat sektor
        2. Untuk setiap target site:
           a. Ambil semua sektor dalam site
           b. Untuk setiap sektor:
              - Query k-nearest neighbors
              - Filter berdasarkan bearing vs Dir sektor
              - Pastikan 1st tier berbeda antar sektor dalam satu site
        3. Return hasil per sektor dengan jarak
        
        Args:
            df_points: DataFrame dengan kolom [site_id, sector, lat, lon, azimuth]
            target_site_ids: List site ID yang ingin dianalisis
            candidates_per_sector: Jumlah kandidat per sektor
            max_radius_km: Radius maksimum pencarian (km)
            
        Returns:
            List dictionary dengan format:
            [
                {
                    "Site ID": "SITE001",
                    "Sector": "A",
                    "1st_Tier": "SITE002",
                    "Average of Distance": 2.45,
                    "Distance_Unit": "km"
                }
            ]
        """
        results = []
        
        try:
            # Step 1: Build BallTree dari semua koordinat
            ball_tree = self._build_balltree(df_points)
            
            # Step 2: Analisis untuk setiap target site
            for site_id in target_site_ids:
                site_results = self._analyze_site_balltree(
                    site_id, df_points, ball_tree, candidates_per_sector, max_radius_km
                )
                if site_results:
                    results.extend(site_results)
            
            return results
            
        except Exception as e:
            print(f"Error dalam BallTree processing: {e}")
            return []
    
    def _build_balltree(self, df_points):
        """
        Build BallTree untuk pencarian cepat:
        1. Convert koordinat lat/lon ke radians
        2. Buat BallTree dengan metric 'haversine'
        3. Return objek BallTree
        """
        # Convert ke radians untuk haversine distance
        coords_rad = np.radians(df_points[['lat', 'lon']].values)
        
        # Build BallTree dengan metric haversine
        ball_tree = BallTree(coords_rad, metric='haversine')
        
        return ball_tree
    
    def _analyze_site_balltree(self, target_site_id, df_points, ball_tree, candidates_per_sector, max_radius_km):
        """
        Analisis BallTree untuk semua sektor dalam satu site:
        1. Ambil semua sektor dalam target site
        2. Untuk setiap sektor:
           a. Query kandidat menggunakan BallTree
           b. Filter berdasarkan bearing vs Dir
           c. Hitung jarak geografis
        3. Pastikan 1st tier berbeda antar sektor
        4. Return hasil per sektor
        """
        results = []
        site_sectors = df_points[df_points['site_id'] == target_site_id]
        
        if site_sectors.empty:
            return results
        
        # Tracking 1st tier yang sudah digunakan untuk menghindari duplikasi
        used_first_tiers = set()
        
        for _, sector_row in site_sectors.iterrows():
            sector_result = self._analyze_sector_balltree(
                sector_row, df_points, ball_tree, candidates_per_sector, 
                max_radius_km, used_first_tiers
            )
            
            if sector_result:
                results.append(sector_result)
                # Tandai 1st tier sebagai terpakai
                used_first_tiers.add(sector_result['1st_Tier'])
        
        return results
    
    def _analyze_sector_balltree(self, sector_row, df_points, ball_tree, candidates_per_sector, max_radius_km, used_first_tiers):
        """
        Analisis BallTree untuk satu sektor:
        1. Query k-nearest neighbors dari BallTree
        2. Filter kandidat yang masih dalam radius
        3. Filter berdasarkan bearing vs Dir sektor
        4. Pilih kandidat terbaik yang belum digunakan
        5. Return hasil dengan format yang sesuai
        """
        try:
            site_id = sector_row['site_id']
            sector = sector_row['sector']
            sector_lat = sector_row['lat']
            sector_lon = sector_row['lon']
            sector_dir = sector_row['azimuth']
            
            # Step 1: Query candidates menggunakan BallTree
            candidates = self._query_balltree_candidates(
                sector_lat, sector_lon, ball_tree, df_points, 
                candidates_per_sector * 10, max_radius_km  # Query lebih banyak untuk filtering
            )
            
            # Step 2: Filter berdasarkan bearing
            filtered_candidates = self._filter_by_bearing(
                sector_lat, sector_lon, sector_dir, candidates
            )
            
            # Step 3: Pilih kandidat terbaik yang belum digunakan
            best_candidate = self._select_best_candidate(
                site_id, filtered_candidates, used_first_tiers
            )
            
            if best_candidate:
                distance_km = self._calculate_geographic_distance(
                    (sector_lat, sector_lon),
                    (best_candidate['lat'], best_candidate['lon'])
                )
                
                return {
                    "Site ID": site_id,
                    "Sector": sector,
                    "1st_Tier": best_candidate['site_id'],
                    "Average of Distance": round(distance_km, 2),
                    "Distance_Unit": "km"
                }
            
            return None
            
        except Exception as e:
            print(f"Error analyzing sector {site_id}-{sector}: {e}")
            return None
    
    def _query_balltree_candidates(self, lat, lon, ball_tree, df_points, k, max_radius_km):
        """
        Query kandidat dari BallTree:
        1. Convert koordinat target ke radians
        2. Query k-nearest neighbors
        3. Filter berdasarkan max_radius
        4. Return list kandidat dengan informasi lengkap
        """
        # Convert ke radians
        target_coord_rad = np.radians([[lat, lon]])
        
        # Query BallTree
        distances, indices = ball_tree.query(target_coord_rad, k=k)
        
        candidates = []
        for i, idx in enumerate(indices[0]):
            candidate_row = df_points.iloc[idx]
            distance_km = distances[0][i] * self.earth_radius_km
            
            # Filter berdasarkan radius
            if distance_km <= max_radius_km and distance_km > 0:  # Exclude self
                candidates.append({
                    'site_id': candidate_row['site_id'],
                    'sector': candidate_row['sector'],
                    'lat': candidate_row['lat'],
                    'lon': candidate_row['lon'],
                    'azimuth': candidate_row['azimuth'],
                    'distance_km': distance_km
                })
        
        return candidates
    
    def _filter_by_bearing(self, source_lat, source_lon, source_dir, candidates):
        """
        Filter kandidat berdasarkan bearing vs Dir sektor:
        1. Hitung bearing dari source ke setiap kandidat
        2. Hitung perbedaan sudut dengan Dir sektor
        3. Filter kandidat yang bearingnya sesuai dengan arah sektor
        4. Return kandidat yang lolos filter
        """
        filtered = []
        bearing_tolerance = 60.0  # Toleransi sudut dalam derajat
        
        for candidate in candidates:
            # Hitung bearing dari source ke candidate
            bearing = self._calculate_bearing(
                source_lat, source_lon,
                candidate['lat'], candidate['lon']
            )
            
            # Hitung perbedaan sudut dengan Dir sektor
            angle_diff = self._calculate_angle_difference(source_dir, bearing)
            
            # Filter berdasarkan toleransi
            if angle_diff <= bearing_tolerance:
                candidate['bearing'] = bearing
                candidate['angle_diff'] = angle_diff
                filtered.append(candidate)
        
        # Sort berdasarkan angle_diff dan distance
        filtered.sort(key=lambda x: (x['angle_diff'], x['distance_km']))
        
        return filtered
    
    def _select_best_candidate(self, source_site_id, candidates, used_first_tiers):
        """
        Pilih kandidat terbaik:
        1. Exclude kandidat dari site yang sama
        2. Exclude kandidat yang sudah digunakan
        3. Pilih kandidat dengan angle_diff terkecil dan jarak terdekat
        4. Return kandidat terbaik atau None
        """
        for candidate in candidates:
            if (candidate['site_id'] != source_site_id and 
                candidate['site_id'] not in used_first_tiers):
                return candidate
        
        return None
    
    def _calculate_bearing(self, lat1, lon1, lat2, lon2):
        """
        Hitung bearing (arah) dari koordinat 1 ke koordinat 2:
        1. Convert koordinat ke radians
        2. Hitung bearing menggunakan formula great circle
        3. Convert hasil ke derajat (0-360)
        4. Return bearing dalam derajat
        """
        # Implementasi perhitungan bearing
        pass
    
    def _calculate_angle_difference(self, angle1, angle2):
        """
        Hitung perbedaan sudut terkecil antara dua sudut:
        1. Hitung selisih sudut
        2. Normalisasi ke range 0-180 derajat
        3. Return perbedaan sudut absolute
        """
        diff = abs(angle1 - angle2)
        return min(diff, 360 - diff)
    
    def _calculate_geographic_distance(self, coord1, coord2):
        """
        Hitung jarak geografis antara dua koordinat:
        1. Gunakan geopy.distance.geodesic untuk akurasi tinggi
        2. Return jarak dalam kilometer
        """
        distance = geodesic(coord1, coord2).kilometers
        return distance
    
    def optimize_candidates_per_sector(self, df_points, target_site_ids, max_radius_km=7.0):
        """
        Optimasi jumlah kandidat per sektor (opsional):
        1. Test berbagai nilai candidates_per_sector
        2. Evaluasi hasil berdasarkan diversity dan coverage
        3. Return nilai optimal
        """
        # Implementasi optimasi parameter
        pass 