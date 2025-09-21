import React, { useState, useEffect } from 'react';
import { Activity, Clock, TrendingUp, AlertCircle, Wifi, WifiOff } from 'lucide-react';

const RealTimeUpdates = ({ predictions, incidents }) => {
  const [updateHistory, setUpdateHistory] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    if (Object.keys(predictions).length > 0) {
      const newUpdate = {
        timestamp: new Date(),
        predictions: { ...predictions },
        type: 'prediction_update'
      };
      setUpdateHistory(prev => [newUpdate, ...prev.slice(0, 9)]); // Keep last 10 updates
    }
  }, [predictions]);

  const getAverageWaitTime = () => {
    const waitTimes = Object.values(predictions).map(p => p.current_wait_time || 0);
    return waitTimes.length > 0 ? Math.round(waitTimes.reduce((a, b) => a + b, 0) / waitTimes.length) : 0;
  };

  const getSystemStatus = () => {
    const avgWait = getAverageWaitTime();
    if (avgWait < 30) return { status: 'Good', color: '#10b981' };
    if (avgWait < 60) return { status: 'Moderate', color: '#f59e0b' };
    return { status: 'High Load', color: '#dc2626' };
  };

  const getTrendDirection = () => {
    if (updateHistory.length < 2) return 'stable';
    
    const current = getAverageWaitTime();
    const previous = updateHistory[1]?.predictions ? 
      Object.values(updateHistory[1].predictions).reduce((sum, p) => sum + (p.current_wait_time || 0), 0) / Object.keys(updateHistory[1].predictions).length : 0;
    
    if (current > previous + 5) return 'increasing';
    if (current < previous - 5) return 'decreasing';
    return 'stable';
  };

  const getTrendIcon = () => {
    const trend = getTrendDirection();
    switch (trend) {
      case 'increasing':
        return <TrendingUp size={16} style={{ color: '#dc2626' }} />;
      case 'decreasing':
        return <TrendingUp size={16} style={{ color: '#10b981', transform: 'rotate(180deg)' }} />;
      default:
        return <Activity size={16} style={{ color: '#6b7280' }} />;
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: true, 
      hour: 'numeric', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const systemStatus = getSystemStatus();
  const avgWait = getAverageWaitTime();
  const trend = getTrendDirection();

  return (
    <div className="card">
      <h3>
        <Activity size={20} />
        Real-time System Status
      </h3>
      
      <div style={{ display: 'grid', gap: '20px' }}>
        {/* System Overview */}
        <div style={{ 
          padding: '20px', 
          background: '#f5f5f5', 
          borderRadius: '8px',
          border: '1px solid #e5e5e5'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h4 style={{ margin: '0 0 4px 0', color: '#1a1a1a', fontSize: '16px', fontWeight: '600' }}>
                System Status
              </h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ 
                  width: '8px', 
                  height: '8px', 
                  borderRadius: '50%', 
                  background: systemStatus.color 
                }}></div>
                <span style={{ fontSize: '14px', color: '#666' }}>{systemStatus.status}</span>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#1a1a1a' }}>
                {avgWait}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>avg wait (min)</div>
            </div>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {getTrendIcon()}
              <span style={{ fontSize: '14px', color: '#666' }}>
                {trend === 'increasing' ? 'Increasing' : 
                 trend === 'decreasing' ? 'Decreasing' : 'Stable'}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#666' }}>
              {isOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
              {isOnline ? 'Online' : 'Offline'}
            </div>
          </div>
        </div>

        {/* Active Incidents */}
        {incidents.length > 0 && (
          <div style={{ 
            padding: '16px', 
            background: '#fef2f2', 
            borderRadius: '8px',
            border: '1px solid #fecaca'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <AlertCircle size={16} style={{ color: '#dc2626' }} />
              <h4 style={{ margin: '0', color: '#dc2626', fontSize: '14px', fontWeight: '600' }}>
                Active Incidents ({incidents.length})
              </h4>
            </div>
            <div style={{ display: 'grid', gap: '8px' }}>
              {incidents.map((incident, index) => (
                <div key={index} style={{ 
                  padding: '8px 12px', 
                  background: 'white', 
                  borderRadius: '4px',
                  border: '1px solid #fecaca',
                  fontSize: '12px'
                }}>
                  <div style={{ fontWeight: '600', color: '#1a1a1a', marginBottom: '2px' }}>
                    {incident.incident?.type || 'Unknown Incident'}
                  </div>
                  <div style={{ color: '#666' }}>
                    Impact on nearby hospitals
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Update History */}
        <div>
          <h4 style={{ margin: '0 0 12px 0', color: '#1a1a1a', fontSize: '14px', fontWeight: '600' }}>
            Recent Updates
          </h4>
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {updateHistory.length > 0 ? (
              <div style={{ display: 'grid', gap: '8px' }}>
                {updateHistory.slice(0, 5).map((update, index) => (
                  <div key={index} style={{ 
                    padding: '8px 12px', 
                    background: '#f5f5f5', 
                    borderRadius: '4px',
                    fontSize: '12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Clock size={12} style={{ color: '#666' }} />
                      <span style={{ color: '#666' }}>
                        {update.type === 'prediction_update' ? 'Predictions updated' : 'System update'}
                      </span>
                    </div>
                    <span style={{ color: '#666', fontSize: '11px' }}>
                      {formatTime(update.timestamp)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ 
                padding: '20px', 
                textAlign: 'center', 
                color: '#666',
                fontSize: '12px',
                background: '#f5f5f5',
                borderRadius: '4px'
              }}>
                No updates yet
              </div>
            )}
          </div>
        </div>

        {/* Last Update Time */}
        <div style={{ 
          padding: '12px', 
          background: '#f5f5f5', 
          borderRadius: '6px',
          textAlign: 'center',
          fontSize: '12px',
          color: '#666'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <Clock size={12} />
            <span>Last updated: {formatTime(lastUpdate)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeUpdates;