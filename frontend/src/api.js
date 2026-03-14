const API_BASE = '';

/**
 * Send a chat message to the backend.
 * @param {string} sessionId - The session ID (or null for new session)
 * @param {string} message - The user's message
 * @returns {Promise<{session_id: string, response: string, flights: Array|null}>}
 */
export async function sendMessage(sessionId, message) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
