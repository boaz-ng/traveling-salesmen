import { useCallback, useEffect, useRef, useState } from 'react'
import {
  ComposableMap,
  Geographies,
  Geography,
  Graticule,
  Line,
  Marker,
  Sphere,
  ZoomableGroup,
} from 'react-simple-maps'
import { geoEqualEarth } from 'd3-geo'

const geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'

// Compute projected world width so we can tile 3 copies for seamless panning
const _proj = geoEqualEarth().scale(160).translate([400, 210])
const WORLD_WIDTH = _proj([180, 0])[0] - _proj([-180, 0])[0]
const OFFSETS = [-WORLD_WIDTH, 0, WORLD_WIDTH]

const AIRPORT_COORDINATES = {
  JFK: [-73.7781, 40.6413],
  LGA: [-73.874, 40.7769],
  EWR: [-74.1745, 40.6895],
  MIA: [-80.2906, 25.7959],
  FLL: [-80.1527, 26.0726],
  TPA: [-82.534, 27.979],
  SJU: [-66.0018, 18.4394],
  LAX: [-118.4085, 33.9416],
  NRT: [140.3929, 35.772],
  PVG: [121.8083, 31.1443],
  EZE: [-58.5358, -34.8222],
  DTW: [-83.3534, 42.2124],
  ORD: [-87.9073, 41.9742],
  ATL: [-84.428, 33.6407],
  DFW: [-97.038, 32.8998],
  SFO: [-122.375, 37.6213],
  SEA: [-122.3088, 47.4502],
  DEN: [-104.6737, 39.8561],
  IAH: [-95.3414, 29.9844],
  CLT: [-80.9431, 35.214],
  PHX: [-112.0116, 33.4373],
  ICN: [126.4505, 37.4602],
  HND: [139.7798, 35.5494],
  GRU: [-46.4731, -23.4356],
  SCL: [-70.7858, -33.393],
  LHR: [-0.4614, 51.4700],
  CDG: [2.5479, 49.0097],
  DXB: [55.3644, 25.2532],
  SIN: [103.9894, 1.3502],
  HKG: [113.9146, 22.3089],
  BKK: [100.7501, 13.6900],
}

const BACKGROUND_CITIES = [
  { name: 'Tokyo', coord: [139.6917, 35.6895], tier: 1 },
  { name: 'London', coord: [-0.1278, 51.5074], tier: 1 },
  { name: 'New York', coord: [-74.006, 40.7128], tier: 1 },
  { name: 'Beijing', coord: [116.4074, 39.9042], tier: 1 },
  { name: 'Mumbai', coord: [72.8777, 19.076], tier: 1 },
  { name: 'São Paulo', coord: [-46.6333, -23.5505], tier: 1 },
  { name: 'Cairo', coord: [31.2357, 30.0444], tier: 1 },
  { name: 'Sydney', coord: [151.2093, -33.8688], tier: 1 },
  { name: 'Moscow', coord: [37.6173, 55.7558], tier: 1 },
  { name: 'Mexico City', coord: [-99.1332, 19.4326], tier: 1 },
  { name: 'Paris', coord: [2.3522, 48.8566], tier: 2 },
  { name: 'Istanbul', coord: [28.9784, 41.0082], tier: 2 },
  { name: 'Dubai', coord: [55.2708, 25.2048], tier: 2 },
  { name: 'Singapore', coord: [103.8198, 1.3521], tier: 2 },
  { name: 'Seoul', coord: [126.978, 37.5665], tier: 2 },
  { name: 'Toronto', coord: [-79.3832, 43.6532], tier: 2 },
  { name: 'Buenos Aires', coord: [-58.3816, -34.6037], tier: 2 },
  { name: 'Lagos', coord: [3.3792, 6.5244], tier: 2 },
  { name: 'Jakarta', coord: [106.8456, -6.2088], tier: 2 },
  { name: 'Bangkok', coord: [100.5018, 13.7563], tier: 2 },
  { name: 'Berlin', coord: [13.405, 52.52], tier: 2 },
  { name: 'Chicago', coord: [-87.6298, 41.8781], tier: 2 },
  { name: 'Rome', coord: [12.4964, 41.9028], tier: 3 },
  { name: 'Madrid', coord: [-3.7038, 40.4168], tier: 3 },
  { name: 'Amsterdam', coord: [4.9041, 52.3676], tier: 3 },
  { name: 'Hong Kong', coord: [114.1694, 22.3193], tier: 3 },
  { name: 'Taipei', coord: [121.5654, 25.033], tier: 3 },
  { name: 'Melbourne', coord: [144.9631, -37.8136], tier: 3 },
  { name: 'Auckland', coord: [174.7633, -36.8485], tier: 3 },
  { name: 'Vancouver', coord: [-123.1216, 49.2827], tier: 3 },
  { name: 'Seattle', coord: [-122.3321, 47.6062], tier: 3 },
  { name: 'Cape Town', coord: [18.4241, -33.9249], tier: 3 },
  { name: 'Nairobi', coord: [36.8219, -1.2921], tier: 3 },
  { name: 'Lima', coord: [-77.0428, -12.0464], tier: 3 },
  { name: 'Santiago', coord: [-70.6693, -33.4489], tier: 3 },
]

