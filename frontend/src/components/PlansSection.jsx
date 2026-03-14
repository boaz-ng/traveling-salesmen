import { useState } from 'react'
import PlanCard from './PlanCard'

function PlansSection({ plans, selectedPlan, onSelectPlan }) {
  const [expandedId, setExpandedId] = useState(null)

  if (!plans || plans.length === 0) {
    return (
      <section className="bg-[#FFFFFF] border border-[#D6C6A8] rounded-2xl shadow-sm p-4 sm:p-5">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-semibold text-[#111111]">Plans</h2>
        </div>
        <p className="text-xs text-[#777777]">
          Once we find good options, your best 4–5 plans will appear here with details and booking
          hooks.
        </p>
      </section>
    )
  }

  return (
    <section className="bg-[#FFFFFF] border border-[#D6C6A8] rounded-2xl shadow-sm p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-semibold text-[#111111]">Recommended plans</h2>
          <p className="text-xs text-[#777777]">
            Expand a plan to see more details. Booking is coming soon.
          </p>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {plans.map(plan => (
          <PlanCard
            key={plan.id}
            plan={plan}
            selected={selectedPlan?.id === plan.id}
            expanded={expandedId === plan.id}
            onClick={() => {
              setExpandedId(prev => (prev === plan.id ? null : plan.id))
              onSelectPlan?.(plan.id)
            }}
          />
        ))}
      </div>
    </section>
  )
}

export default PlansSection

