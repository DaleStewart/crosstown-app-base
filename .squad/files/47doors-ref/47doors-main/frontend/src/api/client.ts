/**
 * API client for the Front Door Support Agent.
 */

import type {
  BrandingResponse,
  BrandingUpdateRequest,
  ChatRequest,
  ChatResponse,
  HealthStatus,
  KnowledgeSearchResponse,
  TicketListResponse,
  TicketStatusResponse,
  TicketUpdateRequest,
  ApiError,
  Department,
} from '../types';
import type { RealtimeSessionResponse } from '../types/voice';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10);

/**
 * Custom error class for API errors.
 */
export class ApiClientError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

/**
 * Make an API request with timeout and error handling.
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorData: ApiError;
      try {
        errorData = await response.json();
      } catch {
        errorData = {
          error: 'unknown_error',
          message: `Request failed with status ${response.status}`,
        };
      }
      throw new ApiClientError(
        errorData.message,
        response.status,
        errorData.details
      );
    }

    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiClientError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new ApiClientError('Request timed out', 408);
      }
      throw new ApiClientError(error.message, 0);
    }

    throw new ApiClientError('An unexpected error occurred', 0);
  }
}

// =============================================================================
// Chat API
// =============================================================================

/**
 * Submit a support query to the chat endpoint.
 */
export async function submitQuery(
  message: string,
  sessionId: string | null
): Promise<ChatResponse> {
  const body: ChatRequest = {
    message,
    session_id: sessionId,
  };

  return request<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

// =============================================================================
// Ticket API
// =============================================================================

/**
 * Get the status of a specific ticket.
 */
export async function getTicketStatus(
  ticketId: string
): Promise<TicketStatusResponse> {
  return request<TicketStatusResponse>(`/tickets/${encodeURIComponent(ticketId)}`);
}

/**
 * List tickets for the current user.
 */
export async function listUserTickets(
  status?: string,
  limit: number = 10
): Promise<TicketListResponse> {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  params.set('limit', limit.toString());

  return request<TicketListResponse>(`/tickets?${params.toString()}`);
}

// =============================================================================
// Knowledge Base API
// =============================================================================

/**
 * Search the knowledge base.
 */
export async function searchKnowledge(
  query: string,
  department?: Department,
  limit: number = 3
): Promise<KnowledgeSearchResponse> {
  const params = new URLSearchParams();
  params.set('q', query);
  if (department) params.set('department', department);
  params.set('limit', limit.toString());

  return request<KnowledgeSearchResponse>(`/knowledge/search?${params.toString()}`);
}

// =============================================================================
// Health API
// =============================================================================

/**
 * Check system health.
 */
export async function getHealthStatus(): Promise<HealthStatus> {
  return request<HealthStatus>('/health');
}

// =============================================================================
// Admin API
// =============================================================================

/**
 * List all tickets for admin view.
 */
export async function adminListAllTickets(
  status?: string,
  department?: Department,
  limit: number = 50
): Promise<TicketListResponse> {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (department) params.set('department', department);
  params.set('limit', limit.toString());

  return request<TicketListResponse>(`/admin/tickets?${params.toString()}`);
}

/**
 * Update a ticket's status (admin action).
 */
export async function adminUpdateTicket(
  ticketId: string,
  update: TicketUpdateRequest
): Promise<TicketStatusResponse> {
  return request<TicketStatusResponse>(`/admin/tickets/${encodeURIComponent(ticketId)}`, {
    method: 'PATCH',
    body: JSON.stringify(update),
  });
}

/**
 * Delete a ticket (admin action).
 */
export async function adminDeleteTicket(
  ticketId: string
): Promise<{ message: string }> {
  return request<{ message: string }>(`/admin/tickets/${encodeURIComponent(ticketId)}`, {
    method: 'DELETE',
  });
}

// =============================================================================
// Branding API
// =============================================================================

/**
 * Get current branding configuration.
 */
export async function getBranding(): Promise<BrandingResponse> {
  return request<BrandingResponse>('/admin/branding');
}

/**
 * Update branding configuration.
 */
export async function updateBranding(
  update: BrandingUpdateRequest
): Promise<BrandingResponse> {
  return request<BrandingResponse>('/admin/branding', {
    method: 'PUT',
    body: JSON.stringify(update),
  });
}

// =============================================================================
// Voice Realtime API
// =============================================================================

/**
 * Create a realtime voice session with an ephemeral token.
 * POST /api/realtime/session
 */
export async function createRealtimeSession(
  options: { sessionId?: string; voice?: string; instructions?: string } = {}
): Promise<RealtimeSessionResponse> {
  return request<RealtimeSessionResponse>('/realtime/session', {
    method: 'POST',
    body: JSON.stringify({
      session_id: options.sessionId,
      voice: options.voice ?? 'marin',
      instructions: options.instructions,
    }),
  });
}

/** Error thrown when voice realtime API is unavailable. */
export class VoiceUnavailableError extends Error {
  constructor(message = 'Voice realtime API is unavailable') {
    super(message);
    this.name = 'VoiceUnavailableError';
  }
}
