/**
 * MessageBubble Component
 * Individual message display with role-based styling
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message } from '../types';
import { formatTimestamp } from '../utils/format';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-bubble ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-role">
          {isUser ? 'You' : 'Souent'}
        </span>
        <span className="message-time">
          {formatTimestamp(message.timestamp)}
        </span>
      </div>
      
      <div className="message-content">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>
      
      {!isUser && message.metadata?.authorization_tier && (
        <div className="message-metadata">
          <span className="metadata-badge">
            {message.metadata.authorization_tier}
          </span>
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
