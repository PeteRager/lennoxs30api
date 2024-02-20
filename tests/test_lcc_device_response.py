"""Tests the lcc serial numbers"""
from lennoxs30api.s30api_async import s30api_async, lennox_system

def test_process_device_serial_number(api_device_lcc: s30api_async):
    """Test processing the device serial number"""
    api = api_device_lcc
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "LCC"
    assert lsystem.serialNumber == "HD21212121"
    assert lsystem.unique_id == "HD21212121"
    assert lsystem.softwareVersion == "3.81.207"
