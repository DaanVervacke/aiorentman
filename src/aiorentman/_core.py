"""Client plumbing: token, pacing, the request path, and cursor iteration."""

import logging
import os
from collections.abc import AsyncIterator
from typing import Self
from urllib.parse import urlsplit

import aiohttp

from ._base import RentmanPage
from ._endpoint_types import Endpoint
from ._ratelimit import RequestPacer
from ._transport import OwnedSession, request_json
from .const import (
    BASE_URL,
    DEFAULT_MAX_CONCURRENT_REQUESTS,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_REQUESTS_PER_SECOND,
    TOKEN_ENV_VAR,
    USER_AGENT,
)
from .exceptions import (
    RentmanAuthenticationError,
    RentmanClientClosedError,
    RentmanInvalidResponseError,
)

_LOGGER = logging.getLogger("aiorentman.client")


class ClientCore:
    """Token, session, pacing, and request plumbing behind every endpoint method."""

    def __init__(
        self,
        session: aiohttp.ClientSession | None = None,
        *,
        token: str | None = None,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        requests_per_second: float | None = DEFAULT_REQUESTS_PER_SECOND,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
    ) -> None:
        """Create a client from a session and an API token.

        The token comes from the argument or from the RENTMAN_TOKEN
        environment variable. Regenerating the token in Rentman invalidates
        the previous one. A requests_per_second that is not positive or a
        max_concurrent below 1 raises ValueError.
        """
        resolved = token or os.environ.get(TOKEN_ENV_VAR)
        if not resolved:
            msg = f"A token is required: pass token or set the {TOKEN_ENV_VAR} environment variable"
            raise RentmanAuthenticationError(msg)
        self._pacer = RequestPacer(
            requests_per_second=requests_per_second,
            max_concurrent=max_concurrent,
        )
        self._owned_session = OwnedSession(
            session=aiohttp.ClientSession() if session is None else session,
            owned=session is None,
        )
        self._token = resolved
        self._request_timeout = request_timeout
        self._closed = False

    async def _call[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, ModelT],
        args: ArgsT,
        cursor_url: str | None = None,
    ) -> ModelT:
        """Run one endpoint against the API and parse the payload."""
        self._assert_open()
        payload = await self._request_json(endpoint, args, cursor_url)
        return endpoint.parse(payload, args)

    async def _request_json[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, ModelT],
        args: ArgsT,
        cursor_url: str | None,
    ) -> object:
        url, params = self._build_request(endpoint, args, cursor_url)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        async with self._pacer.request_slot():
            return await request_json(
                self._owned_session.session,
                method=endpoint.method,
                url=url,
                headers=headers,
                params=params,
                body=endpoint.body(args),
                timeout=self._request_timeout,
            )

    def _build_request[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, ModelT],
        args: ArgsT,
        cursor_url: str | None,
    ) -> tuple[str, dict[str, str] | None]:
        if cursor_url is None:
            return f"{BASE_URL}{endpoint.path(args)}", endpoint.params(args)
        url, query = _split_cursor_url(cursor_url)
        _LOGGER.debug("Following collection cursor to %s", url)
        if not query:
            return url, None
        return f"{url}?{query}", None

    async def _iter_collection[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, RentmanPage[ModelT]],
        args: ArgsT,
    ) -> AsyncIterator[ModelT]:
        """Yield every item of one collection, following next_page_url."""
        cursor_url: str | None = None
        seen_cursors: set[str] = set()
        while True:
            page = await self._call(endpoint, args, cursor_url)
            for item in page.items:
                yield item
            if page.next_page_url is None:
                return
            if page.next_page_url in seen_cursors:
                msg = "The next page URL repeats an earlier page"
                raise RentmanInvalidResponseError(msg)
            seen_cursors.add(page.next_page_url)
            cursor_url = page.next_page_url

    def _assert_open(self) -> None:
        if self._closed:
            msg = "The client is closed"
            raise RentmanClientClosedError(msg)

    async def async_close(self) -> None:
        """Close the session when this library created it."""
        self._closed = True
        await self._owned_session.close_if_owned()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.async_close()


def _split_cursor_url(url: str) -> tuple[str, str]:
    """Validate one next_page_url and split it into its URL and query string."""
    try:
        split = urlsplit(url)
    except ValueError as exc:
        msg = "The next page URL is malformed"
        raise RentmanInvalidResponseError(msg) from exc
    if f"{split.scheme}://{split.netloc}" != BASE_URL:
        msg = f"The next page URL leaves {BASE_URL}"
        raise RentmanInvalidResponseError(msg)
    base = f"{split.scheme}://{split.netloc}{split.path}"
    return base, split.query
