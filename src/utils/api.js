/**
 * OptiCode Backend A — API Integration Client
 * Connects to FastAPI on http://localhost:8000
 */

const API_BASE = 'http://localhost:8000';

// Default mock user ID for development bypass accepted by get_current_user_id()
const DEV_USER_ID = '11111111-2222-3333-4444-555555555555';

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-User-Id': DEV_USER_ID,
    'Authorization': `Bearer ${DEV_USER_ID}`,
  };
}

export const api = {
  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) throw new Error('Health check failed');
      return await res.json();
    } catch {
      return { status: 'offline', service: 'opticode-backend-a' };
    }
  },

  async listConversations() {
    try {
      const res = await fetch(`${API_BASE}/conversations?limit=20`, {
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error('Failed to fetch conversations');
      return await res.json();
    } catch (e) {
      console.warn('Backend unavailable, using local memory state', e);
      return null;
    }
  },

  async createConversation(title) {
    try {
      const res = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ title }),
      });
      if (!res.ok) throw new Error('Failed to create conversation');
      return await res.json();
    } catch (e) {
      console.warn('Backend unavailable, creating local session', e);
      return {
        id: crypto.randomUUID(),
        title,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
  },

  async deleteConversation(conversationId) {
    try {
      const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: getHeaders(),
      });
      return res.ok;
    } catch (e) {
      console.warn('Backend delete failed', e);
      return true;
    }
  },

  async listMessages(conversationId) {
    try {
      const res = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error('Failed to fetch messages');
      return await res.json();
    } catch (e) {
      console.warn('Backend messages unavailable', e);
      return null;
    }
  },

  async createMessage(conversationId, { role = 'user', content, metadata = {} }) {
    try {
      const res = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ role, content, metadata }),
      });
      if (!res.ok) throw new Error('Failed to send message');
      return await res.json();
    } catch (e) {
      console.warn('Backend message save unavailable', e);
      return {
        id: crypto.randomUUID(),
        conversation_id: conversationId,
        role,
        content,
        metadata,
        created_at: new Date().toISOString(),
      };
    }
  },
};
