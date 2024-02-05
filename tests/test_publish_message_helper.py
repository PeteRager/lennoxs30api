"""Test the api publish messsage helper function"""
# pylint: disable=protected-access
import json
import asyncio
from unittest.mock import patch
import aiohttp
import pytest
from lennoxs30api.s30api_async import lennox_system, s30api_async
from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_PUBLISH_MESSAGE,
    S30Exception,
)


class GoodResponse:
    """Mocks a good response"""
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code

    @property
    def status(self) -> int:
        """Response status"""
        return self.status_code

    async def text(self):
        """Response Text"""
        return (
            '{"code":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_publish_message_helper_200(api: s30api_async):
    """Test http 200 response"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        data = '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        mock_post.return_value = GoodResponse(status=200, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(api.publishMessageHelper(system.sysId, data))
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        assert url == 'https://icpublishapi.myicomfort.com/v1/messages/publish'
        data = mock_post.call_args_list[0][1]["data"]
        message = json.loads(data)
        assert message["MessageType"] == "Command"
        assert message["SenderID"] == api.getClientId()
        assert message["MessageID"] == "00000000-0000-0000-0000-000000000002"
        assert message["TargetID"] == system.sysId
        assert message["Data"]["systemControl"]["diagControl"]["level"] == 2
        assert "AdditionalParameters" not in message


def test_publish_message_helper_200_additional_params(api: s30api_async):
    """Test publishing message with additional parameters"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        data = '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        mock_post.return_value = GoodResponse(status=200, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            api.publishMessageHelper(
                system.sysId, data, additional_parameters="/systemControl"
            )
        )
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        assert url == 'https://icpublishapi.myicomfort.com/v1/messages/publish'
        data = mock_post.call_args_list[0][1]["data"]
        message = json.loads(data)
        assert message["MessageType"] == "Command"
        assert message["SenderID"] == api.getClientId()
        assert message["MessageID"] == "00000000-0000-0000-0000-000000000002"
        assert message["TargetID"] == system.sysId
        assert message["AdditionalParameters"] == "/systemControl"
        assert message["Data"]["systemControl"]["diagControl"]["level"] == 2


def test_publish_message_helper_400(api: s30api_async):
    """Test http 400 response"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        additional_parameters = (
            '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        )
        mock_post.return_value = GoodResponse(status=400, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.publishMessageHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_PUBLISH_MESSAGE
        assert "publishMessageHelper" in ex.message
        assert "400" in ex.message
        assert "RequestData: success" in ex.message


def test_publish_message_helper_200_code_0(api: s30api_async):
    """Test receiving a code 0 negative response from S30"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        additional_parameters = (
            '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        )
        mock_post.return_value = GoodResponse(
            status=200, app_id=api._applicationid, code=0
        )
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.publishMessageHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_PUBLISH_MESSAGE
        assert "publishMessageHelper" in ex.message
        assert "code [0]" in ex.message
        assert "RequestData: success" in ex.message


class BadResponse:
    """Mocks a bad response"""
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code

    @property
    def status(self) -> int:
        """Response Status"""
        return self.status_code

    async def text(self):
        """Response text"""
        return (
            '{"code1":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_publish_message_helper_200_no_code(api: s30api_async):
    """Test no code returned"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        additional_parameters = (
            '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        )
        mock_post.return_value = BadResponse(
            status=200, app_id=api._applicationid, code=0
        )
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.publishMessageHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_PUBLISH_MESSAGE
        assert "publishMessageHelper" in ex.message
        assert "['code']" in ex.message
        assert "code1" in ex.message


class BadJSON:
    """Class to mock an invalid JSON response"""
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code

    @property
    def status(self) -> int:
        """Response Status"""
        return self.status_code

    async def text(self):
        """Response Text"""
        return (
            '["code1"::::'
            + str(self.code)
            + ',"message":"Publish: success ['
            + self.app_id
            + ']"}'
        )


def test_publish_message_helper_200_bad_json(api: s30api_async):
    """Verify code handle invalid json"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        additional_parameters = (
            '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        )
        mock_post.return_value = BadJSON(status=200, app_id=api._applicationid, code=0)
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.publishMessageHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_PUBLISH_MESSAGE
        assert "publishMessageHelper" in ex.message
        assert "JSONDecodeError" in ex.message
        assert '["code1"::' in ex.message


def test_publish_message_helper_comms_error(api: s30api_async):
    """Verify handling of a aiohttp communication error"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        additional_parameters = (
            '"Data":{"systemControl":{"diagControl":{"level":' + str(level) + "} } }"
        )
        mock_post.side_effect = aiohttp.ClientResponseError(
            status=400,
            request_info="myurl",
            headers={"header_1": "1", "header_2": "2"},
            message="some other error",
            history={},
        )
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.publishMessageHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_COMMS_ERROR
        assert api.url_publish in ex.message
        assert "some other error" in ex.message
