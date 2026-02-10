/**
 * Header Component
 * Displays the Souent branding and basic controls
 */

import React from 'react';
import { useChatStore } from '../stores/chatStore';

const Header: React.FC = () => {
  const { clearConversation } = useChatStore();

  const handleNewChat = async () => {
    if (window.confirm('Start a new conversation? Current conversation will be cleared.')) {
      await clearConversation();
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-brand">
          <div className="logo-container">
            <div className="logo-icon">S</div>
          </div>
          <div className="brand-text">
            <h1 className="app-title">Souent</h1>
            <p className="app-subtitle">VelaPlex Systems</p>
          </div>
        </div>
        
        <div className="header-actions">
          <button 
            onClick={handleNewChat}
            className="btn-secondary"
            title="Start new conversation"
          >
            New Chat
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
