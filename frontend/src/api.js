const API_BASE = '';

/**
 * Send a chat message to the backend.
 * @param {string} sessionId - The session ID (or null for new session)
 * @param {string} message - The user's message
 * @param {boolean} [originMissing] - True if the user has not yet provided a departure city
 * @returns {Promise<{session_id: string, response: string, flights: Array|null}>}
 */
export async function sendMessage(sessionId, message, originMissing) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      ...(originMissing === true && { origin_missing: true }),
    }),
  });

  if (!response.ok) {
    let detail = `API error: ${response.status}`
    try {
      const body = await response.json()
      if (body.detail) {
        detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      // ignore
    }
    const err = new Error(detail)
    err.status = response.status
    throw err
  }

  return response.json();
}
