"""Tests setting circulation mode"""
import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import (
    LENNOX_CIRCULATE_TIME_MAX,
    LENNOX_CIRCULATE_TIME_MIN,
    lennox_system,
)
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception

@pytest.mark.asyncio
async def test_set_circulate_time(api):
    """Test setting circulate time"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.numberOfZones > 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_circulateTime(LENNOX_CIRCULATE_TIME_MAX - 1)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["circulateTime"] == LENNOX_CIRCULATE_TIME_MAX - 1

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_circulateTime(LENNOX_CIRCULATE_TIME_MIN + 1)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        config = jsbody["Data"]["system"]["config"]
        assert config["circulateTime"] == LENNOX_CIRCULATE_TIME_MIN + 1

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_circulateTime(LENNOX_CIRCULATE_TIME_MAX + 10)
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert str(LENNOX_CIRCULATE_TIME_MAX + 10) in ex.message
        assert str(LENNOX_CIRCULATE_TIME_MAX) in ex.message
        assert str(LENNOX_CIRCULATE_TIME_MIN) in ex.message

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_circulateTime("NOT AN INTEGER")
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "NOT AN INTEGER" in ex.message
        assert str(LENNOX_CIRCULATE_TIME_MAX) in ex.message
        assert str(LENNOX_CIRCULATE_TIME_MIN) in ex.message
