"""Tests the API request data helper"""
# pylint: disable=protected-access
# pylint: disable=line-too-long
import json
import asyncio
from unittest.mock import patch
import aiohttp
import pytest
from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)

from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_REQUEST_DATA_HELPER,
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
        """response status"""
        return self.status_code

    async def json(self):
        """Response json"""
        return {"code": 1, "message": "RequestData: success [homeassistant]"}

    async def text(self):
        """Response Text"""
        return (
            '{"code":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_request_data_helper_200(api: s30api_async):
    """Test a 200 response"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additional_parameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        mock_post.return_value = GoodResponse(status=200, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additional_parameters)
            )
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        assert url == 'https://icrequestdataapi.myicomfort.com/v1/Messages/RequestData'
        data = mock_post.call_args_list[0][1]["data"]
        message = json.loads(data)
        assert message["MessageType"] == "RequestData"
        assert message["SenderID"] == api.getClientId()
        assert message["MessageID"] is not None
        assert message["TargetID"] == system.sysId
        assert (
            message["AdditionalParameters"]["JSONPath"]
            == "1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"
        )


def test_request_data_helper_400(api: s30api_async):
    """Tests processing a 400 response"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additional_parameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        mock_post.return_value = GoodResponse(status=400, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        ex = None
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception =exc.value
        assert ex.error_code == EC_REQUEST_DATA_HELPER
        assert "requestDataHelper" in ex.message
        assert "400" in ex.message
        assert "RequestData: success" in ex.message


class BadJSON:
    """Bad json response"""
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code

    @property
    def status(self) -> int:
        """Response status"""
        return self.status_code

    async def json(self):
        """Response json"""
        t = await self.text()
        return json.loads(t)

    async def text(self):
        """Response text"""
        return (
            '["code1"::::'
            + str(self.code)
            + ',"message":"Publish: success ['
            + self.app_id
            + ']"}'
        )


def test_request_data_helper_200_bad_json(api: s30api_async):
    """Tests receiving bad json"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additional_parameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        mock_post.return_value = BadJSON(status=200, app_id=api._applicationid, code=0)
        loop = asyncio.get_event_loop()
        with pytest.raises(S30Exception) as exc:
            _ = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_REQUEST_DATA_HELPER
        assert "requestDataHelper" in ex.message
        assert "JSONDecodeError" in ex.message


def test_request_data_helper_comms_error(api: s30api_async):
    """Test a commmunication error"""
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additional_parameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
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
                api.requestDataHelper(system.sysId, additional_parameters)
            )
        ex: S30Exception = exc.value
        assert ex.error_code == EC_COMMS_ERROR
        assert api.url_requestdata in ex.message
        assert "some other error" in ex.message
