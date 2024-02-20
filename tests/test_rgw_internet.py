"""Test the controllers internet status"""
from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)
from tests.conftest import loadfile


def test_get_rgw_status(api: s30api_async):
    """Test the RGW status"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"

    assert lsystem.relayServerConnected is None
    assert lsystem.internetStatus is None

    message = loadfile("rgw_initial.json", lsystem.sysId)
    api.processMessage(message)

    assert lsystem.relayServerConnected is False
    assert lsystem.internetStatus is False

    message = loadfile("rgw_incremental.json", lsystem.sysId)
    api.processMessage(message)

    assert lsystem.relayServerConnected is True
    assert lsystem.internetStatus is False

    message["Data"]["rgw"]["status"]["relayServerConnected"] = False
    message["Data"]["rgw"]["status"]["internetStatus"] = True
    api.processMessage(message)
    assert lsystem.relayServerConnected is False
    assert lsystem.internetStatus is True
