"""Client tests: token resolution, wire pinning, cursors, and ownership."""

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

import aiohttp
import pytest
from aioresponses import aioresponses

from aiorentman import Query, RentmanClient, RentmanPage, Sort, eq, is_null, lt
from aiorentman.const import BASE_URL, DEFAULT_REQUESTS_PER_SECOND
from aiorentman.exceptions import (
    RentmanAuthenticationError,
    RentmanClientClosedError,
    RentmanInvalidResponseError,
    RentmanNotFoundError,
    RentmanRateLimitError,
)
from aiorentman.models import ActualContent, Equipment, Repair, SerialNumber

from .conftest import (
    EMPTY_ITEM,
    EMPTY_PAGE,
    TOKEN,
    api_url,
    cursor_api_url,
    make_client,
)

if TYPE_CHECKING:
    from aioresponses.core import RequestCall
    from yarl import URL

COLLECTIONS: tuple[tuple[Callable[[RentmanClient], Awaitable[RentmanPage[Any]]], str], ...] = (
    (lambda client: client.async_list_actual_content(), "/actualcontent"),
    (
        lambda client: client.async_list_actual_content_of_serial_number(41),
        "/serialnumbers/41/actualcontent",
    ),
    (lambda client: client.async_list_equipment(), "/equipment"),
    (
        lambda client: client.async_list_serial_numbers_of_equipment(12),
        "/equipment/12/serialnumbers",
    ),
    (
        lambda client: client.async_list_stock_movements_of_equipment(12),
        "/equipment/12/stockmovements",
    ),
    (lambda client: client.async_list_repairs_of_equipment(12), "/equipment/12/repairs"),
    (
        lambda client: client.async_list_equipment_set_content_of_equipment(34),
        "/equipment/34/equipmentsetscontent",
    ),
    (lambda client: client.async_list_serial_numbers(), "/serialnumbers"),
    (lambda client: client.async_list_equipment_assigned_serials(), "/equipmentassignedserials"),
    (
        lambda client: client.async_list_equipment_assigned_serials_of_serial_number(43),
        "/serialnumbers/43/equipmentassignedserials",
    ),
    (lambda client: client.async_list_equipment_set_content(), "/equipmentsetscontent"),
    (lambda client: client.async_list_folders(), "/folders"),
    (lambda client: client.async_list_stock_locations(), "/stocklocations"),
    (lambda client: client.async_list_warehouse_statuses(), "/warehousestatuses"),
    (lambda client: client.async_list_statuses(), "/statuses"),
    (lambda client: client.async_list_stock_movements(), "/stockmovements"),
    (lambda client: client.async_list_repairs(), "/repairs"),
    (lambda client: client.async_list_projects(), "/projects"),
    (
        lambda client: client.async_list_subprojects_of_project(480),
        "/projects/480/subprojects",
    ),
    (lambda client: client.async_list_subprojects(), "/subprojects"),
    (lambda client: client.async_list_project_equipment(), "/projectequipment"),
    (
        lambda client: client.async_list_project_equipment_of_project(480),
        "/projects/480/projectequipment",
    ),
    (
        lambda client: client.async_list_project_equipment_of_subproject(501),
        "/subprojects/501/projectequipment",
    ),
)

ITEMS: tuple[tuple[Callable[[RentmanClient], Awaitable[Any]], str], ...] = (
    (lambda client: client.async_get_actual_content(700), "/actualcontent/700"),
    (lambda client: client.async_get_equipment(12), "/equipment/12"),
    (lambda client: client.async_get_serial_number(41), "/serialnumbers/41"),
    (
        lambda client: client.async_get_equipment_assigned_serial(900),
        "/equipmentassignedserials/900",
    ),
    (lambda client: client.async_get_equipment_set_content(550), "/equipmentsetscontent/550"),
    (lambda client: client.async_get_folder(3), "/folders/3"),
    (lambda client: client.async_get_stock_location(2), "/stocklocations/2"),
    (lambda client: client.async_get_warehouse_status(1), "/warehousestatuses/1"),
    (lambda client: client.async_get_status(4), "/statuses/4"),
    (lambda client: client.async_get_stock_movement(610), "/stockmovements/610"),
    (lambda client: client.async_get_repair(220), "/repairs/220"),
    (lambda client: client.async_get_project(480), "/projects/480"),
    (lambda client: client.async_get_subproject(501), "/subprojects/501"),
    (lambda client: client.async_get_project_equipment(850), "/projectequipment/850"),
)

