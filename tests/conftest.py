"""Shared fixtures and response mocks for aiorentman tests."""

import inspect
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from unittest.mock import Mock

import aiohttp
import pytest
from aiohttp import ClientResponse
from aioresponses import core as _aioresponses_core

from aiorentman.client import RentmanClient
from aiorentman.const import BASE_URL

FIXTURES_DIR = Path(__file__).parent / "fixtures"

TOKEN = "test-rentman-token"

EMPTY_PAGE: dict[str, Any] = {
    "data": [],
    "itemCount": 0,
    "limit": 300,
    "offset": 0,
    "next_page_url": None,
}

MINIMAL_ITEM: dict[str, Any] = {"data": {"id": 1}}


@pytest.fixture
def load_fixture() -> Callable[[str], Any]:
    """Return a helper that loads a JSON fixture by name."""

    def _load(name: str) -> Any:
        return json.loads((FIXTURES_DIR / name).read_text())

    return _load


@pytest.fixture
def created_sessions(monkeypatch: pytest.MonkeyPatch) -> list[aiohttp.ClientSession]:
    """Track every aiohttp session the library creates."""
    created: list[aiohttp.ClientSession] = []
    real_session_cls = aiohttp.ClientSession

    def _tracking_factory(*args: Any, **kwargs: Any) -> aiohttp.ClientSession:
        session = real_session_cls(*args, **kwargs)
        created.append(session)
        return session

    monkeypatch.setattr(aiohttp, "ClientSession", _tracking_factory)
    return created


_original_build_response = _aioresponses_core.RequestMatch._build_response


def _build_response_with_stream_writer(self: Any, *args: Any, **kwargs: Any) -> Any:
    response_class = kwargs.get("response_class") or ClientResponse
    if "stream_writer" in inspect.signature(response_class).parameters:

        class _StreamWriterCompatResponse(response_class):  # type: ignore[misc, valid-type]
            def __init__(self, *a: Any, **kw: Any) -> None:
                kw.setdefault("stream_writer", Mock(output_size=0))
                super().__init__(*a, **kw)

        kwargs["response_class"] = _StreamWriterCompatResponse
    return _original_build_response(self, *args, **kwargs)


_aioresponses_core.RequestMatch._build_response = _build_response_with_stream_writer  # type: ignore[method-assign]


def fixture_path(name: str) -> Path:
    """Return the path of one fixture file."""
    return FIXTURES_DIR / name


def api_url(path: str) -> re.Pattern[str]:
    """Match one API path regardless of its query string."""
    return re.compile(rf"^{re.escape(BASE_URL)}{re.escape(path)}(\?.*)?$")


def cursor_api_url(path: str) -> re.Pattern[str]:
    """Match one API path that carries a cursor query parameter."""
    return re.compile(rf"^{re.escape(BASE_URL)}{re.escape(path)}\?cursor=[^&]+.*$")


def cast_response(payload: Any) -> dict[str, Any]:
    """Narrow a loaded fixture to a JSON object."""
    return cast("dict[str, Any]", payload)


def make_client(session: aiohttp.ClientSession | None = None) -> RentmanClient:
    """Create a test client with pacing disabled and a fixed token."""
    return RentmanClient(session, token=TOKEN, requests_per_second=None)
