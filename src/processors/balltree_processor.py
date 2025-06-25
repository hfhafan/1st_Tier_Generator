"""
BallTree Processor for 1st Tier Analysis (Sector Level)

This module implements BallTree algorithm for finding 1st tier sectors
in telecommunications networks. Analysis is performed at sector level
with bearing-based filtering.

Algorithm:
1. Build BallTree from all sector coordinates
2. For each target sector, query k-nearest neighbors
3. Filter candidates based on sector bearing/direction
4. Ensure different 1st tier for each sector within same site
5. Return list of 1st tier sectors with distances

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import math

class BallTreeProcessor:
    """
    Processor for BallTree-based 1st tier analysis
    
    This class handles sector-level analysis using BallTree algorithm
    with bearing filtering for telecommunications networks.
    """
    
    def __init__(self):
        self.earth_radius_km = 6371.0  # Earth's radius in kilometers
        self.bearing_tolerance = 60.0  # Default bearing tolerance in degrees
    
    def build_balltree(self, sector_data):
        """
        Build BallTree from sector coordinates
        
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
    
    def query_candidates(self, tree, sector_data, target_sector, k_neighbors, max_radius_km):
        """
        Query k-nearest neighbors for target sector
        
        Args:
            tree: BallTree object
            sector_data (list): List of all sector data
            target_sector (dict): Target sector to find neighbors for
            k_neighbors (int): Number of candidates to find
            max_radius_km (float): Maximum search radius in km
            
        Returns:
            list: List of candidate sector dictionaries
        """
        # Convert target coordinates to radians
        target_lat_rad = math.radians(target_sector['latitude'])
        target_lon_rad = math.radians(target_sector['longitude'])
        target_point = np.array([[target_lat_rad, target_lon_rad]])
        
        # Convert max radius to radians
        max_radius_rad = max_radius_km / self.earth_radius_km
        
        # Query BallTree for candidates
        # Use larger k to have more candidates for filtering
        query_k = min(k_neighbors * 5, len(sector_data))  
        
        distances, indices = tree.query(target_point, k=query_k)
        
        candidates = []
        for i, idx in enumerate(indices[0]):
            # Convert distance back to kilometers
            distance_km = distances[0][i] * self.earth_radius_km
            
            # Filter by maximum radius
            if distance_km <= max_radius_km and distance_km > 0:  # Exclude self (distance = 0)
                candidate = sector_data[idx].copy()
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
    
    def is_within_bearing_range(self, sector_azimuth, bearing_to_candidate, tolerance=60.0):
        """
        Check if candidate is within sector's bearing range
        
        Args:
            sector_azimuth (float): Sector direction in degrees (0-360)
            bearing_to_candidate (float): Bearing to candidate in degrees (0-360)
            tolerance (float): Bearing tolerance in degrees
            
        Returns:
            bool: True if candidate is within bearing range
        """
        # Calculate angular difference
        diff = abs(sector_azimuth - bearing_to_candidate)
        
        # Handle wraparound (e.g., 350° vs 10°)
        if diff > 180:
            diff = 360 - diff
        
        return diff <= tolerance
    
    def filter_by_bearing(self, target_sector, candidates, bearing_tolerance=60.0):
        """
        Filter candidates based on sector bearing/direction
        
        Args:
            target_sector (dict): Target sector with azimuth
            candidates (list): List of candidate sectors
            bearing_tolerance (float): Bearing tolerance in degrees
            
        Returns:
            list: Filtered candidates within bearing range
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
            
            # Check if within bearing range
            if self.is_within_bearing_range(target_azimuth, bearing, bearing_tolerance):
                candidate['bearing'] = bearing
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def ensure_different_tiers(self, site_results):
        """
        Ensure different 1st tier for each sector within same site
        
        Args:
            site_results (list): List of sector results for one site
            
        Returns:
            list: Modified results with different 1st tiers per sector
        """
        if len(site_results) <= 1:
            return site_results
        
        # Track assigned 1st tier sites
        assigned_sites = set()
        final_results = []
        
        # Sort by distance to prioritize closer candidates
        site_results.sort(key=lambda x: x.get('distance_km', float('inf')))
        
        for result in site_results:
            original_tier = result.get('1st_Tier', '')
            
            # If already assigned, find next best candidate
            if original_tier in assigned_sites:
                # Look for alternative from candidates
                alternatives = result.get('alternatives', [])
                found_alternative = False
                
                for alt in alternatives:
                    if alt['site_id'] not in assigned_sites:
                        result['1st_Tier'] = alt['site_id']
                        result['distance_km'] = alt['distance_km']
                        assigned_sites.add(alt['site_id'])
                        found_alternative = True
                        break
                
                if not found_alternative:
                    # Keep original if no alternative found
                    assigned_sites.add(original_tier)
            else:
                assigned_sites.add(original_tier)
            
            final_results.append(result)
        
        return final_results
    
    def run_process(self, df, target_site_ids, candidates_per_sector, max_radius):
        """
        Main process for BallTree-based 1st tier analysis
        
        Process flow:
        1. Build BallTree from all sector coordinates
        2. For each target site:
           a. Get all sectors in site
           b. For each sector:
              - Query k-nearest neighbors using BallTree
              - Filter candidates by bearing/direction
              - Select best candidate as 1st tier
           c. Ensure different 1st tier for each sector in site
        3. Format and return results
        
        Args:
            df (DataFrame): Sector data with columns [site_id, sector, latitude, longitude, azimuth]
            target_site_ids (list): List of site IDs to analyze
            candidates_per_sector (int): Number of candidates per sector
            max_radius (float): Maximum search radius in km
            
        Returns:
            list: List of result dictionaries with format:
                  {
                      "Site ID": target_site_id,
                      "Sector": sector_id,
                      "1st_Tier": best_candidate_site_id,
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
            
            site_results = []
            
            # Step 3: Process each sector in site
            for _, sector_row in site_sectors.iterrows():
                target_sector = sector_row.to_dict()
                
                # Query candidates using BallTree
                candidates = self.query_candidates(
                    tree, sector_list, target_sector, 
                    candidates_per_sector, max_radius
                )
                
                if not candidates:
                    # No candidates found
                    result = {
                        "Site ID": site_id,
                        "Sector": target_sector['sector'],
                        "1st_Tier": "No candidates within radius",
                        "Average of Distance": 0.0,
                        "Distance_Unit": "km"
                    }
                    site_results.append(result)
                    continue
                
                # Filter by bearing
                filtered_candidates = self.filter_by_bearing(
                    target_sector, candidates, self.bearing_tolerance
                )
                
                if not filtered_candidates:
                    # No candidates within bearing range
                    result = {
                        "Site ID": site_id,
                        "Sector": target_sector['sector'],
                        "1st_Tier": "No candidates in bearing range",
                        "Average of Distance": 0.0,
                        "Distance_Unit": "km"
                    }
                    site_results.append(result)
                    continue
                
                # Select best candidate (closest)
                best_candidate = min(filtered_candidates, key=lambda x: x['distance_km'])
                
                result = {
                    "Site ID": site_id,
                    "Sector": target_sector['sector'],
                    "1st_Tier": best_candidate['site_id'],
                    "Average of Distance": round(best_candidate['distance_km'], 2),
                    "Distance_Unit": "km",
                    "alternatives": filtered_candidates[1:candidates_per_sector]  # Store alternatives
                }
                
                site_results.append(result)
            
            # Step 4: Ensure different 1st tier for each sector in site
            final_site_results = self.ensure_different_tiers(site_results)
            
            # Remove alternatives from final results
            for result in final_site_results:
                result.pop('alternatives', None)
            
            results.extend(final_site_results)
        
        return results
    
    def get_sector_statistics(self, results):
        """
        Get statistics from BallTree analysis results
        
        Args:
            results (list): List of result dictionaries
            
        Returns:
            dict: Statistics including success rate, avg distance, etc.
        """
        if not results:
            return {}
        
        successful_results = [r for r in results if r["1st_Tier"] not in 
                            ["No candidates within radius", "No candidates in bearing range"]]
        
        stats = {
            "total_sectors_analyzed": len(results),
            "successful_sectors": len(successful_results),
            "success_rate": round(len(successful_results) / len(results) * 100, 1),
            "sectors_no_candidates": len([r for r in results if "No candidates" in r["1st_Tier"]]),
            "average_distance": round(np.mean([r["Average of Distance"] for r in successful_results]), 2) if successful_results else 0,
            "max_distance": max([r["Average of Distance"] for r in successful_results]) if successful_results else 0,
            "min_distance": min([r["Average of Distance"] for r in successful_results if r["Average of Distance"] > 0]) if successful_results else 0
        }
        
        return stats
    
    def optimize_parameters(self, df, sample_site_ids, max_radius_range=(5, 15), 
                          bearing_tolerance_range=(30, 90)):
        """
        Optimize parameters for BallTree analysis
        
        Args:
            df (DataFrame): Sector data
            sample_site_ids (list): Sample sites for optimization
            max_radius_range (tuple): Range of max radius values to test
            bearing_tolerance_range (tuple): Range of bearing tolerance values to test
            
        Returns:
            dict: Optimal parameters with performance metrics
        """
        best_params = {}
        best_success_rate = 0
        
        for max_radius in range(max_radius_range[0], max_radius_range[1] + 1):
            for bearing_tolerance in range(bearing_tolerance_range[0], bearing_tolerance_range[1] + 1, 10):
                # Test with current parameters
                self.bearing_tolerance = bearing_tolerance
                
                test_results = self.run_process(df, sample_site_ids, 1, max_radius)
                stats = self.get_sector_statistics(test_results)
                
                success_rate = stats.get('success_rate', 0)
                
                if success_rate > best_success_rate:
                    best_success_rate = success_rate
                    best_params = {
                        'max_radius': max_radius,
                        'bearing_tolerance': bearing_tolerance,
                        'success_rate': success_rate,
                        'avg_distance': stats.get('average_distance', 0)
                    }
        
        return best_params 