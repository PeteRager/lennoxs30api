import aiohttp
from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    EC_REQUEST_DATA_HELPER,
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
        return {"code": 1, "message": "RequestData: success [homeassistant]"}

    async def text(self):
        return (
            '{"code":'
            + str(self.code)
            + ',"message":"RequestData: success ['
            + self.app_id
            + ']"}'
        )


def test_request_data_helper_200(api: s30api_async):
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additionalParameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        mock_post.return_value = GoodResponse(status=200, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        error = False
        try:
            result = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additionalParameters)
            )
        except S30Exception as e:
            error = True
        assert error == False
        assert mock_post.call_count == 1
        url = mock_post.call_args_list[0][0][0]
        data = mock_post.call_args_list[0][1]["data"]
        message = json.loads(data)
        assert message["MessageType"] == "RequestData"
        assert message["SenderID"] == api.getClientId()
        assert message["MessageID"] != None
        assert message["TargetID"] == system.sysId
        assert (
            message["AdditionalParameters"]["JSONPath"]
            == "1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"
        )


def test_request_data_helper_400(api: s30api_async):
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additionalParameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        mock_post.return_value = GoodResponse(status=400, app_id=api._applicationid)
        loop = asyncio.get_event_loop()
        error = False
        ex = None
        try:
            result = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additionalParameters)
            )
        except S30Exception as e:
            error = True
            ex = e
        assert error == True
        assert ex.error_code == EC_REQUEST_DATA_HELPER
        assert "requestDataHelper" in ex.message
        assert "400" in ex.message
        assert "RequestData: success" in ex.message


class BadJSON:
    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code
        pass

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self):
        t = await self.text()
        return json.loads(t)

    async def text(self):
        return (
            '["code1"::::'
            + str(self.code)
            + ',"message":"Publish: success ['
            + self.app_id
            + ']"}'
        )


def test_request_data_helper_200_bad_json(api: s30api_async):
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        additionalParameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        mock_post.return_value = BadJSON(status=200, app_id=api._applicationid, code=0)
        loop = asyncio.get_event_loop()
        error = False
        ex = None
        try:
            result = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additionalParameters)
            )
        except S30Exception as e:
            error = True
            ex = e
        assert error == True
        assert ex.error_code == EC_REQUEST_DATA_HELPER
        assert "requestDataHelper" in ex.message
        assert "JSONDecodeError" in ex.message


def test_request_data_helper_comms_error(api: s30api_async):
    system: lennox_system = api.getSystem("0000000-0000-0000-0000-000000000001")

    with patch.object(api, "post") as mock_post:
        level = 2
        additionalParameters = '"AdditionalParameters":{"JSONPath":"1;/systemControl;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
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
            result = loop.run_until_complete(
                api.requestDataHelper(system.sysId, additionalParameters)
            )
        except S30Exception as e:
            error = True
            ex = e
        assert error == True
        assert ex.error_code == EC_COMMS_ERROR
        assert api.url_requestdata in ex.message
        assert "some other error" in ex.message
