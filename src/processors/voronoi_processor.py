"""
Voronoi Processor for 1st Tier Analysis (Site Level)

This module implements Voronoi diagram-based analysis for finding 1st tier sites
in telecommunications networks. Analysis is performed at site level, not sector level.

Algorithm:
1. Extract unique site coordinates from sector data
2. Create Voronoi diagram from site positions
3. Identify neighboring sites sharing boundaries
4. Filter by maximum distance radius
5. Return list of 1st tier sites for each input site

Author: Hadi Fauzan Hanif
Email: hadifauzanhanif@gmail.com
"""

import pandas as pd
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
from geopy.distance import geodesic

class VoronoiProcessor:
    """
    Processor for Voronoi-based 1st tier analysis
    
    This class handles site-level analysis using Voronoi diagrams to identify
    neighboring sites in telecommunications networks.
    """
    
    def __init__(self):
        self.max_distance_km = 20.0  # Maximum search radius in km
    
    def extract_site_coordinates(self, sector_data):
        """
        Extract unique site coordinates from sector-level data
        
        Args:
            sector_data (list): List of sector dictionaries with site_id, lat, lon
            
        Returns:
            dict: Dictionary mapping site_id to (lat, lon) coordinates
        """
        site_coords = {}
        
        for sector in sector_data:
            site_id = sector['site_id']
            lat = sector['latitude']
            lon = sector['longitude']
            
            # Use first occurrence of site coordinates
            if site_id not in site_coords:
                site_coords[site_id] = (lat, lon)
        
        return site_coords
    
    def create_voronoi_diagram(self, site_coordinates):
        """
        Create Voronoi diagram from site coordinates
        
        Args:
            site_coordinates (dict): Dictionary of site_id -> (lat, lon)
            
        Returns:
            tuple: (voronoi_object, site_id_list)
        """
        # Convert coordinates to numpy array
        points = []
        site_ids = []
        
        for site_id, (lat, lon) in site_coordinates.items():
            points.append([lon, lat])  # Note: lon, lat for proper projection
            site_ids.append(site_id)
        
        points = np.array(points)
        
        # Create Voronoi diagram
        voronoi = Voronoi(points)
        
        return voronoi, site_ids
    
    def find_neighboring_sites(self, voronoi, site_ids, target_site_id):
        """
        Find neighboring sites that share Voronoi boundaries with target site
        
        Args:
            voronoi: Scipy Voronoi object
            site_ids (list): List of site IDs corresponding to voronoi points
            target_site_id (str): Site ID to find neighbors for
            
        Returns:
            list: List of neighboring site IDs
        """
        try:
            # Find index of target site
            target_index = site_ids.index(target_site_id)
        except ValueError:
            return []
        
        neighbors = set()
        
        # Check ridge_points to find neighbors
        # ridge_points contains pairs of point indices that share an edge
        for ridge in voronoi.ridge_points:
            if target_index in ridge:
                # Get the other site in the ridge
                other_index = ridge[1] if ridge[0] == target_index else ridge[0]
                neighbors.add(site_ids[other_index])
        
        return list(neighbors)
    
    def calculate_distance(self, coord1, coord2):
        """
        Calculate geodesic distance between two coordinates
        
        Args:
            coord1 (tuple): (latitude, longitude) of first point
            coord2 (tuple): (latitude, longitude) of second point
            
        Returns:
            float: Distance in kilometers
        """
        return geodesic(coord1, coord2).kilometers
    
    def filter_by_distance(self, target_coords, neighbor_coords, max_radius):
        """
        Filter neighbors by maximum distance
        
        Args:
            target_coords (tuple): (lat, lon) of target site
            neighbor_coords (dict): Dict of neighbor_id -> (lat, lon)
            max_radius (float): Maximum distance in km
            
        Returns:
            dict: Filtered neighbors with distances
        """
        filtered_neighbors = {}
        
        for neighbor_id, coords in neighbor_coords.items():
            distance = self.calculate_distance(target_coords, coords)
            
            if distance <= max_radius:
                filtered_neighbors[neighbor_id] = distance
        
        return filtered_neighbors
    
    def run_process(self, target_site_ids, sector_data, max_radius):
        """
        Main process for Voronoi-based 1st tier analysis
        
        Process flow:
        1. Extract site coordinates from sector data
        2. Create Voronoi diagram
        3. For each target site:
           a. Find Voronoi neighbors
           b. Calculate distances
           c. Filter by max radius
           d. Format results
        
        Args:
            target_site_ids (list): List of site IDs to analyze
            sector_data (list): List of sector data dictionaries
            max_radius (float): Maximum search radius in km
            
        Returns:
            list: List of result dictionaries with format:
                  {
                      "Site ID": target_site_id,
                      "Sector": "ALL",  # Site level analysis
                      "1st_Tier": neighbor_site_id,
                      "Average of Distance": distance_km,
                      "Distance_Unit": "km"
                  }
        """
        results = []
        
        # Step 1: Extract site coordinates
        site_coordinates = self.extract_site_coordinates(sector_data)
        
        # Step 2: Create Voronoi diagram
        voronoi, site_ids = self.create_voronoi_diagram(site_coordinates)
        
        # Step 3: Process each target site
        for target_site_id in target_site_ids:
            if target_site_id not in site_coordinates:
                # Site not found in data
                continue
            
            # Find Voronoi neighbors
            neighbors = self.find_neighboring_sites(voronoi, site_ids, target_site_id)
            
            if not neighbors:
                # No neighbors found
                continue
            
            # Get coordinates for distance calculation
            target_coords = site_coordinates[target_site_id]
            neighbor_coords = {
                neighbor_id: site_coordinates[neighbor_id] 
                for neighbor_id in neighbors 
                if neighbor_id in site_coordinates
            }
            
            # Filter by distance
            filtered_neighbors = self.filter_by_distance(
                target_coords, neighbor_coords, max_radius
            )
            
            # Format results
            if filtered_neighbors:
                # Create single result with all neighbors
                neighbor_list = list(filtered_neighbors.keys())
                distances = list(filtered_neighbors.values())
                avg_distance = sum(distances) / len(distances)
                
                result = {
                    "Site ID": target_site_id,
                    "Sector": "ALL",  # Site level analysis
                    "1st_Tier": ",".join(neighbor_list),
                    "Average of Distance": round(avg_distance, 2),
                    "Distance_Unit": "km"
                }
                results.append(result)
            else:
                # No neighbors within radius
                result = {
                    "Site ID": target_site_id,
                    "Sector": "ALL",
                    "1st_Tier": "No neighbors within radius",
                    "Average of Distance": 0.0,
                    "Distance_Unit": "km"
                }
                results.append(result)
        
        return results
    
    def visualize_voronoi(self, voronoi, site_ids, save_path=None):
        """
        Optional: Visualize Voronoi diagram for debugging
        
        Args:
            voronoi: Scipy Voronoi object
            site_ids (list): List of site IDs
            save_path (str, optional): Path to save plot
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(12, 8))
            voronoi_plot_2d(voronoi, ax=ax, show_vertices=False, line_colors='blue', line_width=2)
            
            # Add site labels
            for i, site_id in enumerate(site_ids):
                point = voronoi.points[i]
                ax.annotate(site_id, (point[0], point[1]), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
            
            ax.set_title('Voronoi Diagram - Site Level Analysis')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:
                plt.show()
                
        except ImportError:
            print("Matplotlib not available for visualization")
        except Exception as e:
            print(f"Error in visualization: {e}")
    
    def get_statistics(self, results):
        """
        Get statistics from analysis results
        
        Args:
            results (list): List of result dictionaries
            
        Returns:
            dict: Statistics including total sites, avg neighbors, etc.
        """
        if not results:
            return {}
        
        stats = {
            "total_sites_analyzed": len(results),
            "sites_with_neighbors": len([r for r in results if r["1st_Tier"] != "No neighbors within radius"]),
            "sites_without_neighbors": len([r for r in results if r["1st_Tier"] == "No neighbors within radius"]),
            "average_distance": round(np.mean([r["Average of Distance"] for r in results if r["Average of Distance"] > 0]), 2),
            "max_distance": max([r["Average of Distance"] for r in results]),
            "min_distance": min([r["Average of Distance"] for r in results if r["Average of Distance"] > 0])
        }
        
        return stats 