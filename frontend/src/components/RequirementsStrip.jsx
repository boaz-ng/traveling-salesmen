function Pill({ label, value, placeholder }) {
  const hasValue = value && value.trim().length > 0

  return (
    <div className="flex flex-col min-w-[120px] bg-[#FFFFFF] border border-[#D6C6A8] rounded-full px-4 py-2 shadow-sm">
      <span className="text-[11px] font-medium tracking-wide uppercase text-[#777777]">
        {label}
      </span>
      <span className={`text-sm ${hasValue ? 'text-[#111111]' : 'text-[#B0A795]'}`}>
        {hasValue ? value : placeholder}
      </span>
    </div>
  )
}

function RequirementsStrip({ requirements }) {
  const { origin, destination, region, dates, budget, preference } = requirements || {}

  return (
    <section className="w-full">
      <div className="flex flex-wrap gap-3">
        <Pill
          label="From"
          value={origin}
          placeholder="Add departure"
        />
        <Pill
          label="To / Region"
          value={destination || region}
          placeholder="Anywhere"
        />
        <Pill
          label="Dates"
          value={dates}
          placeholder="Flexible"
        />
        <Pill
          label="Budget"
          value={budget}
          placeholder="Add budget"
        />
        <Pill
          label="Preference"
          value={preference}
          placeholder="Balanced"
        />
      </div>
    </section>
  )
}

export default RequirementsStrip

