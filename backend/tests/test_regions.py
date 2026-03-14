"""Tests for region resolution."""

from app.flights.regions import resolve_region


class TestResolveRegion:
    """Tests for the resolve_region function."""

    def test_northeast_region(self):
        codes = resolve_region("northeast")
        assert "JFK" in codes
        assert "EWR" in codes
        assert "LGA" in codes
        assert "BOS" in codes
        assert "PHL" in codes

    def test_new_york_city(self):
        codes = resolve_region("new york")
        assert codes == ["JFK", "EWR", "LGA"]

    def test_nyc_alias(self):
        codes = resolve_region("nyc")
        assert codes == ["JFK", "EWR", "LGA"]

    def test_southeast(self):
        codes = resolve_region("southeast")
        assert "MIA" in codes
        assert "ATL" in codes

    def test_west_coast(self):
        codes = resolve_region("west coast")
        assert "LAX" in codes
        assert "SFO" in codes
        assert "SEA" in codes

    def test_case_insensitive(self):
        codes = resolve_region("New York")
        assert codes == ["JFK", "EWR", "LGA"]

    def test_case_insensitive_upper(self):
        codes = resolve_region("CHICAGO")
        assert "ORD" in codes

    def test_direct_iata_code(self):
        codes = resolve_region("JFK")
        assert codes == ["JFK"]

    def test_direct_iata_code_lowercase(self):
        codes = resolve_region("lax")
        # "lax" is not in REGION_MAP but as 3-letter alpha, should pass through
        # Actually "la" maps to ["LAX"], and "lax" is 3 letters => upper => "LAX"
        assert codes == ["LAX"]

    def test_comma_separated_codes(self):
        codes = resolve_region("JFK, LAX, ORD")
        assert codes == ["JFK", "LAX", "ORD"]

    def test_unknown_region(self):
        codes = resolve_region("narnia")
        assert codes == []

    def test_whitespace_handling(self):
        codes = resolve_region("  new york  ")
        assert codes == ["JFK", "EWR", "LGA"]

    def test_florida(self):
        codes = resolve_region("florida")
        assert "MIA" in codes
        assert "MCO" in codes

    def test_texas(self):
        codes = resolve_region("texas")
        assert "DFW" in codes
        assert "IAH" in codes
        assert "AUS" in codes

    def test_caribbean(self):
        codes = resolve_region("caribbean")
        assert "CUN" in codes
        assert "SJU" in codes

    def test_sf_alias(self):
        codes = resolve_region("sf")
        assert codes == ["SFO"]

    def test_la_alias(self):
        codes = resolve_region("la")
        assert codes == ["LAX"]
