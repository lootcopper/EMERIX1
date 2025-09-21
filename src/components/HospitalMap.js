import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Clock, Users, Star, Navigation } from 'lucide-react';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const HospitalMap = ({ hospitals, predictions, userLocation }) => {
  const getWaitTimeColor = (waitTime) => {
    if (waitTime < 30) return '#10b981';
    if (waitTime < 60) return '#f59e0b';
    return '#dc2626';
  };

  const getWaitTimeClass = (waitTime) => {
    if (waitTime < 30) return 'low';
    if (waitTime < 60) return 'medium';
    return 'high';
  };

  const createCustomIcon = (waitTime) => {
    const color = getWaitTimeColor(waitTime);
    return L.divIcon({
      className: 'custom-div-icon',
      html: `
        <div style="
          background-color: ${color};
          width: 36px;
          height: 36px;
          border-radius: 50%;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 12px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          transition: all 0.2s;
        ">
          ${waitTime}m
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });
  };

  const createUserIcon = () => {
    return L.divIcon({
      className: 'custom-div-icon',
      html: `
        <div style="
          background-color: #dc2626;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 14px;
          box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
        ">
          👤
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  };

  if (!hospitals || hospitals.length === 0) {
    return (
      <div className="card">
        <h3>
          <MapPin size={20} />
          Hospital Map
        </h3>
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          color: '#666',
          background: '#f5f5f5',
          borderRadius: '8px'
        }}>
          <MapPin size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
          <p>No hospitals found. Please set your location first.</p>
        </div>
      </div>
    );
  }

  // Calculate center point
  const centerLat = userLocation?.latitude || 
    (hospitals.reduce((sum, h) => sum + h.coordinates[0], 0) / hospitals.length);
  const centerLng = userLocation?.longitude || 
    (hospitals.reduce((sum, h) => sum + h.coordinates[1], 0) / hospitals.length);

  return (
    <div className="card">
      <h3>
        <MapPin size={20} />
        Hospital Map
      </h3>
      <div className="map-container">
        <MapContainer
          center={[centerLat, centerLng]}
          zoom={12}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {/* User location marker */}
          {userLocation && (
            <Marker
              position={[userLocation.latitude, userLocation.longitude]}
              icon={createUserIcon()}
            >
              <Popup>
                <div style={{ padding: '8px', textAlign: 'center' }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Your Location</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {userLocation.address || `${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)}`}
                  </div>
                </div>
              </Popup>
            </Marker>
          )}
          
          {/* Hospital markers */}
          {hospitals.map((hospital) => {
            const prediction = predictions[hospital.id];
            const waitTime = prediction?.current_wait_time || 30;
            
            return (
              <Marker
                key={hospital.id}
                position={[hospital.coordinates[0], hospital.coordinates[1]]}
                icon={createCustomIcon(waitTime)}
              >
                <Popup>
                  <div style={{ padding: '12px', minWidth: '250px' }}>
                    <div style={{ marginBottom: '12px' }}>
                      <h4 style={{ margin: '0 0 8px 0', color: '#1a1a1a', fontSize: '16px', fontWeight: '600' }}>
                        {hospital.name}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#666', fontSize: '12px' }}>
                          <Navigation size={12} />
                          {hospital.distance_miles ? `${hospital.distance_miles} miles` : 'Distance unknown'}
                        </div>
                        {hospital.rating && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#666', fontSize: '12px' }}>
                            <Star size={12} fill="#fbbf24" color="#fbbf24" />
                            {hospital.rating}
                          </div>
                        )}
                      </div>
                      {hospital.address && (
                        <p style={{ margin: '0', color: '#666', fontSize: '12px', lineHeight: '1.4' }}>
                          {hospital.address}
                        </p>
                      )}
                    </div>
                    
                    <div style={{ 
                      padding: '12px', 
                      background: '#f5f5f5', 
                      borderRadius: '6px',
                      marginBottom: '12px'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px', fontWeight: '600', color: '#1a1a1a' }}>Wait Time</span>
                        <span style={{ 
                          fontSize: '20px', 
                          fontWeight: '700', 
                          color: getWaitTimeColor(waitTime)
                        }}>
                          {waitTime} min
                        </span>
                      </div>
                      
                      {prediction && (
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          <div style={{ marginBottom: '4px' }}>
                            Confidence: {prediction.confidence || 75}%
                          </div>
                          <div>
                            Method: {prediction.prediction_method || 'AI Analysis'}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {prediction?.recommendation && (
                      <div style={{
                        padding: '8px 12px',
                        background: prediction.recommendation.toLowerCase() === 'go now' ? '#dc2626' : 
                                   prediction.recommendation.toLowerCase() === 'wait' ? '#f59e0b' : '#6b7280',
                        color: 'white',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '600',
                        textAlign: 'center'
                      }}>
                        {prediction.recommendation}
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
      
      <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#666' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#10b981' }}></div>
            <span>Low wait (&lt;30 min)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b' }}></div>
            <span>Medium wait (30-60 min)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#dc2626' }}></div>
            <span>High wait (&gt;60 min)</span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#dc2626' }}></div>
          <span>Your location</span>
        </div>
      </div>
    </div>
  );
};

export default HospitalMap;