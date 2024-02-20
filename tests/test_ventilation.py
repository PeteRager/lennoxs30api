"""Tests ventilation"""
# pylint: disable=line-too-long
import json
from unittest.mock import patch

import pytest

from lennoxs30api.s30api_async import (
    LENNOX_NONE_STR,
    LENNOX_VENTILATION_1_SPEED_ERV,
    LENNOX_VENTILATION_1_SPEED_HRV,
    LENNOX_VENTILATION_2_SPEED_ERV,
    LENNOX_VENTILATION_2_SPEED_HRV,
    LENNOX_VENTILATION_DAMPER,
    lennox_system,
)
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, EC_EQUIPMENT_DNS, S30Exception


def test_has_ventilation(api):
    """Test the different ventilation types"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() is False
    system.ventilationUnitType = None
    assert system.supports_ventilation() is False
    system.ventilationUnitType = LENNOX_VENTILATION_1_SPEED_ERV
    assert system.supports_ventilation() is True
    system.ventilationUnitType = LENNOX_VENTILATION_2_SPEED_ERV
    assert system.supports_ventilation() is True
    system.ventilationUnitType = LENNOX_VENTILATION_1_SPEED_HRV
    assert system.supports_ventilation() is True
    system.ventilationUnitType = LENNOX_VENTILATION_2_SPEED_HRV
    assert system.supports_ventilation() is True
    system.ventilationUnitType = LENNOX_VENTILATION_DAMPER
    assert system.supports_ventilation() is True


@pytest.mark.asyncio
async def test_set_ventilation_on(api):
    """Test turning ventilation on"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await system.ventilation_on()
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["ventilationMode"] == "on"

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await system.ventilation_on()
        ex: S30Exception = exc.value
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message


@pytest.mark.asyncio
async def test_set_ventilation_off(api):
    """Tests turning the ventilation off"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await system.ventilation_off()
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["ventilationMode"] == "off"

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await system.ventilation_off()
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex is not None
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message


@pytest.mark.asyncio
async def test_set_ventilation_installer(api):
    """Tests setting ventilation to installer mode"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await system.ventilation_installer()
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["ventilationMode"] == "installer"

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await system.ventilation_installer()
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message


@pytest.mark.asyncio
async def test_set_ventilation_timed(api):
    """Test setting timed ventilation"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await system.ventilation_timed(600)
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["systemController"]
        assert config["command"] == "ventilateNow 600"

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await system.ventilation_timed(-600)
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "-600" in ex.message

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await system.ventilation_timed("ABC")
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex is not None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "ABC" in ex.message

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await system.ventilation_timed(600)
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex is not None
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message
