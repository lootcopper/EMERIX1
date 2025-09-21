import requests
import json
import logging
import random
from typing import List, Dict, Optional
from datetime import datetime
from config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class GooglePlacesService:
    def __init__(self):
        self.api_key = Config.GOOGLE_PLACES_API_KEY
        self.base_url = Config.GOOGLE_PLACES_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ER-Wait-Time-Predictor/1.0'
        })
    
    def find_hospitals(self, lat: float, lng: float, radius: int = 25000) -> List[Dict]:
        """
        Find hospitals near a location using Google Places API
        """
        if not self.api_key or self.api_key == 'your_google_places_api_key_here':
            logger.warning("Google Places API key not configured, using fallback hospital data")
            return self._get_fallback_hospitals(lat, lng)
        
        # Search for hospitals
        hospitals = self._search_hospitals(lat, lng, radius)
        
        if not hospitals:
            raise Exception("No hospitals found in the specified area")
        
        # Enrich hospital data with details
        enriched_hospitals = []
        for hospital in hospitals:
            try:
                details = self._get_hospital_details(hospital.get('place_id'))
                if details:
                    enriched_hospitals.append(self._merge_hospital_data(hospital, details))
                else:
                    enriched_hospitals.append(self._format_basic_hospital(hospital))
            except Exception as e:
                logger.error(f"Error enriching hospital {hospital.get('name', 'Unknown')}: {e}")
                enriched_hospitals.append(self._format_basic_hospital(hospital))
        
        logger.info(f"Found {len(enriched_hospitals)} hospitals near {lat}, {lng}")
        return enriched_hospitals
    
    def _search_hospitals(self, lat: float, lng: float, radius: int) -> List[Dict]:
        """Search for hospitals using Google Places API"""
        try:
            # Search for hospitals
            url = f"{self.base_url}/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': 'hospital',
                'keyword': 'emergency room',
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return []
            
            results = data.get('results', [])
            
            # Filter for hospitals with emergency rooms
            hospitals = []
            for place in results:
                if self._is_emergency_hospital(place):
                    hospitals.append(place)
            
            # If we don't have enough hospitals, search for general hospitals
            if len(hospitals) < 3:
                hospitals.extend(self._search_general_hospitals(lat, lng, radius))
            
            return hospitals[:10]  # Limit to 10 hospitals
            
        except Exception as e:
            logger.error(f"Error searching hospitals: {e}")
            return []
    
    def _search_general_hospitals(self, lat: float, lng: float, radius: int) -> List[Dict]:
        """Search for general hospitals if emergency hospitals are limited"""
        try:
            url = f"{self.base_url}/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': 'hospital',
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])[:5]  # Limit to 5 additional hospitals
            
        except Exception as e:
            logger.error(f"Error searching general hospitals: {e}")
            return []
    
    def _get_hospital_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a hospital"""
        try:
            if not place_id:
                return None
            
            url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,geometry,formatted_phone_number,website,opening_hours,rating,user_ratings_total,types',
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Google Places Details API error: {data.get('status')}")
                return None
            
            return data.get('result', {})
            
        except Exception as e:
            logger.error(f"Error getting hospital details: {e}")
            return None
    
    def _is_emergency_hospital(self, place: Dict) -> bool:
        """Check if a place is an emergency hospital"""
        types = place.get('types', [])
        name = place.get('name', '').lower()
        
        # Check for emergency-related types
        emergency_types = ['hospital', 'health', 'emergency']
        emergency_keywords = ['emergency', 'er', 'urgent', 'trauma', 'medical center']
        
        # Check types
        has_emergency_type = any(t in emergency_types for t in types)
        
        # Check name for emergency keywords
        has_emergency_name = any(keyword in name for keyword in emergency_keywords)
        
        return has_emergency_type or has_emergency_name
    
    def _merge_hospital_data(self, basic: Dict, details: Dict) -> Dict:
        """Merge basic hospital data with detailed information"""
        return {
            'id': basic.get('place_id', ''),
            'name': details.get('name', basic.get('name', 'Unknown Hospital')),
            'address': details.get('formatted_address', ''),
            'coordinates': [
                details.get('geometry', {}).get('location', {}).get('lat', 0),
                details.get('geometry', {}).get('location', {}).get('lng', 0)
            ],
            'phone': details.get('formatted_phone_number', ''),
            'website': details.get('website', ''),
            'rating': details.get('rating', 0),
            'user_ratings_total': details.get('user_ratings_total', 0),
            'opening_hours': details.get('opening_hours', {}),
            'types': details.get('types', []),
            'capacity': self._estimate_capacity(details),
            'last_updated': datetime.now().isoformat(),
            'source': 'google_places'
        }
    
    def _format_basic_hospital(self, basic: Dict) -> Dict:
        """Format basic hospital data when details are unavailable"""
        return {
            'id': basic.get('place_id', ''),
            'name': basic.get('name', 'Unknown Hospital'),
            'address': basic.get('vicinity', ''),
            'coordinates': [
                basic.get('geometry', {}).get('location', {}).get('lat', 0),
                basic.get('geometry', {}).get('location', {}).get('lng', 0)
            ],
            'phone': '',
            'website': '',
            'rating': basic.get('rating', 0),
            'user_ratings_total': 0,
            'opening_hours': {},
            'types': basic.get('types', []),
            'capacity': self._estimate_capacity(basic),
            'last_updated': datetime.now().isoformat(),
            'source': 'google_places_basic'
        }
    
    def _estimate_capacity(self, hospital_data: Dict) -> int:
        """Estimate hospital capacity based on available data"""
        name = hospital_data.get('name', '').lower()
        types = hospital_data.get('types', [])
        
        # Estimate based on hospital name and type
        if any(keyword in name for keyword in ['medical center', 'university', 'regional']):
            return 100
        elif any(keyword in name for keyword in ['general', 'memorial', 'community']):
            return 75
        elif any(keyword in name for keyword in ['clinic', 'urgent care']):
            return 25
        else:
            return 50  # Default capacity
    
    
    def get_hospital_wait_times(self, hospital_name: str, hospital_coordinates: List[float] = None, 
                              weather_data: Dict = None, traffic_data: Dict = None) -> Optional[Dict]:
        """Get current wait times for a hospital using Gemini AI analysis"""
        try:
            # Use Gemini AI to analyze all factors and predict wait time
            wait_time = self._analyze_with_anthropic(hospital_name, hospital_coordinates, weather_data, traffic_data)
            
            return {
                'current_wait': wait_time,
                'last_updated': datetime.now().isoformat(),
                'source': 'anthropic_ai_analysis'
            }
        except Exception as e:
            logger.error(f"Error getting wait times for {hospital_name}: {e}")
            return None
    
    def _analyze_with_anthropic(self, hospital_name: str, coordinates: List[float] = None, 
                            weather_data: Dict = None, traffic_data: Dict = None) -> int:
        """Use Anthropic AI to analyze all factors and predict wait time"""
        try:
            import anthropic
            
            # Initialize Anthropic
            client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            
            # Prepare comprehensive context for AI analysis
            context = self._prepare_analysis_context(hospital_name, coordinates, weather_data, traffic_data)
            
            # Create detailed prompt for Anthropic
            prompt = f"""You are an expert emergency room wait time predictor. Analyze the following data and predict the current wait time for {hospital_name}:
            
            HOSPITAL INFORMATION:
            - Name: {hospital_name}
            - Coordinates: {coordinates if coordinates else 'Not available'}
            - Hospital Type: {self._classify_hospital_type(hospital_name)}
            
            WEATHER CONDITIONS:
            - Condition: {weather_data.get('condition', 'unknown') if weather_data else 'unknown'}
            - Temperature: {weather_data.get('temperature', 'N/A') if weather_data else 'N/A'}°C
            - Precipitation: {weather_data.get('precipitation', 0) if weather_data else 0}mm
            - Wind Speed: {weather_data.get('wind_speed', 'N/A') if weather_data else 'N/A'} m/s
            
            TRAFFIC CONDITIONS:
            - Traffic Level: {traffic_data.get('level', 'unknown') if traffic_data else 'unknown'}
            - Average Speed: {traffic_data.get('average_speed', 'N/A') if traffic_data else 'N/A'} mph
            - Congestion Level: {traffic_data.get('congestion_level', 'N/A') if traffic_data else 'N/A'}%
            - Accidents: {traffic_data.get('incidents', 0) if traffic_data else 0}
            
            TIME FACTORS:
            - Current Hour: {datetime.now().hour}
            - Day of Week: {datetime.now().weekday()} (0=Monday, 6=Sunday)
            - Peak Hours: 8-10am, 6-8pm
            - Late Night: 11pm-6am
            
            ANALYSIS REQUIREMENTS:
            1. Consider hospital type and size (medical centers vs community hospitals vs clinics)
            2. Factor in weather impact (storms increase accidents, extreme weather affects ER volume)
            3. Account for traffic patterns (rush hour increases accidents)
            4. Consider time of day and day of week patterns
            5. Analyze capacity utilization based on hospital characteristics
            6. Factor in local events and seasonal patterns
            
            Provide your analysis and predict the current wait time in minutes.
            Consider all factors and provide a realistic estimate between 5-300 minutes.
            
            Respond with ONLY a JSON object in this format:
            {{
                "wait_time": <number>,
                "confidence": <number 0-100>,
                "factors": ["factor1", "factor2", "factor3"],
                "reasoning": "Brief explanation of your analysis"
            }}
            """
            
            # Get AI prediction
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,  # Reduced token limit to save costs
                messages=[{"role": "user", "content": prompt}]
            )
            ai_response = response.content[0].text.strip()
            
            # Parse the response
            try:
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    wait_time = int(data.get('wait_time', 30))
                    confidence = int(data.get('confidence', 75))
                    factors = data.get('factors', [])
                    reasoning = data.get('reasoning', 'AI analysis')
                    
                    # Validate wait time
                    if 5 <= wait_time <= 300:
                        logger.info(f"Gemini analysis for {hospital_name}: {wait_time} min (confidence: {confidence}%)")
                        logger.info(f"Factors: {factors}")
                        logger.info(f"Reasoning: {reasoning}")
                        return wait_time
                    else:
                        logger.warning(f"Gemini returned invalid wait time: {wait_time}, using fallback")
                        return self._fallback_analysis(hospital_name, weather_data, traffic_data)
                else:
                    logger.warning("Could not extract JSON from Gemini response")
                    return self._fallback_analysis(hospital_name, weather_data, traffic_data)
                    
            except Exception as e:
                logger.error(f"Error parsing Gemini response: {e}")
                return self._fallback_analysis(hospital_name, weather_data, traffic_data)
                
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._fallback_analysis(hospital_name, weather_data, traffic_data)
    
    def _prepare_analysis_context(self, hospital_name: str, coordinates: List[float] = None, 
                                weather_data: Dict = None, traffic_data: Dict = None) -> Dict:
        """Prepare context data for Gemini analysis"""
        return {
            'hospital_name': hospital_name,
            'coordinates': coordinates,
            'weather': weather_data,
            'traffic': traffic_data,
            'current_time': datetime.now(),
            'hospital_type': self._classify_hospital_type(hospital_name)
        }
    
    def _classify_hospital_type(self, hospital_name: str) -> str:
        """Classify hospital type based on name"""
        name_lower = hospital_name.lower()
        
        if any(keyword in name_lower for keyword in ['medical center', 'university', 'regional', 'trauma']):
            return 'Medical Center'
        elif any(keyword in name_lower for keyword in ['general', 'memorial', 'community', 'county']):
            return 'Community Hospital'
        elif any(keyword in name_lower for keyword in ['clinic', 'urgent care', 'outpatient']):
            return 'Clinic/Urgent Care'
        else:
            return 'General Hospital'
    
    def _fallback_analysis(self, hospital_name: str, weather_data: Dict = None, traffic_data: Dict = None) -> int:
        """Fallback analysis when Gemini fails"""
        try:
            current_hour = datetime.now().hour
            day_of_week = datetime.now().weekday()
            
            # Base wait time based on hospital type
            base_wait = self._get_base_wait_time(hospital_name)
            
            # Time-based adjustments
            time_multiplier = self._get_time_multiplier(current_hour, day_of_week)
            
            # Weather impact
            weather_multiplier = self._get_weather_impact(weather_data)
            
            # Traffic impact
            traffic_multiplier = self._get_traffic_impact(traffic_data)
            
            # Calculate final wait time
            final_wait = int(base_wait * time_multiplier * weather_multiplier * traffic_multiplier)
            
            # Ensure reasonable bounds
            final_wait = max(5, min(300, final_wait))
            
            logger.info(f"Fallback analysis for {hospital_name}: {final_wait} minutes")
            return final_wait
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return 30  # Ultimate fallback
    
    def _analyze_hospital_wait_time(self, hospital_name: str) -> int:
        """Analyze hospital wait time based on comprehensive factors"""
        try:
            current_hour = datetime.now().hour
            day_of_week = datetime.now().weekday()
            
            # Base wait time based on hospital type and size
            base_wait = self._get_base_wait_time(hospital_name)
            
            # Time-based adjustments
            time_multiplier = self._get_time_multiplier(current_hour, day_of_week)
            
            # Weather impact (simulated based on current conditions)
            weather_multiplier = self._get_weather_impact()
            
            # Traffic impact
            traffic_multiplier = self._get_traffic_impact(current_hour)
            
            # Hospital capacity impact
            capacity_multiplier = self._get_capacity_impact(hospital_name)
            
            # Local events impact
            events_multiplier = self._get_events_impact()
            
            # Calculate final wait time
            final_wait = int(base_wait * time_multiplier * weather_multiplier * 
                           traffic_multiplier * capacity_multiplier * events_multiplier)
            
            # Ensure reasonable bounds
            final_wait = max(5, min(300, final_wait))
            
            logger.info(f"Analyzed wait time for {hospital_name}: {final_wait} minutes")
            return final_wait
            
        except Exception as e:
            logger.error(f"Error analyzing hospital wait time: {e}")
            return 45  # Fallback to 45 minutes if analysis fails
    
    def _get_base_wait_time(self, hospital_name: str) -> int:
        """Get base wait time based on hospital characteristics"""
        name_lower = hospital_name.lower()
        
        # Large medical centers typically have longer waits
        if any(keyword in name_lower for keyword in ['medical center', 'university', 'regional', 'trauma']):
            return 45
        # Community hospitals
        elif any(keyword in name_lower for keyword in ['general', 'memorial', 'community', 'county']):
            return 35
        # Smaller facilities
        elif any(keyword in name_lower for keyword in ['clinic', 'urgent care', 'outpatient']):
            return 25
        else:
            return 30  # Default
    
    def _get_time_multiplier(self, hour: int, day_of_week: int) -> float:
        """Get time-based multiplier for wait times"""
        # Peak hours (8-10am, 6-8pm)
        if (8 <= hour <= 10) or (18 <= hour <= 20):
            return 1.4
        # Late night/early morning (11pm-6am)
        elif hour >= 23 or hour <= 6:
            return 0.7
        # Weekend
        elif day_of_week >= 5:
            return 0.9
        # Regular hours
        else:
            return 1.0
    
    def _get_weather_impact(self, weather_data: Dict = None) -> float:
        """Get weather impact on wait times based on actual weather data"""
        if not weather_data:
            return 1.0  # No weather data available
        
        condition = weather_data.get('condition', 'clear').lower()
        temperature = weather_data.get('temperature', 20)
        precipitation = weather_data.get('precipitation', 0)
        wind_speed = weather_data.get('wind_speed', 0)
        
        # Stormy weather increases accidents and ER volume
        if condition in ['stormy', 'thunderstorm']:
            return 1.4
        elif condition in ['snowy', 'snow']:
            return 1.3
        elif condition in ['rainy', 'rain']:
            return 1.2
        elif condition in ['foggy', 'fog']:
            return 1.1
        elif precipitation > 5:  # Heavy precipitation
            return 1.2
        elif wind_speed > 20:  # High winds
            return 1.1
        elif temperature < 0 or temperature > 35:  # Extreme temperatures
            return 1.1
        else:
            return 1.0  # Clear weather
    
    def _get_traffic_impact(self, traffic_data: Dict = None) -> float:
        """Get traffic impact on wait times based on actual traffic data"""
        if not traffic_data:
            return 1.0  # No traffic data available
        
        level = traffic_data.get('level', 'medium').lower()
        congestion = traffic_data.get('congestion_level', 50)
        incidents = traffic_data.get('incidents', 0)
        average_speed = traffic_data.get('average_speed', 50)
        
        # High traffic increases accidents
        if level == 'high' or congestion > 80:
            return 1.3
        elif level == 'medium' or congestion > 60:
            return 1.1
        elif incidents > 2:  # Multiple incidents
            return 1.2
        elif average_speed < 20:  # Very slow traffic
            return 1.1
        else:
            return 1.0  # Low traffic
    
    def _get_capacity_impact(self, hospital_name: str) -> float:
        """Get hospital capacity impact on wait times"""
        # Simulate capacity based on hospital type
        import random
        capacity_utilization = random.uniform(0.6, 0.9)
        
        if capacity_utilization > 0.8:
            return 1.3  # High capacity
        elif capacity_utilization > 0.7:
            return 1.1  # Medium capacity
        else:
            return 1.0  # Low capacity
    
    def _get_events_impact(self) -> float:
        """Get local events impact on wait times"""
        # Simulate local events impact
        import random
        event_impact = random.uniform(0.9, 1.2)
        return event_impact
    
    def search_hospitals_by_name(self, name: str, location: str = None) -> List[Dict]:
        """Search for hospitals by name"""
        try:
            if not self.api_key:
                return []
            
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': f"{name} hospital",
                'key': self.api_key
            }
            
            if location:
                params['location'] = location
                params['radius'] = 50000  # 50km radius
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                return []
            
            results = data.get('results', [])
            hospitals = []
            
            for place in results:
                if self._is_emergency_hospital(place):
                    details = self._get_hospital_details(place.get('place_id'))
                    if details:
                        hospitals.append(self._merge_hospital_data(place, details))
            
            return hospitals
            
        except Exception as e:
            logger.error(f"Error searching hospitals by name: {e}")
            return []
    
    def _get_fallback_hospitals(self, lat: float, lng: float) -> List[Dict]:
        """Get fallback hospital data when Google Places API is not available"""
        logger.info(f"Using fallback hospital data for location: {lat}, {lng}")
        
        # Create some sample hospitals around the location
        hospitals = []
        
        # Add some hospitals with slight coordinate variations
        for i in range(3):
            hospital_lat = lat + (random.uniform(-0.01, 0.01) * (i + 1))
            hospital_lng = lng + (random.uniform(-0.01, 0.01) * (i + 1))
            
            hospital_types = [
                "General Hospital",
                "Medical Center", 
                "Community Hospital"
            ]
            
            hospital_names = [
                "City General Hospital",
                "Regional Medical Center",
                "Community Health Center"
            ]
            
            hospital = {
                'id': f'fallback_hospital_{i+1}',
                'name': f"{hospital_names[i]} {i+1}",
                'address': f"123 Main St, City {i+1}",
                'coordinates': [hospital_lat, hospital_lng],
                'phone': f"(555) 123-{1000+i}",
                'rating': round(random.uniform(3.5, 4.8), 1),
                'type': hospital_types[i],
                'capacity': random.randint(50, 200),
                'website': f"https://hospital{i+1}.com",
                'source': 'fallback_data'
            }
            
            hospitals.append(hospital)
        
        logger.info(f"Generated {len(hospitals)} fallback hospitals")
        return hospitals
