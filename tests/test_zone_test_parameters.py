import asyncio
import json
from unittest import mock
from unittest.mock import patch
from lennoxs30api.lennox_equipment import (
    lennox_equipment_parameter,
)
from lennoxs30api.s30api_async import (
    PID_ZONE_1_BLOWER_CFM,
    PID_ZONE_8_HEATING_CFM,
    lennox_system,
)
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception
from tests.conftest import loadfile


def test_set_zone_test_parameter_value(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]

    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(
                    PID_ZONE_1_BLOWER_CFM, "375.0", True
                )
            )
        except S30Exception as e:
            ex = e
        assert ex is None
        assert _internal_set_zone_test_parameter_value.call_count == 1
        assert (
            _internal_set_zone_test_parameter_value.call_args[0][0]
            == PID_ZONE_1_BLOWER_CFM
        )
        assert _internal_set_zone_test_parameter_value.call_args[0][1] == "375.0"
        assert _internal_set_zone_test_parameter_value.call_args[0][2] == True

    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(
                    PID_ZONE_1_BLOWER_CFM, "375.0", False
                )
            )
        except S30Exception as e:
            ex = e
        assert ex is None
        assert _internal_set_zone_test_parameter_value.call_count == 1
        assert (
            _internal_set_zone_test_parameter_value.call_args[0][0]
            == PID_ZONE_1_BLOWER_CFM
        )
        assert _internal_set_zone_test_parameter_value.call_args[0][1] == "375.0"
        assert _internal_set_zone_test_parameter_value.call_args[0][2] == False


def test_set_zone_test_parameter_value_bad_pid(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[0]
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(100000, "325", False)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
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
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(
                    PID_ZONE_1_BLOWER_CFM, "325", False
                )
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "cannot find parameter" in ex.message
        assert str(PID_ZONE_1_BLOWER_CFM) in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_zone_test_parameter_value_no_eq_0(api):
    system: lennox_system = api.system_list[0]
    system.equipment.pop(0)
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "325", True)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "annot find equipment with equipment_id" in ex.message
        assert "0" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_zone_test_parameter_value_disabled_pid(api):
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[0]
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(PID_ZONE_1_BLOWER_CFM, "325", True)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "cannot set disabled parameter" in ex.message
        assert str(PID_ZONE_1_BLOWER_CFM) in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_zone_test_parameter_value_bad_value(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    with patch.object(
        system, "_internal_set_zone_test_parameter_value"
    ) as _internal_set_zone_test_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                system.set_zone_test_parameter_value(
                    PID_ZONE_1_BLOWER_CFM, "444000", False
                )
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert _internal_set_zone_test_parameter_value.call_count == 0
        assert "444000" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_internal_set_zone_test_parameter_value(api):
    system: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            system._internal_set_zone_test_parameter_value(
                PID_ZONE_1_BLOWER_CFM, "400", True
            )
        )
        assert mock_message_helper.call_count == 1
        assert mock_message_helper.await_args[0][0] == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        assert (
            mock_message_helper.call_args_list[0][1]["additional_parameters"]
            == "/systemControl"
        )
        par_update = jsbody["Data"]["systemControl"]["zoneTestControl"]
        assert par_update["enable"] == True
        assert par_update["parameterNumber"] == PID_ZONE_1_BLOWER_CFM
        assert par_update["value"] == "400"

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            system._internal_set_zone_test_parameter_value(
                PID_ZONE_1_BLOWER_CFM, "400", False
            )
        )
        assert mock_message_helper.call_count == 1
        assert mock_message_helper.await_args[0][0] == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        assert (
            mock_message_helper.call_args_list[0][1]["additional_parameters"]
            == "/systemControl"
        )
        par_update = jsbody["Data"]["systemControl"]["zoneTestControl"]
        assert par_update["enable"] == False
        assert par_update["parameterNumber"] == PID_ZONE_1_BLOWER_CFM
        assert par_update["value"] == "400"
