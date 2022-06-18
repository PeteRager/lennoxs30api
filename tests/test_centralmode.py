from lennoxs30api.s30api_async import (
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def test_set_central_mode_multizone(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.numberOfZones > 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(lsystem.centralMode_on())
        except S30Exception as e:
            ex = e
        assert ex == None
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["centralMode"] == True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(lsystem.centralMode_off())
        except S30Exception as e:
            ex = e
        assert ex == None
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["centralMode"] == False


def test_set_central_mode_singlezone(api):
    lsystem: lennox_system = api.getSystems()[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"
    assert lsystem.numberOfZones == 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(lsystem.centralMode_on())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(lsystem.centralMode_off())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0
