"""Tests the zonetest methods"""
# pylint: disable=protected-access
import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import (
    PID_ZONE_1_BLOWER_CFM,
    PID_ZONE_8_HEATING_CFM,
    lennox_system,
)
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


@pytest.mark.asyncio
async def test_set_zone_test_parameter_value(api_system_04_furn_ac_zoning):
    """Tests zone test parameter value"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]

    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        await system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "375.0", True)
        assert _internal_set_zone_test_parameter_value.call_count == 1
        assert (
            _internal_set_zone_test_parameter_value.call_args[0][0]
            == PID_ZONE_1_BLOWER_CFM
        )
        assert _internal_set_zone_test_parameter_value.call_args[0][1] == "375.0"
        assert _internal_set_zone_test_parameter_value.call_args[0][2] is True

    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        await system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "375.0", False)
        assert _internal_set_zone_test_parameter_value.call_count == 1
        assert (
            _internal_set_zone_test_parameter_value.call_args[0][0]
            == PID_ZONE_1_BLOWER_CFM
        )
        assert _internal_set_zone_test_parameter_value.call_args[0][1] == "375.0"
        assert _internal_set_zone_test_parameter_value.call_args[0][2] is False


@pytest.mark.asyncio
async def test_set_zone_test_parameter_value_bad_pid(api_system_04_furn_ac_zoning):
    """Test a bad parameter id being targeted"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[0]
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        with pytest.raises(S30Exception) as exc:
            await system.set_zone_test_parameter_value(100000, "325", False)
        ex: S30Exception = exc.value
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "must be between" in ex.message
        assert "100000" in ex.message
        assert str(PID_ZONE_1_BLOWER_CFM) in ex.message
        assert str(PID_ZONE_8_HEATING_CFM) in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS

    equipment.parameters.pop(PID_ZONE_1_BLOWER_CFM)
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        with pytest.raises(S30Exception) as exc:
            await system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "325", False)
        ex: S30Exception = exc.value
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "cannot find parameter" in ex.message
        assert str(PID_ZONE_1_BLOWER_CFM) in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


@pytest.mark.asyncio
async def test_set_zone_test_parameter_value_no_eq_0(api):
    """Test method call when equipment does not exist"""
    system: lennox_system = api.system_list[0]
    system.equipment.pop(0)
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        with pytest.raises(S30Exception) as exc:
            await system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "325", True)
        ex: S30Exception = exc.value
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "annot find equipment with equipment_id" in ex.message
        assert "0" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS



@pytest.mark.asyncio
async def test_set_zone_test_parameter_value_disabled_pid(api):
    """Test setting a disabled parameter"""
    system: lennox_system = api.system_list[0]
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        with pytest.raises(S30Exception) as exc:
            await system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "325", True)
        ex: S30Exception = exc.value
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "cannot set disabled parameter" in ex.message
        assert str(PID_ZONE_1_BLOWER_CFM) in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS



@pytest.mark.asyncio
async def test_set_zone_test_parameter_value_bad_value(api_system_04_furn_ac_zoning):
    """Test setting the parameter to an invalid value"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        with pytest.raises(S30Exception) as exc:
            await system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "444000", False)
        ex: S30Exception = exc.value
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "444000" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS



@pytest.mark.asyncio
async def test_internal_set_zone_test_parameter_value(api):
    """Tests the internal helper function"""
    system: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await system._internal_set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "400", True)
        assert mock_message_helper.call_count == 1
        assert mock_message_helper.await_args[0][0] == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        assert (
            mock_message_helper.call_args_list[0][1]["additional_parameters"]
            == "/systemControl"
        )
        par_update = jsbody["Data"]["systemControl"]["zoneTestControl"]
        assert par_update["enable"] is True
        assert par_update["parameterNumber"] == PID_ZONE_1_BLOWER_CFM
        assert par_update["value"] == "400"

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await system._internal_set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "400", False)
        assert mock_message_helper.call_count == 1
        assert mock_message_helper.await_args[0][0] == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        assert (
            mock_message_helper.call_args_list[0][1]["additional_parameters"]
            == "/systemControl"
        )
        par_update = jsbody["Data"]["systemControl"]["zoneTestControl"]
        assert par_update["enable"] is False
        assert par_update["parameterNumber"] == PID_ZONE_1_BLOWER_CFM
        assert par_update["value"] == "400"
