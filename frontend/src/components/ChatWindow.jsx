import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api'
import MessageBubble from './MessageBubble'
import FlightCard from './FlightCard'

function ChatWindow({ sessionId, setSessionId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')

    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const data = await sendMessage(sessionId, userMessage)
      setSessionId(data.session_id)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          flights: data.flights,
        },
      ])
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-lg">👋 Hi! Tell me about your trip.</p>
            <p className="text-sm mt-2">
              Try: &quot;Fly from NYC to somewhere warm in late June, under $400&quot;
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i}>
            <MessageBubble role={msg.role} content={msg.content} />
            {msg.flights && msg.flights.length > 0 && (
              <div className="mt-2 space-y-2 ml-2">
                {msg.flights.map((flight, j) => (
                  <FlightCard key={j} flight={flight} rank={j + 1} />
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2 text-gray-400 ml-2">
            <div className="animate-pulse">Searching flights...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4">
        <div className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Where do you want to fly?"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatWindow
