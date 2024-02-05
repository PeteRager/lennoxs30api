"""Tests the cloud negotiate sequence"""
# pylint: disable=protected-access
import asyncio
from unittest.mock import patch
import pytest
import aiohttp
from lennoxs30api.s30api_async import (
    s30api_async,
)


from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_NEGOTIATE,
    S30Exception,
)


class GoodResponse:
    """Mocks a good response"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Response code"""
        return self.status_code

    async def json(self):
        """Response JSON"""
        return {
            "ConnectionId": "12345",
            "ConnectionToken": "56789",
            "TryWebSockets": "true",
            "Url": "https://someurl.com",
        }

    async def text(self):
        """Response text"""
        return "this is the error"


def test_negotiate_200():
    """Test negotiate with http 200 response"""
    api = s30api_async(
        username="rager", password=None, app_id="myapp_id", ip_address=None
    )
    api.loginToken = "ABCDEF"
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = GoodResponse(200)
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(api.negotiate())
        assert mock_get.call_count == 1
        url = mock_get.call_args_list[0][0][0]
        assert "?clientProtocol=1.3.0.0" in url
        assert "&clientId=" + api.getClientId() in url
        assert "&Authorization=" + api.loginToken in url

        assert api._connectionId == "12345"
        assert api._connectionToken == "56789"
        assert api._tryWebsockets == "true"
        assert api._streamURL == "https://someurl.com"


def test_negotiate_400():
    """Tests negotiate with 400 error response"""
    api = s30api_async(username="rager", password=None, app_id="myapp_id", ip_address=None)
    api.loginToken = "ABCDEF"
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = GoodResponse(400)
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(api.negotiate())
        ex: S30Exception = exc.value
        assert ex.error_code == EC_NEGOTIATE
        assert api.url_negotiate in ex.message
        assert "400" in ex.message
        assert "this is the error" in ex.message


def test_negotiate_comms_error():
    """Test negotiate with a comms error"""
    api = s30api_async(
        username="rager", password=None, app_id="myapp_id", ip_address=None
    )
    api.loginToken = "ABCDEF"
    with patch.object(api, "get") as mock_get:
        mock_get.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="some other error",
            history={},
        )
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(api.negotiate())
        ex: S30Exception = exc.value
        assert ex.error_code == EC_COMMS_ERROR
        assert api.url_negotiate in ex.message
        assert "some other error" in ex.message


class BadResponse:
    """Class to mock a bad response"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Response status"""
        return self.status_code

    async def json(self):
        """Response JSON"""
        return {
            "ConnectionId1": "12345",
            "ConnectionToken": "56789",
            "TryWebSockets": "true",
            "Url": "https://someurl.com",
        }

    async def text(self):
        """Response Text"""
        return "this is the error"


def test_negotiate_200_bad_response():
    """Test negotiate with a bad response"""
    api = s30api_async(
        username="rager", password=None, app_id="myapp_id", ip_address=None
    )
    api.loginToken = "ABCDEF"
    with patch.object(api, "get") as mock_get:
        mock_get.return_value = BadResponse(200)
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(api.negotiate())
        ex: S30Exception = exc.value
        assert ex.error_code == EC_NEGOTIATE
        assert "['ConnectionId']" in ex.message
        assert "TryWebSockets" in ex.message
