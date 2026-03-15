function HotelCard({ hotel, rank }) {
  const ratingColor = (rating) => {
    if (!rating) return 'bg-gray-100 text-gray-500'
    if (rating >= 4.5) return 'bg-green-100 text-green-700'
    if (rating >= 3.5) return 'bg-yellow-100 text-yellow-700'
    return 'bg-orange-100 text-orange-700'
  }

  const stars = hotel.stars
    ? '★'.repeat(hotel.stars) + '☆'.repeat(Math.max(0, 5 - hotel.stars))
    : null

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl overflow-hidden border border-[#D6C6A8]/30 shadow-sm hover:shadow-md transition-all">
      {hotel.image_url && (
        <div className="h-32 w-full overflow-hidden bg-[#F7F5EF]">
          <img
            src={hotel.image_url}
            alt={hotel.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
      )}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-[#B0A795]">#{rank}</span>
              <h3 className="text-sm font-semibold text-[#111111] truncate">{hotel.name}</h3>
            </div>
            {stars && (
              <p className="text-xs text-[#9C8A6A] mt-0.5">{stars}</p>
            )}
            {hotel.address && (
              <p className="text-xs text-[#777777] mt-1 truncate">{hotel.address}</p>
            )}
          </div>
          <div className="text-right shrink-0">
            {hotel.price_per_night != null && (
              <p className="text-base font-semibold text-[#111111]">
                ${Math.round(hotel.price_per_night)}
                <span className="text-xs font-normal text-[#777777]">/night</span>
              </p>
            )}
            {hotel.rating != null && (
              <span className={`inline-flex items-center rounded-full text-[11px] px-2 py-0.5 font-medium mt-1 ${ratingColor(hotel.rating)}`}>
                {hotel.rating.toFixed(1)}
              </span>
            )}
          </div>
        </div>

        {hotel.description && (
          <p className="text-xs text-[#555555] mt-2 line-clamp-2">{hotel.description}</p>
        )}

        {hotel.amenities && hotel.amenities.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {hotel.amenities.slice(0, 4).map((amenity, i) => (
              <span key={i} className="text-[10px] bg-[#F7F5EF] text-[#777777] rounded-full px-2 py-0.5">
                {amenity}
              </span>
            ))}
            {hotel.amenities.length > 4 && (
              <span className="text-[10px] text-[#B0A795]">+{hotel.amenities.length - 4} more</span>
            )}
          </div>
        )}

        {hotel.booking_url && (
          <a
            href={hotel.booking_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 inline-flex items-center text-xs font-medium text-[#9C8A6A] hover:text-[#8A7A5E] hover:underline"
          >
            View details &rarr;
          </a>
        )}
      </div>
    </div>
  )
}

export default HotelCard