function resolveAirportCoord(label) {
  if (!label) return null
  if (AIRPORT_COORDINATES[label]) return AIRPORT_COORDINATES[label]
  const parenMatch = label.match(/\(([A-Z]{3})\)/)
  if (parenMatch && AIRPORT_COORDINATES[parenMatch[1]]) return AIRPORT_COORDINATES[parenMatch[1]]
  const wordMatch = label.match(/\b([A-Z]{3})\b/)
  if (wordMatch && AIRPORT_COORDINATES[wordMatch[1]]) return AIRPORT_COORDINATES[wordMatch[1]]
  return null
}

const geoStyle = {
  default: { outline: 'none', pointerEvents: 'none' },
  hover: { outline: 'none', pointerEvents: 'none' },
  pressed: { outline: 'none', pointerEvents: 'none' },
}

function visibleBackgroundTier(zoom, isGlobe) {
  if (isGlobe) {
    if (zoom >= 2.5) return 3
    if (zoom >= 1.5) return 2
    return 1
  }
  if (zoom >= 4.0) return 3
  if (zoom >= 2.5) return 2
  return 1
}

function DestinationRegionMap({ regionSummary, hasPlans, plans, selectedPlan, requirements }) {
  const [mode, setMode] = useState('map')
  const [mapPosition, setMapPosition] = useState({ coordinates: [0, 20], zoom: 1 })
  const [mapUserMoved, setMapUserMoved] = useState(false)

  const [globeRotation, setGlobeRotation] = useState([0, 0])
  const [globeZoom, setGlobeZoom] = useState(1.2)
  const globeDragRef = useRef({ dragging: false, startX: 0, startY: 0, startRotation: [0, 0] })
  const rafRef = useRef(null)
  const globeContainerRef = useRef(null)

  const originLabel = regionSummary?.originLabel || 'Origin'
  const cityNodes = Array.isArray(regionSummary?.cityNodes) ? regionSummary.cityNodes : []

  // Derive origin from plan-based data first, then fall back to requirements airports
  const originCoordFromPlans = resolveAirportCoord(originLabel)
  const originCoordFromReqs = requirements?.origin_airports?.[0]
    ? AIRPORT_COORDINATES[requirements.origin_airports[0]]
    : null
  const originCoord = originCoordFromPlans || originCoordFromReqs

  const effectiveOriginLabel = originCoordFromPlans
    ? originLabel
    : (requirements?.origin || requirements?.origin_airports?.[0] || 'Origin')

  // Derive destinations from plan-based data first, then fall back to requirements airports
  const knownDestFromPlans = cityNodes
    .map(code => ({ code, coord: AIRPORT_COORDINATES[code] }))
    .filter(d => d.coord)

  const knownDestFromReqs = (requirements?.destination_airports || [])
    .map(code => ({ code, coord: AIRPORT_COORDINATES[code] }))
    .filter(d => d.coord)

  const knownDestinations = knownDestFromPlans.length > 0 ? knownDestFromPlans : knownDestFromReqs

  const destinationCoords = knownDestinations.map(d => d.coord)
  const destinationCoordsKey = destinationCoords.map(c => c.join(',')).join('|')

  const hasMapData = hasPlans || originCoord || knownDestinations.length > 0

  // Auto-fit 2D map around all airports
  useEffect(() => {
    if ((!originCoord && destinationCoords.length === 0) || mode !== 'map') return
    if (mapUserMoved) return

    const allCoords = [...(originCoord ? [originCoord] : []), ...destinationCoords]
    if (allCoords.length === 0) return
    const lons = allCoords.map(c => c[0])
    const lats = allCoords.map(c => c[1])
    const lonMin = Math.min(...lons)
    const lonMax = Math.max(...lons)
    const latMin = Math.min(...lats)
    const latMax = Math.max(...lats)
    const lonSpan = Math.max(1, lonMax - lonMin)
    const latSpan = Math.max(1, latMax - latMin)
    const span = Math.max(lonSpan, latSpan)
    const targetZoom = span < 10 ? 4 : span < 25 ? 2.6 : span < 60 ? 1.8 : span < 120 ? 1.4 : 1

    setMapPosition({
      coordinates: [(lonMin + lonMax) / 2, (latMin + latMax) / 2],
      zoom: targetZoom,
    })
  }, [hasPlans, originCoord, destinationCoordsKey, mode, mapUserMoved])

  useEffect(() => {
    setMapUserMoved(false)
  }, [destinationCoordsKey])

  // --- Globe drag handlers ---

  const handleGlobeMouseDown = (event) => {
    globeDragRef.current = {
      dragging: true,
      startX: event.clientX,
      startY: event.clientY,
      startRotation: globeRotation,
    }
  }

  const handleGlobeMouseMove = useCallback((event) => {
    if (!globeDragRef.current.dragging) return
    if (rafRef.current) return

    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null
      const { startX, startY, startRotation } = globeDragRef.current
      const dx = event.clientX - startX
      const dy = event.clientY - startY
      const rotateSpeed = 0.6
      const rawLon = startRotation[0] - dx * rotateSpeed
      const normalizedLon = ((rawLon + 540) % 360) - 180
      const newLat = Math.max(-80, Math.min(80, startRotation[1] + dy * rotateSpeed))
      setGlobeRotation([normalizedLon, newLat])
    })
  }, [])

  const endGlobeDrag = () => {
    if (globeDragRef.current.dragging) {
      globeDragRef.current.dragging = false
    }
  }

  const handleGlobeWheel = useCallback((event) => {
    event.preventDefault()
    const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
    setGlobeZoom(prev => Math.max(0.8, Math.min(6, prev * zoomFactor)))
  }, [])

  // Re-attach when mode/hasPlans changes so the ref is populated
  useEffect(() => {
    const el = globeContainerRef.current
    if (!el) return
    el.addEventListener('wheel', handleGlobeWheel, { passive: false })
    return () => el.removeEventListener('wheel', handleGlobeWheel)
  }, [handleGlobeWheel, mode, hasMapData])

  const isCityVisibleOnGlobe = (coord) => {
    if (!coord) return false
    const relLon = ((coord[0] - globeRotation[0] + 540) % 360) - 180
    return Math.abs(relLon) <= 90
  }

  const mapTier = visibleBackgroundTier(mapPosition.zoom, false)
  const globeTier = visibleBackgroundTier(globeZoom, true)
  const filteredBgCities2D = BACKGROUND_CITIES.filter(c => c.tier <= mapTier)
  const filteredBgCitiesGlobe = BACKGROUND_CITIES.filter(c => c.tier <= globeTier)

  return (
    <section className="bg-[#FFFFFF] border border-[#D6C6A8] rounded-2xl shadow-sm p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-semibold text-[#111111]">Destination region</h2>
          <p className="text-xs text-[#777777]">
            We sketch an abstract world view based on the best plans.
          </p>
        </div>
        {hasMapData && (
          <div className="inline-flex items-center rounded-full bg-[#F7F5EF] p-1 text-[11px] text-[#777777]">
            <button
              type="button"
              onClick={() => setMode('map')}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                mode === 'map'
                  ? 'bg-[#FFFFFF] text-[#111111] shadow-sm'
                  : 'text-[#777777]'
              }`}
            >
              2D map
            </button>
            <button
              type="button"
              onClick={() => setMode('globe')}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                mode === 'globe'
                  ? 'bg-[#FFFFFF] text-[#111111] shadow-sm'
                  : 'text-[#777777]'
              }`}
            >
              3D globe
            </button>
          </div>
        )}
      </div>

      <div className="relative h-[24rem] sm:h-[30rem] rounded-2xl bg-[#F7F5EF] overflow-hidden flex items-center justify-center">
        {!hasMapData && (
          <div className="text-center px-6">
            <p className="text-sm font-medium text-[#111111]">
              Describe your trip to see regions and routes here.
            </p>
            <p className="mt-1 text-xs text-[#777777]">
              Mention things like &quot;somewhere warm&quot;, &quot;Europe&quot;, or &quot;West
              Coast&quot; and we&apos;ll visualize candidate destinations.
            </p>
          </div>
        )}

        {/* ==================== 2D MAP ==================== */}
        {hasMapData && mode === 'map' && (
          <div className="w-full h-full">
            <ComposableMap
              projection="geoEqualEarth"
              projectionConfig={{ scale: 160 }}
              width={800}
              height={420}
              style={{ width: '100%', height: '100%' }}
            >
              <ZoomableGroup
                center={mapPosition.coordinates}
                zoom={mapPosition.zoom}
                minZoom={0.8}
                maxZoom={8}
                translateExtent={[[-1600, -400], [1600, 800]]}
                onMoveEnd={(pos) => {
                  const [lon, lat] = pos.coordinates
                  const wrappedLon = ((lon + 540) % 360) - 180
                  setMapPosition({ coordinates: [wrappedLon, lat], zoom: pos.zoom })
                  setMapUserMoved(true)
                }}
              >
                {/* Geographies at 3 horizontal offsets for seamless wrapping */}
                <Geographies geography={geoUrl}>
                  {({ geographies }) =>
                    OFFSETS.map(offset => (
                      <g key={`geo-${offset}`} transform={`translate(${offset}, 0)`}>
                        {geographies.map(geo => (
                          <Geography
                            key={geo.rsmKey}
                            geography={geo}
                            fill="#E1D6C0"
                            stroke="#D6C6A8"
                            strokeWidth={0.5}
                            style={geoStyle}
                          />
                        ))}
                      </g>
                    ))
                  }
                </Geographies>

                {/* Markers, lines, and background cities at each offset */}
                {OFFSETS.map(offset => (
                  <g key={`overlay-${offset}`} transform={`translate(${offset}, 0)`}>
                    {/* Route lines: segment-by-segment through waypoints */}
                    {plans.map((plan, pi) => {
                      const wp = (plan.waypoints || [])
                        .map(code => ({ code, coord: AIRPORT_COORDINATES[code] }))
                        .filter(w => w.coord)
                      if (wp.length < 2) return null
                      const isSelected = selectedPlan?.id === plan.id
                      return wp.slice(0, -1).map((from, si) => (
                        <Line
                          key={`route-${pi}-${si}`}
                          from={from.coord}
                          to={wp[si + 1].coord}
                          stroke={isSelected ? '#9C8A6A' : '#C4B8A0'}
                          strokeWidth={isSelected ? 2 : 1}
                          strokeDasharray={isSelected ? '6 3' : '4 4'}
                          strokeOpacity={isSelected ? 1 : 0.5}
                        />
                      ))
                    })}

                    {/* Layover markers (intermediate waypoints) */}
                    {plans.map((plan, pi) => {
                      const wp = plan.waypoints || []
                      if (wp.length <= 2) return null
                      const layovers = wp.slice(1, -1)
                      return layovers.map((code, li) => {
                        const coord = AIRPORT_COORDINATES[code]
                        if (!coord) return null
                        const isSelected = selectedPlan?.id === plan.id
                        return (
                          <Marker key={`layover-${pi}-${li}`} coordinates={coord}>
                            <circle
                              r={3}
                              fill={isSelected ? '#FFFFFF' : '#F7F5EF'}
                              stroke={isSelected ? '#9C8A6A' : '#C4B8A0'}
                              strokeWidth={1}
                            />
                            <text
                              textAnchor="start"
                              x={5}
                              y={3}
                              style={{
                                fontSize: Math.max(7, 9 / mapPosition.zoom),
                                fill: isSelected ? '#9C8A6A' : '#B5A88E',
                                pointerEvents: 'none',
                                opacity: isSelected ? 0.9 : 0.5,
                              }}
                            >
                              {code}
                            </text>
                          </Marker>
                        )
                      })
                    })}

                    {/* Fallback: if no plans yet, draw simple origin-to-destination lines from requirements */}
                    {!hasPlans && originCoord && knownDestinations.map((dest, i) => (
                      <Line
                        key={`req-line-${dest.code || i}`}
                        from={originCoord}
                        to={dest.coord}
                        stroke="#C4B8A0"
                        strokeWidth={1}
                        strokeDasharray="4 4"
                        strokeOpacity={0.5}
                      />
                    ))}

                    {originCoord && (
                      <Marker coordinates={originCoord}>
                        <circle r={5} fill="#9C8A6A" />
                        <text
                          textAnchor="start"
                          x={8}
                          y={4}
                          style={{
                            fontSize: Math.max(8, 10 / mapPosition.zoom),
                            fill: '#111111',
                            pointerEvents: 'none',
                          }}
                        >
                          {effectiveOriginLabel}
                        </text>
                      </Marker>
                    )}

                    {knownDestinations.map((dest, index) => (
                      <Marker key={dest.code || index} coordinates={dest.coord}>
                        <circle r={4} fill="#FFFFFF" stroke="#9C8A6A" strokeWidth={1.5} />
                        <text
                          textAnchor="start"
                          x={6}
                          y={3}
                          style={{
                            fontSize: Math.max(8, 10 / mapPosition.zoom),
                            fill: '#9C8A6A',
                            pointerEvents: 'none',
                          }}
                        >
                          {dest.code}
                        </text>
                      </Marker>
                    ))}

                    {filteredBgCities2D.map(city => (
                      <Marker key={city.name} coordinates={city.coord}>
                        <circle r={1.5} fill="#C4B8A0" opacity={0.5} />
                        <text
                          textAnchor="start"
                          x={4}
                          y={3}
                          style={{
                            fontSize: Math.max(6, 8 / mapPosition.zoom),
                            fill: '#B5A88E',
                            pointerEvents: 'none',
                            opacity: 0.6,
                          }}
                        >
                          {city.name}
                        </text>
                      </Marker>
                    ))}
                  </g>
                ))}
              </ZoomableGroup>
            </ComposableMap>
          </div>
        )}

        {/* ==================== 3D GLOBE ==================== */}
        {hasMapData && mode === 'globe' && (
          <div
            ref={globeContainerRef}
            className="w-full h-full cursor-grab active:cursor-grabbing"
            onMouseDown={handleGlobeMouseDown}
            onMouseMove={handleGlobeMouseMove}
            onMouseUp={endGlobeDrag}
            onMouseLeave={endGlobeDrag}
          >
            <ComposableMap
              projection="geoOrthographic"
              projectionConfig={{
                scale: 140 * globeZoom,
                rotate: [-globeRotation[0], -globeRotation[1], 0],
              }}
              style={{ width: '100%', height: '100%' }}
            >
              <Sphere fill="#F7F5EF" stroke="#D6C6A8" strokeWidth={0.5} />
              <Graticule stroke="#D6C6A8" strokeWidth={0.3} strokeOpacity={0.4} />

              <Geographies geography={geoUrl}>
                {({ geographies }) =>
                  geographies.map(geo => (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill="#E1D6C0"
                      stroke="#D6C6A8"
                      strokeWidth={0.5}
                      style={geoStyle}
                    />
                  ))
                }
              </Geographies>

              {/* Route lines: segment-by-segment through waypoints */}
              {plans.map((plan, pi) => {
                const wp = (plan.waypoints || [])
                  .map(code => ({ code, coord: AIRPORT_COORDINATES[code] }))
                  .filter(w => w.coord)
                if (wp.length < 2) return null
                const isSelected = selectedPlan?.id === plan.id
                return wp.slice(0, -1).map((from, si) => (
                  <Line
                    key={`globe-route-${pi}-${si}`}
                    from={from.coord}
                    to={wp[si + 1].coord}
                    stroke={isSelected ? '#9C8A6A' : '#C4B8A0'}
                    strokeWidth={isSelected ? 2 : 1}
                    strokeDasharray={isSelected ? '6 3' : '4 4'}
                    strokeOpacity={isSelected ? 1 : 0.5}
                  />
                ))
              })}

              {/* Layover markers on globe */}
              {plans.map((plan, pi) => {
                const wp = plan.waypoints || []
                if (wp.length <= 2) return null
                const layovers = wp.slice(1, -1)
                return layovers.map((code, li) => {
                  const coord = AIRPORT_COORDINATES[code]
                  if (!coord || !isCityVisibleOnGlobe(coord)) return null
                  const isSelected = selectedPlan?.id === plan.id
                  return (
                    <Marker key={`globe-layover-${pi}-${li}`} coordinates={coord}>
                      <circle
                        r={3}
                        fill={isSelected ? '#FFFFFF' : '#F7F5EF'}
                        stroke={isSelected ? '#9C8A6A' : '#C4B8A0'}
                        strokeWidth={1}
                      />
                      <text
                        textAnchor="start"
                        x={5}
                        y={3}
                        style={{
                          fontSize: 8,
                          fill: isSelected ? '#9C8A6A' : '#B5A88E',
                          pointerEvents: 'none',
                          opacity: isSelected ? 0.9 : 0.5,
                        }}
                      >
                        {code}
                      </text>
                    </Marker>
                  )
                })
              })}

              {/* Fallback lines from requirements when no plans yet */}
              {!hasPlans && originCoord && knownDestinations.map((dest, i) => (
                <Line
                  key={`globe-req-line-${dest.code || i}`}
                  from={originCoord}
                  to={dest.coord}
                  stroke="#C4B8A0"
                  strokeWidth={1}
                  strokeDasharray="4 4"
                  strokeOpacity={0.5}
                />
              ))}

              {originCoord && isCityVisibleOnGlobe(originCoord) && (
                <Marker coordinates={originCoord}>
                  <circle r={5} fill="#9C8A6A" />
                  <text
                    textAnchor="start"
                    x={8}
                    y={4}
                    style={{ fontSize: 10, fill: '#111111', pointerEvents: 'none' }}
                  >
                    {effectiveOriginLabel}
                  </text>
                </Marker>
              )}

              {knownDestinations.map((dest, index) => {
                if (!isCityVisibleOnGlobe(dest.coord)) return null
                return (
                  <Marker key={dest.code || index} coordinates={dest.coord}>
                    <circle r={4} fill="#FFFFFF" stroke="#9C8A6A" strokeWidth={1.5} />
                    <text
                      textAnchor="start"
                      x={6}
                      y={3}
                      style={{ fontSize: 10, fill: '#9C8A6A', pointerEvents: 'none' }}
                    >
                      {dest.code}
                    </text>
                  </Marker>
                )
              })}

              {filteredBgCitiesGlobe.map(city => {
                if (!isCityVisibleOnGlobe(city.coord)) return null
                return (
                  <Marker key={city.name} coordinates={city.coord}>
                    <circle r={1.5} fill="#C4B8A0" opacity={0.5} />
                    <text
                      textAnchor="start"
                      x={4}
                      y={3}
                      style={{
                        fontSize: 8,
                        fill: '#B5A88E',
                        pointerEvents: 'none',
                        opacity: 0.6,
                      }}
                    >
                      {city.name}
                    </text>
                  </Marker>
                )
              })}
            </ComposableMap>
          </div>
        )}
      </div>
    </section>
  )
}

export default DestinationRegionMap
