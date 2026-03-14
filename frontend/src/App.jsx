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

function derivePlans(latestFlights) {
  if (!Array.isArray(latestFlights)) return []

  return latestFlights.slice(0, 5).map((flight, index) => {
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
      id: `${origin || 'origin'}-${destination || 'dest'}-${index}`,
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

  return (
    <div className="flex flex-col min-h-screen bg-[#F7F5EF]">
      <header className="bg-[#F7F5EF] border-b border-[#D6C6A8]/60 px-6 py-4">
        <div className="max-w-5xl mx-auto flex flex-col gap-1">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold text-[#111111]">
                ✈️ Traveling Salesmen
              </h1>
              <p className="text-sm text-[#777777]">
                Tell me about your ideal trip and we&apos;ll map the best routes.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-flex items-center rounded-full border border-[#D6C6A8] bg-[#FFFFFF] px-3 py-1 text-xs font-medium text-[#9C8A6A]">
                Trip planner preview
              </span>
              <button
                type="button"
                onClick={loadDemoTrip}
                className="inline-flex items-center rounded-full bg-[#9C8A6A] px-3 py-1 text-xs font-semibold text-white shadow-sm hover:shadow-md transition-shadow"
              >
                Load sample trip
              </button>
              <button
                type="button"
                onClick={loadGlobalDemo}
                className="inline-flex items-center rounded-full bg-[#9C8A6A] px-3 py-1 text-xs font-semibold text-white shadow-sm hover:shadow-md transition-shadow"
              >
                Load global demo
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto w-full px-4 py-4 space-y-6">
          <section className="bg-white rounded-2xl shadow-sm border border-[#E5E0D2]">
            <div className="p-4 sm:p-5">
              <ChatWindow
                sessionId={sessionId}
                setSessionId={setSessionId}
                onConversationUpdate={handleConversationUpdate}
              />
            </div>
          </section>

          <TripPlannerLayout
            requirements={requirements}
            regionSummary={regionSummary}
            plans={plans}
            selectedPlan={selectedPlan}
            onSelectPlan={setSelectedPlanId}
          />
        </div>
      </main>
    </div>
  )
}

export default App
