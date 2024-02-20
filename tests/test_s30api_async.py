"""Tests the s30api_async methods not covered by other tests"""
# pylint: disable=line-too-long
# pylint: disable=protected-access
# pylint: disable=protected-access
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import logging
from unittest.mock import AsyncMock, patch
import pytest
from lennoxs30api.s30api_async import s30api_async


def test_seturl_protocol(api: s30api_async):
    api._protocol = "https"
    assert api.set_url_protocol("https://myurl.com") == "https://myurl.com"
    api._protocol = "http"
    assert api.set_url_protocol("https://myurl.com") == "http://myurl.com"


def test_getClientId(api: s30api_async):
    api.isLANConnection = True
    assert api.getClientId() == api._applicationid
    api.isLANConnection = False
    assert api.getClientId() == f"{api._applicationid}_{api._username}"


@pytest.mark.asyncio
async def test_shutdown(api: s30api_async):
    with patch.object(api, "logout") as mock_logout, patch.object(api, "_close_session") as mock_close_session:
        api.isLANConnection = False
        api.loginBearerToken = None
        await api.shutdown()
        mock_logout.assert_not_called()
        mock_close_session.assert_called_once()

    with patch.object(api, "logout") as mock_logout, patch.object(api, "_close_session") as mock_close_session:
        api.isLANConnection = True
        api.loginBearerToken = None
        api._create_session()
        await api.shutdown()
        mock_logout.assert_called_once()
        mock_close_session.assert_called_once()

    with patch.object(api, "logout") as mock_logout, patch.object(api, "_close_session") as mock_close_session:
        api.isLANConnection = False
        api.loginBearerToken = "ABC"
        await api.shutdown()
        mock_logout.assert_called_once()
        mock_close_session.assert_called_once()


class TestSession(object):
    """Helper to mock closing sessions"""

    def __init__(self, raise_exception=False):
        self.call_count = 0
        self.raise_exception = raise_exception

    async def close(self):
        if self.raise_exception is True:
            raise ValueError("bad value")
        self.call_count += 1


@pytest.mark.asyncio
async def test_close_session(api: s30api_async, caplog):
    api._session = None
    await api._close_session()

    session = TestSession()
    api._session = session
    await api._close_session()
    assert session.call_count == 1
    assert api._session is None

    with caplog.at_level(logging.ERROR):
        caplog.clear()
        session = TestSession(True)
        api._session = session
        await api._close_session()
        assert api._session is None
        assert len(caplog.messages) == 1
        assert "close_session" in caplog.messages[0]
        assert "bad value" in caplog.messages[0]


@pytest.mark.asyncio
async def test_create_session(api: s30api_async):
    api._session = None
    assert api.timeout == 300
    api._create_session()
    assert api._session is not None
    assert api._session.timeout.total == 300


@pytest.mark.asyncio
async def test_server_connect(api: s30api_async):
    with patch.object(api, "_close_session") as mock_close_session, patch.object(
        api, "_create_session"
    ) as mock_create_session, patch.object(api, "authenticate") as mock_authenticate, patch.object(
        api, "login"
    ) as mock_login, patch.object(
        api, "negotiate"
    ) as mock_negotiate:
        api.metrics.last_reconnect_time = None
        await api.serverConnect()
        mock_close_session.assert_called_once()
        mock_create_session.assert_called_once()
        mock_authenticate.assert_called_once()
        mock_login.assert_called_once()
        mock_negotiate.assert_called_once()
        assert api.metrics.last_reconnect_time is not None


def test_homes(api: s30api_async):
    home = api.getOrCreateHome(1234567)
    home1 = api.getHomeByIdx(0)
    assert home is home1
    assert api.getHomeByIdx(1) is None

    home_list = api.getHomes()
    assert home_list[0] is home


class MockResponse(object):
    """Mock Response"""
    def __init__(self, return_value: int):
        self.status: int = return_value


@pytest.mark.asyncio
async def test_post(api: s30api_async):
    api._create_session()
    with patch.object(api._session, "post", new=AsyncMock()) as mock_post:
        api.isLANConnection = False
        api.metrics.reset()
        api.ssl = True
        mock_response = MockResponse(200)
        mock_post.return_value = mock_response
        response = await api.post("www.google.com", headers="headers", data="test")
        assert response is mock_response
        call = mock_post.mock_calls[0]
        assert call.args[0] == "www.google.com"
        assert call.kwargs["headers"] == "headers"
        assert call.kwargs["data"] == "test"
        assert call.kwargs["ssl"] is True

        assert api.metrics.bytes_out == 4
        assert api.metrics.send_count == 1
        assert api.metrics.receive_count == 1
        assert api.metrics.http_2xx_cnt == 1

    with patch.object(api._session, "post", new=AsyncMock()) as mock_post:
        api.isLANConnection = True
        api.metrics.reset()
        api.ssl = False
        mock_response = MockResponse(400)
        mock_post.return_value = mock_response
        response = await api.post("www.google.com", headers="headers", data="test")
        assert response is mock_response
        call = mock_post.mock_calls[0]
        assert call.args[0] == "www.google.com"
        assert call.kwargs["headers"] is None
        assert call.kwargs["data"] == "test"
        assert call.kwargs["ssl"] is False

        assert api.metrics.bytes_out == 4
        assert api.metrics.send_count == 1
        assert api.metrics.receive_count == 1
        assert api.metrics.http_2xx_cnt == 0
        assert api.metrics.http_4xx_cnt == 1
        assert api.metrics.error_count == 1

    with patch.object(api._session, "post", new=AsyncMock()) as mock_post:
        api.isLANConnection = True
        api.metrics.reset()
        api.ssl = False
        mock_response = MockResponse(200)
        mock_post.return_value = mock_response
        response = await api.post("www.google.com", headers="headers")
        assert response is mock_response
        call = mock_post.mock_calls[0]
        assert call.args[0] == "www.google.com"
        assert call.kwargs["headers"] is None
        assert call.kwargs["data"] is None
        assert call.kwargs["ssl"] is False

        assert api.metrics.send_count == 0
        assert api.metrics.bytes_out == 0
        assert api.metrics.receive_count == 1
        assert api.metrics.http_2xx_cnt == 1


@pytest.mark.asyncio
async def test_get(api: s30api_async):
    api._create_session()
    with patch.object(api._session, "get", new=AsyncMock()) as mock_get:
        api.isLANConnection = False
        api.metrics.reset()
        api.ssl = True
        mock_response = MockResponse(200)
        mock_get.return_value = mock_response
        response = await api.get("www.google.com", headers="headers")
        assert response is mock_response
        call = mock_get.mock_calls[0]
        assert call.args[0] == "www.google.com"
        assert call.kwargs["headers"] == "headers"
        assert call.kwargs["ssl"] is True

        assert api.metrics.receive_count == 1
        assert api.metrics.http_2xx_cnt == 1

    with patch.object(api._session, "get", new=AsyncMock()) as mock_get:
        api.isLANConnection = True
        api.metrics.reset()
        api.ssl = False
        mock_response = MockResponse(400)
        mock_get.return_value = mock_response
        response = await api.get("www.google.com", headers="headers")
        assert response is mock_response
        call = mock_get.mock_calls[0]
        assert call.args[0] == "www.google.com"
        assert call.kwargs["headers"] is None
        assert call.kwargs["ssl"] is False

        assert api.metrics.receive_count == 1
        assert api.metrics.http_2xx_cnt == 0
        assert api.metrics.http_4xx_cnt == 1
        assert api.metrics.error_count == 1
