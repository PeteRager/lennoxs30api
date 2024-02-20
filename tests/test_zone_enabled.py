"""Tests zone enabled"""
from lennoxs30api.s30api_async import (
    LENNOX_ZONING_MODE_CENTRAL,
    lennox_system,
    s30api_async,
)


def test_test_zone_enabled(api: s30api_async):
    """Test zone enabled"""
    lsystem: lennox_system = api.system_list[0]
    zone0 = lsystem.getZone(0)
    zone1 = lsystem.getZone(1)
    zone2 = lsystem.getZone(2)
    zone3 = lsystem.getZone(3)

    assert zone0.is_zone_disabled is False
    assert zone1.is_zone_disabled is False
    assert zone2.is_zone_disabled is False
    assert zone3.is_zone_disabled is False

    lsystem.zoningMode = LENNOX_ZONING_MODE_CENTRAL

    assert zone0.is_zone_disabled is False
    assert zone1.is_zone_disabled is True
    assert zone2.is_zone_disabled is True
    assert zone3.is_zone_disabled is True
