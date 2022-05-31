from lennoxs30api.s30api_async import (
    LENNOX_CIRCULATE_TIME_MAX,
    LENNOX_CIRCULATE_TIME_MIN,
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, EC_EQUIPMENT_DNS, S30Exception


def test_set_enhancedDehumidificationOvercoolingF(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.enhancedDehumidificationOvercoolingF_enable == True
    assert lsystem.dehumidifierType != None

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=0)
            )
        except S30Exception as e:
            ex = e
        assert ex == None
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
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=2)
            )
        except S30Exception as e:
            ex = e
        assert ex == None
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
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=3)
            )
        except S30Exception as e:
            ex = e
        assert ex == None
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
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=5)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "5" in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingF_min) in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingF_max) in ex.message

    lsystem.enhancedDehumidificationOvercoolingF_enable = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=2)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS

    lsystem.enhancedDehumidificationOvercoolingF_enable = True
    lsystem.dehumidifierType = None
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_f=2)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS


def test_set_enhancedDehumidificationOvercoolingC(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.enhancedDehumidificationOvercoolingC_enable == True
    assert lsystem.dehumidifierType != None

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=0)
            )
        except S30Exception as e:
            ex = e
        assert ex == None
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
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=1.5)
            )
        except S30Exception as e:
            ex = e
        assert ex == None
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
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2)
            )
        except S30Exception as e:
            ex = e
        assert ex == None
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
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2.5)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "5" in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingC_min) in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingC_max) in ex.message

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=1.75)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "5" in ex.message
        assert str(lsystem.enhancedDehumidificationOvercoolingC_inc) in ex.message

    lsystem.enhancedDehumidificationOvercoolingC_enable = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS

    lsystem.enhancedDehumidificationOvercoolingC_enable = True
    lsystem.dehumidifierType = None
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                lsystem.set_enhancedDehumidificationOvercooling(r_c=2)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS
