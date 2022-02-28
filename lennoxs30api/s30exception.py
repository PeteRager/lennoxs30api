EC_AUTHENTICATE = 1
EC_LOGIN = 2
EC_NEGOTIATE = 3
EC_SUBSCRIBE = 4
EC_RETRIEVE = 5
EC_REQUEST_DATA_HELPER = 6
EC_BAD_PARAMETERS = 7
EC_SETMODE_HELPER = 8
EC_PUBLISH_MESSAGE = 9
EC_PROCESS_MESSAGE = 10
EC_COMMS_ERROR = 11
EC_NO_SCHEDULE = 12
EC_HTTP_ERR = 13
EC_LOGOUT = 14
EC_CONFIG_TIMEOUT = 15
EC_UNAUTHORIZED = 401

from asyncio import TimeoutError

from aiohttp import (
    ClientResponseError,
    ServerDisconnectedError,
    ClientConnectorError,
    ClientConnectionError,
)

from lennoxs30api.metrics import Metrics


class S30Exception(Exception):
    def __init__(self, value: str, error_code: int, reference: int) -> None:
        """Initialize error."""
        super().__init__(self, value)
        self.message = value
        self.error_code = error_code
        self.reference = reference

    def as_string(self) -> str:
        return f"Code [{self.error_code}] Reference [{self.reference}] [{self.message}]"

    pass


def s30exception_from_comm_exception(
    e: Exception, operation: str, url: str, metrics: Metrics
) -> S30Exception:
    if isinstance(e, ClientResponseError):
        metrics.inc_client_response_errors()
        msg = (
            f"Error while executing request: [{e.message}]: "
            f"error={type(e)}, resp.status=[{e.status}], "
            f"resp.request_info=[{e.request_info}], "
            f"resp.headers=[{e.headers}]"
        )
        # When this is seen: "Content-Length can't be present with Transfer-Encoding"
        # indicates that the client subscription needs to be re-established.
        return S30Exception(
            f"{operation} failed due to client response error [{url}] ClientResponseError {msg}",
            EC_COMMS_ERROR,
            100,
        )
    if isinstance(e, ServerDisconnectedError):
        metrics.inc_server_disconnect()
        return S30Exception(
            f"{operation} failed due Server Disconnected [{url}]",
            EC_COMMS_ERROR,
            200,
        )
    if isinstance(e, TimeoutError):
        metrics.inc_timeout()
        return S30Exception(
            f"{operation} failed - Communication TimeoutError exceeded configured timeout [{url}]",
            EC_COMMS_ERROR,
            300,
        )
    if isinstance(e, ClientConnectorError):
        metrics.inc_client_response_errors()
        return S30Exception(
            f"{operation} Client Connector Error - failed due host not reachable url [{url}]",
            EC_COMMS_ERROR,
            400,
        )
    if isinstance(e, ClientConnectionError):
        metrics.inc_connection_errors()
        return S30Exception(
            f"{operation} failed due host not reachable url [{url}] {e}",
            EC_COMMS_ERROR,
            500,
        )
    return None
