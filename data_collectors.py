import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
from google_weather_service import GoogleWeatherService
from google_routes_service import GoogleRoutesService

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.weather_service = GoogleWeatherService()
        self.routes_service = GoogleRoutesService()
    
    def get_weather_data(self, lat: float = None, lng: float = None):
        """Get current weather data using Google Weather Service"""
        if not lat or not lng:
            lat, lng = 40.7128, -74.0060  # Default to New York
        
        try:
            # Use Google Weather Service
            weather_data = self.weather_service.get_weather_data(lat, lng)
            logger.info("Weather data updated successfully")
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return {
                'condition': 'unknown',
                'temperature': 20,
                'wind_speed': 0,
                'precipitation': 0,
                'humidity': 50,
                'pressure': 1013,
                'timestamp': datetime.now().isoformat(),
                'source': 'fallback'
            }
    
    def get_traffic_data(self, origin_lat: float = None, origin_lng: float = None, 
                        destination_lat: float = None, destination_lng: float = None):
        """Get current traffic data - simulated based on time patterns"""
        import random
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        # Simulate traffic patterns based on time
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # Rush hours
            traffic_level = 'high'
            accident_probability = 0.3
            average_speed = random.randint(15, 35)
        elif 10 <= current_hour <= 16:  # Daytime
            traffic_level = 'medium'
            accident_probability = 0.15
            average_speed = random.randint(25, 45)
        elif 22 <= current_hour or current_hour <= 6:  # Late night/early morning
            traffic_level = 'low'
            accident_probability = 0.05
            average_speed = random.randint(40, 65)
        else:
            traffic_level = 'medium'
            accident_probability = 0.1
            average_speed = random.randint(30, 50)
        
        # Weekend patterns
        if day_of_week >= 5:  # Weekend
            traffic_level = 'low' if traffic_level == 'low' else 'medium'
            accident_probability *= 0.8
        
        traffic_data = {
            'level': traffic_level,
            'accident_probability': accident_probability,
            'average_speed': average_speed,
            'free_flow_speed': 65,
            'congestion_level': 100 - int((average_speed / 65) * 100),
            'incidents': random.randint(0, 3),
            'timestamp': datetime.now().isoformat(),
            'source': 'simulated'
        }
        
        logger.info("Traffic data updated successfully")
        return traffic_data
    
    def get_hospital_data(self, weather_data: Dict = None, traffic_data: Dict = None):
        """Get current hospital wait times and capacity using Anthropic AI analysis"""
        from google_places_service import GooglePlacesService
        
        hospital_data = {}
        places_service = GooglePlacesService()
        
        for hospital in Config.HOSPITALS:
            try:
                # Use Google Places service with Anthropic AI analysis
                wait_time_data = places_service.get_hospital_wait_times(
                    hospital['name'], 
                    hospital.get('coordinates', []),
                    weather_data,
                    traffic_data
                )
                
                if wait_time_data:
                    wait_time = wait_time_data['current_wait']
                    source = wait_time_data['source']
                else:
                    # Fallback to analysis if Gemini fails
                    wait_time = places_service._fallback_analysis(
                        hospital['name'], weather_data, traffic_data
                    )
                    source = 'fallback_analysis'
                
                # Calculate capacity utilization based on time and hospital type
                capacity_utilization = self._calculate_capacity_utilization(hospital)
                
                hospital_data[hospital['id']] = {
                    'name': hospital['name'],
                    'current_wait_time': wait_time,
                    'capacity_utilization': capacity_utilization,
                    'available_beds': max(0, int(hospital.get('capacity', 50) * (1 - capacity_utilization))),
                    'last_updated': datetime.now().isoformat(),
                    'source': source
                }
                
                logger.info(f"Collected data for {hospital['name']}: {wait_time} min wait, {capacity_utilization:.1%} capacity")
                
            except Exception as e:
                logger.error(f"Error collecting data for {hospital['name']}: {e}")
                hospital_data[hospital['id']] = self._get_default_hospital_data(hospital)
        
        return hospital_data
    
    def _calculate_capacity_utilization(self, hospital):
        """Calculate realistic capacity utilization based on hospital characteristics"""
        import random
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        # Base capacity based on hospital type
        name_lower = hospital['name'].lower()
        if any(keyword in name_lower for keyword in ['medical center', 'university', 'regional', 'trauma']):
            base_capacity = 0.75  # Large hospitals typically busier
        elif any(keyword in name_lower for keyword in ['general', 'memorial', 'community']):
            base_capacity = 0.65  # Medium hospitals
        else:
            base_capacity = 0.55  # Smaller hospitals
        
        # Time-based adjustments
        if 8 <= current_hour <= 10 or 18 <= current_hour <= 20:  # Peak hours
            time_multiplier = 1.2
        elif 22 <= current_hour or current_hour <= 6:  # Late night/early morning
            time_multiplier = 0.6
        else:  # Regular hours
            time_multiplier = 1.0
        
        # Weekend adjustments
        if day_of_week >= 5:  # Weekend
            time_multiplier *= 0.9
        
        # Add some randomness
        final_capacity = base_capacity * time_multiplier
        final_capacity += random.uniform(-0.1, 0.1)
        
        # Ensure reasonable bounds
        return max(0.1, min(0.95, final_capacity))
    
    def scrape_hospital_website(self, hospital_url):
        """Scrape hospital website for wait times"""
        try:
            # This would be implemented to scrape actual hospital websites
            # For demo, we'll return simulated data
            return {
                'wait_time': random.randint(15, 120),
                'status': random.choice(['normal', 'busy', 'very_busy']),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Website scraping error: {e}")
            return None
    
    def get_emergency_services_data(self):
        """Get emergency services dispatch data"""
        try:
            # Simulate emergency services data
            return {
                'active_calls': random.randint(5, 25),
                'ambulance_availability': random.randint(2, 8),
                'police_scanner_incidents': random.randint(0, 10),
                'fire_department_calls': random.randint(0, 5),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Emergency services data error: {e}")
            return self._get_default_emergency_data()
    
    def _simulate_hospital_wait_time(self, hospital_id):
        """Simulate realistic wait times based on various factors"""
        base_wait = random.randint(20, 60)
        
        # Add time-based variations
        current_hour = datetime.now().hour
        if 2 <= current_hour <= 6:  # Late night/early morning
            base_wait *= 0.7
        elif 8 <= current_hour <= 10 or 18 <= current_hour <= 20:  # Peak hours
            base_wait *= 1.5
        
        # Add random variation
        variation = random.randint(-10, 20)
        return max(5, base_wait + variation)
    
    def _simulate_hospital_capacity(self, hospital_id):
        """Simulate hospital capacity utilization"""
        base_capacity = random.uniform(0.3, 0.9)
        
        # Add time-based variations
        current_hour = datetime.now().hour
        if 2 <= current_hour <= 6:
            base_capacity *= 0.8
        elif 8 <= current_hour <= 10 or 18 <= current_hour <= 20:
            base_capacity = min(0.95, base_capacity * 1.2)
        
        return round(base_capacity, 2)
    
