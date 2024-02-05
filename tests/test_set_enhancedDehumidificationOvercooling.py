"""Test dehumidification"""
import json
import asyncio
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import (
    LENNOX_NONE_STR,
    lennox_system,
)
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, EC_EQUIPMENT_DNS, S30Exception


def test_set_enhanced_dehumidification_overcooling_f(api):
    """Test setting dehumidification overcooling"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.enhancedDehumidificationOvercoolingF_enable is True
    assert lsystem.is_none(lsystem.dehumidifierType) is False

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            lsystem.set_enhancedDehumidificationOvercooling(r_f=0)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["enhancedDehumidificationOvercoolingF"] == 0
        assert config["enhancedDehumidificationOvercoolingC"] == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            lsystem.set_enhancedDehumidificationOvercooling(r_f=2)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["enhancedDehumidificationOvercoolingF"] == 2
        assert config["enhancedDehumidificationOvercoolingC"] == 1

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            lsystem.set_enhancedDehumidificationOvercooling(r_f=3)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["enhancedDehumidificationOvercoolingF"] == 3
        assert config["enhancedDehumidificationOvercoolingC"] == 1.5

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=5)
            )
        assert mock_message_helper.call_count == 0
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert "5" in exc.value.message
        assert str(lsystem.enhancedDehumidificationOvercoolingF_min) in exc.value.message
        assert str(lsystem.enhancedDehumidificationOvercoolingF_max) in exc.value.message

    lsystem.enhancedDehumidificationOvercoolingF_enable = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=2)
            )
        assert mock_message_helper.call_count == 0
        assert exc.value.error_code == EC_EQUIPMENT_DNS

    lsystem.enhancedDehumidificationOvercoolingF_enable = True
    lsystem.dehumidifierType = LENNOX_NONE_STR
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=2)
            )
        assert mock_message_helper.call_count == 0
        assert exc.value.error_code == EC_EQUIPMENT_DNS


def test_set_enhanced_dehumidification_overcooling_c(api):
    """Test celsuis"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.enhancedDehumidificationOvercoolingC_enable is True
    assert lsystem.dehumidifierType is not None

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            lsystem.set_enhancedDehumidificationOvercooling(r_c=0)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["enhancedDehumidificationOvercoolingF"] == 0
        assert config["enhancedDehumidificationOvercoolingC"] == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            lsystem.set_enhancedDehumidificationOvercooling(r_c=1.5)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["enhancedDehumidificationOvercoolingF"] == 3
        assert config["enhancedDehumidificationOvercoolingC"] == 1.5

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            lsystem.set_enhancedDehumidificationOvercooling(r_c=2)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["enhancedDehumidificationOvercoolingF"] == 4
        assert config["enhancedDehumidificationOvercoolingC"] == 2

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2.5)
            )
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "5" in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingC_min) in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingC_max) in ex.message

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=1.75)
            )
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "5" in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingC_inc) in ex.message

    lsystem.enhancedDehumidificationOvercoolingC_enable = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2)
            )
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS

    lsystem.enhancedDehumidificationOvercoolingC_enable = True
    lsystem.dehumidifierType = LENNOX_NONE_STR
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2)
            )
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS
