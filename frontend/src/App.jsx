import { useCallback, useMemo, useState } from 'react'
import ChatWindow from './components/ChatWindow'
import TripPlannerLayout from './components/TripPlannerLayout'

const EMPTY_REQUIREMENTS = {
  origin: undefined,
  destination: undefined,
  origin_airports: undefined,
  destination_airports: undefined,
  dates: undefined,
  budget: undefined,
  preference: undefined,
}

function mergeRequirements(prev, incoming) {
  if (!incoming) return prev
  const merged = { ...prev }
  if (incoming.origin) merged.origin = incoming.origin
  if (incoming.destination) merged.destination = incoming.destination
  if (incoming.origin_airports?.length) merged.origin_airports = incoming.origin_airports
  if (incoming.destination_airports?.length) merged.destination_airports = incoming.destination_airports
  if (incoming.departure_dates) merged.dates = incoming.departure_dates
  if (incoming.budget) merged.budget = incoming.budget
  if (incoming.preference) merged.preference = incoming.preference
  if (incoming.cabin_class) merged.cabin_class = incoming.cabin_class
  if (incoming.passengers) merged.passengers = incoming.passengers
  if (incoming.return_dates) merged.return_dates = incoming.return_dates
  return merged
}

const PLAN_LIST_CAP = 10

function getPlanIdFromFlight(flight, index) {
  const segments = flight?.outbound_segments || []
  const firstSeg = segments[0]
  const lastSeg = segments[segments.length - 1]
  const origin = firstSeg?.departure_airport || 'origin'
  const destination = lastSeg?.arrival_airport || 'dest'
  return `${origin}-${destination}-${index}`
}

function derivePlans(latestFlights) {
  if (!Array.isArray(latestFlights)) return []

  return latestFlights.slice(0, PLAN_LIST_CAP).map((flight, index) => {
    const segments = flight.outbound_segments || []
    const firstSeg = segments[0]
    const lastSeg = segments[segments.length - 1]
    const origin = firstSeg?.departure_airport
    const destination = lastSeg?.arrival_airport

    const waypoints = segments.map(s => s.departure_airport).filter(Boolean)
    if (lastSeg?.arrival_airport) waypoints.push(lastSeg.arrival_airport)

    let tagline = 'Solid option'
    if (index === 0) {
      tagline = 'Best overall pick'
    } else if (flight.stops === 0) {
      tagline = 'Fast, direct route'
    } else if (flight.price) {
      tagline = 'Great value for this route'
    }

    return {
      id: getPlanIdFromFlight(flight, index),
      rank: index + 1,
      price: flight.price,
      score: flight.score,
      airline: flight.airline,
      origin,
      destination,
      waypoints,
      stops: flight.stops,
      durationMinutes: flight.total_duration_minutes,
      departureTime: firstSeg?.departure_time,
      arrivalTime: lastSeg?.arrival_time,
      tagline,
    }
  })
}

