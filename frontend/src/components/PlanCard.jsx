function DetailRow({ label, value }) {
  if (!value) return null
  return (
    <div className="flex items-center justify-between text-xs text-[#55514A]">
      <span className="text-[11px] uppercase tracking-wide text-[#9C8A6A]">
        {label}
      </span>
      <span className="font-medium text-[#111111]">{value}</span>
    </div>
  )
}

function PlanCard({ plan, expanded, selected, onClick }) {
  const {
    rank,
    price,
    score,
    airline,
    origin,
    destination,
    waypoints,
    stops,
    durationMinutes,
    departureTime,
    arrivalTime,
    tagline,
  } = plan

  const routeLabel = waypoints && waypoints.length > 1
    ? waypoints.join(' → ')
    : `${origin || 'Origin'} → ${destination || 'Destination'}`

  const hours = durationMinutes != null ? Math.floor(durationMinutes / 60) : null
  const minutes = durationMinutes != null ? durationMinutes % 60 : null
  const durationLabel =
    durationMinutes != null
      ? minutes > 0
        ? `${hours}h ${minutes}m`
        : `${hours}h`
      : undefined

  const stopsLabel =
    stops === 0
      ? 'Direct'
      : stops != null
        ? `${stops} stop${stops > 1 ? 's' : ''}`
        : undefined

  const isBest = rank === 1

  return (
    <article
      className={`flex flex-col bg-white/80 backdrop-blur-sm rounded-2xl overflow-hidden border transition-all ${
        selected ? 'border-[#9C8A6A] shadow-md' : 'border-[#D6C6A8]/30 shadow-sm hover:shadow-md'
      }`}
    >
      <button
        type="button"
        onClick={onClick}
        className="flex-1 text-left p-4 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#9C8A6A] focus-visible:ring-offset-2 focus-visible:ring-offset-[#FFFFFF]"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-[#B0A795]">#{rank}</span>
            <div>
              <p className="text-sm font-semibold text-[#111111]">{airline}</p>
              <p className="text-xs text-[#777777]">
                {routeLabel}
              </p>
              {tagline && (
                <p className="mt-1 text-xs text-[#9C8A6A]">
                  {tagline}
                </p>
              )}
            </div>
          </div>
          <div className="text-right space-y-1">
            {isBest && (
              <span className="inline-flex items-center rounded-full bg-[#9C8A6A] text-white text-[11px] px-2 py-0.5 font-medium">
                Best plan
              </span>
            )}
            {price != null && (
              <p className="text-base font-semibold text-[#111111]">
                ${Number(price).toFixed(0)}
              </p>
            )}
            {score != null && (
              <span className="inline-flex items-center rounded-full bg-[#F7F5EF] text-[11px] px-2 py-0.5 text-[#55514A]">
                Score {Number(score).toFixed(2)}
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-[#777777]">
          <div className="flex items-center gap-2">
            {departureTime && arrivalTime && (
              <span>
                {departureTime} → {arrivalTime}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {durationLabel && <span>{durationLabel}</span>}
            {stopsLabel && (
              <span className={stops === 0 ? 'text-[#2F855A] font-medium' : ''}>
                {stopsLabel}
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-[#777777]">
          <span>{expanded ? 'Hide details' : 'View details'}</span>
          <span
            className={`transition-transform ${expanded ? 'rotate-180' : ''}`}
            aria-hidden="true"
          >
            ˅
          </span>
        </div>
      </button>

      {expanded && (
        <div className="border-t border-[#E5E0D2] px-4 pb-4 pt-3 space-y-3 text-xs bg-[#FDFBF6]">
          <div className="grid grid-cols-2 gap-3">
            <DetailRow label="Route" value={routeLabel} />
            <DetailRow label="Duration" value={durationLabel} />
            <DetailRow label="Stops" value={stopsLabel} />
            {price != null && <DetailRow label="Estimated price" value={`$${Number(price).toFixed(0)}`} />}
          </div>

          <div className="space-y-1">
            <p className="text-[11px] font-semibold text-[#777777]">
              Why we like this
            </p>
            <ul className="list-disc list-inside text-xs text-[#55514A] space-y-0.5">
              {isBest && <li>Best overall balance across price, timing, and route.</li>}
              {stops === 0 && <li>Direct flight keeps the journey simple.</li>}
              {stops > 0 && <li>Includes connections that open up more options.</li>}
              {score != null && <li>High score compared with other options we found.</li>}
            </ul>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-full bg-[#9C8A6A] px-4 py-2 text-xs font-semibold text-white shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
              disabled
              onClick={() => {
                // Placeholder for future booking integration
                // eslint-disable-next-line no-console
                console.log('Book this plan clicked (coming soon)')
              }}
            >
              Book this plan
            </button>
            <p className="text-[11px] text-[#777777]">
              Booking flow coming soon — for now, use this as your decision helper.
            </p>
          </div>
        </div>
      )}
    </article>
  )
}

export default PlanCard

