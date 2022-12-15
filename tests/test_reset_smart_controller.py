from lennoxs30api.s30api_async import (
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def test_reset_smart_controller(api):
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(lsystem.reset_smart_controller())
        assert mock_message_helper.call_count == 1

        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        assert (
            mock_message_helper.call_args_list[0][1]["additional_parameters"]
            == "/resetLcc"
        )

        state = jsbody["Data"]["resetLcc"]["state"]
        assert state == "reset"
