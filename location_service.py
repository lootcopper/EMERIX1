import requests
import json
import math
import logging
from typing import List, Dict, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google_places_service import GooglePlacesService
from config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="er_wait_time_predictor")
        self.google_places = GooglePlacesService()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_user_location(self, location_input: str) -> Optional[Dict]:
        """
        Get user location from various input formats
        """
        try:
            # Try to parse as coordinates first
            if ',' in location_input:
                try:
                    lat, lng = map(float, location_input.split(','))
                    return self._get_location_from_coords(lat, lng)
                except ValueError:
                    pass
            
            # Try geocoding the input
            location = self.geocoder.geocode(location_input, timeout=10)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address,
                    'city': self._extract_city(location.address),
                    'state': self._extract_state(location.address),
                    'country': self._extract_country(location.address)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user location: {e}")
            return None
    
    def _get_location_from_coords(self, lat: float, lng: float) -> Dict:
        """Get location details from coordinates"""
        try:
            location = self.geocoder.reverse(f"{lat}, {lng}", timeout=10)
            if location:
                return {
                    'latitude': lat,
                    'longitude': lng,
                    'address': location.address,
                    'city': self._extract_city(location.address),
                    'state': self._extract_state(location.address),
                    'country': self._extract_country(location.address)
                }
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
        
        return {
            'latitude': lat,
            'longitude': lng,
            'address': f"{lat}, {lng}",
            'city': 'Unknown',
            'state': 'Unknown',
            'country': 'Unknown'
        }
    
    def find_nearby_hospitals(self, user_location: Dict, radius_miles: float = 25) -> List[Dict]:
        """
        Find hospitals near the user's location using Google Places API
        """
        lat = user_location['latitude']
        lng = user_location['longitude']
        radius_meters = int(radius_miles * 1609.34)  # Convert to meters
        
        # Use Google Places API to find hospitals
        try:
            hospitals = self.google_places.find_hospitals(lat, lng, radius_meters)
        except Exception as e:
            logger.error(f"Error finding hospitals: {e}")
            hospitals = []
        
        if not hospitals:
            logger.warning("No hospitals found, using fallback data")
            # Use fallback hospitals
            hospitals = self.google_places._get_fallback_hospitals(lat, lng)
        
        # Calculate distances and add to hospital data
        user_coords = (lat, lng)
        for hospital in hospitals:
            hospital_coords = (hospital['coordinates'][0], hospital['coordinates'][1])
            distance = geodesic(user_coords, hospital_coords).miles
            hospital['distance_miles'] = round(distance, 1)
            hospital['distance_km'] = round(distance * 1.60934, 1)
        
        # Sort by distance
        hospitals.sort(key=lambda x: x['distance_miles'])
        
        # Limit to closest 10 hospitals
        return hospitals[:10]
    
    
    def get_weather_data_for_location(self, location: Dict) -> Dict:
        """Get weather data for specific location using Google Weather Service"""
        lat = location['latitude']
        lng = location['longitude']
        
        # Use Google Weather Service
        from google_weather_service import GoogleWeatherService
        weather_service = GoogleWeatherService()
        
        return weather_service.get_weather_data(lat, lng)
    
    def get_traffic_data_for_location(self, location: Dict) -> Dict:
        """Get traffic data for specific location - not available with Google APIs"""
        # Google Routes API requires specific origin/destination, not general area traffic
        return {
            'error': 'Traffic data not available - Google Routes API requires specific routes',
            'source': 'unavailable'
        }
    
    def _map_weather_code(self, code: int) -> str:
        """Map Open-Meteo weather codes to conditions"""
        weather_codes = {
            0: 'clear',
            1: 'clear', 2: 'clear', 3: 'clear',
            45: 'cloudy', 48: 'cloudy',
            51: 'rainy', 53: 'rainy', 55: 'rainy',
            61: 'rainy', 63: 'rainy', 65: 'rainy',
            71: 'stormy', 73: 'stormy', 75: 'stormy',
            77: 'stormy',
            80: 'rainy', 81: 'rainy', 82: 'rainy',
            85: 'stormy', 86: 'stormy',
            95: 'stormy', 96: 'stormy', 99: 'stormy'
        }
        return weather_codes.get(code, 'clear')
    
    def _extract_city(self, address: str) -> str:
        """Extract city from address"""
        try:
            parts = address.split(',')
            if len(parts) >= 2:
                return parts[-3].strip() if len(parts) >= 3 else parts[-2].strip()
        except:
            pass
        return 'Unknown'
    
    def _extract_state(self, address: str) -> str:
        """Extract state from address"""
        try:
            parts = address.split(',')
            if len(parts) >= 2:
                return parts[-2].strip()
        except:
            pass
        return 'Unknown'
    
    def _extract_country(self, address: str) -> str:
        """Extract country from address"""
        try:
            parts = address.split(',')
            if len(parts) >= 1:
                return parts[-1].strip()
        except:
            pass
        return 'Unknown'
    
    def _get_fallback_weather_data(self) -> Dict:
        """Fallback weather data"""
        return {
            'condition': 'clear',
            'temperature': 72,
            'wind_speed': 10,
            'precipitation': 0,
            'humidity': 50,
            'timestamp': '',
            'source': 'fallback'
        }
    
    def _get_fallback_traffic_data(self) -> Dict:
        """Fallback traffic data"""
        return {
            'level': 'medium',
            'accident_probability': 0.1,
            'average_speed': 35,
            'free_flow_speed': 55,
            'congestion_level': 0.5,
            'incidents': 2,
            'timestamp': '',
            'source': 'fallback'
        }
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in miles"""
        return geodesic(coord1, coord2).miles
    
    def get_driving_time_estimate(self, from_coords: Tuple[float, float], to_coords: Tuple[float, float]) -> Dict:
        """Get estimated driving time between two points"""
        try:
            distance = self.calculate_distance(from_coords, to_coords)
            
            # Simple estimation based on distance
            # Assume average speed of 25 mph in city
            estimated_time = (distance / 25) * 60  # minutes
            
            return {
                'distance_miles': round(distance, 1),
                'estimated_time_minutes': round(estimated_time, 0),
                'estimated_time_hours': round(estimated_time / 60, 1)
            }
        except Exception as e:
            logger.error(f"Error calculating driving time: {e}")
            return {
                'distance_miles': 0,
                'estimated_time_minutes': 0,
                'estimated_time_hours': 0
            }
