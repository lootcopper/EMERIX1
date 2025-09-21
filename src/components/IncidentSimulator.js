import React, { useState } from 'react';
import { AlertTriangle, Car, Users, Zap } from 'lucide-react';

const IncidentSimulator = ({ onSimulateIncident }) => {
  const [incidentType, setIncidentType] = useState('car_accident');
  const [severity, setSeverity] = useState('moderate');
  const [location, setLocation] = useState({ lat: 40.7128, lng: -74.0060 });
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState(null);

  const incidentTypes = [
    { value: 'car_accident', label: 'Car Accident', icon: <Car size={20} /> },
    { value: 'mass_casualty', label: 'Mass Casualty', icon: <Users size={20} /> },
    { value: 'natural_disaster', label: 'Natural Disaster', icon: <Zap size={20} /> },
    { value: 'fire', label: 'Fire Emergency', icon: <AlertTriangle size={20} /> }
  ];

  const severityLevels = [
    { value: 'low', label: 'Low', color: '#28a745' },
    { value: 'moderate', label: 'Moderate', color: '#ffc107' },
    { value: 'high', label: 'High', color: '#dc3545' }
  ];

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const incidentData = {
        type: incidentType,
        location: [location.lat, location.lng],
        severity: severity
      };
      
      const response = await onSimulateIncident(incidentData);
      setResult(response);
    } catch (error) {
      console.error('Error simulating incident:', error);
      setResult({ error: 'Failed to simulate incident' });
    } finally {
      setSimulating(false);
    }
  };

  const getSeverityColor = (level) => {
    return severityLevels.find(s => s.value === level)?.color || '#6c757d';
  };

  return (
    <div className="card">
      <h3>
        <AlertTriangle size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
        Incident Impact Simulator
      </h3>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Simulate different types of incidents to see how they would affect ER wait times at nearby hospitals.
      </p>
      
      <div style={{ display: 'grid', gap: '20px', marginBottom: '20px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Incident Type:
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
            {incidentTypes.map(type => (
              <button
                key={type.value}
                type="button"
                className={`severity-option ${incidentType === type.value ? 'selected' : ''}`}
                onClick={() => setIncidentType(type.value)}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '12px',
                  border: '2px solid #007bff',
                  borderRadius: '8px',
                  background: incidentType === type.value ? '#007bff' : 'transparent',
                  color: incidentType === type.value ? 'white' : '#007bff',
                  cursor: 'pointer',
                  transition: 'all 0.3s'
                }}
              >
                {type.icon}
                {type.label}
              </button>
            ))}
          </div>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Severity Level:
          </label>
          <div style={{ display: 'flex', gap: '10px' }}>
            {severityLevels.map(level => (
              <button
                key={level.value}
                type="button"
                className={`severity-option ${severity === level.value ? 'selected' : ''}`}
                onClick={() => setSeverity(level.value)}
                style={{
                  backgroundColor: severity === level.value ? level.color : 'transparent',
                  color: severity === level.value ? 'white' : level.color,
                  borderColor: level.color
                }}
              >
                {level.label}
              </button>
            ))}
          </div>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Location (Latitude, Longitude):
          </label>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="number"
              step="0.0001"
              value={location.lat}
              onChange={(e) => setLocation(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
              placeholder="Latitude"
              style={{
                flex: 1,
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
            <input
              type="number"
              step="0.0001"
              value={location.lng}
              onChange={(e) => setLocation(prev => ({ ...prev, lng: parseFloat(e.target.value) }))}
              placeholder="Longitude"
              style={{
                flex: 1,
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>
        </div>
      </div>
      
      <button
        onClick={handleSimulate}
        disabled={simulating}
        className="check-button"
        style={{
          backgroundColor: '#dc3545',
          color: 'white',
          border: 'none',
          padding: '12px 24px',
          borderRadius: '4px',
          fontSize: '16px',
          fontWeight: 'bold',
          cursor: simulating ? 'not-allowed' : 'pointer',
          opacity: simulating ? 0.6 : 1,
          transition: 'all 0.3s'
        }}
      >
        {simulating ? 'Simulating...' : 'Simulate Incident'}
      </button>
      
      {result && !result.error && (
        <div style={{ marginTop: '20px' }}>
          <h4 style={{ margin: '0 0 15px 0', color: '#333' }}>
            Impact on Nearby Hospitals:
          </h4>
          <div style={{ display: 'grid', gap: '10px' }}>
            {Object.entries(result).map(([hospitalId, impact]) => (
              <div 
                key={hospitalId}
                style={{
                  padding: '15px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h5 style={{ margin: '0 0 5px 0', color: '#333' }}>
                      {impact.hospital_name}
                    </h5>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      Distance: {impact.distance_miles} miles
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: '1.2em', 
                      fontWeight: 'bold',
                      color: impact.impact_level === 'high' ? '#dc3545' : 
                             impact.impact_level === 'medium' ? '#ffc107' : '#28a745'
                    }}>
                      +{impact.wait_time_increase} min
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#666' }}>
                      New wait: {impact.estimated_new_wait} min
                    </div>
                  </div>
                </div>
                <div style={{ 
                  marginTop: '10px',
                  padding: '5px 10px',
                  backgroundColor: impact.impact_level === 'high' ? '#dc3545' : 
                                 impact.impact_level === 'medium' ? '#ffc107' : '#28a745',
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '0.8em',
                  fontWeight: 'bold',
                  textAlign: 'center'
                }}>
                  {(impact.impact_level || 'unknown').toUpperCase()} IMPACT
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {result?.error && (
        <div className="error" style={{ marginTop: '20px' }}>
          {result.error}
        </div>
      )}
    </div>
  );
};

export default IncidentSimulator;
