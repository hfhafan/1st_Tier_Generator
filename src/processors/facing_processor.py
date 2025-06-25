"""
Facing Processor for 1st Tier Analysis - Head-to-Head (H2H) Detection

This module implements advanced facing sector analysis for telecommunications networks.
Combines BallTree algorithm for candidate finding with sophisticated H2H detection.

Algorithm:
1. Use BallTree to find candidates within radius
2. Filter candidates based on sector beam width
3. Calculate bearing between sectors  
4. Detect Head-to-Head conditions:
   - Source sector Dir within beam_width of bearing to target
   - Target sector Dir within beam_width of bearing to source
   - Distance meets H2H threshold criteria
5. Return results with H2H status and facing sector details

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import math

class FacingProcessor:
    """
    Processor for Facing/H2H analysis (Sector Level)
    
    This class handles advanced sector-level analysis with Head-to-Head detection
    for telecommunications network optimization.
    """
    
    def __init__(self):
        self.earth_radius_km = 6371.0  # Earth's radius in kilometers
        self.default_beam_width = 120.0  # Default beam width in degrees
        self.default_h2h_threshold = 30.0  # Default H2H threshold in degrees
        self.h2h_distance_threshold = 1.5  # H2H distance threshold in km
    
    def build_balltree(self, sector_data):
        """
        Build BallTree from sector coordinates for fast spatial queries
        
        Args:
            sector_data (list): List of sector dictionaries with coordinates
            
        Returns:
            tuple: (BallTree object, sector_data_list)
        """
        # Convert coordinates to radians for BallTree
        coords = []
        for sector in sector_data:
            lat_rad = math.radians(sector['latitude'])
            lon_rad = math.radians(sector['longitude'])
            coords.append([lat_rad, lon_rad])
        
        coords = np.array(coords)
        
        # Build BallTree with haversine metric for geographic data
        tree = BallTree(coords, metric='haversine')
        
        return tree, sector_data
    
    def query_candidates(self, tree, sector_data, target_sector, max_radius_km):
        """
        Query all candidates within radius using BallTree
        
        Args:
            tree: BallTree object
            sector_data (list): List of all sector data
            target_sector (dict): Target sector to find candidates for
            max_radius_km (float): Maximum search radius in km
            
        Returns:
            list: List of candidate sector dictionaries with distances
        """
        # Convert target coordinates to radians
        target_lat_rad = math.radians(target_sector['latitude'])
        target_lon_rad = math.radians(target_sector['longitude'])
        target_point = np.array([[target_lat_rad, target_lon_rad]])
        
        # Convert max radius to radians
        max_radius_rad = max_radius_km / self.earth_radius_km
        
        # Query all points within radius
        indices = tree.query_radius(target_point, r=max_radius_rad)[0]
        
        candidates = []
        for idx in indices:
            candidate = sector_data[idx].copy()
            
            # Calculate exact distance
            target_coords = (target_sector['latitude'], target_sector['longitude'])
            candidate_coords = (candidate['latitude'], candidate['longitude'])
            distance_km = geodesic(target_coords, candidate_coords).kilometers
            
            # Exclude self and filter by distance
            if distance_km > 0 and distance_km <= max_radius_km:
                candidate['distance_km'] = distance_km
                candidates.append(candidate)
        
        return candidates
    
    def calculate_bearing(self, coord1, coord2):
        """
        Calculate bearing from coord1 to coord2
        
        Args:
            coord1 (tuple): (latitude, longitude) of first point
            coord2 (tuple): (latitude, longitude) of second point
            
        Returns:
            float: Bearing in degrees (0-360)
        """
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360  # Normalize to 0-360
        
        return bearing
    
    def is_within_beam_width(self, sector_azimuth, bearing, beam_width):
        """
        Check if bearing is within sector's beam width
        
        Args:
            sector_azimuth (float): Sector direction in degrees (0-360)
            bearing (float): Bearing to check in degrees (0-360)
            beam_width (float): Beam width in degrees
            
        Returns:
            bool: True if bearing is within beam width
        """
        # Calculate angular difference
        diff = abs(sector_azimuth - bearing)
        
        # Handle wraparound (e.g., 350° vs 10°)
        if diff > 180:
            diff = 360 - diff
        
        # Check if within half beam width on each side
        return diff <= (beam_width / 2)
    
    def detect_head_to_head(self, sector_a, sector_b, beam_width, h2h_threshold):
        """
        Detect Head-to-Head condition between two sectors
        
        H2H Criteria:
        1. Sector A Dir within beam_width of bearing to Sector B
        2. Sector B Dir within beam_width of bearing to Sector A  
        3. Distance between sectors < h2h_distance_threshold
        4. Angular difference between sector directions < h2h_threshold
        
        Args:
            sector_a (dict): First sector data
            sector_b (dict): Second sector data
            beam_width (float): Beam width for filtering
            h2h_threshold (float): H2H detection threshold in degrees
            
        Returns:
            tuple: (is_h2h: bool, details: dict)
        """
        coords_a = (sector_a['latitude'], sector_a['longitude'])
        coords_b = (sector_b['latitude'], sector_b['longitude'])
        
        # Calculate bearings
        bearing_a_to_b = self.calculate_bearing(coords_a, coords_b)
        bearing_b_to_a = self.calculate_bearing(coords_b, coords_a)
        
        # Check condition 1: A points towards B
        a_points_to_b = self.is_within_beam_width(
            sector_a['azimuth'], bearing_a_to_b, beam_width
        )
        
        # Check condition 2: B points towards A  
        b_points_to_a = self.is_within_beam_width(
            sector_b['azimuth'], bearing_b_to_a, beam_width
        )
        
        # Check condition 3: Distance threshold
        distance_km = geodesic(coords_a, coords_b).kilometers
        distance_ok = distance_km <= self.h2h_distance_threshold
        
        # Check condition 4: Angular difference threshold
        azimuth_diff = abs(sector_a['azimuth'] - sector_b['azimuth'])
        if azimuth_diff > 180:
            azimuth_diff = 360 - azimuth_diff
        angle_diff_ok = azimuth_diff <= h2h_threshold
        
        # H2H if all conditions met
        is_h2h = a_points_to_b and b_points_to_a and distance_ok and angle_diff_ok
        
        details = {
            'bearing_a_to_b': bearing_a_to_b,
            'bearing_b_to_a': bearing_b_to_a,
            'a_points_to_b': a_points_to_b,
            'b_points_to_a': b_points_to_a,
            'distance_km': distance_km,
            'distance_ok': distance_ok,
            'azimuth_difference': azimuth_diff,
            'angle_diff_ok': angle_diff_ok,
            'h2h_score': sum([a_points_to_b, b_points_to_a, distance_ok, angle_diff_ok])
        }
        
        return is_h2h, details
    
    def filter_by_beam_width(self, target_sector, candidates, beam_width):
        """
        Filter candidates based on sector beam width
        
        Args:
            target_sector (dict): Target sector with azimuth
            candidates (list): List of candidate sectors
            beam_width (float): Beam width in degrees
            
        Returns:
            list: Filtered candidates within beam width
        """
        filtered_candidates = []
        target_coords = (target_sector['latitude'], target_sector['longitude'])
        target_azimuth = target_sector['azimuth']
        
        for candidate in candidates:
            # Skip same site
            if candidate['site_id'] == target_sector['site_id']:
                continue
            
            candidate_coords = (candidate['latitude'], candidate['longitude'])
            
            # Calculate bearing to candidate
            bearing = self.calculate_bearing(target_coords, candidate_coords)
            
            # Check if within beam width
            if self.is_within_beam_width(target_azimuth, bearing, beam_width):
                candidate['bearing'] = bearing
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def run_process(self, df, target_site_ids, max_radius, beam_width, h2h_threshold):
        """
        Main process for Facing/H2H analysis
        
        Process flow:
        1. Build BallTree for fast spatial queries
        2. For each target site:
           a. Get all sectors in site
           b. For each sector:
              - Find candidates within radius using BallTree
              - Filter candidates by beam width
              - Detect H2H conditions with remaining candidates
              - Select best candidate based on distance and H2H status
        3. Format and return results with H2H status
        
        Args:
            df (DataFrame): Sector data with columns [site_id, sector, latitude, longitude, azimuth]
            target_site_ids (list): List of site IDs to analyze
            max_radius (float): Maximum search radius in km
            beam_width (float): Beam width for filtering in degrees
            h2h_threshold (float): H2H detection threshold in degrees
            
        Returns:
            list: List of result dictionaries with format:
                  {
                      "Site ID": target_site_id,
                      "Sector": sector_id,
                      "1st_Tier": best_candidate_site_id,
                      "1st_Tier_Sector": best_candidate_sector_id,
                      "H2H_Status": "Yes" or "No",
                      "Average of Distance": distance_km,
                      "Distance_Unit": "km"
                  }
        """
        results = []
        
        # Step 1: Convert DataFrame to list and build BallTree
        sector_data = df.to_dict('records')
        tree, sector_list = self.build_balltree(sector_data)
        
        # Step 2: Process each target site
        for site_id in target_site_ids:
            site_sectors = df[df['site_id'] == site_id]
            
            if site_sectors.empty:
                continue
            
            # Step 3: Process each sector in site
            for _, sector_row in site_sectors.iterrows():
                target_sector = sector_row.to_dict()
                
                # Find candidates within radius using BallTree
                candidates = self.query_candidates(
                    tree, sector_list, target_sector, max_radius
                )
                
                if not candidates:
                    # No candidates found
                    result = {
                        "Site ID": site_id,
                        "Sector": target_sector['sector'],
                        "1st_Tier": "No candidates within radius",
                        "1st_Tier_Sector": "",
                        "H2H_Status": "No",
                        "Average of Distance": 0.0,
                        "Distance_Unit": "km"
                    }
                    results.append(result)
                    continue
                
                # Filter by beam width
                filtered_candidates = self.filter_by_beam_width(
                    target_sector, candidates, beam_width
                )
                
                if not filtered_candidates:
                    # No candidates within beam width
                    result = {
                        "Site ID": site_id,
                        "Sector": target_sector['sector'],
                        "1st_Tier": "No candidates in beam range",
                        "1st_Tier_Sector": "",
                        "H2H_Status": "No",
                        "Average of Distance": 0.0,
                        "Distance_Unit": "km"
                    }
                    results.append(result)
                    continue
                
                # Detect H2H and select best candidate
                best_candidate = None
                best_h2h_status = "No"
                best_distance = float('inf')
                
                for candidate in filtered_candidates:
                    # Check H2H condition
                    is_h2h, h2h_details = self.detect_head_to_head(
                        target_sector, candidate, beam_width, h2h_threshold
                    )
                    
                    candidate['is_h2h'] = is_h2h
                    candidate['h2h_details'] = h2h_details
                    
                    # Prioritize H2H candidates, then by distance
                    if is_h2h:
                        if best_candidate is None or not best_candidate.get('is_h2h', False):
                            best_candidate = candidate
                            best_h2h_status = "Yes"
                        elif candidate['distance_km'] < best_candidate['distance_km']:
                            best_candidate = candidate
                            best_h2h_status = "Yes"
                    elif best_candidate is None or (not best_candidate.get('is_h2h', False) and 
                                                   candidate['distance_km'] < best_distance):
                        best_candidate = candidate
                        best_distance = candidate['distance_km']
                
                if best_candidate:
                    result = {
                        "Site ID": site_id,
                        "Sector": target_sector['sector'],
                        "1st_Tier": best_candidate['site_id'],
                        "1st_Tier_Sector": best_candidate['sector'],
                        "H2H_Status": best_h2h_status,
                        "Average of Distance": round(best_candidate['distance_km'], 2),
                        "Distance_Unit": "km"
                    }
                else:
                    result = {
                        "Site ID": site_id,
                        "Sector": target_sector['sector'],
                        "1st_Tier": "No suitable candidates",
                        "1st_Tier_Sector": "",
                        "H2H_Status": "No",
                        "Average of Distance": 0.0,
                        "Distance_Unit": "km"
                    }
                
                results.append(result)
        
        return results
    
    def get_h2h_statistics(self, results):
        """
        Get statistics from H2H analysis results
        
        Args:
            results (list): List of result dictionaries
            
        Returns:
            dict: Statistics including H2H rate, distances, etc.
        """
        if not results:
            return {}
        
        successful_results = [r for r in results if r["1st_Tier"] not in 
                            ["No candidates within radius", "No candidates in beam range", "No suitable candidates"]]
        h2h_results = [r for r in successful_results if r["H2H_Status"] == "Yes"]
        
        stats = {
            "total_sectors_analyzed": len(results),
            "successful_sectors": len(successful_results),
            "success_rate": round(len(successful_results) / len(results) * 100, 1) if results else 0,
            "h2h_sectors": len(h2h_results),
            "h2h_rate": round(len(h2h_results) / len(successful_results) * 100, 1) if successful_results else 0,
            "sectors_no_candidates": len([r for r in results if "No candidates" in r["1st_Tier"]]),
            "average_distance": round(np.mean([r["Average of Distance"] for r in successful_results]), 2) if successful_results else 0,
            "h2h_average_distance": round(np.mean([r["Average of Distance"] for r in h2h_results]), 2) if h2h_results else 0,
            "max_distance": max([r["Average of Distance"] for r in successful_results]) if successful_results else 0,
            "min_distance": min([r["Average of Distance"] for r in successful_results if r["Average of Distance"] > 0]) if successful_results else 0
        }
        
        return stats
    
    def analyze_h2h_patterns(self, results):
        """
        Analyze H2H patterns for network optimization insights
        
        Args:
            results (list): List of result dictionaries
            
        Returns:
            dict: H2H pattern analysis
        """
        h2h_results = [r for r in results if r["H2H_Status"] == "Yes"]
        
        if not h2h_results:
            return {"message": "No H2H relationships found"}
        
        # Analyze distance patterns
        distances = [r["Average of Distance"] for r in h2h_results]
        
        # Analyze site pairs
        site_pairs = {}
        for result in h2h_results:
            pair = tuple(sorted([result["Site ID"], result["1st_Tier"]]))
            if pair not in site_pairs:
                site_pairs[pair] = []
            site_pairs[pair].append(result)
        
        # Find multi-sector H2H relationships
        multi_sector_pairs = {pair: sectors for pair, sectors in site_pairs.items() if len(sectors) > 1}
        
        analysis = {
            "total_h2h_relationships": len(h2h_results),
            "unique_site_pairs": len(site_pairs),
            "multi_sector_h2h_pairs": len(multi_sector_pairs),
            "distance_statistics": {
                "mean": round(np.mean(distances), 2),
                "median": round(np.median(distances), 2),
                "std": round(np.std(distances), 2),
                "min": round(min(distances), 2),
                "max": round(max(distances), 2)
            },
            "distance_distribution": {
                "under_0.5km": len([d for d in distances if d < 0.5]),
                "0.5_to_1km": len([d for d in distances if 0.5 <= d < 1.0]),
                "1_to_1.5km": len([d for d in distances if 1.0 <= d < 1.5]),
                "over_1.5km": len([d for d in distances if d >= 1.5])
            }
        }
        
        return analysis 