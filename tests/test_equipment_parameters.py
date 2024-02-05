"""Test the equipment parameters"""
import asyncio
import json
from unittest.mock import patch
from lennoxs30api import s30api_async
from lennoxs30api.lennox_equipment import lennox_equipment_parameter
from lennoxs30api.s30api_async import lennox_system
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception
from tests.conftest import loadfile


def test_equipment_parameter():
    """Tests the equipment parameter class"""
    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    assert par.equipment_id == 10
    assert par.pid == 11
    assert par.name is None
    assert par.defaultValue is None
    assert par.descriptor is None
    assert par.enabled is None
    assert par.format is None
    assert par.value is None
    assert len(par.radio) == 0
    assert par.range_min is None
    assert par.range_max is None
    assert par.range_inc is None
    assert par.string_max is None
    assert par.unit is None

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {}
    par.fromJson(js)
    assert par.equipment_id == 10
    assert par.pid == 11
    assert par.name is None
    assert par.defaultValue is None
    assert par.descriptor is None
    assert par.enabled is None
    assert par.format is None
    assert par.value is None
    assert len(par.radio) == 0
    assert par.range_min is None
    assert par.range_max is None
    assert par.range_inc is None
    assert par.string_max is None
    assert par.unit is None

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {"badParameter": True, "anotherBadOne": 10}
    par.fromJson(js)
    assert par.equipment_id == 10
    assert par.pid == 11
    assert par.name is None
    assert par.defaultValue is None
    assert par.descriptor is None
    assert par.enabled is None
    assert par.format is None
    assert par.value is None
    assert len(par.radio) == 0
    assert par.range_min is None
    assert par.range_max is None
    assert par.range_inc is None
    assert par.string_max is None
    assert par.unit is None

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {"defaultValue": "100"}
    par.fromJson(js)
    assert par.equipment_id == 10
    assert par.pid == 11
    assert par.name is None
    assert par.defaultValue == "100"
    assert par.descriptor is None
    assert par.enabled is None
    assert par.format is None
    assert par.value is None
    assert len(par.radio) == 0
    assert par.range_min is None
    assert par.range_max is None
    assert par.range_inc is None
    assert par.string_max is None
    assert par.unit is None

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {
        "defaultValue": "0.5",
        "descriptor": "range",
        "enabled": False,
        "format": "0_5",
        "name": "4th Stage Differential",
        "pid": 147,
        "range": {"inc": "0.5", "max": "8", "min": "0.5"},
        "unit": "F",
        "value": "0.5",
    }
    par.fromJson(js)
    assert par.equipment_id == 10
    assert par.pid == 147
    assert par.name == "4th Stage Differential"
    assert par.defaultValue == "0.5"
    assert par.descriptor == "range"
    assert par.enabled is False
    assert par.format == "0_5"
    assert par.value == "0.5"
    assert len(par.radio) == 0
    assert par.range_min == "0.5"
    assert par.range_max == "8"
    assert par.range_inc == "0.5"
    assert par.string_max is None
    assert par.unit == "F"

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {
        "defaultValue": "1",
        "descriptor": "radio",
        "enabled": False,
        "format": "uint8",
        "name": "Staged Delay Timers",
        "pid": 164,
        "radio": {
            "max": "1",
            "texts": [{"id": 0, "text": "Disabled"}, {"id": 1, "text": "Enabled"}],
        },
        "unit": "",
        "value": "0",
    }
    par.fromJson(js)
    assert par.equipment_id == 10
    assert par.pid == 164
    assert par.name == "Staged Delay Timers"
    assert par.defaultValue == "1"
    assert par.descriptor == "radio"
    assert par.enabled is False
    assert par.format == "uint8"
    assert par.value == "0"
    assert len(par.radio) == 2
    par.radio[0] = "Disabled"
    par.radio[1] = "Enabled"
    assert par.range_min is None
    assert par.range_max is None
    assert par.range_inc is None
    assert par.string_max is None
    assert par.unit == ""

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {
        "defaultValue": "1",
        "descriptor": "radio",
        "enabled": False,
        "format": "uint8",
        "name": "Staged Delay Timers",
        "pid": 164,
        "radio": {
            "max": "1",
            "texters": [{"id": 0, "text": "Disabled"}, {"id": 1, "text": "Enabled"}],
        },
        "unit": "",
        "value": "0",
    }
    par.fromJson(js)
    assert len(par.radio) == 0

    par: lennox_equipment_parameter = lennox_equipment_parameter(10, 11)
    js = {
        "defaultValue": "1",
        "descriptor": "radio",
        "enabled": False,
        "format": "uint8",
        "name": "Staged Delay Timers",
        "pid": 164,
        "radio": {
            "max": "1",
            "texts": [{"id2": 0, "tdext": "Disabled"}, {"id2": 1, "texdt": "Enabled"}],
        },
        "unit": "",
        "value": "0",
    }
    par.fromJson(js)
    assert len(par.radio) == 0