function deriveRegionSummary(requirements, plans) {
  const firstPlan = plans[0]
  const originLabel = firstPlan?.origin || requirements.origin || 'Origin'
  const destinationLabel = firstPlan?.destination || requirements.destination || 'Destination'

  const allAirports = new Set()
  for (const p of plans) {
    if (p.waypoints) {
      for (const code of p.waypoints) {
        if (code && code !== p.origin) allAirports.add(code)
      }
    } else if (p.destination) {
      allAirports.add(p.destination)
    }
  }

  return {
    originLabel,
    destinationLabel,
    cityNodes: Array.from(allAirports),
  }
}

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [requirements, setRequirements] = useState(EMPTY_REQUIREMENTS)
  const [latestFlights, setLatestFlights] = useState([])
  const [selectedPlanId, setSelectedPlanId] = useState(null)
  const [chatOpen, setChatOpen] = useState(true)

  const loadDemoTrip = () => {
    const demoFlights = [
      {
        airline: 'Demo Air',
        price: 365,
        score: 0.18,
        total_duration_minutes: 320,
        stops: 0,
        outbound_segments: [
          {
            departure_airport: 'JFK',
            arrival_airport: 'MIA',
            departure_time: '08:20',
            arrival_time: '13:40',
          },
        ],
      },
      {
        airline: 'Sunline',
        price: 340,
        score: 0.26,
        total_duration_minutes: 410,
        stops: 1,
        outbound_segments: [
          {
            departure_airport: 'JFK',
            arrival_airport: 'TPA',
            departure_time: '09:15',
            arrival_time: '15:05',
          },
        ],
      },
      {
        airline: 'Coastal',
        price: 385,
        score: 0.31,
        total_duration_minutes: 295,
        stops: 0,
        outbound_segments: [
          {
            departure_airport: 'LGA',
            arrival_airport: 'FLL',
            departure_time: '11:05',
            arrival_time: '15:00',
          },
        ],
      },
      {
        airline: 'Island Hop',
        price: 310,
        score: 0.38,
        total_duration_minutes: 460,
        stops: 1,
        outbound_segments: [
          {
            departure_airport: 'JFK',
            arrival_airport: 'SJU',
            departure_time: '17:45',
            arrival_time: '23:20',
          },
        ],
      },
    ]

    setRequirements({
      origin: 'New York City',
      destination: 'Miami / Caribbean',
      origin_airports: ['JFK', 'LGA'],
      destination_airports: ['MIA', 'TPA', 'FLL', 'SJU'],
      dates: 'late June',
      budget: 'under $400',
      preference: 'balanced',
    })
    setLatestFlights(demoFlights)
  }

  const loadGlobalDemo = () => {
    const demoFlights = [
      {
        airline: 'Pacific Wings',
        price: 820,
        score: 0.15,
        total_duration_minutes: 690,
        stops: 0,
        outbound_segments: [
          {
            departure_airport: 'LAX',
            arrival_airport: 'NRT',
            departure_time: '11:30',
            arrival_time: '15:00+1',
          },
        ],
      },
      {
        airline: 'Orient Express Air',
        price: 780,
        score: 0.22,
        total_duration_minutes: 740,
        stops: 1,
        outbound_segments: [
          {
            departure_airport: 'LAX',
            arrival_airport: 'ICN',
            departure_time: '01:15',
            arrival_time: '05:40+1',
          },
          {
            departure_airport: 'ICN',
            arrival_airport: 'PVG',
            departure_time: '07:10+1',
            arrival_time: '08:35+1',
          },
        ],
      },
      {
        airline: 'Southern Cross',
        price: 870,
        score: 0.28,
        total_duration_minutes: 780,
        stops: 1,
        outbound_segments: [
          {
            departure_airport: 'LAX',
            arrival_airport: 'DFW',
            departure_time: '22:45',
            arrival_time: '04:10+1',
          },
          {
            departure_airport: 'DFW',
            arrival_airport: 'EZE',
            departure_time: '06:00+1',
            arrival_time: '17:45+1',
          },
        ],
      },
    ]

    setRequirements({
      origin: 'Los Angeles',
      destination: 'Tokyo / Shanghai / Buenos Aires',
      origin_airports: ['LAX'],
      destination_airports: ['NRT', 'PVG', 'EZE'],
      dates: 'mid August',
      budget: 'under $900',
      preference: 'balanced',
    })
    setLatestFlights(demoFlights)
  }

  const handleConversationUpdate = useCallback(({ flights, parsedIntent }) => {
    setRequirements(prev => mergeRequirements(prev, parsedIntent))
    setLatestFlights(flights ?? [])
  }, [])

  const plans = useMemo(
    () => derivePlans(latestFlights),
    [latestFlights],
  )

  const selectedPlan = useMemo(
    () => plans.find(p => p.id === selectedPlanId) || null,
    [plans, selectedPlanId],
  )

  const regionSummary = useMemo(
    () => deriveRegionSummary(requirements, plans),
    [requirements, plans],
  )

  const [barInput, setBarInput] = useState('')
  const [pendingMessage, setPendingMessage] = useState(null)

  const handleBarSubmit = (e) => {
    e.preventDefault()
    if (!barInput.trim()) return
    setPendingMessage(barInput.trim())
    setBarInput('')
    setChatOpen(true)
  }

  return (
    <div className="flex h-full min-h-0 bg-[#F7F5EF]">
      {/* Left side: header + trip planner */}
      <div className={`flex-1 flex flex-col min-h-0 overflow-hidden ${chatOpen ? 'hidden md:flex' : 'flex'}`}>
        <div className="px-6 pt-4 pb-2 shrink-0">
          <div className="flex items-center justify-between gap-3">
            <h1 className="text-lg font-semibold text-[#111111] tracking-tight">
              Traveling Salesman
            </h1>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={loadDemoTrip}
                className="inline-flex items-center rounded-full bg-[#9C8A6A]/10 text-[#9C8A6A] px-3 py-1 text-xs font-medium hover:bg-[#9C8A6A]/20 transition-colors"
              >
                Sample trip
              </button>
              <button
                type="button"
                onClick={loadGlobalDemo}
                className="inline-flex items-center rounded-full bg-[#9C8A6A]/10 text-[#9C8A6A] px-3 py-1 text-xs font-medium hover:bg-[#9C8A6A]/20 transition-colors"
              >
                Global demo
              </button>
            </div>
          </div>
        </div>
        <div className={`flex-1 overflow-y-auto ${chatOpen ? 'pb-4' : 'pb-20'}`}>
          <div className="max-w-5xl mx-auto w-full px-4 py-2 space-y-5">
            <TripPlannerLayout
              requirements={requirements}
              regionSummary={regionSummary}
              plans={plans}
              selectedPlan={selectedPlan}
              onSelectPlan={setSelectedPlanId}
            />
          </div>
        </div>
      </div>

      {/* Right side: chat panel — always mounted, hidden via CSS when closed */}
      <div className={`
        ${chatOpen ? 'flex' : 'hidden'}
        w-full md:w-1/2 lg:w-[45%]
        flex-col bg-white shrink-0 min-h-0 overflow-hidden
        md:rounded-l-2xl md:shadow-[-8px_0_30px_-12px_rgba(0,0,0,0.12)]
      `}>
        {/* Mobile header */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 bg-white/80 backdrop-blur-sm">
          <button
            type="button"
            onClick={() => setChatOpen(false)}
            className="text-[#9C8A6A] hover:text-[#111111] transition-colors text-sm font-medium"
          >
            &larr; Back
          </button>
          <span className="text-sm font-semibold text-[#111111]">Chat</span>
        </div>
        {/* Desktop header */}
        <div className="hidden md:flex items-center justify-between px-5 py-3">
          <span className="text-sm font-semibold text-[#111111]">Traveling Salesman</span>
          <button
            type="button"
            onClick={() => setChatOpen(false)}
            className="w-6 h-6 flex items-center justify-center rounded-full bg-[#F7F5EF] text-[#9C8A6A] hover:bg-[#E5E0D2] transition-colors text-xs"
          >
            &times;
          </button>
        </div>
        <div className="flex-1 min-h-0 flex flex-col">
          <ChatWindow
            sessionId={sessionId}
            setSessionId={setSessionId}
            onConversationUpdate={handleConversationUpdate}
            pendingMessage={pendingMessage}
            clearPendingMessage={() => setPendingMessage(null)}
          />
        </div>
      </div>

      {/* Bottom bar: inline input with chat icon + submit — visible when chat is closed */}
      {!chatOpen && (
        <div className="fixed bottom-0 inset-x-0 z-50 px-4 pt-2 pb-[max(1rem,env(safe-area-inset-bottom))] bg-gradient-to-t from-[#F7F5EF] via-[#F7F5EF] to-transparent">
          <form
            onSubmit={handleBarSubmit}
            className="max-w-xl mx-auto flex items-center gap-2 bg-white rounded-full shadow-lg border border-[#D6C6A8]/50 px-2 py-1.5"
          >
            <button
              type="button"
              onClick={() => setChatOpen(true)}
              className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full bg-[#9C8A6A] text-white hover:bg-[#8A7A5E] transition-colors"
              aria-label="Open chat"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </button>
            <input
              type="text"
              value={barInput}
              onChange={(e) => setBarInput(e.target.value)}
              placeholder="Ask about flights..."
              className="flex-1 bg-transparent text-sm text-[#111111] placeholder-[#B0A795] px-2 py-1.5 focus:outline-none"
            />
            <button
              type="submit"
              disabled={!barInput.trim()}
              className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full bg-[#9C8A6A] text-white hover:bg-[#8A7A5E] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="Send"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default App
