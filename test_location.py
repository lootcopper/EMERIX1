#!/usr/bin/env python3
"""
Test script to debug location service
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from location_service import LocationService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_location_service():
    """Test the location service"""
    print("Testing Location Service...")
    
    try:
        # Initialize location service
        location_service = LocationService()
        print("✅ Location service initialized")
        
        # Test getting user location
        print("\n1. Testing user location...")
        user_location = location_service.get_user_location("New York, NY")
        if user_location:
            print(f"✅ User location found: {user_location}")
        else:
            print("❌ Failed to get user location")
            return
        
        # Test finding nearby hospitals
        print("\n2. Testing hospital discovery...")
        try:
            hospitals = location_service.find_nearby_hospitals(user_location, 25)
            if hospitals:
                print(f"✅ Found {len(hospitals)} hospitals:")
                for i, hospital in enumerate(hospitals, 1):
                    print(f"  {i}. {hospital['name']} - {hospital.get('distance_miles', 'N/A')} miles")
            else:
                print("❌ No hospitals found")
        except Exception as e:
            print(f"❌ Error finding hospitals: {e}")
            import traceback
            traceback.print_exc()
        
        # Test weather data
        print("\n3. Testing weather data...")
        try:
            weather_data = location_service.get_weather_data_for_location(user_location)
            print(f"✅ Weather data: {weather_data.get('condition', 'unknown')} - {weather_data.get('temperature', 'N/A')}°C")
        except Exception as e:
            print(f"❌ Error getting weather: {e}")
        
        # Test traffic data
        print("\n4. Testing traffic data...")
        try:
            traffic_data = location_service.get_traffic_data_for_location(user_location)
            print(f"✅ Traffic data: {traffic_data.get('level', 'unknown')} - {traffic_data.get('congestion_level', 'N/A')}%")
        except Exception as e:
            print(f"❌ Error getting traffic: {e}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_location_service()