def test_process_equipment_parameters(api: s30api_async):
    """Test processing equipment parameters"""
    lsystem: lennox_system = api.system_list[0]
    assert len(lsystem.equipment) == 3

    assert len(lsystem.equipment[0].parameters) == 164
    assert len(lsystem.equipment[1].parameters) == 8
    assert len(lsystem.equipment[2].parameters) == 15

    eq = lsystem.equipment[0]
    par = eq.parameters[18]
    assert par.defaultValue == "Subnet Controller"
    assert par.descriptor == "string"
    assert par.enabled is True
    assert par.format == "nts"
    assert par.name == "Equipment Name"
    assert par.pid == 18
    assert len(par.radio) == 1
    assert par.range_inc == ""
    assert par.range_max == ""
    assert par.range_min == ""
    assert par.string_max == "64"
    assert par.unit == ""
    assert par.value == "Subnet Controller"

    par = eq.parameters[72]
    assert par.defaultValue == "0"
    assert par.descriptor == "range"
    assert par.enabled is True
    assert par.format == "16q4"
    assert par.name == "Temp Reading Calibration"
    assert par.pid == 72
    assert len(par.radio) == 0
    assert float(par.range_inc) == 0.5
    assert int(par.range_max) == 5
    assert int(par.range_min) == -5
    assert par.string_max is None
    assert par.unit == "F"
    assert par.value == "0"

    par = eq.parameters[107]
    assert par.defaultValue == "0"
    assert par.descriptor == "radio"
    assert par.enabled is False
    assert par.format == "uint8"
    assert par.name == "Dehumidification Control Mode"
    assert par.pid == 107
    assert len(par.radio) == 3
    assert par.radio[0] == "Display Only"
    assert par.radio[1] == "Basic"
    assert par.radio[2] == "Precision"
    assert par.string_max is None
    assert par.unit == ""
    assert par.value == "0"

    par = eq.parameters[114]
    assert par.defaultValue == "1.5"
    assert par.descriptor == "range"
    assert par.enabled is False
    assert par.format == "16q4"
    assert par.name == "Minimum Gas Heating Off Time"
    assert par.pid == 114
    assert len(par.radio) == 0
    assert float(par.range_inc) == 0.5
    assert int(par.range_max) == 10
    assert float(par.range_min) == 1.5
    assert par.string_max is None
    assert par.unit == "min"
    assert par.value == "1.5"


class DirtySubscription:
    """Mock for a subscription"""
    def __init__(self, system: lennox_system, attr_name: str):
        self.triggered: int = 0
        self.triggered_id = None
        self.id = attr_name
        system.registerOnUpdateCallbackEqParameters(self.update_callback, [attr_name])

    def update_callback(self, par_id: str):
        """Subscription callback"""
        self.triggered = self.triggered + 1
        self.triggered_id = par_id


def test_process_equipment_parameters_subscription(api: s30api_async):
    """Tests the equipment parameters subscription"""
    system: lennox_system = api.system_list[0]
    assert len(system.equipment) == 3

    assert len(system.equipment[0].parameters) == 164
    assert len(system.equipment[1].parameters) == 8
    assert len(system.equipment[2].parameters) == 15

    par = system.equipment[0].parameters[114]
    assert par.value == "1.5"
    sub = DirtySubscription(system, "0_114")
    assert sub.triggered == 0
    assert sub.triggered_id is None
    message = loadfile("equipments_0_pid_114_update.json", system.sysId)
    system.processMessage(message)
    assert sub.triggered == 1
    assert sub.triggered_id == "0_114"
    assert par.value == "15"


def test_equipment_parameters_validate_and_translate_radio(api: s30api_async):
    """Verify translation of parameter radio buttons"""
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[107]

    assert parameter.validate_and_translate("Display Only") == 0
    assert parameter.validate_and_translate("Basic") == 1
    assert parameter.validate_and_translate("Precision") == 2

    ex = None
    try:
        parameter.validate_and_translate("BadValue") == 2
    except S30Exception as e:
        ex = e

    assert ex is not None
    assert ex.error_code == EC_BAD_PARAMETERS
    assert "BadValue" in ex.message
    assert str(parameter.pid) in ex.message
    assert str(parameter.name) in ex.message
    assert str("Display Only") in ex.message
    assert str("Basic") in ex.message
    assert str("Precision") in ex.message


