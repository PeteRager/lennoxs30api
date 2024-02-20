"""Tests processing system uptime"""
import logging
from lennoxs30api.s30api_async import s30api_async, lennox_system
from tests.conftest import loadfile

def test_system_uptime(api: s30api_async, caplog):
    """Test system uptime"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.sysUpTime == 698820

    with caplog.at_level(logging.WARNING):
        caplog.clear()
        data = loadfile("system_uptime.json")
        api.processMessage(data)
        assert lsystem.sysUpTime == 5039520
        assert len(caplog.records) == 0

        data = loadfile("system_uptime_reset.json")
        api.processMessage(data)
        assert lsystem.sysUpTime == 500
        assert len(caplog.records) == 1
