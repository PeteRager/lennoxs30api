"""Test subscription registration"""
# pylint: disable=line-too-long
# pylint: disable=assert-on-tuple
import json
import asyncio
import os
from unittest.mock import patch

import logging

from lennoxs30api.s30api_async import s30api_async
from lennoxs30api.s30exception import S30Exception


class GoodResponse:
    """Mocks a good response from the devcice"""

    def __init__(self, status=200, app_id="app_id", code=1):
        self.status_code = status
        self.app_id = app_id
        self.code = code

    @property
    def status(self) -> int:
        """Return mock status code"""
        return self.status_code

    async def json(self):
        """Return json response"""
        script_dir = os.path.dirname(__file__) + "/messages/"
        file_path = os.path.join(script_dir, "login_response.json")
        with open(file_path, encoding="UTF-8") as handle:
            return json.load(handle)

    async def text(self):
        """Return text response"""
        return '{"code":' + str(self.code) + ',"message":"RequestData: success [' + self.app_id + ']"}'


def test_subscribe_200(api: s30api_async):
    """Tests the 200 return code"""
    system = api.system_list[0]

    api.isLANConnection = True
    with patch.object(api, "requestDataHelper") as mock_request_data_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(api.subscribe(system))
        except S30Exception as exc:
            ex = exc
        assert ex is None
        assert mock_request_data_helper.call_count == 2
        assert mock_request_data_helper.mock_calls[0].args[0] == system.sysId
        assert (
            mock_request_data_helper.mock_calls[0].args[1]
            == '"AdditionalParameters":{"JSONPath":"1;/systemControl;/systemController;/reminderSensors;/reminders;/alerts/active;/alerts/meta;/bleProvisionDB;/ble;/indoorAirQuality;/fwm;/rgw;/devices;/zones;/equipments;/schedules;/occupancy;/system"}'
        )
        assert mock_request_data_helper.mock_calls[1].args[0] == system.sysId
        assert (
            mock_request_data_helper.mock_calls[1].args[1]
            == '"AdditionalParameters":{"JSONPath":"1;/automatedTest;/zoneTestControl;/homes;/reminders;/algorithm;/historyReportFileDetails;/interfaces;/logs"}'
        )

    api.isLANConnection = False
    with patch.object(api, "requestDataHelper") as mock_request_data_helper:
        with patch.object(system, "update_system_online_cloud") as update_system_online_cloud:
            loop = asyncio.get_event_loop()
            ex = None
            try:
                _ = loop.run_until_complete(api.subscribe(system))
            except S30Exception as exc:
                ex = exc
            assert ex is None
            assert update_system_online_cloud.call_count == 1
            assert mock_request_data_helper.call_count == 2

            call_args = mock_request_data_helper.call_args_list[0]
            assert call_args[0][0] == system.sysId
            assert (
                call_args[0][1]
                == '"AdditionalParameters":{"JSONPath":"1;/system;/zones;/occupancy;/schedules;/reminderSensors;/reminders;/alerts/active;"}'
            )

            call_args = mock_request_data_helper.call_args_list[1]
            assert call_args[0][0] == system.sysId
            assert (
                call_args[0][1]
                == '"AdditionalParameters":{"JSONPath":"1;/alerts/meta;/dealers;/devices;/equipments;/system;/fwm;/ocst;"}',
            )


def test_subscribe_exception(api: s30api_async, caplog):
    """Tests subscription exceptions"""
    system = api.system_list[0]

    api.isLANConnection = True
    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as mock_request_data_helper:
            mock_request_data_helper.side_effect = S30Exception("Simulated Exception", 10, 1)
            loop = asyncio.get_event_loop()
            ex = None
            try:
                _ = loop.run_until_complete(api.subscribe(system))
            except S30Exception as exc:
                ex = exc
            assert ex is not None
            assert "Simulated Exception" in ex.message
            assert len(caplog.records) == 1
            assert system.sysId in caplog.messages[0]
            assert "subscribe fail loca [1]" in caplog.messages[0]
            assert "Simulated Exception" in caplog.messages[0]

    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as mock_request_data_helper:
            mock_request_data_helper.side_effect = ValueError("bad key")
            loop = asyncio.get_event_loop()
            ex = None
            try:
                _ = loop.run_until_complete(api.subscribe(system))
            except S30Exception as exc:
                ex = exc
            assert ex is not None
            assert "bad key" in ex.message
            assert len(caplog.records) == 1
            assert system.sysId in caplog.messages[0]
            assert "subscribe fail locb [1]" in caplog.messages[0]
            assert "bad key" in caplog.messages[0]

    api.isLANConnection = False
    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as mock_request_data_helper:
            with patch.object(system, "update_system_online_cloud"):
                mock_request_data_helper.side_effect = S30Exception("Simulated Exception", 10, 1)
                loop = asyncio.get_event_loop()
                ex = None
                try:
                    _ = loop.run_until_complete(api.subscribe(system))
                except S30Exception as exc:
                    ex = exc
                assert ex is not None
                assert "Simulated Exception" in ex.message
                assert len(caplog.records) == 1
                assert system.sysId in caplog.messages[0]
                assert "subscribe fail locc [2]" in caplog.messages[0]
                assert "Simulated Exception" in caplog.messages[0]

    with caplog.at_level(logging.ERROR):
        caplog.clear()
        with patch.object(api, "requestDataHelper") as mock_request_data_helper:
            with patch.object(system, "update_system_online_cloud"):
                mock_request_data_helper.side_effect = ValueError("bad key")
                loop = asyncio.get_event_loop()
                ex = None
                try:
                    _ = loop.run_until_complete(api.subscribe(system))
                except S30Exception as exc:
                    ex = exc
                assert ex is not None
                assert "bad key" in ex.message
                assert len(caplog.records) == 1
                assert system.sysId in caplog.messages[0]
                assert "subscribe fail locd [2]" in caplog.messages[0]
                assert "bad key" in caplog.messages[0]
