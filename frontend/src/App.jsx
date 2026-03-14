import { useMemo, useState } from 'react'
import ChatWindow from './components/ChatWindow'
import TripPlannerLayout from './components/TripPlannerLayout'

function deriveRequirements(latestUserMessage) {
  if (!latestUserMessage) {
    return {
      origin: undefined,
      destination: undefined,
      region: undefined,
      dates: undefined,
      budget: undefined,
      preference: undefined,
    }
  }

  const text = latestUserMessage

  // Very lightweight budget extraction like "under $400"
  const budgetMatch = text.match(/under\s+\$?(\d+[\d,]*)/i)
  const budget = budgetMatch ? `$${budgetMatch[1]}` : undefined

  // From / To extraction like "from NYC" / "from New York City (JFK)"
  const fromMatch = text.match(/from\s+([A-Za-z\s()]+)/i)
  const toMatch = text.match(/to\s+([A-Za-z\s()]+)/i)

  const origin =
    fromMatch?.[1]
      .replace(/,\s*$/,'')
      .trim() || undefined

  const destination =
    toMatch?.[1]
      .replace(/,\s*$/,'')
      .trim() || undefined

  // Very loose date phrase capture like "in late June" or "in July"
  const datesMatch = text.match(/in\s+([A-Za-z]+\s+[0-9]{4}|(early|mid|late)\s+[A-Za-z]+)/i)
  const dates = datesMatch ? datesMatch[0].trim() : undefined

  // Preference like "preference is balanced" or "balanced between cost and comfort"
  let preference
  if (/comfort/i.test(text) && /cost/i.test(text)) {
    preference = 'balanced'
  } else if (/cheapest|low cost|budget|price/i.test(text)) {
    preference = 'cost'
  } else if (/more comfortable|comfort first|business/i.test(text)) {
    preference = 'comfort'
  }

  return {
    origin,
    destination,
    region: undefined,
    dates,
    budget,
    preference,
  }
}

function derivePlans(latestFlights) {
  if (!Array.isArray(latestFlights)) return []

  return latestFlights.slice(0, 5).map((flight, index) => {
    const outbound = flight.outbound_segments?.[0]
    const origin = outbound?.departure_airport
    const destination = outbound?.arrival_airport

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
      stops: flight.stops,
      durationMinutes: flight.total_duration_minutes,
      departureTime: outbound?.departure_time,
      arrivalTime: outbound?.arrival_time,
      tagline,
    }
  })
}

function deriveRegionSummary(requirements, plans) {
  const firstPlan = plans[0]
  const originLabel = firstPlan?.origin || requirements.origin || 'Origin'
  const destinationLabel = firstPlan?.destination || requirements.destination || 'Destination'

  const cityNodes = Array.from(
    new Set(
      plans
        .map(p => p.destination)
        .filter(Boolean),
    ),
  )

  return {
    originLabel,
    destinationLabel,
    cityNodes,
  }
}

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [latestUserMessage, setLatestUserMessage] = useState(null)
  const [latestAssistantMessage, setLatestAssistantMessage] = useState(null)
  const [latestFlights, setLatestFlights] = useState([])
  const [selectedPlanId, setSelectedPlanId] = useState(null)

  const loadDemoTrip = () => {
    const demoUserMessage =
      'Fly from New York City (JFK) to somewhere warm like Miami or the Caribbean in late June, under $400, balanced between cost and comfort.'

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

    setLatestUserMessage(demoUserMessage)
    setLatestAssistantMessage({
      role: 'assistant',
      content: 'Here are a few warm destinations from NYC in late June that balance cost and comfort.',
      flights: demoFlights,
    })
    setLatestFlights(demoFlights)
  }

  const loadGlobalDemo = () => {
    const demoUserMessage =
      'Fly from Los Angeles (LAX) to Tokyo, Shanghai, or Buenos Aires in mid August, under $900, balanced between cost and comfort.'

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
            arrival_airport: 'PVG',
            departure_time: '01:15',
            arrival_time: '06:35+1',
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
            arrival_airport: 'EZE',
            departure_time: '22:45',
            arrival_time: '11:45+1',
          },
        ],
      },
    ]

    setLatestUserMessage(demoUserMessage)
    setLatestAssistantMessage({
      role: 'assistant',
      content: 'Here are intercontinental options from LA across the Pacific and to South America.',
      flights: demoFlights,
    })
    setLatestFlights(demoFlights)
  }

  const handleConversationUpdate = ({ userMessage, assistantMessage, flights }) => {
    setLatestUserMessage(userMessage)
    setLatestAssistantMessage(assistantMessage)
    setLatestFlights(flights ?? [])
  }

  const requirements = useMemo(
    () => deriveRequirements(latestUserMessage),
    [latestUserMessage],
  )

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
                ✈️ Flight Concierge
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
