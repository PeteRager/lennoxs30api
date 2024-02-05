"""Test receive errors"""
# pylint: disable=protected-access
import asyncio
import logging
from unittest.mock import patch
import aiohttp
import pytest
from lennoxs30api.s30api_async import s30api_async
from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_HTTP_ERR,
    EC_UNAUTHORIZED,
    S30Exception,
)


@pytest.mark.asyncio
async def test_client_response_error(api: s30api_async, caplog):
    """Test handling a client response error"""
    api.metrics.reset()
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="unexpected content-length header",
            history={},
        )
        with caplog.at_level(logging.DEBUG):
            assert api.metrics.last_error_time is None
            caplog.clear()
            with pytest.raises(S30Exception) as exc:
                await api.messagePump()
            e: S30Exception = exc.value
            assert e.error_code == EC_COMMS_ERROR
            assert "unexpected content-length header" in e.message
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
        with caplog.at_level(logging.DEBUG):
            assert api.metrics.last_error_time is None
            caplog.clear()
            with pytest.raises(S30Exception) as exc:
                await api.messagePump()
            e: S30Exception = exc.value
            assert e.error_code == EC_COMMS_ERROR
            assert "some other error" in e.message
            assert len(caplog.records) == 0
            assert api.metrics.client_response_errors == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None

    api.metrics.reset()
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = aiohttp.ServerDisconnectedError()
        with caplog.at_level(logging.DEBUG):
            assert api.metrics.last_error_time is None
            caplog.clear()
            with pytest.raises(S30Exception) as exc:
                await api.messagePump()
            e: S30Exception = exc.value
            assert e.error_code == EC_COMMS_ERROR
            assert "Server Disconnected" in e.message
            assert len(caplog.records) == 0
            assert api.metrics.client_response_errors == 0
            assert api.metrics.server_disconnects == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None


@pytest.mark.asyncio
async def test_client_connection_error(api: s30api_async, caplog):
    """Test client connection errors"""
    api.metrics.reset()
    api.url_retrieve = "http://0.0.0.0:8888/test.html"
    api._session = aiohttp.ClientSession()
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        with pytest.raises(S30Exception) as exc:
            await api.messagePump()
        e: S30Exception = exc.value
        assert e.error_code == EC_COMMS_ERROR
        assert "0.0.0.0" in e.message
        assert "8888" in e.message
        assert len(caplog.records) == 0
        assert api.metrics.client_response_errors == 1
        assert api.metrics.server_disconnects == 0
        assert api.metrics.error_count == 1
        assert api.metrics.last_error_time is not None


class HttpResp:
    """Mock an http response"""
    def __init__(self, status):
        self.status = status
        self.content_length = 100


@pytest.mark.asyncio
async def test_client_http_204(api: s30api_async, caplog):
    """Test http 204 response"""
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = HttpResp(204)
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            result = await api.messagePump()
            assert result is False
            assert len(caplog.records) == 0


@pytest.mark.asyncio
async def test_client_http_502(api: s30api_async, caplog):
    """Test http 502 response"""
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = HttpResp(502)
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            with pytest.raises(S30Exception) as exc:
                await api.messagePump()
            e: S30Exception = exc.value
            assert e.error_code == EC_HTTP_ERR
            assert e.reference == 502
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == "INFO"


@pytest.mark.asyncio
async def test_client_http_401(api: s30api_async, caplog):
    """Test http 401 response"""
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = HttpResp(401)
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            with pytest.raises(S30Exception) as exc:
                await api.messagePump()
            e: S30Exception = exc.value
            assert e.error_code == EC_UNAUTHORIZED
            assert e.reference == 401
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == "INFO"


@pytest.mark.asyncio
async def test_client_timeout_error(api: s30api_async, caplog):
    """Tests client timeout error"""
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = asyncio.TimeoutError()
        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            with pytest.raises(S30Exception) as exc:
                await api.messagePump()
            ex: S30Exception = exc.value
            assert ex.error_code == EC_COMMS_ERROR
            assert "TimeoutError" in ex.message
            assert api.metrics.client_response_errors == 0
            assert api.metrics.server_disconnects == 0
            assert api.metrics.timeouts == 1
            assert api.metrics.error_count == 1
            assert api.metrics.last_error_time is not None
