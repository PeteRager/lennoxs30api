"""Test sibling processing"""
import logging
from lennoxs30api.s30api_async import (
    lennox_system,
    s30api_async,
)

from tests.conftest import loadfile


def test_process_sibling_message(api: s30api_async):
    """Test processing a message from a sibling S30"""
    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"

    assert len(lsystem.siblings)== 0
    message = loadfile("sibling.json")
    api.processMessage(message)

    assert lsystem.siblings[0].sibling_self_identifier == "KL21J00001"
    assert lsystem.siblings[0].sibling_identifier == "KL21J00002"
    assert lsystem.siblings[0].sibling_systemName == '"Bedrooms"'
    assert lsystem.siblings[0].sibling_nodePresent is True
    assert lsystem.siblings[0].sibling_portNumber == 443
    assert lsystem.siblings[0].sibling_ipAddress == "10.0.0.2"


def test_process_multiple_sibling_message(api: s30api_async, caplog):
    """Test processing multiple messages from a sibling S30"""
    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"

    assert len(lsystem.siblings) == 0

    # Testing the error reporting if we encouter multiple siblings
    message = loadfile("sibling_multiple.json")
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        api.processMessage(message)
        assert len(lsystem.siblings) == 2   
        # The first record should process
        assert lsystem.siblings[0].sibling_self_identifier == "KL21J00001"
        assert lsystem.siblings[0].sibling_identifier == "KL21J00002"
        assert lsystem.siblings[0].sibling_systemName == '"Bedrooms"'
        assert lsystem.siblings[0].sibling_nodePresent is True
        assert lsystem.siblings[0].sibling_portNumber == 443
        assert lsystem.siblings[0].sibling_ipAddress == "10.0.0.2"

        assert lsystem.siblings[1].sibling_self_identifier == "KL21J00003"
        assert lsystem.siblings[1].sibling_identifier == "KL21J00004"
        assert lsystem.siblings[1].sibling_systemName == '"Living Room"'
        assert lsystem.siblings[1].sibling_nodePresent is True
        assert lsystem.siblings[1].sibling_portNumber == 443
        assert lsystem.siblings[1].sibling_ipAddress == "10.0.0.3"


def test_process_zero_sibling_message(api: s30api_async, caplog):
    """Test processing no sibling message"""
    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"

    assert len(lsystem.siblings) == 0

    message = loadfile("sibling_zero.json")
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        api.processMessage(message)
        assert len(lsystem.siblings) == 0
        assert len(caplog.records) == 0

def test_process_unknown_sender(api: s30api_async, caplog):
    """Test processing from unknown sender"""
    message = loadfile("system_uptime.json","bad_sender")
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        api.processMessage(message)
        assert len(caplog.records) == 2
        assert "bad_sender" in caplog.messages[0]
        assert "currentTime" in caplog.messages[1]        
        api.processMessage(message)
        assert len(caplog.records) == 2

def test_process_unknown_sender_no_init(api: s30api_async, caplog):
    """Test processing from unknown sender when systems are not all initialized."""
    lsystem: lennox_system = api.system_list[1]
    lsystem.systemMessageProcessed = False
    message = loadfile("system_uptime.json","bad_sender")
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        api.processMessage(message)
        assert len(caplog.records) == 0

def test_process_message_from_sibling(api: s30api_async, caplog):
    """Test processing message from sibling"""

    message = loadfile("sibling.json")
    api.processMessage(message)
    message = loadfile("system_uptime.json","KL21J00002")
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        api.processMessage(message)
        assert len(caplog.records) == 2
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[1].levelname == "WARNING"
        assert "KL21J00002" in caplog.messages[0]
        assert "currentTime" in caplog.messages[1]        
