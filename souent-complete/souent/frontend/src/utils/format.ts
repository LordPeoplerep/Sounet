/**
 * Utility Functions
 */

import { format, formatDistanceToNow } from 'date-fns';

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    
    // If less than 24 hours ago, show relative time
    if (diffMs < 24 * 60 * 60 * 1000) {
      return formatDistanceToNow(date, { addSuffix: true });
    }
    
    // Otherwise show formatted date and time
    return format(date, 'MMM d, h:mm a');
  } catch (error) {
    return '';
  }
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Generate a unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}