ITERATORS: tuple[tuple[Callable[[RentmanClient, Query | None], Any], str], ...] = (
    (lambda client, query: client.async_iter_actual_content(query), "/actualcontent"),
    (
        lambda client, query: client.async_iter_actual_content_of_serial_number(41, query),
        "/serialnumbers/41/actualcontent",
    ),
    (lambda client, query: client.async_iter_equipment(query), "/equipment"),
    (
        lambda client, query: client.async_iter_serial_numbers_of_equipment(12, query),
        "/equipment/12/serialnumbers",
    ),
    (
        lambda client, query: client.async_iter_stock_movements_of_equipment(12, query),
        "/equipment/12/stockmovements",
    ),
    (
        lambda client, query: client.async_iter_repairs_of_equipment(12, query),
        "/equipment/12/repairs",
    ),
    (
        lambda client, query: client.async_iter_equipment_set_content_of_equipment(34, query),
        "/equipment/34/equipmentsetscontent",
    ),
    (lambda client, query: client.async_iter_serial_numbers(query), "/serialnumbers"),
    (
        lambda client, query: client.async_iter_equipment_assigned_serials(query),
        "/equipmentassignedserials",
    ),
    (
        lambda client, query: client.async_iter_equipment_assigned_serials_of_serial_number(
            43, query
        ),
        "/serialnumbers/43/equipmentassignedserials",
    ),
    (lambda client, query: client.async_iter_equipment_set_content(query), "/equipmentsetscontent"),
    (lambda client, query: client.async_iter_folders(query), "/folders"),
    (lambda client, query: client.async_iter_stock_locations(query), "/stocklocations"),
    (lambda client, query: client.async_iter_warehouse_statuses(query), "/warehousestatuses"),
    (lambda client, query: client.async_iter_statuses(query), "/statuses"),
    (lambda client, query: client.async_iter_stock_movements(query), "/stockmovements"),
    (lambda client, query: client.async_iter_repairs(query), "/repairs"),
    (lambda client, query: client.async_iter_projects(query), "/projects"),
    (
        lambda client, query: client.async_iter_subprojects_of_project(480, query),
        "/projects/480/subprojects",
    ),
    (lambda client, query: client.async_iter_subprojects(query), "/subprojects"),
    (lambda client, query: client.async_iter_project_equipment(query), "/projectequipment"),
    (
        lambda client, query: client.async_iter_project_equipment_of_project(480, query),
        "/projects/480/projectequipment",
    ),
    (
        lambda client, query: client.async_iter_project_equipment_of_subproject(501, query),
        "/subprojects/501/projectequipment",
    ),
)


def recorded_call(
    log: dict[tuple[str, URL], list[RequestCall]],
    method: str,
    url_prefix: str,
) -> RequestCall:
    """Return the first recorded call whose URL starts with one prefix."""
    for key, calls in log.items():
        recorded_method, recorded_url = key
        if recorded_method == method and str(recorded_url).startswith(url_prefix):
            return calls[0]
    msg = f"no recorded request for {method} {url_prefix}"
    raise AssertionError(msg)


async def test_collection_methods_hit_their_paths() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            for _, path in COLLECTIONS:
                m.get(api_url(path), payload=EMPTY_PAGE)
            client = make_client(session)
            for call, path in COLLECTIONS:
                page = await call(client)
                assert isinstance(page, RentmanPage), path
                assert page.items == (), path


async def test_item_methods_hit_their_paths() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            for _, path in ITEMS:
                m.get(api_url(path), payload=EMPTY_ITEM)
            client = make_client(session)
            for call, path in ITEMS:
                assert await call(client) is not None, path


async def test_iter_methods_consume_one_page() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            for _, path in ITERATORS:
                m.get(api_url(path), payload=EMPTY_PAGE)
            client = make_client(session)
            for call, path in ITERATORS:
                consumed = [item async for item in call(client, None)]
                assert consumed == [], path


async def test_list_equipment_pins_the_wire_request() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), payload=EMPTY_PAGE)
            client = make_client(session)
            await client.async_list_equipment(
                Query(
                    fields=("name", "code"),
                    sort=(Sort("name"), Sort("code", ascending=False)),
                    expand=("folder",),
                    filters=(
                        eq("code", "AUD-001"),
                        lt("price", 200),
                        is_null("image", value=False),
                    ),
                    limit=10,
                    offset=20,
                )
            )
            call = recorded_call(m.requests, "GET", f"{BASE_URL}/equipment")
    assert dict(call.kwargs["params"]) == {
        "fields": "name,code",
        "sort": "+name,-code",
        "expand": "folder",
        "code": "AUD-001",
        "price[lt]": "200",
        "image[isnull]": "false",
        "limit": "10",
        "offset": "20",
    }
    assert call.kwargs["headers"]["Authorization"] == f"Bearer {TOKEN}"
    assert call.kwargs["headers"]["Accept"] == "application/json"
    assert call.kwargs["headers"]["User-Agent"].startswith("aiorentman/")


async def test_item_requests_carry_the_token() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment/12"), payload=EMPTY_ITEM)
            client = make_client(session)
            equipment = await client.async_get_equipment(12)
            call = recorded_call(m.requests, "GET", f"{BASE_URL}/equipment/12")
    assert isinstance(equipment, Equipment)
    assert call.kwargs["headers"]["Authorization"] == f"Bearer {TOKEN}"


