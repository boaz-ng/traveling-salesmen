import { useState } from 'react'
import PlanCard from './PlanCard'

function PlansSection({ plans, selectedPlan, onSelectPlan }) {
  const [expandedId, setExpandedId] = useState(null)

  if (!plans || plans.length === 0) {
    return (
      <section className="rounded-2xl p-4 sm:p-5">
        <p className="text-xs text-[#777777]">
          Once we find good options, your best plans will appear here.
        </p>
      </section>
    )
  }

  return (
    <section className="space-y-3">
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

