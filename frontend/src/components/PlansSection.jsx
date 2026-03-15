import { useState, useEffect, useRef } from 'react'
import PlanCard from './PlanCard'

const PAGE_SIZE = 2

function PlansSection({ plans, selectedPlan, onSelectPlan, onAddToTrip, tripSaving, tripFlights }) {
  const [expandedIds, setExpandedIds] = useState(new Set())
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)
  const prevPlansRef = useRef(plans)

  // Reset to showing top 2 whenever a new set of flights arrives
  useEffect(() => {
    if (plans !== prevPlansRef.current) {
      setVisibleCount(PAGE_SIZE)
      setExpandedIds(new Set())
      prevPlansRef.current = plans
    }
  }, [plans])

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

  const visiblePlans = plans.slice(0, visibleCount)
  const hasMore = visibleCount < plans.length
  const remaining = plans.length - visibleCount

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[#111111]">
          Top flights
          <span className="ml-1.5 text-[#9C8A6A] font-normal">
            {visibleCount < plans.length
              ? `${visibleCount} of ${plans.length}`
              : `${plans.length}`}
          </span>
        </h2>
        {visibleCount > PAGE_SIZE && (
          <button
            type="button"
            onClick={() => setVisibleCount(PAGE_SIZE)}
            className="text-xs text-[#9C8A6A] hover:text-[#8A7A5E] hover:underline"
          >
            Show less
          </button>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-2 md:items-start">
        {visiblePlans.map(plan => (
          <PlanCard
            key={plan.id}
            plan={plan}
            selected={selectedPlan?.id === plan.id}
            expanded={expandedIds.has(plan.id)}
            onClick={() => {
              toggleExpanded(plan.id)
              onSelectPlan?.(plan.id)
            }}
            onAddToTrip={onAddToTrip}
            tripSaving={tripSaving}
            tripFlights={tripFlights}
          />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-1">
          <button
            type="button"
            onClick={() => setVisibleCount(prev => Math.min(prev + PAGE_SIZE, plans.length))}
            className="inline-flex items-center gap-1.5 px-5 py-2 rounded-full border border-[#D6C6A8]/50 bg-white text-sm font-medium text-[#9C8A6A] hover:bg-[#F7F5EF] hover:border-[#9C8A6A]/40 transition-colors shadow-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
            Show {Math.min(PAGE_SIZE, remaining)} more flight{Math.min(PAGE_SIZE, remaining) > 1 ? 's' : ''}
          </button>
        </div>
      )}
    </section>
  )
}

export default PlansSection

