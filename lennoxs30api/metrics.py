from datetime import datetime
import pytz


class Metrics:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
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

        self.sibling_message_drop: int = 0
        self.sender_message_drop: int = 0

        self.bytes_in: int = 0
        self.bytes_out: int = 0

    def now(self) -> datetime:
        return pytz.utc.localize(datetime.utcnow())

    def getMetricList(self):
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
        self.message_count += 1
        self.last_message_time = self.now()
        self.last_metric_time = self.now()

    def inc_send_count(self, bytes: int) -> None:
        self.send_count += 1
        self.last_send_time = self.now()
        self.bytes_out += bytes

    def inc_receive_count(self) -> None:
        self.receive_count += 1
        self.last_receive_time = self.now()

    def inc_receive_bytes(self, bytes: int) -> None:
        if bytes != None:
            self.bytes_in += bytes

    def inc_receive_message_error(self) -> None:
        self.last_error_time = self.now()
        self.error_count += 1

    def inc_timeout(self) -> None:
        self.timeouts += 1
        self.last_error_time = self.now()

    def inc_connection_errors(self) -> None:
        self.connection_errors += 1
        self.last_error_time = self.now()

    def inc_server_disconnect(self) -> None:
        self.server_disconnects += 1
        self.last_error_time = self.now()

    def inc_client_response_errors(self) -> None:
        self.client_response_errors += 1
        self.last_error_time = self.now()

    def inc_sibling_message_drop(self) -> None:
        self.sibling_message_drop += 1

    def inc_sender_message_drop(self) -> None:
        self.sender_message_drop += 1

    def process_http_code(self, http_code: int) -> None:
        if http_code >= 200 and http_code <= 299:
            self.http_2xx_cnt += 1
            return

        self.error_count += 1
        if http_code >= 400 and http_code <= 499:
            self.http_4xx_cnt += 1
        elif http_code >= 500 and http_code <= 599:
            self.http_5xx_cnt += 1

        self.last_error_time = self.now()
