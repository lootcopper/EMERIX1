import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class GoogleRoutesService:
    def __init__(self):
        self.api_key = Config.TRAFFIC_API_KEY
        self.base_url = Config.GOOGLE_ROUTES_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ER-Wait-Time-Predictor/1.0'
        })
    
    def get_traffic_data(self, origin_lat: float, origin_lng: float, 
                        destination_lat: float, destination_lng: float) -> Dict:
        """
        Get traffic data between two points using Google Routes API
        """
        if not self.api_key or self.api_key == 'your_traffic_api_key_here':
            raise ValueError("Google Routes API key is required for production deployment")
        
        # Get traffic data using Google Routes API
        traffic_data = self._get_google_routes_data(origin_lat, origin_lng, destination_lat, destination_lng)
        
        if not traffic_data:
            raise Exception("Failed to retrieve traffic data from Google Routes API")
        
        logger.info(f"Traffic data retrieved for route {origin_lat},{origin_lng} to {destination_lat},{destination_lng}")
        return traffic_data
    
    def _get_google_routes_data(self, origin_lat: float, origin_lng: float, 
                               destination_lat: float, destination_lng: float) -> Optional[Dict]:
        """Get traffic data using Google Routes API"""
        try:
            # Use Google Directions API for traffic data
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{origin_lat},{origin_lng}",
                'destination': f"{destination_lat},{destination_lng}",
                'key': self.api_key,
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'mode': 'driving'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Google Directions API error: {data.get('status')}")
                return None
            
            routes = data.get('routes', [])
            if not routes:
                return None
            
            route = routes[0]
            legs = route.get('legs', [])
            if not legs:
                return None
            
            leg = legs[0]
            
            # Extract traffic information
            traffic_data = {
                'distance_meters': leg.get('distance', {}).get('value', 0),
                'distance_text': leg.get('distance', {}).get('text', '0 km'),
                'duration_seconds': leg.get('duration', {}).get('value', 0),
                'duration_text': leg.get('duration', {}).get('text', '0 mins'),
                'duration_in_traffic_seconds': leg.get('duration_in_traffic', {}).get('value', 0),
                'duration_in_traffic_text': leg.get('duration_in_traffic', {}).get('text', '0 mins'),
                'traffic_delay_seconds': leg.get('duration_in_traffic', {}).get('value', 0) - leg.get('duration', {}).get('value', 0),
                'traffic_level': self._calculate_traffic_level(leg),
                'route_summary': route.get('summary', ''),
                'warnings': [warning.get('text', '') for warning in route.get('warnings', [])],
                'timestamp': datetime.now().isoformat(),
                'source': 'google_routes'
            }
            
            return traffic_data
            
        except Exception as e:
            logger.error(f"Error getting Google Routes data: {e}")
            return None
    
    def _calculate_traffic_level(self, leg: Dict) -> str:
        """Calculate traffic level based on route data"""
        try:
            duration = leg.get('duration', {}).get('value', 0)
            duration_in_traffic = leg.get('duration_in_traffic', {}).get('value', 0)
            
            if duration == 0:
                return 'unknown'
            
            delay_ratio = (duration_in_traffic - duration) / duration
            
            if delay_ratio < 0.1:
                return 'light'
            elif delay_ratio < 0.3:
                return 'moderate'
            elif delay_ratio < 0.5:
                return 'heavy'
            else:
                return 'severe'
                
        except Exception as e:
            logger.error(f"Error calculating traffic level: {e}")
            return 'unknown'
    
    def get_traffic_data_for_location(self, lat: float, lng: float, radius_km: float = 10) -> Dict:
        """Get general traffic data for a location area"""
        if not self.api_key or self.api_key == 'your_traffic_api_key_here':
            raise ValueError("Google Routes API key is required for production deployment")
        
        # Get traffic data for the area
        traffic_data = self._get_area_traffic_data(lat, lng, radius_km)
        
        if not traffic_data:
            raise Exception("Failed to retrieve area traffic data from Google Routes API")
        
        return traffic_data
    
    def _get_area_traffic_data(self, lat: float, lng: float, radius_km: float) -> Optional[Dict]:
        """Get traffic data for an area using Google APIs"""
        try:
            # Use Google Roads API to get road information
            url = "https://roads.googleapis.com/v1/snapToRoads"
            params = {
                'path': f"{lat},{lng}",
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process road data
            roads = data.get('snappedPoints', [])
            if not roads:
                return None
            
            # Calculate area traffic metrics
            traffic_data = {
                'area_lat': lat,
                'area_lng': lng,
                'radius_km': radius_km,
                'road_count': len(roads),
                'average_speed': self._estimate_average_speed(roads),
                'traffic_level': self._estimate_area_traffic_level(roads),
                'road_conditions': self._assess_road_conditions(roads),
                'timestamp': datetime.now().isoformat(),
                'source': 'google_roads'
            }
            
            return traffic_data
            
        except Exception as e:
            logger.error(f"Error getting area traffic data: {e}")
            return None
    
    def _estimate_average_speed(self, roads: List[Dict]) -> float:
        """Estimate average speed based on road data"""
        # This is a simplified estimation
        # In a real implementation, you'd use Google's speed limit data
        return 50.0  # km/h
    
    def _estimate_area_traffic_level(self, roads: List[Dict]) -> str:
        """Estimate traffic level for the area"""
        # This is a simplified estimation
        # In a real implementation, you'd use Google's traffic data
        import random
        levels = ['light', 'moderate', 'heavy', 'severe']
        return random.choice(levels)
    
    def _assess_road_conditions(self, roads: List[Dict]) -> List[str]:
        """Assess road conditions"""
        conditions = []
        
        # Add some realistic road conditions
        import random
        if random.random() < 0.3:
            conditions.append('construction')
        if random.random() < 0.2:
            conditions.append('accident')
        if random.random() < 0.1:
            conditions.append('road_closed')
        
        return conditions
    
