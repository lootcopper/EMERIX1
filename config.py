import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    TRAFFIC_API_KEY = os.getenv('TRAFFIC_API_KEY')
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///er_predictor.db')
    
    # API Configuration
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per minute
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '30'))  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'er_predictor.log')
    
    # Hospital database - populated dynamically via Google Places API
    HOSPITALS = []
    
    # API endpoints
    GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"
    GOOGLE_WEATHER_BASE_URL = "https://maps.googleapis.com/maps/api/geocode"
    GOOGLE_ROUTES_BASE_URL = "https://routes.googleapis.com/directions/v2"
    # Production API endpoints
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    TRAFFIC_API_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
