"""Modules to log messages to files"""
# pylint: disable=line-too-long

import logging
import json
import copy

REDACTED: str = "**redacted**"


class MessageLogger(object):
    """Class to log messages"""
    def __init__(
        self, logger=None, enabled: bool = True, message_logging_file: str = None
    ):
        if message_logging_file is not None:
            self.logger_name = __name__ + "." + message_logging_file
            self.logger = logging.getLogger(self.logger_name)
            self.logger.setLevel(level=logging.DEBUG)
            log_formatter = logging.Formatter(
                "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
            )
            ## If the logger already exists and has a handler to write to the file then do not add another one.
            if len(self.logger.handlers) == 0:
                file_handler = logging.FileHandler(message_logging_file)
                file_handler.setFormatter(log_formatter)
                file_handler.setLevel(logging.DEBUG)
                self.logger.addHandler(file_handler)
            # When running in this mode, message should only appear in the message log and not also the default log.
            self.logger.propagate = False
        else:
            self.logger = logger
        self.enabled = enabled
        self.redacted_fields = [
            "streetAddress1",
            "streetAddress2",
            "city",
            "country",
            "email",
            "firstName",
            "lastName",
            "tel",
            "zip",
            "latitude",
            "longitude",
            "encoded",
            "refreshToken",
            "macAddr",
            "ssid",
            "bssid",
            "deviceKey",
            "hvacGuid",
            "connectionString",
            "deviceId",
            "ip",
            "router",
            "dns",
            "subnetMask",
            "password",
            "oldPassword",
            "ip4addr",
            "ConnectionToken",
            "ConnectionId",
        ]

    def remove_redacted_fields(self, log_message):
        """Removes redacted fields from messages"""
        for k, v in log_message.items():
            if isinstance(v, dict):
                log_message[k] = self.remove_redacted_fields(v)
            elif isinstance(v, list):
                log_message[k] = [self.remove_redacted_fields(i) for i in v]
        for field in self.redacted_fields:
            if field in log_message:
                log_message[field] = REDACTED
        return log_message

    def log_message(self, pii_in_messages: bool, msg) -> None:
        """Logs a message"""
        if (
            self.logger is None
            or self.enabled is False
            or self.logger.isEnabledFor(logging.DEBUG) is False
        ):
            return

        if pii_in_messages is False:
            log_message = copy.deepcopy(msg)
            if "TargetID" in log_message:
                if "@" in log_message["TargetID"]:
                    log_message["TargetID"] = REDACTED
            log_message = self.remove_redacted_fields(log_message)
        else:
            log_message = msg
        self.logger.debug(json.dumps(log_message, indent=4))