def test_equipment_parameters_validate_and_translate_range(api):
    """Verify parameter range validation"""
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[114]

    assert parameter.validate_and_translate("10") == "10"
    assert parameter.validate_and_translate("1.5") == "1.5"
    assert parameter.validate_and_translate("2.0") == "2.0"
    assert parameter.validate_and_translate("2.5") == "2.5"

    ex = None
    try:
        parameter.validate_and_translate("BadValue") == 2
    except S30Exception as e:
        ex = e
    assert ex is not None
    assert ex.error_code == EC_BAD_PARAMETERS
    assert "BadValue" in ex.message
    assert "could not convert" in ex.message
    assert str(parameter.pid) in ex.message
    assert str(parameter.range_inc) in ex.message
    assert str(parameter.range_max) in ex.message
    assert str(parameter.range_min) in ex.message
    assert str(parameter.name) in ex.message

    ex = None
    try:
        parameter.validate_and_translate("1.0") == "1.0"
    except S30Exception as e:
        ex = e
    assert ex is not None
    assert ex.error_code == EC_BAD_PARAMETERS
    assert "1.0" in ex.message
    assert str(parameter.pid) in ex.message
    assert str(parameter.range_inc) in ex.message
    assert str(parameter.range_max) in ex.message
    assert str(parameter.range_min) in ex.message
    assert str(parameter.name) in ex.message
    assert "between" in ex.message

    ex = None
    try:
        parameter.validate_and_translate("10.5") == "1.0"
    except S30Exception as e:
        ex = e
    assert ex is not None
    assert ex.error_code == EC_BAD_PARAMETERS
    assert "10.5" in ex.message
    assert str(parameter.pid) in ex.message
    assert str(parameter.range_inc) in ex.message
    assert str(parameter.range_max) in ex.message
    assert str(parameter.range_min) in ex.message
    assert str(parameter.name) in ex.message
    assert "between" in ex.message

    ex = None
    try:
        parameter.validate_and_translate("2.25") == "1.0"
    except S30Exception as e:
        ex = e
    assert ex is not None
    assert ex.error_code == EC_BAD_PARAMETERS
    assert "2.25" in ex.message
    assert str(parameter.pid) in ex.message
    assert str(parameter.range_inc) in ex.message
    assert str(parameter.range_max) in ex.message
    assert str(parameter.range_min) in ex.message
    assert str(parameter.name) in ex.message
    assert "multiple" in ex.message


def test_equipment_parameters_validate_and_translate_bad_descriptor(api):
    """Test error conditions"""
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[114]
    parameter.descriptor = "bad_type"
    ex = None
    try:
        parameter.validate_and_translate("10.0") == 2
    except S30Exception as e:
        ex = e
    assert ex is not None
    assert ex.error_code == EC_BAD_PARAMETERS
    assert "bad_type" in ex.message
    assert "unsupported descriptor" in ex.message
    assert str(parameter.pid) in ex.message
    assert str(parameter.name) in ex.message


def test_set_equipment_parameter_value(api: s30api_async):
    """Test setting the equipment parameter value"""
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[1]
    with patch.object(system, "set_parameter_value") as set_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                system.set_equipment_parameter_value(1, 44, "325")
            )
        except S30Exception as e:
            ex = e
        assert ex is None
        assert set_parameter_value.call_count == 1
        assert set_parameter_value.call_args[0][0] == equipment.equipType
        assert set_parameter_value.call_args[0][1] == 44
        assert set_parameter_value.call_args[0][2] == "325"


def test_set_equipment_parameter_value_bad_equipment(api):
    """Test setting parameter with bad values"""
    system: lennox_system = api.system_list[0]
    with patch.object(system, "set_parameter_value") as set_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                system.set_equipment_parameter_value(10, 44, "325")
            )
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert set_parameter_value.call_count == 0
        assert "cannot find equipment" in ex.message
        assert "10" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_equipment_parameter_value_bad_pid(api: s30api_async):
    """Test setting equipment parameters to bad values"""
    system: lennox_system = api.system_list[0]
    with patch.object(system, "set_parameter_value") as set_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                system.set_equipment_parameter_value(1, 440, "325")
            )
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert set_parameter_value.call_count == 0
        assert "cannot find parameter" in ex.message
        assert "1" in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_equipment_parameter_value_disabled_pid(api: s30api_async):
    """Test setting a disabled parameter"""
    system: lennox_system = api.system_list[0]
    equipment = system.equipment[1]
    parameter = equipment.parameters[44]
    parameter.enabled = False
    with patch.object(system, "set_parameter_value") as set_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                system.set_equipment_parameter_value(1, 44, "325")
            )
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert set_parameter_value.call_count == 0
        assert "cannot set disabled parameter" in ex.message
        assert "1" in ex.message
        assert "325" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_equipment_parameter_value_bad_value(api: s30api_async):
    """Test setting parameters to bad values"""
    system: lennox_system = api.system_list[0]
    with patch.object(system, "set_parameter_value") as set_parameter_value:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                system.set_equipment_parameter_value(1, 44, "32500")
            )
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert set_parameter_value.call_count == 0
        assert "32500" in ex.message
        assert ex.error_code == EC_BAD_PARAMETERS


def test_set_parameter_value(api):
    """Test setting parameter value"""
    system: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(system.set_parameter_value(19, 44, "325"))
        assert mock_message_helper.call_count == 1
        assert mock_message_helper.await_args[0][0] == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        assert (
            mock_message_helper.call_args_list[0][1]["additional_parameters"]
            == "/systemControl"
        )
        par_update = jsbody["Data"]["systemControl"]["parameterUpdate"]
        assert par_update["et"] == 19
        assert par_update["pid"] == 44
        assert par_update["value"] == "325"
