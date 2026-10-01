"""Transport tests: status mapping, payload handling, and session ownership."""

from typing import cast
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest
from aioresponses import aioresponses

from aiorentman._transport import (
    OwnedSession,
    _error_detail,
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


async def test_status_500_maps_to_communication_error_with_detail() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=500, body="upstream failure")
            with pytest.raises(RentmanCommunicationError, match="upstream failure") as info:
                await request_json(session, method="GET", url=f"{BASE_URL}/equipment")
    assert info.value.status == 500


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
