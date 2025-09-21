import React, { useState } from 'react';
import { Clock, TrendingUp, AlertCircle, CheckCircle, MapPin, Star } from 'lucide-react';

const PredictionCards = ({ hospitals, predictions, loading }) => {
  const [camNote, setCamNote] = useState(null);

  const getWaitTimeClass = (waitTime) => {
    if (waitTime < 30) return 'low';
    if (waitTime < 60) return 'medium';
    return 'high';
  };

  const getRecommendationIcon = (waitLabel) => {
    switch (waitLabel?.toLowerCase()) {
      case 'high wait':
        return <AlertCircle size={20} style={{ color: '#dc2626' }} />;
      case 'medium wait':
        return <Clock size={20} style={{ color: '#f59e0b' }} />;
      case 'low wait':
        return <CheckCircle size={20} style={{ color: '#10b981' }} />;
      default:
        return <Clock size={20} style={{ color: '#f59e0b' }} />;
    }
  };

  const getRecommendationClass = (recommendation) => {
    switch (recommendation?.toLowerCase()) {
      case 'go now':
        return 'go-now';
      case 'wait':
        return 'wait';
      case 'consider alternatives':
        return 'alternatives';
      default:
        return 'wait';
    }
  };

  const getWaitTimeLabel = (waitTime) => {
    if (waitTime < 30) return 'Low wait';
    if (waitTime < 60) return 'Medium wait';
    return 'High wait';
  };

  const pingStreetCam = async () => {
    try {
      const res = await fetch('http://localhost:5001/api/street-cam-insight');
      const data = await res.json();
      if (data && data.status === 'ok') {
        const a = data.insight.analysis;
        setCamNote(`street cam vibe: ${a.traffic_level} • ~${a.estimated_cars} cars • conf ${a.confidence}%`);
      }
    } catch(_) {}
  };

  if (loading) {
    return (
      <div className="card">
        <h3>
          <TrendingUp size={20} />
          Wait Time Predictions
        </h3>
        <div className="loading">
          <p>Loading predictions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>
        <TrendingUp size={20} />
        Wait Time Predictions
      </h3>
      {camNote && (
        <div style={{ background: '#f8f8f8', border: '1px dashed #ddd', padding: 10, borderRadius: 8, marginBottom: 12, color: '#555', fontSize: 13 }}>
          {camNote}
        </div>
      )}
      <button onClick={pingStreetCam} className="current-location-button" style={{ marginBottom: 12 }}>peek street cam demo</button>
      <div style={{ display: 'grid', gap: '16px' }}>
        {hospitals.map((hospital) => {
          const prediction = predictions[hospital.id];
          const currentWait = prediction?.current_wait_time || 30;
          const waitClass = getWaitTimeClass(currentWait);
          
          return (
            <div 
              key={hospital.id}
              className={`prediction-card ${waitClass}-wait`}
              style={{
                padding: '20px',
                borderRadius: '12px',
                border: '1px solid #e5e5e5',
                background: 'white',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#1a1a1a', fontSize: '18px', fontWeight: '600' }}>
                    {hospital.name}
                  </h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#666', fontSize: '14px' }}>
                      <MapPin size={14} />
                      {hospital.distance_miles ? `${hospital.distance_miles} miles` : 'Distance unknown'}
                    </div>
                    {hospital.rating && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#666', fontSize: '14px' }}>
                        <Star size={14} fill="#fbbf24" color="#fbbf24" />
                        {hospital.rating}
                      </div>
                    )}
                  </div>
                  {hospital.address && (
                    <p style={{ margin: '0', color: '#666', fontSize: '14px', lineHeight: '1.4' }}>
                      {hospital.address}
                    </p>
                  )}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className={`wait-time ${waitClass}`} style={{ fontSize: '28px', fontWeight: '700', margin: '0' }}>
                    {currentWait}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                    minutes
                  </div>
                </div>
              </div>
              
              {prediction && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '14px', color: '#666' }}>Confidence:</span>
                      <span style={{ fontSize: '14px', fontWeight: '600', color: '#1a1a1a' }}>
                        {prediction.confidence || 75}%
                      </span>
                    </div>
                  </div>
                  
                  {prediction.factors && prediction.factors.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>Key Factors:</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {prediction.factors.map((factor, index) => (
                          <span 
                            key={index}
                            style={{
                              fontSize: '12px',
                              padding: '4px 8px',
                              background: '#fef2f2',
                              color: '#dc2626',
                              borderRadius: '12px',
                              border: '1px solid #fecaca'
                            }}
                          >
                            {factor}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className={`recommendation ${waitClass}-wait`}>
                    {getRecommendationIcon(getWaitTimeLabel(currentWait))}
                    {getWaitTimeLabel(currentWait)}
                  </div>
                </div>
              )}
              
              {!prediction && (
                <div style={{ 
                  padding: '12px', 
                  background: '#f5f5f5', 
                  borderRadius: '6px', 
                  textAlign: 'center',
                  color: '#666',
                  fontSize: '14px'
                }}>
                  No prediction available
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PredictionCards;