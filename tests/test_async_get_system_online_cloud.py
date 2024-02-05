"""Test processing the online/offline thermostat status from the cloud"""
# pylint: disable=line-too-long
import json
import logging
import asyncio
from unittest.mock import patch

import aiohttp
from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)


from lennoxs30api.s30exception import S30Exception
from tests.conftest import loadfile


class GoodResponse:
    """Mocks a good response"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """API status"""
        return self.status_code

    async def json(self):
        """JSON message"""
        return {
            "code": 1,
            "message": '{"presence":[{"id":0,"endpointId":"0000000-0000-0000-0000-000000000001","status":"online"}]}',
            "retry_after": 0,
        }

    async def text(self):
        """Text version of message"""
        return "this is the error"


class DirtySubscription:
    """Subscription handler"""
    def __init__(self, system: lennox_system, attr_name: str):
        self.triggered_count = 0
        system.registerOnUpdateCallback(self.update_callback, [attr_name])

    def update_callback(self):
        """Callback for updates"""
        self.triggered_count += 1


def test_get_system_online_cloud(api: s30api_async):
    """Tests the online response from cloud"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.cloud_status = None
    with patch.object(api, "post") as mock_post:
        ds = DirtySubscription(system, "cloud_status")
        mock_post.return_value = GoodResponse(200)
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(system.update_system_online_cloud())
        except S30Exception as e:
            ex = e
        assert ex is None
        assert mock_post.call_count == 1
        data = mock_post.call_args_list[0][1]["data"]
        message = json.loads(data)
        assert message["MessageType"] == "RequestData"
        assert message["SenderID"] == api.getClientId()
        assert message["MessageID"] is not None
        assert message["TargetID"] == "ic3server"
        assert message["AdditionalParameters"]["publisherpresence"] == "true"
        assert message["Data"]["presence"][0]["id"] == 0
        assert message["Data"]["presence"][0]["endpointId"] == system.sysId
        assert system.cloud_status == "online"
        assert ds.triggered_count == 1


def test_get_system_online_cloud_400(api: s30api_async, caplog):
    """Test a 400 return code"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.cloud_status = None

    with patch.object(api, "post") as mock_post:
        ds = DirtySubscription(system, "cloud_status")
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = GoodResponse(400)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                _ = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                ex = e
            assert ex is not None
            assert "requestDataHelper" in ex.message
            assert "400" in ex.message
            assert "this is the error" in ex.message
            assert system.cloud_status is None
            assert ds.triggered_count == 0


class BadResponseDiffSysId:
    """Mocks a bad response for a different system"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Status Code"""
        return self.status_code

    async def json(self):
        """JSON message"""
        return {
            "code": 1,
            "message": '{"presence":[{"id":0,"endpointId":"0000000-0000-0000-0000-000000000002","status":"online"}]}',
            "retry_after": 0,
        }

    async def text(self):
        """Text message"""
        return "this is the error"


def test_get_system_online_cloud_diff_sysid(api: s30api_async, caplog):
    """Tests a cloud response that returns a different sysid"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.cloud_status = None

    with patch.object(api, "post") as mock_post:
        caplog.clear()
        ds = DirtySubscription(system, "cloud_status")
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponseDiffSysId(200)
            loop = asyncio.get_event_loop()
            _ = loop.run_until_complete(system.update_system_online_cloud())
            assert len(caplog.records) == 1
            assert system.sysId in caplog.messages[0]
            assert "0000000-0000-0000-0000-000000000002" in caplog.messages[0]
            assert "unexpected sysId" in caplog.messages[0]
            assert system.cloud_status is None
            assert ds.triggered_count == 0


class BadResponseNoMessage:
    """Mock to returns a bad response"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Status Code"""
        return self.status_code

    async def json(self):
        """JSON value"""
        return {
            "code": 1,
            "retry_after": 0,
        }

    async def text(self):
        """Text version"""
        return "this is the error"


