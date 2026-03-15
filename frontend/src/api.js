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

// ── Trip API ──

export async function createTrip(name = 'My Trip') {
  const res = await fetch(`${API_BASE}/wallets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
  if (!res.ok) throw new Error(`Create trip failed: ${res.status}`)
  return res.json()
}

export async function getTrip(tripId) {
  const res = await fetch(`${API_BASE}/wallets/${tripId}`)
  if (res.status === 404) return null
  if (!res.ok) throw new Error(`Get trip failed: ${res.status}`)
  return res.json()
}

export async function addFlightToTrip(tripId, flightData, addedBy = 'Anonymous', notes = '') {
  const res = await fetch(`${API_BASE}/wallets/${tripId}/flights`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flight_data: flightData, added_by: addedBy, notes }),
  })
  if (!res.ok) throw new Error(`Add flight failed: ${res.status}`)
  return res.json()
}

export async function removeFlightFromTrip(tripId, flightId) {
  const res = await fetch(`${API_BASE}/wallets/${tripId}/flights/${flightId}`, {
    method: 'DELETE',
  })
  if (!res.ok && res.status !== 204) throw new Error(`Remove flight failed: ${res.status}`)
}
