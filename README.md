# Emerix - AI-Powered Emergency Room Wait Time Predictor

Emerix helps you find nearby hospitals and predicts ER wait times using real-time data and advanced AI analysis. It's designed to help you make informed decisions in urgent situations, so you can get care faster and with less stress.

## Features

- **Location-Based Hospital Discovery**: Find nearby hospitals using Google Places API
- **AI-Powered Wait Time Predictions**: Uses Anthropic Claude to analyze multiple data sources
- **Real-Time Data Integration**: Weather, traffic, police incidents, and local events
- **Interactive Maps**: Visual hospital locations with wait time indicators
- **Current Location Support**: GPS-based location detection
- **Street Cam Analysis**: Mock traffic camera insights for better predictions

## Tech Stack

### Backend
- **Flask** - Python web framework
- **Anthropic Claude** - AI for wait time analysis
- **Google Places API** - Hospital discovery
- **Google Weather API** - Weather data
- **Google Routes API** - Traffic analysis
- **Open-Meteo API** - Free weather data
- **Socket.io** - Real-time updates

### Frontend
- **React** - UI framework
- **Leaflet** - Interactive maps
- **Lucide React** - Icons
- **CSS3** - Modern styling with animations

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- API Keys:
  - Anthropic API key
  - Google Cloud API key (Places, Weather, Routes)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ERWTPHACK
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_PLACES_API_KEY=your_google_key_here
   GOOGLE_WEATHER_API_KEY=your_google_key_here
   GOOGLE_TRAFFIC_API_KEY=your_google_key_here
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   python app.py
   ```
   The Flask server will run on `http://localhost:5001`

2. **Start the frontend** (in a new terminal)
   ```bash
   npm start
   ```
   The React app will run on `http://localhost:3000`

3. **Open your browser**
   Navigate to `http://localhost:3000`

## How It Works

1. **Enter Location**: User enters their location or uses GPS
2. **Hospital Discovery**: System finds nearby hospitals using Google Places
3. **Data Collection**: Gathers weather, traffic, and local event data
4. **AI Analysis**: Anthropic Claude analyzes all factors to predict wait times
5. **Results Display**: Shows hospitals on map with predicted wait times

## API Endpoints

- `POST /api/location` - Set user location and get hospitals
- `GET /api/hospitals` - Get list of hospitals
- `GET /api/predictions` - Get current predictions
- `GET /api/hospital/<id>` - Get specific hospital details
- `GET /api/weather` - Get weather data
- `GET /api/traffic` - Get traffic data
- `GET /api/street-cam-insight` - Get street cam analysis

## Project Structure

```
ERWTPHACK/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies
├── .env                           # Environment variables
├── data_collectors.py             # Data collection services
├── location_service.py            # Location and hospital services
├── prediction_engine_anthropic.py # AI prediction engine
├── google_places_service.py       # Google Places integration
├── street_cam_service.py          # Street cam analysis
└── src/                          # React frontend
    ├── App.js                     # Main React component
    ├── index.css                  # Global styles
    └── components/
        ├── LocationInput.js       # Location input component
        ├── HospitalMap.js         # Map component
        ├── PredictionCards.js     # Prediction display
        ├── PulseBackground.js    # Animated background
        └── NodeNetworkBackground.js # Node network background
```

## Configuration

Edit `config.py` to customize:
- API endpoints
- Logging levels
- Hospital search radius
- Prediction update intervals

## Production Deployment

1. **Set up environment variables** in your production environment
2. **Install dependencies** on your server
3. **Run the production script**:
   ```bash
   python start_production.py
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This application is for demonstration purposes. Always consult with healthcare professionals for medical emergencies.
