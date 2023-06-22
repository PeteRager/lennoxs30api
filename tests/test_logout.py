"""Tests the api.logout function"""
# pylint: disable=line-too-long
# pylint: disable=protected-access
# pylint: disable=protected-access
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import asyncio
import logging
from unittest.mock import patch

import aiohttp
from lennoxs30api.s30api_async import CLOUD_LOGOUT_URL, s30api_async
from lennoxs30api.s30exception import EC_LOGOUT, S30Exception


class GoodResponse:
    """Simulates a good response"""

    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        return self.status_code


def test_logout_local_200():
    api = s30api_async(username=None, password=None, app_id="myapp_id", ip_address="10.0.0.1")
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(200)
        loop = asyncio.get_event_loop()
        error = False
        try:
            _ = loop.run_until_complete(api.logout())
        except S30Exception:
            error = True
        assert error is False
        assert mock_post.call_count == 1
        assert mock_post.call_args_list[0][0][0] == api.url_logout
        assert "10.0.0.1" in api.url_logout
        assert "myapp_id" in api.url_logout
        assert "Disconnect" in api.url_logout


def test_logout_cloud():
    api = s30api_async(username=None, password=None, app_id="myapp_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(200)
        loop = asyncio.get_event_loop()
        error = False
        try:
            _ = loop.run_until_complete(api.logout())
        except S30Exception:
            error = True
        assert error == False
        assert mock_post.call_count == 1
        assert mock_post.call_args_list[0][0][0] == CLOUD_LOGOUT_URL


def test_logout_local_400(caplog):
    api = s30api_async(username=None, password=None, app_id="myapp_id", ip_address="10.0.0.1")
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(400)
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            loop = asyncio.get_event_loop()
            error = False
            ex = None
            try:
                _ = loop.run_until_complete(api.logout())
            except S30Exception as e:
                error = True
                ex = e
            assert error is True
            assert ex.error_code == EC_LOGOUT
            assert api.url_logout in ex.message
            assert "400" in ex.message
            assert mock_post.call_count == 1
            assert mock_post.call_args_list[0][0][0] == api.url_logout
            assert "10.0.0.1" in api.url_logout
            assert "myapp_id" in api.url_logout
            assert "Disconnect" in api.url_logout
            assert len(caplog.records) == 1


def test_logout_local_s40(api_system_04_furn_ac_zoning: s30api_async):
    api = api_system_04_furn_ac_zoning
    assert api.isLANConnection
    with patch.object(api, "post") as mock_post:
        api.system_list[0].productType = "S40"
        mock_post.return_value = GoodResponse(200)

        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(api.logout())
        assert mock_post.call_count == 0


def test_logout_cloud_comm_exception(caplog):
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
            loop = asyncio.get_event_loop()
            error = False
            ex = None
            try:
                _ = loop.run_until_complete(api.logout())
            except S30Exception as e:
                error = True
                ex = e
            assert error is True
            assert "logout" in ex.message
            assert api.url_logout in ex.message
            assert "some other error" in ex.message
            assert len(caplog.records) == 0

    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.side_effect = KeyError("bad key")
            loop = asyncio.get_event_loop()
            error = False
            ex = None
            try:
                _ = loop.run_until_complete(api.logout())
            except S30Exception as e:
                error = True
                ex = e
            assert error is True
            assert "logout failed" in ex.message
            assert "bad key" in ex.message
            assert len(caplog.records) == 1
            assert "please raise an issue" in caplog.messages[0]
