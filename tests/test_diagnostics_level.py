"""Tests the controller diagnostic level"""
from lennoxs30api.s30api_async import lennox_system, s30api_async
from tests.conftest import loadfile

def test_get_diagnostic_level(api: s30api_async):
    """Tests getting the diagnostic level from message"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.diagLevel is None

    message = loadfile("systemControl_diag_level_0.json")
    message["SenderID"] = lsystem.sysId
    api.processMessage(message)
    assert lsystem.diagLevel == 0

    message = loadfile("systemControl_diag_level_1.json")
    message["SenderID"] = lsystem.sysId
    api.processMessage(message)
    assert lsystem.diagLevel == 1
