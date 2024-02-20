"""Test unit system rounding"""
from lennoxs30api.s30api_async import lennox_system

def test_celsius_round(api):
    """Tests rounding celsius to 0.5 degrees"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.celsius_round(20.7) == 20.5
    assert lsystem.celsius_round(20.0) == 20.0
    assert lsystem.celsius_round(20.8) == 21.0


def test_faren_round(api):
    """Tests rounding fahen to 1.0 degrees"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.faren_round(75.0) == 75
    assert lsystem.faren_round(75.4) == 75
    assert lsystem.faren_round(75.6) == 76
