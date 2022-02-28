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


def test_client_response_error(api: s30api_async, caplog):
    api.metrics.reset()
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="unexpected content-length header",
            history={},
        )
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            assert api.metrics.last_error_time is None
            caplog.clear()
            try:
                result = loop.run_until_complete(api.messagePump())
            except S30Exception as e:
                assert e.error_code == EC_COMMS_ERROR
                assert "unexpected content-length header" in e.message
                error = True
            assert error == True
            assert api.metrics.client_response_errors == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None

    api.metrics.reset()
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="some other error",
            history={},
        )
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            assert api.metrics.last_error_time is None
            caplog.clear()
            error = False
            try:
                result = loop.run_until_complete(api.messagePump())
            except S30Exception as e:
                assert e.error_code == EC_COMMS_ERROR
                assert "some other error" in e.message
                error = True
            assert error == True
            assert len(caplog.records) == 0
            assert api.metrics.client_response_errors == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None

    api.metrics.reset()
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = aiohttp.ServerDisconnectedError()
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            assert api.metrics.last_error_time is None
            caplog.clear()
            error = False
            try:
                result = loop.run_until_complete(api.messagePump())
            except S30Exception as e:
                assert e.error_code == EC_COMMS_ERROR
                assert "Server Disconnected" in e.message
                error = True
            assert error == True
            assert len(caplog.records) == 0
            assert api.metrics.client_response_errors == 0
            assert api.metrics.server_disconnects == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None


def test_client_connection_error(api: s30api_async, caplog):
    api.metrics.reset()
    api.url_retrieve = "http://0.0.0.0:8888/test.html"
    api._session = aiohttp.ClientSession()
    loop = asyncio.get_event_loop()
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        error = False
        try:
            result = loop.run_until_complete(api.messagePump())
        except S30Exception as e:
            assert e.error_code == EC_COMMS_ERROR
            assert "0.0.0.0" in e.message
            assert "8888" in e.message
            error = True
        assert error == True
        assert len(caplog.records) == 0
        assert api.metrics.client_response_errors == 1
        assert api.metrics.server_disconnects == 0
        assert api.metrics.error_count == 1
        assert api.metrics.last_error_time is not None


class http_resp:
    def __init__(self, status):
        self.status = status
        self.content_length = 100


def test_client_http_204(api: s30api_async, caplog):
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = http_resp(204)
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            error = False
            result = loop.run_until_complete(api.messagePump())
            assert result == False
            assert len(caplog.records) == 0


def test_client_http_502(api: s30api_async, caplog):
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = http_resp(502)
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            error = False
            try:
                result = loop.run_until_complete(api.messagePump())
            except S30Exception as e:
                assert e.error_code == EC_HTTP_ERR
                assert e.reference == 502
                error = True
            assert error == True
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == "INFO"


def test_client_http_401(api: s30api_async, caplog):
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = http_resp(401)
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            error = False
            try:
                result = loop.run_until_complete(api.messagePump())
            except S30Exception as e:
                assert e.error_code == EC_UNAUTHORIZED
                assert e.reference == 401
                error = True
            assert error == True
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == "INFO"


def test_client_timeout_error(api: s30api_async, caplog):
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = asyncio.TimeoutError()
        loop = asyncio.get_event_loop()
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            ex: S30Exception = None
            try:
                result = loop.run_until_complete(api.messagePump())
            except S30Exception as e:
                ex = e
            assert ex != None
            assert ex.error_code == EC_COMMS_ERROR
            assert "TimeoutError" in ex.message
            assert api.metrics.client_response_errors == 0
            assert api.metrics.server_disconnects == 0
            assert api.metrics.timeouts == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None
