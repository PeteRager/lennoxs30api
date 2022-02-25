import logging

import aiohttp
from lennoxs30api.s30api_async import (
    CERTIFICATE,
    s30api_async,
)

import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import S30Exception


def test_authenticate_local():
    api = s30api_async(
        username=None, password=None, app_id="app_id", ip_address="10.0.0.1"
    )
    with patch.object(api, "post") as mock_post:
        loop = asyncio.get_event_loop()
        error = False
        try:
            result = loop.run_until_complete(api.authenticate())
        except S30Exception as e:
            error = True
        assert error == False
        assert mock_post.call_count == 0


class GoodResponse:
    def __init__(self, status=200):
        self.status_code = status
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        return {
            "serverAssigned": {
                "security": {"certificateToken": {"encoded": "encodedCertificate"}}
            }
        }

    async def text(self):
        return "this is the error"


def test_authenticate_cloud_200():
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(200)
        loop = asyncio.get_event_loop()
        error = False
        try:
            result = loop.run_until_complete(api.authenticate())
        except S30Exception as e:
            error = True
        assert error == False
        assert api.authBearerToken == "encodedCertificate"
        assert mock_post.call_count == 1
        assert mock_post.call_args_list[0][1]["data"] == CERTIFICATE


def test_authenticate_cloud_400(caplog):
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = GoodResponse(400)
            loop = asyncio.get_event_loop()
            error = False
            ex = None
            try:
                result = loop.run_until_complete(api.authenticate())
            except S30Exception as e:
                error = True
                ex = e
            assert error == True
            assert "authenticate" in ex.message
            assert "400" in ex.message
            assert "this is the error" in ex.message
            assert api.authBearerToken == None
            assert mock_post.call_count == api.AUTHENTICATE_RETRIES
            assert len(caplog.records) == api.AUTHENTICATE_RETRIES


class BadResponse:
    def __init__(self, status=200):
        self.status_code = status
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        return {
            "serverAssigned2": {
                "security": {"certificateToken": {"encoded": "encodedCertificate"}}
            }
        }

    async def text(self):
        return "this is the error"


def test_authenticate_cloud_bad_response(caplog):
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponse(200)
            loop = asyncio.get_event_loop()
            error = False
            ex = None
            try:
                result = loop.run_until_complete(api.authenticate())
            except S30Exception as e:
                error = True
                ex = e
            assert error == True
            assert "authenticate" in ex.message
            assert "['serverAssigned']" in ex.message
            assert "serverAssigned2" in ex.message
            assert api.authBearerToken == None
            assert mock_post.call_count == 1
            assert len(caplog.records) == 0


def test_authenticate_cloud_comm_exception(caplog):
    api = s30api_async(username=None, password=None, app_id="app_id", ip_address=None)
    with patch.object(api, "post") as mock_post:
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
                result = loop.run_until_complete(api.authenticate())
            except S30Exception as e:
                error = True
                ex = e
            assert error == True
            assert "authenticate" in ex.message
            assert api.url_authenticate in ex.message
            assert "some other error" in ex.message
            assert len(caplog.records) == 0
