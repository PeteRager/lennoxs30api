from lennoxs30api.message_logger import REDACTED, MessageLogger

import logging
import json
import os
import timeit


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


def test_logging_enable_disable(caplog):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    msg = {"test": "a", "test": "b"}
    mlog = MessageLogger(logger)
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        mlog.log_message(pii_in_messages=True, msg=msg)
        assert len(caplog.records) == 0
    logger.setLevel(logging.DEBUG)
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        mlog.log_message(pii_in_messages=True, msg=msg)
        assert len(caplog.records) == 1
        log_msg = caplog.messages[0]
        assert log_msg == json.dumps(msg, indent=4)


def test_logging_remove_email(caplog):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    mlog = MessageLogger(logger)
    msg = loadfile("ventilation_system_on.json")
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        mlog.log_message(pii_in_messages=True, msg=msg)
        assert len(caplog.records) == 1
        log_msg = caplog.messages[0]
        assert log_msg == json.dumps(msg, indent=4)
    logger.setLevel(logging.DEBUG)
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        mlog.log_message(pii_in_messages=False, msg=msg)
        assert len(caplog.records) == 1
        log_msg = caplog.messages[0]
        assert log_msg != json.dumps(msg, indent=4)
        msg_cleaned = json.loads(log_msg)
        assert msg_cleaned["TargetID"] == REDACTED


def test_logging_remove_redacted(caplog):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    mlog = MessageLogger(logger)
    msg = loadfile("login_response.json")
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        mlog.log_message(pii_in_messages=False, msg=msg)
        assert len(caplog.records) == 1
        log_msg = caplog.messages[0]
        assert log_msg != json.dumps(msg, indent=4)
        msg_cleaned = json.loads(log_msg)
        home_addr = msg_cleaned["readyHomes"]["homes"][0]["address"]
        assert home_addr["streetAddress1"] == REDACTED
        assert home_addr["streetAddress2"] == REDACTED
        assert home_addr["city"] == REDACTED
        assert home_addr["state"] != REDACTED
        assert home_addr["country"] == REDACTED
        assert home_addr["zip"] == REDACTED
        assert home_addr["latitude"] == REDACTED
        assert home_addr["longitude"] == REDACTED
        # Verify we are not redacting the passed in message!
        home_addr = msg["readyHomes"]["homes"][0]["address"]
        assert home_addr["streetAddress1"] != REDACTED
        assert home_addr["streetAddress2"] != REDACTED
        assert home_addr["city"] != REDACTED
        assert home_addr["state"] != REDACTED
        assert home_addr["country"] != REDACTED
        assert home_addr["zip"] != REDACTED
        assert home_addr["latitude"] != REDACTED
        assert home_addr["longitude"] != REDACTED

        user_token = msg_cleaned["ServerAssignedRoot"]["serverAssigned"]["security"][
            "userToken"
        ]
        assert user_token["encoded"] == REDACTED
        assert user_token["refreshToken"] == REDACTED

        user_token = msg["ServerAssignedRoot"]["serverAssigned"]["security"][
            "userToken"
        ]
        assert user_token["encoded"] != REDACTED
        assert user_token["refreshToken"] != REDACTED


def test_logging_redacted_performance(caplog):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    mlog = MessageLogger(logger)
    msg = loadfile("config_response_system_01.json")
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        t = timeit.timeit(
            lambda: mlog.log_message(pii_in_messages=False, msg=msg), number=1
        )
        print(t)
        t1 = timeit.timeit(
            lambda: mlog.log_message(pii_in_messages=True, msg=msg), number=1
        )
        print(t1)
        pass
