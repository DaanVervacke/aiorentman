"""Transport tests: status mapping, payload handling, and session ownership."""

from typing import cast
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from aiorentman._transport import (
    OwnedSession,
    _error_detail,
    _raise_for_status,
    _retry_after,
    json_payload,
    request,
    request_json,
)
from aiorentman.const import BASE_URL
from aiorentman.exceptions import (
    RentmanAuthenticationError,
    RentmanAuthorizationError,
    RentmanCommunicationError,
    RentmanInvalidResponseError,
    RentmanNotFoundError,
    RentmanRateLimitError,
    RentmanTimeoutError,
    RentmanValidationError,
)

from .conftest import api_url


async def test_request_json_returns_the_parsed_body() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment/12"), payload={"data": {"id": 12}})
            result = await request_json(session, method="GET", url=f"{BASE_URL}/equipment/12")
    assert result == {"data": {"id": 12}}


async def test_status_401_maps_to_authentication_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment/12"), status=401)
            with pytest.raises(RentmanAuthenticationError, match="rejected the token") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment/12")
    assert info.value.status == 401


async def test_status_403_maps_to_authorization_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment/12"), status=403)
            with pytest.raises(RentmanAuthorizationError, match="does not grant access") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment/12")
    assert info.value.status == 403


async def test_status_404_maps_to_not_found_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment/99999"), status=404)
            with pytest.raises(RentmanNotFoundError, match="no such object") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment/99999")
    assert info.value.status == 404


async def test_status_429_maps_to_rate_limit_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=429)
            with pytest.raises(RentmanRateLimitError, match="rate limit") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")
    assert info.value.status == 429
    assert info.value.retry_after is None


async def test_status_400_maps_to_validation_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=400, body="color is required")
            with pytest.raises(RentmanValidationError, match="rejected the request") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")
    assert info.value.status == 400
    assert "color is required" in str(info.value)


async def test_status_400_without_a_body_carries_no_detail() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=400, body="")
            with pytest.raises(RentmanValidationError, match="rejected the request as invalid"):
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")


async def test_request_json_sends_the_body() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.post(api_url("/tasks"), payload={"data": {"id": 1}})
            result = await request_json(
                session,
                method="POST",
                url=f"{BASE_URL}/tasks",
                body={"color": "#ffffff"},
            )
            call = m.requests[("POST", URL(f"{BASE_URL}/tasks"))][0]
    assert result == {"data": {"id": 1}}
    assert call.kwargs["json"] == {"color": "#ffffff"}


async def test_status_500_maps_to_communication_error_with_detail() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=500, body="upstream failure")
            with pytest.raises(RentmanCommunicationError, match="upstream failure") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")
    assert info.value.status == 500
    assert "/equipment" in str(info.value)


async def test_error_without_a_body_carries_no_detail() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=500, body="")
            with pytest.raises(RentmanCommunicationError, match="Rentman API error 500"):
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")


async def test_error_detail_is_truncated() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=500, body="x" * 500)
            with pytest.raises(RentmanCommunicationError) as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")
    assert "x" * 200 in str(info.value)
    assert "x" * 201 not in str(info.value)


async def test_timeout_maps_to_timeout_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), exception=TimeoutError())
            with pytest.raises(RentmanTimeoutError, match="Timeout"):
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")


async def test_client_error_maps_to_communication_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), exception=aiohttp.ClientError("boom"))
            with pytest.raises(RentmanCommunicationError, match="ClientError"):
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")


async def test_request_can_skip_status_checking() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=500, payload={"data": []})
            async with request(
                session,
                method="GET",
                url=f"{BASE_URL}/equipment",
                raise_on_error=False,
            ) as response:
                assert response.status == 500


async def test_json_payload_returns_none_for_an_empty_body() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), body="")
            result = await request_json(session, method="GET", url=f"{BASE_URL}/equipment")
    assert result is None


async def test_json_payload_rejects_invalid_json() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), body="not json")
            with pytest.raises(RentmanInvalidResponseError, match="not valid JSON"):
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")


async def test_json_payload_maps_read_failures() -> None:
    response = Mock(spec=aiohttp.ClientResponse)
    response.text = AsyncMock(side_effect=aiohttp.ClientError("unreadable"))
    with pytest.raises(RentmanInvalidResponseError, match="could not be read"):
        await json_payload(cast("aiohttp.ClientResponse", response))


async def test_error_detail_survives_unreadable_bodies() -> None:
    response = Mock(spec=aiohttp.ClientResponse)
    response.text = AsyncMock(side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "bad"))
    assert await _error_detail(cast("aiohttp.ClientResponse", response)) == ""


async def test_owned_session_closes_only_what_it_created() -> None:
    async with aiohttp.ClientSession() as injected:
        owned = OwnedSession(session=injected, owned=False)
        await owned.close_if_owned()
        assert not injected.closed
    foreign = OwnedSession(session=aiohttp.ClientSession(), owned=True)
    await foreign.close_if_owned()
    assert foreign.session.closed


def test_retry_after_reads_numeric_headers() -> None:
    response = Mock(spec=aiohttp.ClientResponse)
    response.headers = {"Retry-After": "30"}
    assert _retry_after(cast("aiohttp.ClientResponse", response)) == 30


def test_retry_after_returns_none_without_the_header() -> None:
    response = Mock(spec=aiohttp.ClientResponse)
    response.headers = {}
    assert _retry_after(cast("aiohttp.ClientResponse", response)) is None


def test_retry_after_returns_none_for_non_numeric_headers() -> None:
    response = Mock(spec=aiohttp.ClientResponse)
    response.headers = {"Retry-After": "soon"}
    assert _retry_after(cast("aiohttp.ClientResponse", response)) is None


async def test_rate_limit_error_carries_retry_after() -> None:
    response = Mock(spec=aiohttp.ClientResponse)
    response.status = 429
    response.headers = {"Retry-After": "30"}
    with pytest.raises(RentmanRateLimitError) as info:
        await _raise_for_status(
            cast("aiohttp.ClientResponse", response),
            method="GET",
            path="/equipment",
        )
    assert info.value.retry_after == 30
    assert info.value.status == 429
