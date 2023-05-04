"""Tests lennox system methods"""
from lennoxs30api.s30api_async import lennox_system


def test_get_unique_id(api_system_04_furn_ac_zoning):
    """Tests the unique id is pulled differently for S40 vs S30"""
    api = api_system_04_furn_ac_zoning
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.productType == "S30"
    assert lsystem.unique_id == "HD20H10111"
    lsystem.productType = "S40"
    assert lsystem.unique_id == "KL20H56000"
