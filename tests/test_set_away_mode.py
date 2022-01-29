from lennoxs30api.s30api_async import (
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def test_set_manual_mode(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(lsystem.set_manual_away_mode(True))
        mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        ma = jsbody["Data"]["occupancy"]["manualAway"]
        assert ma == True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(lsystem.set_manual_away_mode(False))
        mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        ma = jsbody["Data"]["occupancy"]["manualAway"]
        assert ma == False


def test_set_smart_away_cancel(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.sa_enabled == True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(lsystem.cancel_smart_away())
        mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        sa_cancel = jsbody["Data"]["occupancy"]["smartAway"]["config"]["cancel"]
        assert sa_cancel == True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        lsystem.sa_enabled = False
        loop = asyncio.get_event_loop()
        error = False
        try:
            result = loop.run_until_complete(lsystem.cancel_smart_away())
        except S30Exception as e:
            error = True
            ec = e.error_code
        assert error == True
        assert ec == EC_BAD_PARAMETERS
        mock_message_helper.call_count == 0


def test_enable_smart_away(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(lsystem.enable_smart_away(True))
        mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        sa_enabled = jsbody["Data"]["occupancy"]["smartAway"]["config"]["enabled"]
        assert sa_enabled == True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(lsystem.enable_smart_away(False))
        mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        sa_enabled = jsbody["Data"]["occupancy"]["smartAway"]["config"]["enabled"]
        assert sa_enabled == False

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        lsystem.sa_enabled = False
        loop = asyncio.get_event_loop()
        error = False
        try:
            result = loop.run_until_complete(lsystem.enable_smart_away("Bogon"))
        except S30Exception as e:
            error = True
            ec = e.error_code
        assert error == True
        assert ec == EC_BAD_PARAMETERS
        mock_message_helper.call_count == 0
