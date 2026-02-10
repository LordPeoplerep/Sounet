/**
 * Zustand Store for Chat State Management
 */

import { create } from 'zustand';
import type { Message, UserPreferences } from '../types';
import { apiService } from '../services/api';

interface ChatState {
  // State
  messages: Message[];
  sessionId: string | null;
  userId: string | null;
  isLoading: boolean;
  error: string | null;
  preferences: UserPreferences | null;
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  clearConversation: () => Promise<void>;
  startNewSession: () => Promise<void>;
  loadPreferences: (userId: string) => Promise<void>;
  updatePreferences: (preferences: UserPreferences) => Promise<void>;
  setUserId: (userId: string) => void;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  sessionId: null,
  userId: null,
  isLoading: false,
  error: null,
  preferences: null,

  // Send a message to Souent
  sendMessage: async (content: string) => {
    const { sessionId, userId, preferences } = get();
    
    set({ isLoading: true, error: null });

    try {
      // Add user message to UI immediately
      const userMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, userMessage],
      }));

      // Send to API
      const response = await apiService.sendMessage({
        message: content,
        session_id: sessionId || undefined,
        user_id: userId || undefined,
        authorization_tier: 'basic',
      });

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        metadata: response.metadata,
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        sessionId: response.session_id,
        isLoading: false,
      }));
    } catch (error: any) {
      console.error('Error sending message:', error);
      set({
        error: error.response?.data?.detail || 'Failed to send message',
        isLoading: false,
      });
    }
  },

  // Clear current conversation
  clearConversation: async () => {
    const { sessionId } = get();
    
    if (sessionId) {
      try {
        await apiService.clearSession(sessionId);
      } catch (error) {
        console.error('Error clearing session:', error);
      }
    }

    set({
      messages: [],
      sessionId: null,
      error: null,
    });
  },

  // Start a new session
  startNewSession: async () => {
    try {
      const response = await apiService.createNewSession();
      set({
        messages: [],
        sessionId: response.session_id,
        error: null,
      });
    } catch (error: any) {
      console.error('Error creating new session:', error);
      set({
        error: error.response?.data?.detail || 'Failed to create new session',
      });
    }
  },

  // Load user preferences
  loadPreferences: async (userId: string) => {
    try {
      const preferences = await apiService.getPreferences(userId);
      set({ preferences, userId });
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  },

  // Update user preferences
  updatePreferences: async (preferences: UserPreferences) => {
    try {
      const updated = await apiService.updatePreferences(preferences);
      set({ preferences: updated });
    } catch (error) {
      console.error('Error updating preferences:', error);
      set({ error: 'Failed to update preferences' });
    }
  },

  // Set user ID
  setUserId: (userId: string) => {
    set({ userId });
  },

  // Set error
  setError: (error: string | null) => {
    set({ error });
  },
}));
