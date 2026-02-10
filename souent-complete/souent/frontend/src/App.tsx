/**
 * Main App Component
 */

import React, { useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import StatusBar from './components/StatusBar';
import { useChatStore } from './stores/chatStore';

const App: React.FC = () => {
  const { startNewSession } = useChatStore();

  useEffect(() => {
    // Initialize session on mount
    startNewSession();
  }, []);

  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        <ChatInterface />
      </main>
      <StatusBar />
    </div>
  );
};

export default App;
