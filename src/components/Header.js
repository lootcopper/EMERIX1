import React from 'react';
import { Activity, MapPin, Clock } from 'lucide-react';

const Header = () => {
  return (
    <div className="header">
      <h1>
        <Activity size={40} style={{ marginRight: '10px', verticalAlign: 'middle' }} />
        ER Wait Time Predictor
      </h1>
      <p>
        <MapPin size={20} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
        Real-time emergency room wait time predictions
      </p>
      <div style={{ marginTop: '10px', fontSize: '0.9em', opacity: 0.8 }}>
        <Clock size={16} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default Header;
