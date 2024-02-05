"""Communication Metrics for communication to lennox controller"""
# pylint: disable=invalid-name

from datetime import datetime
import pytz


class Metrics:
    """Communication Metrics"""
    def __init__(self):
        self.error_count: int = 0
        self.message_count: int = 0
        self.receive_count: int = 0
        self.send_count: int = 0
        self.http_2xx_cnt: int = 0
        self.http_4xx_cnt: int = 0
        self.http_5xx_cnt: int = 0
        self.timeouts: int = 0
        self.server_disconnects: int = 0
        self.client_response_errors: int = 0
        self.connection_errors: int = 0
        self.last_receive_time: datetime = None
        self.last_send_time: datetime = None
        self.last_error_time: datetime = None
        self.last_reconnect_time: datetime = None
        self.last_message_time: datetime = None
        self.last_metric_time: datetime = None
        self.sibling_message_drop: int = 0
        self.sender_message_drop: int = 0
        self.bytes_in: int = 0
        self.bytes_out: int = 0

    def reset(self) -> None:
        """Reset the metrics"""
        self.error_count = 0
        self.message_count = 0
        self.receive_count = 0
        self.send_count = 0
        self.http_2xx_cnt = 0
        self.http_4xx_cnt = 0
        self.http_5xx_cnt = 0
        self.timeouts = 0
        self.server_disconnects = 0
        self.client_response_errors = 0
        self.connection_errors = 0
        self.last_receive_time= None
        self.last_send_time = None
        self.last_error_time = None
        self.last_reconnect_time = None
        self.last_metric_time = None
        self.last_message_time = None
        self.sibling_message_drop = 0
        self.sender_message_drop = 0
        self.bytes_in = 0
        self.bytes_out = 0

    def now(self) -> datetime:
        """Returns the localized datetime"""
        return pytz.utc.localize(datetime.utcnow())

    def getMetricList(self) -> dict[str, any]:
        """Return metric list as dict"""
        return {
            "message_count": self.message_count,
            "send_count": self.send_count,
            "receive_count": self.receive_count,
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
            "error_count": self.error_count,
            "http_2xx_cnt": self.http_2xx_cnt,
            "http_4xx_cnt": self.http_4xx_cnt,
            "http_5xx_cnt": self.http_5xx_cnt,
            "timeouts": self.timeouts,
            "client_response_errors": self.client_response_errors,
            "server_disconnects": self.server_disconnects,
            "connection_errors": self.connection_errors,
            "last_receive_time": self.last_receive_time,
            "last_error_time": self.last_error_time,
            "last_reconnect_time": self.last_reconnect_time,
            "last_message_time": self.last_message_time,
            "sender_message_drop": self.sender_message_drop,
            "sibling_message_drop": self.sibling_message_drop,
        }

    def inc_message_count(self) -> None:
        """Increment the message count"""
        self.message_count += 1
        self.last_message_time = self.now()
        self.last_metric_time = self.now()

    def inc_send_count(self, number_of_bytes: int) -> None:
        """Increment the send count"""
        self.send_count += 1
        self.last_send_time = self.now()
        self.bytes_out += number_of_bytes

    def inc_receive_count(self) -> None:
        """Increment the receive count"""
        self.receive_count += 1
        self.last_receive_time = self.now()

    def inc_receive_bytes(self, number_of_bytes: int) -> None:
        """Increment the receive number of bytes"""
        if number_of_bytes is not None:
            self.bytes_in += number_of_bytes

    def inc_receive_message_error(self) -> None:
        """Increment recevie errors"""
        self.last_error_time = self.now()
        self.error_count += 1

    def inc_timeout(self) -> None:
        """Increment timeouts"""
        self.timeouts += 1
        self.last_error_time = self.now()

    def inc_connection_errors(self) -> None:
        """Increment connection errors"""
        self.connection_errors += 1
        self.last_error_time = self.now()

    def inc_server_disconnect(self) -> None:
        """Increment server disconnects"""
        self.server_disconnects += 1
        self.last_error_time = self.now()

    def inc_client_response_errors(self) -> None:
        """Increment client response errors"""
        self.client_response_errors += 1
        self.last_error_time = self.now()

    def inc_sibling_message_drop(self) -> None:
        """Increment sibling message drops"""
        self.sibling_message_drop += 1

    def inc_sender_message_drop(self) -> None:
        """Increment sender message drops"""
        self.sender_message_drop += 1

    def process_http_code(self, http_code: int) -> None:
        """Process http return cord and increments appropriate counters"""
        if http_code >= 200 and http_code <= 299:
            self.http_2xx_cnt += 1
            return

        self.error_count += 1
        if http_code >= 400 and http_code <= 499:
            self.http_4xx_cnt += 1
        elif http_code >= 500 and http_code <= 599:
            self.http_5xx_cnt += 1

        self.last_error_time = self.now()
