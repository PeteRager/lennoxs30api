import json
from multiprocessing.sharedctypes import Value
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


def test_subscribe_200(api: s30api_async):
    system = api._systemList[0]

    api._isLANConnection = True
    with patch.object(api, "requestDataHelper") as requestDataHelper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(api.subscribe(system))
        except S30Exception as e:
            ex = e
        assert ex == None
        assert requestDataHelper.call_count == 1
        assert requestDataHelper.call_args[0][0] == system.sysId
        assert (
            requestDataHelper.call_args[0][1]
            == '"AdditionalParameters":{"JSONPath":"1;/systemControl;/systemController;/reminderSensors;/reminders;/alerts/active;/alerts/meta;/fwm;/rgw;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        )

    api._isLANConnection = False
    with patch.object(api, "requestDataHelper") as requestDataHelper:
        with patch.object(
            system, "update_system_online_cloud"
        ) as update_system_online_cloud:
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(api.subscribe(system))
            except S30Exception as e:
                ex = e
            assert ex == None
            assert update_system_online_cloud.call_count == 1
            assert requestDataHelper.call_count == 2

            call_args = requestDataHelper.call_args_list[0]
            s = call_args[0][0]
            assert s == system.sysId
            assert (
                call_args[0][1]
                == '"AdditionalParameters":{"JSONPath":"1;/system;/zones;/occupancy;/schedules;"}'
            )

            call_args = requestDataHelper.call_args_list[1]
            s = call_args[0][0]
            assert s == system.sysId
            assert (
                call_args[0][1]
                == '"AdditionalParameters":{"JSONPath":"1;/reminderSensors;/reminders;/alerts/active;/alerts/meta;/dealers;/devices;/equipments;/fwm;/ocst;"}'
            )


def test_subscribe_exception(api: s30api_async, caplog):
    system = api._systemList[0]

    api._isLANConnection = True
    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as requestDataHelper:
            requestDataHelper.side_effect = S30Exception("Simulated Exception", 10, 1)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(api.subscribe(system))
            except S30Exception as e:
                ex = e
            assert ex != None
            assert "Simulated Exception" in ex.message
            assert len(caplog.records) == 1
            assert system.sysId in caplog.messages[0]
            assert "subscribe fail loca [1]" in caplog.messages[0]
            assert "Simulated Exception" in caplog.messages[0]

    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as requestDataHelper:
            requestDataHelper.side_effect = ValueError("bad key")
            loop = asyncio.get_event_loop()
            ex = None
            try:
                result = loop.run_until_complete(api.subscribe(system))
            except S30Exception as e:
                ex = e
            assert ex != None
            assert "bad key" in ex.message
            assert len(caplog.records) == 1
            assert system.sysId in caplog.messages[0]
            assert "subscribe fail locb [1]" in caplog.messages[0]
            assert "bad key" in caplog.messages[0]

    api._isLANConnection = False
    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as requestDataHelper:
            with patch.object(
                system, "update_system_online_cloud"
            ) as update_system_online_cloud:
                requestDataHelper.side_effect = S30Exception(
                    "Simulated Exception", 10, 1
                )
                loop = asyncio.get_event_loop()
                ex = None
                try:
                    result = loop.run_until_complete(api.subscribe(system))
                except S30Exception as e:
                    ex = e
                assert ex != None
                assert "Simulated Exception" in ex.message
                assert len(caplog.records) == 1
                assert system.sysId in caplog.messages[0]
                assert "subscribe fail locc [2]" in caplog.messages[0]
                assert "Simulated Exception" in caplog.messages[0]

    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as requestDataHelper:
            with patch.object(
                system, "update_system_online_cloud"
            ) as update_system_online_cloud:
                requestDataHelper.side_effect = ValueError("bad key")
                loop = asyncio.get_event_loop()
                ex = None
                try:
                    result = loop.run_until_complete(api.subscribe(system))
                except S30Exception as e:
                    ex = e
                assert ex != None
                assert "bad key" in ex.message
                assert len(caplog.records) == 1
                assert system.sysId in caplog.messages[0]
                assert "subscribe fail locd [2]" in caplog.messages[0]
                assert "bad key" in caplog.messages[0]
