/**
 * MessageList Component
 * Renders the list of chat messages
 */

import React from 'react';
import type { Message } from '../types';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} />
      ))}
    </div>
  );
};

export default MessageList;
