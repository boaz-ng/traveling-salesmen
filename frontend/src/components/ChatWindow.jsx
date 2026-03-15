import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api'
import MessageBubble from './MessageBubble'

function ChatWindow({
  sessionId,
  setSessionId,
  onConversationUpdate,
  pendingMessage,
  clearPendingMessage,
  originMissing,
  showLocationPrompt,
  onRequestLocation,
}) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const sentPendingRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const doSend = async (text) => {
    if (!text) return
    const userMessage = text.trim()
    if (!userMessage) return

    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const data = await sendMessage(sessionId, userMessage, originMissing)
      setSessionId(data.session_id)

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        flights: data.flights,
      }

      setMessages(prev => [...prev, assistantMessage])

      if (onConversationUpdate) {
        onConversationUpdate({
          userMessage,
          assistantMessage,
          flights: data.flights ?? [],
          hotels: data.hotels ?? [],
          parsedIntent: data.parsed_intent ?? null,
        })
      }
    } catch (err) {
      const message = err?.message && err.message !== 'Failed to fetch'
        ? err.message
        : 'Sorry, something went wrong. Please try again.'
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: message },
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (pendingMessage && pendingMessage !== sentPendingRef.current) {
      sentPendingRef.current = pendingMessage
      clearPendingMessage()
      doSend(pendingMessage)
    }
  }, [pendingMessage])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const text = input.trim()
    setInput('')
    doSend(text)
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[200px]">
        {messages.length === 0 && (
          <div className="text-center mt-12 md:mt-16 px-2">
            <p className="text-xl font-semibold text-[#111111]">
              {showLocationPrompt ? 'Where are you flying from?' : 'Tell me about your trip.'}
            </p>
            <p className="text-sm mt-3 text-[#555555] max-w-sm mx-auto">
              {showLocationPrompt
                ? 'Share your location or tell me your city (e.g. NYC, San Francisco).'
                : 'Try: "Fly from NYC to somewhere warm in late June, under $400"'}
            </p>
            {showLocationPrompt && onRequestLocation && (
              <button
                type="button"
                onClick={onRequestLocation}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#9C8A6A] text-white text-sm font-medium hover:bg-[#8A7A5E] transition-colors"
              >
                Use my location for &quot;From&quot;
              </button>
            )}
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i}>
            <MessageBubble role={msg.role} content={msg.content} />
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2 text-[#9C8A6A] ml-2">
            <div className="animate-pulse">Searching flights...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="bg-white px-4 py-3 shrink-0">
        <div className="flex items-center gap-2 bg-[#F7F5EF] rounded-full px-3 py-1.5">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Where do you want to fly?"
            className="flex-1 bg-transparent text-sm text-[#111111] placeholder-[#B0A795] px-1 py-1.5 focus:outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-[#9C8A6A] text-white hover:bg-[#8A7A5E] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatWindow
