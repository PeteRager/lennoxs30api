import logging
from lennoxs30api.s30api_async import (
    LENNOX_ZONING_MODE_CENTRAL,
    lennox_system,
    s30api_async,
)

from tests.conftest import loadfile


def test_test_zone_enabled(api: s30api_async):
    lsystem: lennox_system = api.getSystems()[0]
    zone0 = lsystem.getZone(0)
    zone1 = lsystem.getZone(1)
    zone2 = lsystem.getZone(2)
    zone3 = lsystem.getZone(3)

    assert zone0.is_zone_disabled == False
    assert zone1.is_zone_disabled == False
    assert zone2.is_zone_disabled == False
    assert zone3.is_zone_disabled == False

    lsystem.zoningMode = LENNOX_ZONING_MODE_CENTRAL

    assert zone0.is_zone_disabled == False
    assert zone1.is_zone_disabled == True
    assert zone2.is_zone_disabled == True
    assert zone3.is_zone_disabled == True
