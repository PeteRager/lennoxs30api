from lennoxs30api.s30api_async import (
    LENNOX_NONE_STR,
    LENNOX_VENTILATION_1_SPEED_ERV,
    LENNOX_VENTILATION_1_SPEED_HRV,
    LENNOX_VENTILATION_2_SPEED_ERV,
    LENNOX_VENTILATION_2_SPEED_HRV,
    LENNOX_VENTILATION_DAMPER,
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, EC_EQUIPMENT_DNS, S30Exception


def test_has_ventilation(api):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() == False
    system.ventilationUnitType = None
    assert system.supports_ventilation() == False
    system.ventilationUnitType = LENNOX_VENTILATION_1_SPEED_ERV
    assert system.supports_ventilation() == True
    system.ventilationUnitType = LENNOX_VENTILATION_2_SPEED_ERV
    assert system.supports_ventilation() == True
    system.ventilationUnitType = LENNOX_VENTILATION_1_SPEED_HRV
    assert system.supports_ventilation() == True
    system.ventilationUnitType = LENNOX_VENTILATION_2_SPEED_HRV
    assert system.supports_ventilation() == True
    system.ventilationUnitType = LENNOX_VENTILATION_DAMPER
    assert system.supports_ventilation() == True


def test_set_ventilation_on(api):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_on())
        except S30Exception as e:
            ex = e
        assert ex == None
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["ventilationMode"] == "on"

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() == False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_on())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message


def test_set_ventilation_off(api):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_off())
        except S30Exception as e:
            ex = e
        assert ex == None
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["ventilationMode"] == "off"

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() == False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_off())
        except S30Exception as e:
            ex = e
        assert mock_message_helper.call_count == 0
        assert ex != None
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message


def test_set_ventilation_timed(api):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    assert system.supports_ventilation()
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_timed(600))
        except S30Exception as e:
            ex = e
        assert ex == None
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == system.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["systemController"]
        assert config["command"] == "ventilateNow 600"

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_timed(-600))
        except S30Exception as e:
            ex = e
        assert mock_message_helper.call_count == 0
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "-600" in ex.message

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_timed("ABC"))
        except S30Exception as e:
            ex = e
        assert mock_message_helper.call_count == 0
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "ABC" in ex.message

    system.ventilationUnitType = LENNOX_NONE_STR
    assert system.supports_ventilation() == False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.ventilation_timed(600))
        except S30Exception as e:
            ex = e
        assert mock_message_helper.call_count == 0
        assert ex != None
        assert ex.error_code == EC_EQUIPMENT_DNS
        assert LENNOX_NONE_STR in ex.message
