"""Tests the S30Exception class"""
import asyncio
import aiohttp
from lennoxs30api.metrics import Metrics
from lennoxs30api.s30exception import (
    EC_COMMS_ERROR,
    S30Exception,
    s30exception_from_comm_exception,
)


def test_client_response_error(metrics: Metrics):
    """Test client response error"""
    operation = "test_op"
    url = "testurl.com"
    metrics.reset()
    e: Exception = aiohttp.ClientResponseError(
        status=400,
        request_info="myurl",
        headers={"header_1": "1", "header_2": "2"},
        message="unexpected content-length header",
        history={},
    )
    se: S30Exception = s30exception_from_comm_exception(
        e, operation=operation, url=url, metrics=metrics
    )
    assert se is not None
    assert isinstance(se, S30Exception)
    assert se.error_code == EC_COMMS_ERROR
    assert se.reference == 100
    assert "unexpected content-length header" in se.message
    assert operation in se.message
    assert url in se.message
    assert metrics.client_response_errors == 1
    assert metrics.error_count == 0
    assert metrics.timeouts == 0
    assert metrics.server_disconnects == 0
    assert metrics.last_error_time is not None

    metrics.reset()
    e: Exception = aiohttp.ClientResponseError(
        status=400,
        request_info="myurl",
        headers={"header_1": "1", "header_2": "2"},
        message="some other error",
        history={},
    )
    se: S30Exception = s30exception_from_comm_exception(
        e, operation=operation, url=url, metrics=metrics
    )

    assert se is not None
    assert isinstance(se, S30Exception)
    assert se.error_code == EC_COMMS_ERROR
    assert se.reference == 100
    assert "some other error" in se.message
    assert operation in se.message
    assert url in se.message
    assert metrics.client_response_errors == 1
    assert metrics.error_count == 0
    assert metrics.timeouts == 0
    assert metrics.server_disconnects == 0
    assert metrics.last_error_time is not None

    metrics.reset()
    e = aiohttp.ServerDisconnectedError()
    se: S30Exception = s30exception_from_comm_exception(
        e, operation=operation, url=url, metrics=metrics
    )
    assert se is not None
    assert isinstance(se, S30Exception)
    assert se.error_code == EC_COMMS_ERROR
    assert se.reference == 200
    assert "Server Disconnected" in se.message
    assert operation in se.message
    assert url in se.message
    assert metrics.client_response_errors == 0
    assert metrics.error_count == 0
    assert metrics.timeouts == 0
    assert metrics.server_disconnects == 1
    assert metrics.last_error_time is not None

    metrics.reset()
    e = asyncio.TimeoutError()
    se: S30Exception = s30exception_from_comm_exception(
        e, operation=operation, url=url, metrics=metrics
    )
    assert se is not None
    assert isinstance(se, S30Exception)
    assert se.error_code == EC_COMMS_ERROR
    assert se.reference == 300
    assert "Timeout" in se.message
    assert operation in se.message
    assert url in se.message
    assert metrics.client_response_errors == 0
    assert metrics.error_count == 0
    assert metrics.timeouts == 1
    assert metrics.server_disconnects == 0
    assert metrics.last_error_time is not None

    metrics.reset()
