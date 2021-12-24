import logging
import json
import copy

REDACTED: str = "**redacted**"


class MessageLogger(object):
    def __init__(
        self, logger=None, enabled: bool = True, message_logging_file: str = None
    ):
        if message_logging_file != None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(level=logging.DEBUG)
            logFormatter = logging.Formatter(
                "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
            )

            fileHandler = logging.FileHandler(message_logging_file)
            fileHandler.setFormatter(logFormatter)
            fileHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(fileHandler)
            # When running in this mode, message should only appear in the message log and not also the default log.
            self.logger.propagate = False
        else:
            self.logger = logger
        self.enabled = enabled
        self.redacted_fields = [
            "streetAddress1",
            "streetAddress2",
            "city",
            "state",
            "country",
            "zip",
            "latitude",
            "longitude",
            "encoded",
            "refreshToken",
            "SenderId",
            "SenderID",
            "macAddr",
            "ssid",
            "ip",
            "router",
            "dns",
            "subnetMask",
            "password",
            "ip4addr",
            "ConnectionToken",
            "ConnectionId",
        ]

    def remove_redacted_fields(self, log_message):
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
        if (
            self.logger == None
            or self.enabled == False
            or self.logger.isEnabledFor(logging.DEBUG) == False
        ):
            return

        if pii_in_messages == False:
            log_message = copy.deepcopy(msg)
            if "TargetID" in log_message:
                if "@" in log_message["TargetID"]:
                    log_message["TargetID"] = REDACTED
            log_message = self.remove_redacted_fields(log_message)
        else:
            log_message = msg
        self.logger.debug(json.dumps(log_message, indent=4))
