import { useState } from 'react'

function TripFlightCard({ flight, onRemove }) {
  const d = flight.flight_data || {}
  const airline = d.airline || 'Unknown'
  const price = d.price
  const origin = d.origin || '?'
  const destination = d.destination || '?'
  const stops = d.stops
  const durationMinutes = d.durationMinutes
  const hours = durationMinutes != null ? Math.floor(durationMinutes / 60) : null
  const minutes = durationMinutes != null ? durationMinutes % 60 : null
  const durationLabel =
    durationMinutes != null
      ? minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`
      : null

  return (
    <div className="bg-white rounded-xl border border-[#D6C6A8]/30 p-4 shadow-sm space-y-2">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-[#111111]">{airline}</p>
          <p className="text-xs text-[#777777]">{origin} → {destination}</p>
        </div>
        {price != null && (
          <p className="text-base font-semibold text-[#111111]">${Number(price).toFixed(0)}</p>
        )}
      </div>

      <div className="flex items-center gap-3 text-xs text-[#777777]">
        {durationLabel && <span>{durationLabel}</span>}
        {stops != null && (
          <span className={stops === 0 ? 'text-[#2F855A] font-medium' : ''}>
            {stops === 0 ? 'Direct' : `${stops} stop${stops > 1 ? 's' : ''}`}
          </span>
        )}
        {d.score != null && (
          <span className="rounded-full bg-[#F7F5EF] px-2 py-0.5 text-[11px] text-[#55514A]">
            Score {Number(d.score).toFixed(2)}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between pt-1 border-t border-[#E5E0D2]">
        <div className="flex items-center gap-2 text-[11px] text-[#9C8A6A]">
          <span>Added by {flight.added_by}</span>
          {flight.notes && (
            <span className="italic text-[#777777]">— {flight.notes}</span>
          )}
        </div>
        {onRemove && (
          <button
            type="button"
            onClick={() => onRemove(flight.id)}
            className="text-[11px] text-red-400 hover:text-red-600 transition-colors"
          >
            Remove
          </button>
        )}
      </div>

      <div className="pt-1">
        <button
          type="button"
          className="inline-flex items-center justify-center rounded-full bg-[#9C8A6A] px-4 py-2 text-xs font-semibold text-white shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
          disabled
        >
          Book this plan
        </button>
      </div>
    </div>
  )
}

function TripSection({ tripId, tripFlights, tripName, onRemoveFlight, onRefresh }) {
  const [copied, setCopied] = useState(false)

  if (!tripId) return null

  const shareUrl = `${window.location.origin}${window.location.pathname}?trip=${tripId}`

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      window.prompt('Copy this link:', shareUrl)
    }
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[#111111]">
          {tripName || 'Shared Trip'}
          {tripFlights.length > 0 && (
            <span className="ml-1.5 text-[#9C8A6A] font-normal">{tripFlights.length}</span>
          )}
        </h2>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              className="text-xs text-[#9C8A6A] hover:text-[#8A7A5E] hover:underline"
            >
              Refresh
            </button>
          )}
          <button
            type="button"
            onClick={handleShare}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[#D6C6A8]/50 bg-white text-xs font-medium text-[#9C8A6A] hover:bg-[#F7F5EF] hover:border-[#9C8A6A]/40 transition-colors shadow-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            {copied ? 'Link copied!' : 'Share trip'}
          </button>
        </div>
      </div>

      {tripFlights.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[#D6C6A8]/50 p-5 text-center">
          <p className="text-xs text-[#777777]">
            No flights saved yet. Click &quot;Add to Trip&quot; on any flight above to start comparing.
          </p>
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {tripFlights.map(f => (
            <TripFlightCard
              key={f.id}
              flight={f}
              onRemove={onRemoveFlight}
            />
          ))}
        </div>
      )}
    </section>
  )
}

export default TripSection
