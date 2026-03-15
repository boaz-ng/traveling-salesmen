function Pill({ label, value, placeholder, action }) {
  const hasValue = value && value.trim().length > 0

  return (
    <div className="flex flex-col min-w-[120px] bg-white/70 border border-[#D6C6A8]/40 rounded-full px-4 py-2">
      <span className="text-[11px] font-medium tracking-wide uppercase text-[#777777]">
        {label}
      </span>
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className={`text-sm ${hasValue ? 'text-[#111111]' : 'text-[#B0A795]'}`}>
          {hasValue ? value : placeholder}
        </span>
        {action}
      </div>
    </div>
  )
}

function RequirementsStrip({ requirements, locationStatus, onRequestLocation }) {
  const { origin, destination, region, dates, budget, preference } = requirements || {}
  const fromPlaceholder =
    locationStatus === 'loading'
      ? 'Detecting location…'
      : 'Add departure'
  const fromAction =
    !origin && locationStatus !== 'loading' && onRequestLocation ? (
      <button
        type="button"
        onClick={onRequestLocation}
        className="text-[11px] text-[#9C8A6A] hover:text-[#8A7A5E] hover:underline"
      >
        Use my location
      </button>
    ) : null

  return (
    <section className="w-full">
      <div className="flex flex-wrap gap-3">
        <Pill
          label="From"
          value={origin}
          placeholder={fromPlaceholder}
          action={fromAction}
        />
        <Pill
          label="To / Region"
          value={destination || region}
          placeholder="Anywhere"
          action={null}
        />
        <Pill
          label="Dates"
          value={dates}
          placeholder="Flexible"
          action={null}
        />
        <Pill
          label="Budget"
          value={budget}
          placeholder="Add budget"
          action={null}
        />
        <Pill
          label="Preference"
          value={preference}
          placeholder="Balanced"
          action={null}
        />
      </div>
    </section>
  )
}

export default RequirementsStrip

