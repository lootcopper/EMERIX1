#!/bin/bash

# Emergency Room Wait Time Predictor - Production Runner

echo "🏥 Emergency Room Wait Time Predictor - Production Mode"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
python3 -c "import flask, flask_cors, flask_socketio, google.generativeai, requests, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
fi

# Check Node.js dependencies
echo "🔍 Checking Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install --legacy-peer-deps
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node.js dependencies"
        exit 1
    fi
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# Emergency Room Wait Time Predictor - Environment Configuration

# Gemini API Key (required for AI predictions - FREE!)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Places API Key (required for hospital discovery)
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Weather API Key (OpenWeatherMap)
WEATHER_API_KEY=your_weather_api_key_here

# Traffic API Key (TomTom)
TRAFFIC_API_KEY=your_traffic_api_key_here

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=change-this-secret-key-in-production

# Database Configuration
DATABASE_URL=sqlite:///er_predictor.db

# API Configuration
API_RATE_LIMIT=100
UPDATE_INTERVAL=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=er_predictor.log
EOF
    echo "📝 .env file created."
    echo "❌ REQUIRED: Please update .env file with your actual API keys before running."
    echo "   All Google API keys are required for production deployment."
    exit 1
fi

# Check if API keys are configured
if grep -q "your_.*_api_key_here" .env; then
    echo "❌ API keys not configured in .env file."
    echo "   Please update .env file with your actual API keys."
    echo "   All Google API keys are required for production deployment."
    exit 1
fi

# Test system components
echo "🧪 Testing system components..."
python3 -c "
from config import Config
from data_collectors import DataCollector
from prediction_engine_gemini import PredictionEngine
from google_places_service import GooglePlacesService
from google_weather_service import GoogleWeatherService
from google_routes_service import GoogleRoutesService

print('✅ Config loaded')
dc = DataCollector()
print('✅ DataCollector initialized')
pe = PredictionEngine()
print('✅ PredictionEngine initialized')
gps = GooglePlacesService()
print('✅ GooglePlacesService initialized')
gws = GoogleWeatherService()
print('✅ GoogleWeatherService initialized')
grs = GoogleRoutesService()
print('✅ GoogleRoutesService initialized')
print('🎉 All components ready!')
"

if [ $? -ne 0 ]; then
    echo "❌ System component test failed"
    exit 1
fi

echo ""
echo "🚀 Starting Emergency Room Wait Time Predictor..."
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"
echo "⚠️  Press Ctrl+C to stop"
echo ""

# Start the production system
python3 start_production.py
