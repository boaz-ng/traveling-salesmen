import RequirementsStrip from './RequirementsStrip'
import DestinationRegionMap from './DestinationRegionMap'
import PlansSection from './PlansSection'
import TripSection from './TripSection'

function TripPlannerLayout({
  requirements,
  regionSummary,
  plans,
  selectedPlan,
  onSelectPlan,
  tripId,
  tripName,
  tripFlights,
  tripSaving,
  onAddToTrip,
  onRemoveFromTrip,
  onRefreshTrip,
}) {
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
        onAddToTrip={onAddToTrip}
        tripSaving={tripSaving}
        tripFlights={tripFlights}
      />
      <TripSection
        tripId={tripId}
        tripName={tripName}
        tripFlights={tripFlights}
        onRemoveFlight={onRemoveFromTrip}
        onRefresh={onRefreshTrip}
      />
    </section>
  )
}

export default TripPlannerLayout
