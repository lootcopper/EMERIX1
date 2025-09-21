import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import LocationInput from './components/LocationInput';
import HospitalMap from './components/HospitalMap';
import PredictionCards from './components/PredictionCards';
import PulseBackground from './components/PulseBackground';
import NodeNetworkBackground from './components/NodeNetworkBackground';
import './index.css';

const API_BASE_URL = 'http://localhost:5001/api';

function About() {
  return (
    <div style={{ maxWidth: 600, margin: '80px auto', padding: 32, background: 'white', borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
      <h1 style={{ color: '#dc2626', fontWeight: 700 }}>About Emerix</h1>
      <p style={{ fontSize: 18, margin: '24px 0' }}>
        <b>Emerix</b> helps you find nearby hospitals and predicts ER wait times using real-time data and advanced AI analysis. 
        It’s designed to help you make informed decisions in urgent situations, so you can get care faster and with less stress. Designed to reduce Ambulance response times.
      </p>
      <p style={{ color: '#666' }}>
        Emerix uses live hospital, weather, and traffic cam data to provide the most accurate wait time predictions possible.
      </p>
      <Link to="/" className="header-link">← Back to Home</Link>
    </div>
  );
}

function App() {
  const [hospitals, setHospitals] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [locationSet, setLocationSet] = useState(false);

  useEffect(() => {
    if (locationSet) {
      loadHospitals();
      loadPredictions();
    } else {
      setLoading(false);
    }
  }, [locationSet]);

  const loadHospitals = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/hospitals`);
      const data = await response.json();
      setHospitals(data.hospitals);
    } catch (err) {
      setError('Failed to load hospitals');
      console.error('Error loading hospitals:', err);
    }
  };

  const loadPredictions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/predictions`);
      const data = await response.json();
      setPredictions(data.predictions);
      setLoading(false);
    } catch (err) {
      setError('Failed to load predictions');
      setLoading(false);
      console.error('Error loading predictions:', err);
    }
  };

  const setLocation = async (location) => {
    try {
      const response = await fetch(`${API_BASE_URL}/location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setUserLocation(data.user_location);
        setHospitals(data.hospitals);
        setLocationSet(true);
        setLoading(false);
        if (data.predictions) {
          setPredictions(data.predictions);
        } else {
          loadPredictions();
        }
      } else {
        setError(data.error || 'Failed to set location');
      }
      return data;
    } catch (err) {
      console.error('Error setting location:', err);
      setError('Failed to set location');
      return null;
    }
  };

  const handleLocationSet = (locationData) => {
    setUserLocation(locationData.user_location);
    setHospitals(locationData.hospitals);
    setLocationSet(true);
    setLoading(false);
    if (locationData.predictions) {
      setPredictions(locationData.predictions);
    } else {
      loadPredictions();
    }
  };

  if (!locationSet) {
    return (
      <div className="App">
        <NodeNetworkBackground />
        <PulseBackground />
        <header className="header">
          <div className="header-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <a href="/" className="logo">Emerix</a>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <a href="#about-scroll" className="header-link">About</a>
                <button className="settings-button">⚙️</button>
              </div>
            </div>
          </div>
        </header>
        <div className="hero">
          <div className="hero-content">
            <h1>
              Turn your location into <span className="hero-highlight">AI-powered ER predictions</span>
            </h1>
            <p>
              Get real-time wait time predictions for nearby hospitals using advanced AI analysis of weather, traffic, and hospital capacity data.
            </p>
            <div className="cta-block">
              <LocationInput onLocationSet={handleLocationSet} userLocation={userLocation} setUserLocation={setUserLocation} />
            </div>
          </div>
        </div>
        <section id="about-scroll" style={{ background: '#f8f8f8', padding: '48px 0', marginTop: 48, borderTop: '1px solid #eee', textAlign: 'center' }}>
          <h2 style={{ color: '#dc2626', fontWeight: 700, fontSize: 28, marginBottom: 16 }}>About Emerix</h2>
          <p style={{ maxWidth: 600, margin: '0 auto', fontSize: 18, color: '#444', lineHeight: 1.6 }}>
            <b>Emerix</b> helps you find nearby hospitals and predicts ER wait times using real-time data and advanced AI analysis. It’s designed to help you make informed decisions in urgent situations, so you can get care faster and with less stress.<br /><br />
            Emerix uses live hospital, weather, and traffic data to provide the most accurate wait time predictions possible.
          </p>
        </section>
        {error && <div className="error">{error}</div>}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="App">
        <NodeNetworkBackground />
        <PulseBackground />
        <div className="loading">
          <h2>Loading Emergency Room Data...</h2>
          <p>Please wait while we gather real-time information</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <NodeNetworkBackground />
        <PulseBackground />
        <header className="header">
          <div className="header-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <a href="/" className="logo">Emerix</a>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <button className="settings-button">⚙️</button>
              </div>
            </div>
          </div>
        </header>
        {error && <div className="error">{error}</div>}
        <Routes>
          <Route path="/" element={
            <div>
              <div className="fixed-header">
                <h2 style={{ margin: 0, fontSize: '24px', textAlign: 'center' }}>Nearby Hospitals</h2>
              </div>
              <div className="grid">
                <HospitalMap hospitals={hospitals} predictions={predictions} />
                <PredictionCards hospitals={hospitals} predictions={predictions} />
              </div>
              <div className="fixed-footer">
                <p style={{ margin: 0, fontSize: '14px', color: '#666', textAlign: 'center' }}>Data updates automatically every few minutes</p>
              </div>
            </div>
          } />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;