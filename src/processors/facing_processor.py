"""
Facing Processor - Head-to-Head Sector Analysis

Modul untuk analisis 1st tier dengan deteksi facing sector dan Head-to-Head (H2H).
Menggunakan pendekatan optimized dengan filtering berdasarkan beam width dan bearing.

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import math


class FacingProcessor:
    """Processor untuk analisis Facing/H2H (Sector Level)"""
    
    def __init__(self):
        self.results = []
        self.earth_radius_km = 6371.0
        self.h2h_distance_threshold = 1.5  # km
    
    def run_process(self, df_points, target_site_ids, max_radius_km=10.0, beam_width=120.0, h2h_threshold=30.0):
        """
        Algoritma Facing/H2H untuk identifikasi 1st tier per sektor:
        
        1. Build BallTree dari semua koordinat sektor
        2. Untuk setiap target site:
           a. Ambil semua sektor dalam site
           b. Untuk setiap sektor:
              - Cari kandidat dalam radius menggunakan BallTree
              - Filter berdasarkan beam_width sektor
              - Hitung bearing antar sektor
              - Deteksi kondisi Head-to-Head
        3. Return hasil per sektor dengan status H2H
        
        Args:
            df_points: DataFrame dengan kolom [site_id, sector, lat, lon, azimuth]
            target_site_ids: List site ID yang ingin dianalisis
            max_radius_km: Radius pencarian maksimum (km)
            beam_width: Lebar beam sektor untuk filtering (derajat)
            h2h_threshold: Threshold untuk deteksi H2H (derajat)
            
        Returns:
            List dictionary dengan format:
            [
                {
                    "Site ID": "SITE001",
                    "Sector": "A",
                    "1st_Tier": "SITE002",
                    "1st_Tier_Sector": "B",
                    "H2H_Status": "Ya",
                    "Average of Distance": 1.23,
                    "Distance_Unit": "km"
                }
            ]
        """
        results = []
        
        try:
            # Step 1: Build BallTree untuk pencarian cepat
            ball_tree = self._build_balltree(df_points)
            
            # Step 2: Analisis untuk setiap target site
            for site_id in target_site_ids:
                site_results = self._analyze_site_facing(
                    site_id, df_points, ball_tree, max_radius_km, beam_width, h2h_threshold
                )
                if site_results:
                    results.extend(site_results)
            
            return results
            
        except Exception as e:
            print(f"Error dalam Facing processing: {e}")
            return []
    
    def _build_balltree(self, df_points):
        """
        Build BallTree untuk pencarian cepat:
        1. Convert koordinat lat/lon ke radians
        2. Buat BallTree dengan metric 'haversine'
        3. Return objek BallTree
        """
        coords_rad = np.radians(df_points[['lat', 'lon']].values)
        ball_tree = BallTree(coords_rad, metric='haversine')
        return ball_tree
    
    def _analyze_site_facing(self, target_site_id, df_points, ball_tree, max_radius_km, beam_width, h2h_threshold):
        """
        Analisis Facing untuk semua sektor dalam satu site:
        1. Ambil semua sektor dalam target site
        2. Untuk setiap sektor:
           a. Cari kandidat 1st tier
           b. Deteksi facing dan H2H
        3. Return hasil per sektor
        """
        results = []
        site_sectors = df_points[df_points['site_id'] == target_site_id]
        
        if site_sectors.empty:
            return results
        
        for _, sector_row in site_sectors.iterrows():
            sector_result = self._analyze_sector_facing(
                sector_row, df_points, ball_tree, max_radius_km, beam_width, h2h_threshold
            )
            
            if sector_result:
                results.append(sector_result)
        
        return results
    
    def _analyze_sector_facing(self, sector_row, df_points, ball_tree, max_radius_km, beam_width, h2h_threshold):
        """
        Analisis Facing untuk satu sektor:
        1. Cari kandidat dalam radius menggunakan BallTree
        2. Filter berdasarkan beam_width sektor
        3. Hitung bearing antar sektor
        4. Deteksi kondisi Head-to-Head
        5. Return hasil dengan status H2H
        """
        try:
            site_id = sector_row['site_id']
            sector = sector_row['sector']
            sector_lat = sector_row['lat']
            sector_lon = sector_row['lon']
            sector_dir = sector_row['azimuth']
            
            # Step 1: Cari kandidat dalam radius
            candidates = self._find_candidates_in_radius(
                sector_lat, sector_lon, ball_tree, df_points, max_radius_km
            )
            
            # Step 2: Filter berdasarkan beam_width
            beam_filtered_candidates = self._filter_by_beam_width(
                sector_lat, sector_lon, sector_dir, beam_width, candidates
            )
            
            # Step 3: Pilih kandidat terbaik dan deteksi H2H
            best_candidate = self._find_best_facing_candidate(
                site_id, sector_lat, sector_lon, sector_dir, 
                beam_filtered_candidates, h2h_threshold
            )
            
            if best_candidate:
                return {
                    "Site ID": site_id,
                    "Sector": sector,
                    "1st_Tier": best_candidate['site_id'],
                    "1st_Tier_Sector": best_candidate['sector'],
                    "H2H_Status": best_candidate['h2h_status'],
                    "Average of Distance": round(best_candidate['distance_km'], 2),
                    "Distance_Unit": "km"
                }
            
            return None
            
        except Exception as e:
            print(f"Error analyzing facing sector {site_id}-{sector}: {e}")
            return None
    
    def _find_candidates_in_radius(self, lat, lon, ball_tree, df_points, max_radius_km):
        """
        Cari semua sektor kandidat dalam radius:
        1. Query BallTree untuk mendapatkan tetangga dalam radius
        2. Filter hasil berdasarkan max_radius
        3. Return list kandidat dengan informasi lengkap
        """
        # Convert ke radians
        target_coord_rad = np.radians([[lat, lon]])
        
        # Query semua tetangga dalam radius
        indices = ball_tree.query_radius(target_coord_rad, r=max_radius_km/self.earth_radius_km)
        
        candidates = []
        for idx in indices[0]:
            candidate_row = df_points.iloc[idx]
            distance_km = self._calculate_geographic_distance(
                (lat, lon),
                (candidate_row['lat'], candidate_row['lon'])
            )
            
            # Exclude self dan filter berdasarkan jarak
            if distance_km > 0 and distance_km <= max_radius_km:
                candidates.append({
                    'site_id': candidate_row['site_id'],
                    'sector': candidate_row['sector'],
                    'lat': candidate_row['lat'],
                    'lon': candidate_row['lon'],
                    'azimuth': candidate_row['azimuth'],
                    'distance_km': distance_km
                })
        
        return candidates
    
    def _filter_by_beam_width(self, source_lat, source_lon, source_dir, beam_width, candidates):
        """
        Filter kandidat berdasarkan beam width sektor:
        1. Hitung bearing dari source ke setiap kandidat
        2. Cek apakah bearing berada dalam beam width sektor
        3. Return kandidat yang berada dalam beam width
        """
        filtered = []
        half_beam = beam_width / 2.0
        
        for candidate in candidates:
            # Hitung bearing dari source ke candidate
            bearing = self._calculate_bearing(
                source_lat, source_lon,
                candidate['lat'], candidate['lon']
            )
            
            # Cek apakah bearing dalam beam width
            if self._is_within_beam(source_dir, bearing, half_beam):
                candidate['bearing'] = bearing
                filtered.append(candidate)
        
        return filtered
    
    def _find_best_facing_candidate(self, source_site_id, source_lat, source_lon, source_dir, candidates, h2h_threshold):
        """
        Cari kandidat terbaik dan deteksi H2H:
        1. Exclude kandidat dari site yang sama
        2. Untuk setiap kandidat, deteksi kondisi H2H:
           - Dir sektor sumber dalam beam_width bearing ke tujuan
           - Dir sektor tujuan dalam beam_width bearing ke sumber
           - Jarak < threshold H2H
        3. Prioritas kandidat H2H, kemudian yang terdekat
        4. Return kandidat terbaik dengan status H2H
        """
        valid_candidates = []
        
        for candidate in candidates:
            if candidate['site_id'] != source_site_id:
                # Deteksi H2H
                h2h_status = self._detect_head_to_head(
                    source_lat, source_lon, source_dir,
                    candidate['lat'], candidate['lon'], candidate['azimuth'],
                    candidate['distance_km'], h2h_threshold
                )
                
                candidate['h2h_status'] = "Ya" if h2h_status else "Tidak"
                candidate['h2h_priority'] = 1 if h2h_status else 2
                valid_candidates.append(candidate)
        
        if valid_candidates:
            # Sort: prioritas H2H, kemudian jarak terdekat
            valid_candidates.sort(key=lambda x: (x['h2h_priority'], x['distance_km']))
            return valid_candidates[0]
        
        return None
    
    def _detect_head_to_head(self, lat1, lon1, dir1, lat2, lon2, dir2, distance_km, h2h_threshold):
        """
        Deteksi kondisi Head-to-Head (H2H):
        1. Hitung bearing dari sektor 1 ke sektor 2
        2. Hitung bearing dari sektor 2 ke sektor 1
        3. Cek apakah Dir sektor 1 mengarah ke sektor 2 (dalam threshold)
        4. Cek apakah Dir sektor 2 mengarah ke sektor 1 (dalam threshold)
        5. Cek apakah jarak < threshold H2H
        6. Return True jika semua kondisi terpenuhi
        """
        # Kondisi 1: Jarak harus < threshold
        if distance_km >= self.h2h_distance_threshold:
            return False
        
        # Kondisi 2: Dir sektor 1 mengarah ke sektor 2
        bearing_1_to_2 = self._calculate_bearing(lat1, lon1, lat2, lon2)
        angle_diff_1 = self._calculate_angle_difference(dir1, bearing_1_to_2)
        
        if angle_diff_1 > h2h_threshold:
            return False
        
        # Kondisi 3: Dir sektor 2 mengarah ke sektor 1
        bearing_2_to_1 = self._calculate_bearing(lat2, lon2, lat1, lon1)
        angle_diff_2 = self._calculate_angle_difference(dir2, bearing_2_to_1)
        
        if angle_diff_2 > h2h_threshold:
            return False
        
        # Semua kondisi terpenuhi
        return True
    
    def _is_within_beam(self, sector_dir, bearing, half_beam_width):
        """
        Cek apakah bearing berada dalam beam width sektor:
        1. Hitung perbedaan sudut antara sector_dir dan bearing
        2. Bandingkan dengan half_beam_width
        3. Return True jika dalam beam width
        """
        angle_diff = self._calculate_angle_difference(sector_dir, bearing)
        return angle_diff <= half_beam_width
    
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
    
    def generate_h2h_report(self, results):
        """
        Generate laporan khusus untuk H2H (opsional):
        1. Kelompokkan hasil berdasarkan status H2H
        2. Hitung statistik H2H
        3. Return laporan summary
        """
        h2h_count = sum(1 for r in results if r.get('H2H_Status') == 'Ya')
        total_count = len(results)
        
        report = {
            'total_sectors': total_count,
            'h2h_sectors': h2h_count,
            'h2h_percentage': round((h2h_count / total_count * 100), 2) if total_count > 0 else 0,
            'non_h2h_sectors': total_count - h2h_count
        }
        
        return report
    
    def optimize_beam_width(self, df_points, target_site_ids, max_radius_km=10.0):
        """
        Optimasi beam width untuk hasil terbaik (opsional):
        1. Test berbagai nilai beam_width
        2. Evaluasi coverage dan akurasi
        3. Return beam_width optimal
        """
        # Implementasi optimasi beam width
        pass 