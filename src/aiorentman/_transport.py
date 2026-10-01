"""HTTP plumbing: session ownership and the request and JSON helpers."""

import asyncio
import json
import logging
import socket
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from urllib.parse import urlsplit

import aiohttp

from .exceptions import (
    RentmanAuthenticationError,
    RentmanAuthorizationError,
    RentmanCommunicationError,
    RentmanError,
    RentmanInvalidResponseError,
    RentmanNotFoundError,
    RentmanRateLimitError,
    RentmanTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class OwnedSession:
    """A ClientSession plus whether this library created and must close it."""

    session: aiohttp.ClientSession
    owned: bool

    async def close_if_owned(self) -> None:
        """Close the session when this library created it."""
        if self.owned:
            await self.session.close()


@asynccontextmanager
async def request(
    session: aiohttp.ClientSession,
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    raise_on_error: bool = True,
    timeout: float = 30.0,  # noqa: ASYNC109
) -> AsyncIterator[aiohttp.ClientResponse]:
    """Perform one HTTP request and map failures to library exceptions."""
    try:
        started = time.monotonic()
        async with asyncio.timeout(timeout):
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            ) as response:
                split = urlsplit(url)
                _LOGGER.debug(
                    "%s %s%s -> %s in %.3fs",
                    method,
                    split.netloc,
                    split.path,
                    response.status,
                    time.monotonic() - started,
                )
                if raise_on_error:
                    await _raise_for_status(response)
                yield response
    except RentmanError:
        raise
    except TimeoutError as exc:
        msg = f"Timeout communicating with the Rentman API ({exc.__class__.__name__})"
        raise RentmanTimeoutError(msg) from exc
    except (aiohttp.ClientError, socket.gaierror) as exc:
        msg = f"Error communicating with the Rentman API ({exc.__class__.__name__})"
        raise RentmanCommunicationError(msg) from exc


async def _raise_for_status(response: aiohttp.ClientResponse) -> None:
    if response.status == HTTPStatus.UNAUTHORIZED:
        msg = "The Rentman API rejected the token (401)"
        raise RentmanAuthenticationError(msg, status=401)
    if response.status == HTTPStatus.FORBIDDEN:
        msg = "The token does not grant access to this resource (403)"
        raise RentmanAuthorizationError(msg, status=403)
    if response.status == HTTPStatus.NOT_FOUND:
        msg = "The Rentman API has no such object (404)"
        raise RentmanNotFoundError(msg, status=404)
    if response.status == HTTPStatus.TOO_MANY_REQUESTS:
        msg = "The Rentman rate limit was exceeded (429)"
        raise RentmanRateLimitError(msg, status=429)
    if response.status >= HTTPStatus.BAD_REQUEST:
        detail = await _error_detail(response)
        msg = f"Rentman API error {response.status}"
        if detail:
            msg = f"{msg}: {detail}"
        raise RentmanCommunicationError(msg, status=response.status)


_ERROR_DETAIL_LIMIT = 200


async def _error_detail(response: aiohttp.ClientResponse) -> str:
    try:
        text = await response.text()
    except aiohttp.ClientError, UnicodeDecodeError:
        return ""
    if len(text) > _ERROR_DETAIL_LIMIT:
        return text[:_ERROR_DETAIL_LIMIT]
    return text.strip()


async def request_json(
    session: aiohttp.ClientSession,
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    timeout: float = 30.0,  # noqa: ASYNC109
) -> Any:
    """Make a request and return the parsed JSON body."""
    async with request(
        session,
        method=method,
        url=url,
        headers=headers,
        params=params,
        timeout=timeout,
    ) as response:
        return await json_payload(response)


async def json_payload(response: aiohttp.ClientResponse) -> Any:
    """Parse the response body as JSON of any shape, returning None for an empty body."""
    try:
        text = await response.text()
    except aiohttp.ClientError as exc:
        msg = "Response body could not be read"
        raise RentmanInvalidResponseError(msg) from exc
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except ValueError as exc:
        msg = "Response body is not valid JSON"
        raise RentmanInvalidResponseError(msg) from exc