def test_get_system_online_cloud_no_message(api: s30api_async, caplog):
    """Tests no message"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        ds = DirtySubscription(system, "cloud_status")
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponseNoMessage(200)
            loop = asyncio.get_event_loop()
            _ = loop.run_until_complete(system.update_system_online_cloud())
            assert len(caplog.records) == 1
            assert "No message element in response" in caplog.messages[0]
            assert "code" in caplog.messages[0]
            assert ds.triggered_count == 0


class BadResponseNoPresence:
    """Mocks a bad respone with no presence information"""
    def __init__(self, status=200):
        self.status_code = status

    @property
    def status(self) -> int:
        """Status Code"""
        return self.status_code

    async def json(self):
        """JSON"""
        return {
            "code": 1,
            "message": '{"nopresense":"off"}',
            "retry_after": 0,
        }

    async def text(self):
        """Text Version"""
        return "this is the error"


def test_get_system_online_cloud_no_presence(api: s30api_async, caplog):
    """Tests system online with no presence"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.cloud_status = None

    with patch.object(api, "post") as mock_post:
        caplog.clear()
        ds = DirtySubscription(system, "cloud_status")
        with caplog.at_level(logging.WARNING):
            mock_post.return_value = BadResponseNoPresence(200)
            loop = asyncio.get_event_loop()
            _ = loop.run_until_complete(system.update_system_online_cloud())
            assert len(caplog.records) == 1
            assert "No presense element in response" in caplog.messages[0]
            assert "nopresense" in caplog.messages[0]
            assert system.cloud_status is None
            assert ds.triggered_count == 0


def test_get_system_online_cloud_no_result(api: s30api_async, caplog):
    """Tests response with no result"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.cloud_status = None

    with patch.object(api, "requestDataHelper") as request_data_helper:
        caplog.clear()
        ds = DirtySubscription(system, "cloud_status")
        with caplog.at_level(logging.WARNING):
            request_data_helper.return_value = None
            loop = asyncio.get_event_loop()
            _ = loop.run_until_complete(system.update_system_online_cloud())
            assert len(caplog.records) == 1
            assert "No Response Received" in caplog.messages[0]
            assert system.cloud_status is None
            assert ds.triggered_count == 0


def test_get_system_online_cloud_comm_exception(api: s30api_async, caplog):
    """Test comm exception on request"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "post") as mock_post:
        caplog.clear()
        ds = DirtySubscription(system, "cloud_status")
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
                _ = loop.run_until_complete(system.update_system_online_cloud())
            except S30Exception as e:
                error = True
                ex = e
            assert error is True
            assert "requestDataHelper" in ex.message
            assert api.url_requestdata in ex.message
            assert "some other error" in ex.message
            assert "ClientResponseError" in ex.message
            assert len(caplog.records) == 0
            assert ds.triggered_count == 0


def test_get_system_online_cloud_process_message(api: s30api_async):
    """Tests processing message"""
    system: lennox_system = api.system_list[0]
    assert system.sysId == "0000000-0000-0000-0000-000000000001"
    system.cloud_status = "offline"

    ds = DirtySubscription(system, "cloud_status")
    data = loadfile("mut_sys1_zone1_cool_sched.json", system.sysId)
    api.processMessage(data)
    assert system.cloud_status == "online"
    assert ds.triggered_count == 1

    ds = DirtySubscription(system, "cloud_status")
    data = loadfile("mut_sys1_zone1_cool_sched.json", system.sysId)
    api.processMessage(data)
    assert system.cloud_status == "online"
    assert ds.triggered_count == 0

    system.cloud_status = None
    api.isLANConnection = True
    ds = DirtySubscription(system, "cloud_status")
    data = loadfile("mut_sys1_zone1_cool_sched.json", system.sysId)
    api.processMessage(data)
    assert system.cloud_status is None
    assert ds.triggered_count == 0
