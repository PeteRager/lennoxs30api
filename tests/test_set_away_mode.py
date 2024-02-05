"""Tests for setting away mode"""
import json
import asyncio
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import lennox_system
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def test_set_manual_away_mode(api):
    """Set manual away mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(lsystem.set_manual_away_mode(True))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        ma = jsbody["Data"]["occupancy"]["manualAway"]
        assert ma is True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(lsystem.set_manual_away_mode(False))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        ma = jsbody["Data"]["occupancy"]["manualAway"]
        assert ma is False


def test_set_smart_away_cancel(api):
    """Cancelling smart away"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.sa_enabled is True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(lsystem.cancel_smart_away())
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        sa_cancel = jsbody["Data"]["occupancy"]["smartAway"]["config"]["cancel"]
        assert sa_cancel is True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        lsystem.sa_enabled = False
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(lsystem.cancel_smart_away())
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0


def test_enable_smart_away(api):
    """Test enabling smart away"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(lsystem.enable_smart_away(True))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        sa_enabled = jsbody["Data"]["occupancy"]["smartAway"]["config"]["enabled"]
        assert sa_enabled is True

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(lsystem.enable_smart_away(False))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        sa_enabled = jsbody["Data"]["occupancy"]["smartAway"]["config"]["enabled"]
        assert sa_enabled is False

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        lsystem.sa_enabled = False
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(lsystem.enable_smart_away("Bogon"))
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0
