function FlightCard({ flight, rank }) {
  const formatDuration = (minutes) => {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return m > 0 ? `${h}h ${m}m` : `${h}h`
  }

  const scoreColor = (score) => {
    if (score === null || score === undefined) return 'bg-gray-100 text-gray-600'
    if (score <= 0.3) return 'bg-green-100 text-green-700'
    if (score <= 0.6) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  const outbound = flight.outbound_segments?.[0]

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-lg font-bold text-gray-400">#{rank}</span>
          <div>
            <p className="font-semibold text-gray-800">{flight.airline}</p>
            {outbound && (
              <p className="text-xs text-gray-500">{outbound.flight_number}</p>
            )}
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-gray-900">
            ${flight.price.toFixed(0)}
          </p>
          <span className={`text-xs px-2 py-0.5 rounded-full ${scoreColor(flight.score)}`}>
            {flight.score !== null && flight.score !== undefined
              ? `Score: ${flight.score.toFixed(2)}`
              : 'N/A'}
          </span>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center space-x-4">
          {outbound && (
            <>
              <span>{outbound.departure_airport}</span>
              <span className="text-gray-300">→</span>
              <span>{outbound.arrival_airport}</span>
            </>
          )}
        </div>
        <div className="flex items-center space-x-4">
          <span>{formatDuration(flight.total_duration_minutes)}</span>
          <span className={flight.stops === 0 ? 'text-green-600 font-medium' : 'text-gray-500'}>
            {flight.stops === 0 ? 'Direct' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
          </span>
        </div>
      </div>

      {outbound && (
        <div className="mt-2 text-xs text-gray-400">
          {outbound.departure_time} → {outbound.arrival_time}
        </div>
      )}
    </div>
  )
}

export default FlightCard
