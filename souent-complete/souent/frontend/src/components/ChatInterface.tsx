/**
 * ChatInterface Component
 * Main chat UI with messages and input
 */

import React, { useEffect, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatInterface: React.FC = () => {
  const { messages, isLoading, error } = useChatStore();
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-interface">
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠</span>
          <span className="error-text">{error}</span>
        </div>
      )}
      
      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-content">
              <div className="welcome-icon">S</div>
              <h2 className="welcome-title">Welcome to Souent</h2>
              <p className="welcome-subtitle">
                Powered by Anthroi-1 (SLM-A1) - Logic-First Reasoning
              </p>
              <div className="welcome-features">
                <div className="feature-item">
                  <span className="feature-icon">⚡</span>
                  <span>Conservative inference</span>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">🎯</span>
                  <span>Explicit uncertainty handling</span>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">🔒</span>
                  <span>No emotional simulation</span>
                </div>
              </div>
              <p className="welcome-prompt">Ask me anything to get started</p>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
        
        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="loading-text">Souent is thinking...</span>
          </div>
        )}
      </div>
      
      <MessageInput disabled={isLoading} />
    </div>
  );
};

export default ChatInterface;
