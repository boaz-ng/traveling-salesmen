import RequirementsStrip from './RequirementsStrip'
import DestinationRegionMap from './DestinationRegionMap'
import PlansSection from './PlansSection'

function TripPlannerLayout({ requirements, regionSummary, plans, selectedPlan, onSelectPlan }) {
  const hasPlans = Array.isArray(plans) && plans.length > 0

  return (
    <section className="w-full max-w-5xl mx-auto px-4 pb-8 space-y-6">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-[#111111]">Your Trip Outline</h2>
        <p className="text-sm text-[#777777]">
          As you describe your trip, we summarize your requirements, visualize candidate destinations,
          and highlight the best plans.
        </p>
      </div>

      <div className="space-y-4">
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
      </div>
    </section>
  )
}

export default TripPlannerLayout

