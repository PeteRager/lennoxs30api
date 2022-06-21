from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)

import json
import os

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception
from tests.conftest import loadfile


def test_get_rgw_status(api: s30api_async):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"

    assert lsystem.relayServerConnected == None
    assert lsystem.internetStatus == None

    message = loadfile("relay_internet_status.json")
    message["SenderID"] = lsystem.sysId
    api.processMessage(message)

    assert lsystem.relayServerConnected == False
    assert lsystem.internetStatus == False

    message["Data"]["rgw"]["status"]["relayServerConnected"] = True
    api.processMessage(message)
    assert lsystem.relayServerConnected == True
    assert lsystem.internetStatus == False

    message["Data"]["rgw"]["status"]["relayServerConnected"] = False
    message["Data"]["rgw"]["status"]["internetStatus"] = True
    api.processMessage(message)
    assert lsystem.relayServerConnected == False
    assert lsystem.internetStatus == True
