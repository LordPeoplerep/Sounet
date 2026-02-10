/**
 * StatusBar Component
 * Displays connection status and model information
 */

import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import type { SystemStatus } from '../types';

const StatusBar: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiService.healthCheck();
        setStatus(health);
        setIsOnline(true);
      } catch (error) {
        console.error('Health check failed:', error);
        setIsOnline(false);
      }
    };

    // Initial check
    checkHealth();

    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-bar">
      <div className="status-content">
        <div className="status-indicator">
          <span className={`status-dot ${isOnline ? 'online' : 'offline'}`}></span>
          <span className="status-text">
            {isOnline ? 'Connected' : 'Offline'}
          </span>
        </div>
        
        {status && (
          <>
            <div className="status-divider"></div>
            <div className="status-info">
              <span className="info-label">Model:</span>
              <span className="info-value">SLM-A1 (Anthroi-1)</span>
            </div>
            
            <div className="status-divider"></div>
            <div className="status-info">
              <span className="info-label">Version:</span>
              <span className="info-value">{status.version}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default StatusBar;
