import { useState } from 'react'
import ChatWindow from './components/ChatWindow'

function App() {
  const [sessionId, setSessionId] = useState(null)

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-800">✈️ Flight Concierge</h1>
        <p className="text-sm text-gray-500">Tell me where you want to fly</p>
      </header>
      <main className="flex-1 overflow-hidden">
        <ChatWindow sessionId={sessionId} setSessionId={setSessionId} />
      </main>
    </div>
  )
}

export default App
