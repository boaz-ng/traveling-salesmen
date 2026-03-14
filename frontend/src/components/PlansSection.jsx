import { useState } from 'react'
import PlanCard from './PlanCard'

function PlansSection({ plans, selectedPlan, onSelectPlan }) {
  const [expandedIds, setExpandedIds] = useState(new Set())

  const toggleExpanded = (planId) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(planId)) next.delete(planId)
      else next.add(planId)
      return next
    })
  }

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
      <div className="grid gap-3 md:grid-cols-2 md:items-center">
        {plans.map(plan => (
          <PlanCard
            key={plan.id}
            plan={plan}
            selected={selectedPlan?.id === plan.id}
            expanded={expandedIds.has(plan.id)}
            onClick={() => {
              toggleExpanded(plan.id)
              onSelectPlan?.(plan.id)
            }}
          />
        ))}
      </div>
    </section>
  )
}

export default PlansSection

