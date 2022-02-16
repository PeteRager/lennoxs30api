from lennoxs30api.s30api_async import (
    s30api_async,
)

import asyncio
import aiohttp
import logging

from unittest.mock import patch

from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_HTTP_ERR,
    EC_UNAUTHORIZED,
    S30Exception,
)


def test_login_client_response_error(api: s30api_async, caplog):
    with patch.object(api, "post") as mock_post:
        mock_post.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="unexpected content-length header",
            history={},
        )
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.ERROR):
            caplog.clear()
            try:
                result = loop.run_until_complete(api.login())
            except S30Exception as e:
                assert e.error_code == EC_COMMS_ERROR
                assert "unexpected content-length header" in e.message
                error = True
            assert error == True

    with patch.object(api, "post") as mock_post:
        mock_post.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="some other error",
            history={},
        )
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.ERROR):
            caplog.clear()
            error = False
            try:
                result = loop.run_until_complete(api.login())
            except S30Exception as e:
                assert e.error_code == EC_COMMS_ERROR
                assert "some other error" in e.message
                error = True
            assert error == True
            assert len(caplog.records) == 0

    with patch.object(api, "post") as mock_post:
        mock_post.side_effect = aiohttp.ServerDisconnectedError()
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.ERROR):
            assert api.metrics.last_error_time is None
            caplog.clear()
            error = False
            try:
                result = loop.run_until_complete(api.login())
            except S30Exception as e:
                assert e.error_code == EC_COMMS_ERROR
                assert "Server Disconnected" in e.message
                error = True
            assert error == True
            assert len(caplog.records) == 0
