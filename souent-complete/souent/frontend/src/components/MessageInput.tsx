/**
 * MessageInput Component
 * Text input for user messages
 */

import React, { useState, useRef, KeyboardEvent } from 'react';
import { useChatStore } from '../stores/chatStore';

interface MessageInputProps {
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ disabled = false }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { sendMessage } = useChatStore();

  const handleSubmit = async () => {
    if (!input.trim() || disabled) return;

    const message = input.trim();
    setInput('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    await sendMessage(message);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  return (
    <div className="message-input-container">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask Souent anything..."
          disabled={disabled}
          className="message-textarea"
          rows={1}
        />
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || disabled}
          className="send-button"
          title="Send message"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      <div className="input-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
};

export default MessageInput;
