import json
import os
from lennoxs30api.s30api_async import (
    s30api_async,
)

import asyncio
import aiohttp
import logging

from unittest.mock import patch

from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_LOGIN,
    S30Exception,
)


class GoodResponse:
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        script_dir = os.path.dirname(__file__) + "/messages/"
        file_path = os.path.join(script_dir, "login_response.json")
        with open(file_path) as f:
            return json.load(f)

    async def text(self):
        return (
            '{"code":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_login_local_200(caplog):
    api: s30api_async = s30api_async(
        username=None, password=None, app_id="myapp_id", ip_address="10.0.0.1"
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(app_id="myapp_id")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(api.login())
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        assert url == api.url_login
        assert "myapp_id" in url


def test_login_local_204(caplog):
    api: s30api_async = s30api_async(
        username=None, password=None, app_id="myapp_id", ip_address="10.0.0.1"
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(status=204, app_id="myapp_id")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(api.login())
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        assert url == api.url_login
        assert "myapp_id" in url


def test_login_local_400(caplog):
    api: s30api_async = s30api_async(
        username=None, password=None, app_id="myapp_id", ip_address="10.0.0.1"
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(status=400, app_id="myapp_id")
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(api.login())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_LOGIN
        assert "400" in ex.message
        assert "login" in ex.message
        assert api.url_login in ex.message


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
            assert api.metrics.last_error_time != None
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


def test_login_cloud_200(caplog):
    api: s30api_async = s30api_async(
        username="pete@rager.com",
        password="password",
        app_id="myapp_id",
        ip_address=None,
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(app_id="myapp_id")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(api.login())
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        assert url == api.url_login
        data = mock_post.call_args_list[0][1]["data"]
        assert (
            data
            == "username=pete@rager.com&password=password&grant_type=password&applicationid=myapp_id"
        )


def test_login_cloud_400(caplog):
    api: s30api_async = s30api_async(
        username="pete@rager.com",
        password="password",
        app_id="myapp_id",
        ip_address=None,
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(status=400, app_id="myapp_id")
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(api.login())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_LOGIN
        assert "400" in ex.message
        assert "login" in ex.message
        assert api.url_login in ex.message


class BadJSONResponse:
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        x = "this:::isnot_json"
        return json.loads(x)

    async def text(self):
        return (
            '{"code":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_login_bad_json(caplog):
    api: s30api_async = s30api_async(
        username="pete@rager.com",
        password="password",
        app_id="myapp_id",
        ip_address=None,
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = BadJSONResponse(status=200, app_id="myapp_id")
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(api.login())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_LOGIN
        assert "JSONDecodeError" in ex.message
        assert "login" in ex.message


class BadJSONKeyResponse:
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        script_dir = os.path.dirname(__file__) + "/messages/"
        file_path = os.path.join(script_dir, "login_response.json")
        with open(file_path) as f:
            x = json.load(f)
            x["ServerAssignedRoot"] = "foobar"
            return x

    async def text(self):
        return (
            '{"code":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_login_bad_missing_key(caplog):
    api: s30api_async = s30api_async(
        username="pete@rager.com",
        password="password",
        app_id="myapp_id",
        ip_address=None,
    )
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = BadJSONKeyResponse(status=200, app_id="myapp_id")
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(api.login())
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_LOGIN
        assert "login" in ex.message
