"""Tests dehumidification modes"""
# pylint: disable=line-too-long
import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import (
    LENNOX_DEHUMIDIFICATION_MODES,
    LENNOX_NONE_STR,
    lennox_system,
)
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, EC_EQUIPMENT_DNS, S30Exception


@pytest.mark.asyncio
async def test_set_dehumidification_mode(api):
    """Tests setting the dehumidification mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.is_none(lsystem.dehumidifierType) is False
    for mode in LENNOX_DEHUMIDIFICATION_MODES:
        with patch.object(api, "publishMessageHelper") as mock_message_helper:
            await lsystem.set_dehumidificationMode(mode)
            assert mock_message_helper.call_count == 1
            arg0 = mock_message_helper.await_args[0][0]
            assert arg0 == lsystem.sysId
            arg1 = mock_message_helper.await_args[0][1]
            jsbody = json.loads("{" + arg1 + "}")

            config = jsbody["Data"]["system"]["config"]
            assert config["dehumidificationMode"] == mode

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_dehumidificationMode("INVALID_MODE")
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "INVALID_MODE" in ex.message
        assert str(LENNOX_DEHUMIDIFICATION_MODES) in ex.message

    lsystem.dehumidifierType = LENNOX_NONE_STR
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_dehumidificationMode("LENNOX_DEHUMIDIFICATION_MODE_HIGH")
        ex: S30Exception = exc.value
        assert mock_message_helper.call_count == 0
        assert ex.error_code == EC_EQUIPMENT_DNS
