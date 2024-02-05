"""Test diagnostic level setting"""
import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import lennox_system
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


@pytest.mark.asyncio
async def test_set_diagnostic_level(api):
    """Test setting diagnostic level"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_diagnostic_level(3)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    for test_level in (0, 1, 2):
        with patch.object(api, "requestDataHelper") as mock_request_data_helper:
            with patch.object(api, "publishMessageHelper") as mock_message_helper:
                await lsystem.set_diagnostic_level(test_level)
                assert mock_message_helper.call_count == 1
                arg0 = mock_message_helper.await_args[0][0]
                assert arg0 == lsystem.sysId
                arg1 = mock_message_helper.await_args[0][1]
                jsbody = json.loads("{" + arg1 + "}")

                level = jsbody["Data"]["systemControl"]["diagControl"]["level"]
                assert level == test_level

                assert mock_request_data_helper.call_count == 1
                arg0 = mock_request_data_helper.await_args[0][0]
                assert arg0 == lsystem.sysId
                arg1 = mock_request_data_helper.await_args[0][1]
                jsbody = json.loads("{" + arg1 + "}")
                assert jsbody["AdditionalParameters"]["JSONPath"] == "/systemControl"

    with patch.object(api, "requestDataHelper") as mock_request_data_helper:
        with patch.object(api, "publishMessageHelper") as mock_message_helper:
            await lsystem.set_diagnostic_level(1.0)
            assert mock_message_helper.call_count == 1
            arg0 = mock_message_helper.await_args[0][0]
            assert arg0 == lsystem.sysId
            arg1 = mock_message_helper.await_args[0][1]
            jsbody = json.loads("{" + arg1 + "}")

            level = jsbody["Data"]["systemControl"]["diagControl"]["level"]
            assert level == 1

            assert mock_request_data_helper.call_count == 1
            arg0 = mock_request_data_helper.await_args[0][0]
            assert arg0 == lsystem.sysId
            arg1 = mock_request_data_helper.await_args[0][1]
            jsbody = json.loads("{" + arg1 + "}")
            assert jsbody["AdditionalParameters"]["JSONPath"] == "/systemControl"
