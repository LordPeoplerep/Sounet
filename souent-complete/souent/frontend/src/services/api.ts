/**
 * API Service Client
 * Handles all communication with the Souent backend
 */

import axios, { AxiosInstance } from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  UserPreferences,
  SystemStatus,
  Message
} from '../types';

class ApiService {
  private client: AxiosInstance;
  private apiKey?: string;

  constructor() {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set API key for authorization tier elevation
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  /**
   * Get authorization headers
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    return headers;
  }

  // ===== CHAT ENDPOINTS =====

  /**
   * Send a message to Souent
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      '/api/v1/chat/message',
      request,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  /**
   * Get conversation history
   */
  async getHistory(sessionId: string): Promise<Message[]> {
    const response = await this.client.get(`/api/v1/chat/history/${sessionId}`);
    return response.data.messages;
  }

  /**
   * Clear a session
   */
  async clearSession(sessionId: string): Promise<void> {
    await this.client.delete(`/api/v1/chat/session/${sessionId}`);
  }

  /**
   * Create a new session
   */
  async createNewSession(): Promise<{ session_id: string }> {
    const response = await this.client.post('/api/v1/chat/session/new');
    return response.data;
  }

  // ===== MEMORY ENDPOINTS =====

  /**
   * Get user preferences
   */
  async getPreferences(userId: string): Promise<UserPreferences> {
    const response = await this.client.get<UserPreferences>(
      `/api/v1/memory/preferences/${userId}`
    );
    return response.data;
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: UserPreferences): Promise<UserPreferences> {
    const response = await this.client.put<UserPreferences>(
      '/api/v1/memory/preferences',
      preferences
    );
    return response.data;
  }

  /**
   * Get canon memory info
   */
  async getCanonInfo(): Promise<any> {
    const response = await this.client.get('/api/v1/memory/canon/info');
    return response.data;
  }

  // ===== SYSTEM ENDPOINTS =====

  /**
   * Health check
   */
  async healthCheck(): Promise<SystemStatus> {
    const response = await this.client.get<SystemStatus>('/api/v1/system/health');
    return response.data;
  }

  /**
   * Get available models
   */
  async getModels(): Promise<any> {
    const response = await this.client.get('/api/v1/system/models');
    return response.data;
  }

  /**
   * Get system status
   */
  async getSystemStatus(): Promise<any> {
    const response = await this.client.get('/api/v1/system/status');
    return response.data;
  }

  /**
   * Get system capabilities
   */
  async getCapabilities(): Promise<any> {
    const response = await this.client.get('/api/v1/system/capabilities');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
