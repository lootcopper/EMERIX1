import React, { useState } from 'react';
import { MapPin, Search, Navigation, Globe } from 'lucide-react';

const LocationInput = ({ onLocationSet, userLocation, setUserLocation }) => {
  const [locationInput, setLocationInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!locationInput.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5001/api/location', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ location: locationInput.trim() }),
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        onLocationSet(data);
      } else {
        alert(data.error || 'Failed to set location');
      }
    } catch (err) {
      console.error('Error setting location:', err);
      alert('Failed to set location');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      setIsLoading(true);
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            const response = await fetch('http://localhost:5001/api/location', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ location: `${latitude}, ${longitude}` }),
            });
            const data = await response.json();
            
            if (data.status === 'success') {
              onLocationSet(data);
            } else {
              alert(data.error || 'Failed to set location');
            }
          } catch (err) {
            console.error('Error setting location:', err);
            alert('Failed to set location');
          } finally {
            setIsLoading(false);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your current location. Please enter a location manually.');
          setIsLoading(false);
        }
      );
    } else {
      alert('Geolocation is not supported by this browser.');
    }
  };

  return (
    <div className="location-input-container">
      <form onSubmit={handleSubmit} className="location-form">
        <div className="input-group" style={{ justifyContent: 'center' }}>
          <div className="input-wrapper">
            <Globe className="input-icon" size={20} />
            <input
              type="text"
              value={locationInput}
              onChange={(e) => setLocationInput(e.target.value)}
              placeholder="Enter city, address, or coords"
              className="location-input"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !locationInput.trim()}
            className="search-button"
          >
            {isLoading ? (
              <>
                <div className="spinning">⏳</div>
                Searching...
              </>
            ) : (
              <>
                <Search size={20} />
                Search Hospitals
              </>
            )}
          </button>
        </div>
        <div className="centered-location-row">
          <button
            type="button"
            onClick={handleGetCurrentLocation}
            disabled={isLoading}
            className="current-location-button"
          >
            <Navigation size={16} />
            Use My Current Location
          </button>
        </div>
      </form>
    </div>
  );
};

export default LocationInput;