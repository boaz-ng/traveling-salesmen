import RequirementsStrip from './RequirementsStrip'
import DestinationRegionMap from './DestinationRegionMap'
import PlansSection from './PlansSection'

function TripPlannerLayout({ requirements, regionSummary, plans, selectedPlan, onSelectPlan }) {
  const hasPlans = Array.isArray(plans) && plans.length > 0

  return (
    <section className="w-full max-w-5xl mx-auto px-4 pb-8 space-y-5">
      <RequirementsStrip requirements={requirements} />
      <DestinationRegionMap
        regionSummary={regionSummary}
        hasPlans={hasPlans}
        plans={plans}
        selectedPlan={selectedPlan}
        requirements={requirements}
      />
      <PlansSection
        plans={plans}
        selectedPlan={selectedPlan}
        onSelectPlan={onSelectPlan}
      />
    </section>
  )
}

export default TripPlannerLayout

