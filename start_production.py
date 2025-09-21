#!/usr/bin/env python3
"""
Emergency Room Wait Time Predictor - Production Startup Script
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    

    try:
        import flask
        import flask_cors
        import flask_socketio
        import anthropic
        import requests
        import pandas
        import numpy
        print("✅ Python dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
  
    if not Path('node_modules').exists():
        print("📦 Installing Node.js dependencies...")
        try:
            subprocess.run(['npm', 'install', '--legacy-peer-deps'], check=True)
            print("✅ Node.js dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Node.js dependencies")
            print("Please run: npm install --legacy-peer-deps")
            return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    if not Path('.env').exists():
        print("⚠️  No .env file found. Creating from template...")
        create_env_file()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_places_key = os.getenv('GOOGLE_PLACES_API_KEY')
    weather_key = os.getenv('WEATHER_API_KEY')
    traffic_key = os.getenv('TRAFFIC_API_KEY')
    
    if not anthropic_key or anthropic_key == 'your_anthropic_api_key_here':
        print("❌ Anthropic API key not configured - REQUIRED for production")
        return False
    else:
        print("✅ Anthropic API key configured")
    
    if not google_places_key or google_places_key == 'your_google_places_api_key_here':
        print("⚠️  Google Places API key not configured - hospital discovery will use fallback")
    else:
        print("✅ Google Places API key configured")
    
    if not weather_key or weather_key == 'your_weather_api_key_here':
        print("⚠️  Weather API key not configured - will use Open-Meteo (free)")
    else:
        print("✅ Weather API key configured")
    
    if not traffic_key or traffic_key == 'your_traffic_api_key_here':
        print("⚠️  Traffic API key not configured - will use simulated traffic data")
    else:
        print("✅ Traffic API key configured")
    
    return True

def create_env_file():
    """Create .env file from template"""
    env_content = """# Emergency Room Wait Time Predictor - Environment Configuration

# Anthropic API Key (required for AI predictions)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

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
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("📝 .env file created. Please edit it with your API keys.")

def run_flask_app():
    """Run the Flask backend"""
    print("🚀 Starting Flask backend...")
    try:
        os.environ['FLASK_ENV'] = 'production'
        
        sys.path.append(str(Path(__file__).parent))
        from app import app, socketio
        
        socketio.run(
            app, 
            debug=False, 
            host='0.0.0.0', 
            port=5001,
            log_output=True
        )
    except Exception as e:
        print(f"❌ Flask backend error: {e}")
        return False

def run_react_app():
    """Run the React frontend"""
    print("🚀 Starting React frontend...")
    try:
        os.chdir(Path(__file__).parent)
        
        subprocess.run(['npm', 'start'], check=True)
    except Exception as e:
        print(f"❌ React frontend error: {e}")
        return False

def main():
    """Main production startup"""
    print("🏥 Emergency Room Wait Time Predictor - Production Mode")
    print("=" * 60)
    
    if not Path('app.py').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        print("\n❌ REQUIRED API keys are not configured.")
        print("   All Google API keys are required for production deployment.")
        print("   Please configure all API keys in the .env file.")
        sys.exit(1)
    
    print("\n🎯 Starting production system...")
    print("📱 Frontend will be available at: http://localhost:3000")
    print("🔧 Backend API will be available at: http://localhost:5000")
    print("⚠️  Press Ctrl+C to stop the system")
    
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    print("⏳ Waiting for backend to initialize...")
    time.sleep(5)
    
    try:
        run_react_app()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        print("👋 Emergency Room Wait Time Predictor stopped. Thank you!")

if __name__ == "__main__":
    main()
