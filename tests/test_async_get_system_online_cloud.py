import json
import logging

import aiohttp
from lennoxs30api.s30api_async import (
    CERTIFICATE,
    lennox_system,
    s30api_async,
)

import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import S30Exception


class GoodResponse:
    def __init__(self, status=200):
        self.status_code = status
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        return {
            "code": 1,
            "message": '{"presence":[{"id":0,"endpointId":"0000000-0000-0000-0000-000000000001","status":"online"}]}',
            "retry_after": 0,
        }

    async def text(self):
        return "this is the error"


def test_get_system_online_cloud(api: s30api_async):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        mock_post.return_value = GoodResponse(200)
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(system.update_system_online_cloud())
        except S30Exception as e:
            ex = e
        assert ex == None
        assert mock_post.call_count == 1
        data = mock_post.call_args_list[0][1]["data"]
        message = json.loads(data)
        assert message["MessageType"] == "RequestData"
        assert message["SenderID"] == api.getClientId()
        assert message["MessageID"] != None
        assert message["TargetID"] == "ic3server"
        assert message["AdditionalParameters"]["publisherpresence"] == "true"
        assert message["Data"]["presence"][0]["id"] == 0
        assert message["Data"]["presence"][0]["endpointId"] == system.sysId
        assert system.cloud_status == "online"
        assert "cloud_status" in system._dirtyList


def test_get_system_online_cloud_400(api: s30api_async, caplog):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = GoodResponse(400)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                ex = e
            assert ex != None
            assert "requestDataHelper" in ex.message
            assert "400" in ex.message
            assert "this is the error" in ex.message
            assert system.cloud_status == None
            assert "cloud_status" not in system._dirtyList


class BadResponse_DiffSysId:
    def __init__(self, status=200):
        self.status_code = status
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        return {
            "code": 1,
            "message": '{"presence":[{"id":0,"endpointId":"0000000-0000-0000-0000-000000000002","status":"online"}]}',
            "retry_after": 0,
        }

    async def text(self):
        return "this is the error"


def test_get_system_online_cloud_diff_sysid(api: s30api_async, caplog):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponse_DiffSysId(200)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                ex = e
            assert ex == None
            assert len(caplog.records) == 1
            assert system.sysId in caplog.messages[0]
            assert "0000000-0000-0000-0000-000000000002" in caplog.messages[0]
            assert "unexpected sysId" in caplog.messages[0]
            assert system.cloud_status == None
            assert "cloud_status" not in system._dirtyList


class BadResponse_NoMessage:
    def __init__(self, status=200):
        self.status_code = status
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        return {
            "code": 1,
            "retry_after": 0,
        }

    async def text(self):
        return "this is the error"


def test_get_system_online_cloud_no_message(api: s30api_async, caplog):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponse_NoMessage(200)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                ex = e
            assert ex == None
            assert len(caplog.records) == 1
            assert "No message element in response" in caplog.messages[0]
            assert "code" in caplog.messages[0]


class BadResponse_NoPresence:
    def __init__(self, status=200):
        self.status_code = status
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        return {
            "code": 1,
            "message": '{"nopresense":"off"}',
            "retry_after": 0,
        }

    async def text(self):
        return "this is the error"


def test_get_system_online_cloud_no_presence(api: s30api_async, caplog):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponse_NoPresence(200)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                ex = e
            assert ex == None
            assert len(caplog.records) == 1
            assert "No presense element in response" in caplog.messages[0]
            assert "nopresense" in caplog.messages[0]
            assert system.cloud_status == None
            assert "cloud_status" not in system._dirtyList


def test_get_system_online_cloud_no_result(api: s30api_async, caplog):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "requestDataHelper") as requestDataHelper:
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            requestDataHelper.return_value = None
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                ex = e
            assert ex == None
            assert len(caplog.records) == 1
            assert "No Response Received" in caplog.messages[0]
            assert system.cloud_status == None
            assert "cloud_status" not in system._dirtyList


def test_get_system_online_cloud_comm_exception(api: s30api_async, caplog):
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
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
                result = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                error = True
                ex = e
            assert error == True
            assert "requestDataHelper" in ex.message
            assert api.url_requestdata in ex.message
            assert "some other error" in ex.message
            assert "ClientResponseError" in ex.message
            assert len(caplog.records) == 0