async def test_iter_serial_numbers_follows_the_cursor() -> None:
    first_page = {
        "data": [{"id": 41, "equipment": "/equipment/12", "serial": "QL5-000041"}],
        "itemCount": 1,
        "limit": 300,
        "offset": 0,
        "next_page_url": f"{BASE_URL}/serialnumbers?cursor=abc123",
    }
    second_page = {
        "data": [{"id": 42, "equipment": "/equipment/12", "serial": "QL5-000042"}],
        "itemCount": 1,
        "limit": 300,
        "offset": 0,
        "next_page_url": None,
    }
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/serialnumbers"), payload=first_page)
            m.get(cursor_api_url("/serialnumbers"), payload=second_page)
            client = make_client(session)
            serials = [item async for item in client.async_iter_serial_numbers()]
            calls = m.requests
    assert [serial.id for serial in serials] == [41, 42]
    assert all(isinstance(serial, SerialNumber) for serial in serials)
    assert recorded_call(calls, "GET", f"{BASE_URL}/serialnumbers?cursor=")


async def test_iter_rejects_cursor_urls_that_leave_the_api() -> None:
    hostile_page = {
        "data": [{"id": 41, "equipment": "/equipment/12", "serial": "QL5-000041"}],
        "itemCount": 1,
        "limit": 300,
        "offset": 0,
        "next_page_url": "https://evil.example.com/serialnumbers?cursor=abc",
    }
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/serialnumbers"), payload=hostile_page)
            client = make_client(session)
            with pytest.raises(RentmanInvalidResponseError, match="leaves"):
                async for _serial in client.async_iter_serial_numbers():
                    pass


async def test_closed_client_rejects_calls() -> None:
    client = make_client()
    await client.async_close()
    with pytest.raises(RentmanClientClosedError, match="client is closed"):
        await client.async_list_equipment()


async def test_authentication_error_propagates() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=401)
            client = make_client(session)
            with pytest.raises(RentmanAuthenticationError):
                await client.async_list_equipment()


async def test_rate_limit_error_propagates() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), status=429)
            client = make_client(session)
            with pytest.raises(RentmanRateLimitError):
                await client.async_list_equipment()


async def test_not_found_error_propagates() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment/99999"), status=404)
            client = make_client(session)
            with pytest.raises(RentmanNotFoundError):
                await client.async_get_equipment(99999)


async def test_client_creates_and_closes_its_own_session(
    created_sessions: list[aiohttp.ClientSession],
) -> None:
    client = RentmanClient(token=TOKEN, requests_per_second=None)
    assert len(created_sessions) == 1
    await client.async_close()
    assert created_sessions[0].closed


async def test_client_leaves_injected_sessions_open() -> None:
    async with aiohttp.ClientSession() as session:
        client = make_client(session)
        await client.async_close()
        assert not session.closed


async def test_token_comes_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RENTMAN_TOKEN", "env-token")
    client = RentmanClient(requests_per_second=None)
    await client.async_close()


def test_missing_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RENTMAN_TOKEN", raising=False)
    with pytest.raises(RentmanAuthenticationError, match="token is required"):
        RentmanClient()


async def test_explicit_token_wins_over_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RENTMAN_TOKEN", "env-token")
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), payload=EMPTY_PAGE)
            client = RentmanClient(session, token=TOKEN, requests_per_second=None)
            await client.async_list_equipment()
            call = recorded_call(m.requests, "GET", f"{BASE_URL}/equipment")
    assert call.kwargs["headers"]["Authorization"] == f"Bearer {TOKEN}"


async def test_client_paces_by_default() -> None:
    client = RentmanClient(token=TOKEN)
    assert client._pacer._interval == 1 / DEFAULT_REQUESTS_PER_SECOND
    await client.async_close()


async def test_repairs_parse_through_the_client(load_fixture: Any) -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/repairs"), payload=load_fixture("repair_page.json"))
            client = make_client(session)
            page = await client.async_list_repairs()
    assert isinstance(page.items[0], Repair)
    assert page.items[0].number == "REP-2026-014"


async def test_actual_content_of_serial_number_parses(load_fixture: Any) -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(
                api_url("/serialnumbers/43/actualcontent"),
                payload=load_fixture("actualcontent_page.json"),
            )
            client = make_client(session)
            page = await client.async_list_actual_content_of_serial_number(43)
    assert all(isinstance(item, ActualContent) for item in page.items)
    assert page.item_count == 2


async def test_context_manager_closes_the_client() -> None:
    async with make_client() as client:
        assert not client._closed
    assert client._closed


async def test_pacing_still_serves_requests() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(api_url("/equipment"), payload=EMPTY_PAGE)
            client = RentmanClient(session, token=TOKEN, requests_per_second=100.0)
            page = await client.async_list_equipment()
    assert page.items == ()
