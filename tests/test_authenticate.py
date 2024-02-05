"""Tests authenticate"""
# pylint: disable=line-too-long
import logging
from unittest.mock import patch
import aiohttp
import pytest

from lennoxs30api.s30api_async import CERTIFICATE, s30api_async
from lennoxs30api.s30exception import S30Exception

@pytest.mark.asyncio
async def test_authenticate_local():
    """Test the local authentication process"""
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address="10.0.0.1")
    with patch.object(api, "post") as mock_post:
        await api.authenticate()
        assert mock_post.call_count == 0


class GoodResponse:
    """Mocks a good response"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Response status"""
        return self.status_code

    async def json(self):
        """Response JSON"""
        return {"serverAssigned": {"security": {"certificateToken": {"encoded": "encodedCertificate"}}}}

    async def text(self):
        """Response Text"""
        return "this is the error"


@pytest.mark.asyncio
async def test_authenticate_cloud_200():
    """Test an http 200 response"""
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(200)
        await api.authenticate()
        assert api.authBearerToken == "encodedCertificate"
        assert mock_post.call_count == 1
        assert mock_post.call_args_list[0][1]["data"] == CERTIFICATE


@pytest.mark.asyncio
async def test_authenticate_cloud_400(caplog):
    """Tests receiving a 400 response"""
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = GoodResponse(400)
            with pytest.raises(S30Exception) as exc:
                await api.authenticate()
            ex: S30Exception = exc.value
            assert "authenticate" in ex.message
            assert "400" in ex.message
            assert "this is the error" in ex.message
            assert api.authBearerToken is None
            assert mock_post.call_count == api.AUTHENTICATE_RETRIES
            assert len(caplog.records) == api.AUTHENTICATE_RETRIES


class BadResponse:
    """Mock a bad api response"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Response status"""
        return self.status_code

    async def json(self):
        """Response JSON"""
        return {"serverAssigned2": {"security": {"certificateToken": {"encoded": "encodedCertificate"}}}}

    async def text(self):
        """Response Text"""
        return "this is the error"


@pytest.mark.asyncio
async def test_authenticate_cloud_bad_response(caplog):
    """Tests a bad response from authenticating"""
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponse(200)
            with pytest.raises(S30Exception) as exc:
                await api.authenticate()
            ex: S30Exception = exc.value
            assert "authenticate" in ex.message
            assert "['serverAssigned']" in ex.message
            assert "serverAssigned2" in ex.message
            assert api.authBearerToken is None
            assert mock_post.call_count == 1
            assert len(caplog.records) == 0


@pytest.mark.asyncio
async def test_authenticate_cloud_comm_exception(caplog):
    """Tests a communication exception when authenticating"""
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.side_effect = aiohttp.ClientResponseError(
                status=400,
                request_info="myurl",
                headers={"header_1": "1", "header_2": "2"},
                message="some other error",
                history={},
            )
            with pytest.raises(S30Exception) as exc:
                await api.authenticate()
            ex: S30Exception = exc.value
            assert "authenticate" in ex.message
            assert api.url_authenticate in ex.message
            assert "some other error" in ex.message
            assert len(caplog.records) == 0

    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.side_effect = ValueError("bad key")
            with pytest.raises(S30Exception) as exc:
                await api.authenticate()
            ex: S30Exception = exc.value
            assert "authenticate" in ex.message
            assert len(caplog.records) == 1
            assert "please raise as issue" in caplog.messages[0]
