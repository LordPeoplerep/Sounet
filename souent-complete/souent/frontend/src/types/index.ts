/**
 * TypeScript type definitions for Souent
 */

export type MessageRole = 'user' | 'assistant' | 'system';

export type AuthorizationTier = 'basic' | 'advisory' | 'admin_ready';

export interface Message {
  role: MessageRole;
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: string;
  authorization_tier?: AuthorizationTier;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  model: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface UserPreferences {
  user_id: string;
  tone_preference: 'concise' | 'balanced' | 'detailed';
  max_response_length: number;
  enable_clarification_questions: boolean;
  custom_settings?: Record<string, any>;
  updated_at: string;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'offline';
  app_name: string;
  version: string;
  model: string;
  memory_storage: string;
  uptime_seconds: number;
  timestamp: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  timestamp: string;
}
