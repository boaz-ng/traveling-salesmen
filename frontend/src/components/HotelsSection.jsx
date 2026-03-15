import HotelCard from './HotelCard'

function HotelsSection({ hotels }) {
  if (!hotels || hotels.length === 0) return null

  return (
    <section className="space-y-3">
      <h2 className="text-sm font-semibold text-[#111111] tracking-tight">
        Hotels near your destination
      </h2>
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {hotels.map((hotel, i) => (
          <HotelCard key={`${hotel.name}-${i}`} hotel={hotel} rank={i + 1} />
        ))}
      </div>
    </section>
  )
}

export default HotelsSection
