from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import time
import threading
import logging
from datetime import datetime, timedelta
import random

from data_collectors import DataCollector
from prediction_engine_anthropic import PredictionEngine
from location_service import LocationService
from config import Config
from street_cam_service import StreetCamVision


logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


try:
    data_collector = DataCollector()
    prediction_engine = PredictionEngine()
    location_service = LocationService()
    street_cam = StreetCamVision()
    logger.info("Components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    raise


current_predictions = {}
hospital_data = {}
system_status = {
    'status': 'initializing',
    'last_update': None,
    'error_count': 0,
    'api_status': {
        'openai': False,
        'weather': False,
        'traffic': False
    }
}



@app.route('/api/location', methods=['POST'])
def set_user_location():
    """Set user location and find nearby hospitals"""
    try:
        data = request.get_json()
        location_input = data.get('location', '')
        
        if not location_input:
            return jsonify({'error': 'Location is required', 'status': 'error'}), 400
        
  
        user_location = location_service.get_user_location(location_input)
        if not user_location:
            return jsonify({'error': 'Could not find location', 'status': 'error'}), 400
        
        # Find nearby hospitals
        nearby_hospitals = location_service.find_nearby_hospitals(user_location, 25)
        if not nearby_hospitals:
            return jsonify({'error': 'No hospitals found nearby', 'status': 'error'}), 404
        
        # Update global hospital list
        Config.HOSPITALS = nearby_hospitals
        
        # Get weather and traffic data for location
        weather_data = location_service.get_weather_data_for_location(user_location)
        traffic_data = location_service.get_traffic_data_for_location(user_location)
        
        # Run AI predictions for all hospitals (this is where token usage happens)
        logger.info("Running AI predictions for hospitals...")
        try:
            # Collect hospital data with weather and traffic context
            hospital_data = data_collector.get_hospital_data(weather_data, traffic_data)
            

            predictions = prediction_engine.generate_predictions(
                weather_data, traffic_data, hospital_data
            )
            
            # Update current predictions
            current_predictions.update(predictions)
            
            logger.info(f"Generated predictions for {len(predictions)} hospitals")
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            # Continue without predictions if AI fails
            predictions = {}
        
        return jsonify({
            'user_location': user_location,
            'hospitals': nearby_hospitals,
            'weather': weather_data,
            'traffic': traffic_data,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error setting location: {e}")
        return jsonify({'error': 'Failed to set location', 'status': 'error'}), 500

@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    """Get list of hospitals for current location"""
    try:
        return jsonify({
            'hospitals': Config.HOSPITALS,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting hospitals: {e}")
        return jsonify({'error': 'Failed to get hospitals', 'status': 'error'}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get current wait time predictions for all hospitals"""
    try:
        return jsonify({
            'predictions': current_predictions,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({'error': 'Failed to get predictions', 'status': 'error'}), 500

@app.route('/api/hospital/<hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    """Get detailed information for a specific hospital"""
    hospital = next((h for h in Config.HOSPITALS if h['id'] == hospital_id), None)
    if not hospital:
        return jsonify({'error': 'Hospital not found'}), 404
    
    prediction = current_predictions.get(hospital_id, {})
    return jsonify({
        'hospital': hospital,
        'prediction': prediction,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get current weather data"""
    try:
        weather_data = data_collector.get_weather_data()
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic', methods=['GET'])
def get_traffic():
    """Get current traffic data"""
    try:
        traffic_data = data_collector.get_traffic_data()
        return jsonify(traffic_data)
    except Exception as e:
        logger.error(f"Error getting traffic data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate-incident', methods=['POST'])
def simulate_incident():
    """Simulate an incident and show impact on wait times"""
    data = request.get_json()
    incident_type = data.get('type', 'car_accident')
    location = data.get('location', [40.7128, -74.0060])
    severity = data.get('severity', 'moderate')
    
    # Simulate impact on nearby hospitals
    impact_data = prediction_engine.simulate_incident(incident_type, location, severity)
    
    # Emit real-time update
    socketio.emit('incident_update', {
        'incident': {
            'type': incident_type,
            'location': location,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        },
        'impact': impact_data
    })
    
    return jsonify(impact_data)

@app.route('/api/street-cam-insight', methods=['GET'])
def street_cam_insight():
    if not Config.HOSPITALS:
        return jsonify({
            'status': 'error',
            'message': 'set a location first so we know where to look',
        }), 400
    first = Config.HOSPITALS[0]
    coords = first.get('coordinates', [37.7749, -122.4194])
    lat, lng = coords[0], coords[1]
    info = street_cam.get_insight(lat, lng)
    return jsonify({ 'status': 'ok', 'insight': info })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to ER Wait Time Predictor'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

logger.info("Prediction system ready - will run on-demand when hospitals are searched")

if __name__ == '__main__':
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
