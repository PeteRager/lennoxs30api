'''Test module for processing messages'''
# pylint: disable=protected-access

import logging
from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)

from tests.conftest import loadfile


def test_api_process_sibling_message(api: s30api_async, caplog):
    '''Tests the processing of sibling messages'''
    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"

    message = loadfile("sibling.json")
    api.processMessage(message)

    assert lsystem.sibling_self_identifier == "KL21J00001"
    assert lsystem.sibling_identifier == "KL21J00002"
    assert api.metrics.sibling_message_drop == 0
    message = loadfile("mut_sys1_zone1_status.json")
    message["SenderId"] = "KL21J00002"
    caplog.clear()
    api.metrics.reset()
    with caplog.at_level(logging.DEBUG):
        api.processMessage(message)
        assert len(caplog.records) == 1
        assert "KL21J00002" in caplog.messages[0]
        assert caplog.records[0].levelname == "WARNING"
        assert api.metrics.sibling_message_drop == 1
        assert api.metrics.sender_message_drop == 0

        api.processMessage(message)
        assert len(caplog.records) == 2
        assert "KL21J00002" in caplog.messages[1]
        assert caplog.records[1].levelname == "DEBUG"
        assert api.metrics.sibling_message_drop == 2
        assert api.metrics.sender_message_drop == 0


def test_api_process_unknown_sender(api: s30api_async, caplog):
    '''Tests processing a message from an unknown sender'''
    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"
    message = loadfile("mut_sys1_zone1_status.json")
    message["SenderId"] = "KL21J00002"
    caplog.clear()
    api.metrics.reset()
    with caplog.at_level(logging.DEBUG):
        # First message should result in an Error Logged and an entry for the bad second in the dict
        api.processMessage(message)
        assert len(caplog.records) == 1
        assert "KL21J00002" in caplog.messages[0]
        assert caplog.records[0].levelname == "ERROR"
        assert api.metrics.sibling_message_drop == 0
        assert api.metrics.sender_message_drop == 1
        assert len(api._badSenderDict) == 1
        assert "KL21J00002" in api._badSenderDict
        # Second message should result in an Debug message logged
        caplog.clear()
        api.processMessage(message)
        assert len(caplog.records) == 1
        assert "KL21J00002" in caplog.messages[0]
        assert caplog.records[0].levelname == "DEBUG"
        assert api.metrics.sibling_message_drop == 0
        assert api.metrics.sender_message_drop == 2
        assert len(api._badSenderDict) == 1
        assert "KL21J00002" in api._badSenderDict

        message["SenderId"] = "KL21J00003"
        caplog.clear()
        api.processMessage(message)
        assert len(caplog.records) == 1
        assert "KL21J00003" in caplog.messages[0]
        assert caplog.records[0].levelname == "ERROR"
        assert api.metrics.sibling_message_drop == 0
        assert api.metrics.sender_message_drop == 3
        assert len(api._badSenderDict) == 2
        assert "KL21J00002" in api._badSenderDict
        assert "KL21J00003" in api._badSenderDict
