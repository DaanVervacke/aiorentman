"""Capture live payloads from the Rentman API into the captures directory.

Reads the API token from the RENTMAN_TOKEN variable in the environment or a
.env file next to the repository root, then dumps one page of every in-scope
collection into captures/. Linked collections probe the parent ids found in
earlier captures until one parent returns items. Raw captures stay untracked.
Run scripts/_redact.py before committing any of them as fixtures.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import aiohttp

BASE_URL = "https://api.rentman.net"
CAPTURES = Path(__file__).resolve().parent.parent / "captures"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
PAGE_LIMIT = 50
PROBE_LIMIT = 8

COLLECTIONS: tuple[tuple[str, str], ...] = (
    ("actual_content", "/actualcontent"),
    ("equipment", "/equipment"),
    ("equipment_assigned_serials", "/equipmentassignedserials"),
    ("equipment_set_content", "/equipmentsetscontent"),
    ("folders", "/folders"),
    ("project_equipment", "/projectequipment"),
    ("projects", "/projects"),
    ("repairs", "/repairs"),
    ("serial_numbers", "/serialnumbers"),
    ("statuses", "/statuses"),
    ("stock_locations", "/stocklocations"),
    ("stock_movements", "/stockmovements"),
    ("subprojects", "/subprojects"),
    ("warehouse_statuses", "/warehousestatuses"),
    ("accessories", "/accessories"),
    ("alternatives", "/alternatives"),
    ("suppliers", "/suppliers"),
    ("vehicles", "/vehicles"),
    ("extra_input_fields", "/extrainputfields"),
    ("project_statuses", "/projectstatuses"),
    ("project_types", "/projecttypes"),
    ("project_crew", "/projectcrew"),
    ("project_function_groups", "/projectfunctiongroups"),
    ("project_functions", "/projectfunctions"),
    ("project_vehicles", "/projectvehicles"),
    ("project_equipment_groups", "/projectequipmentgroup"),
    ("project_costs", "/costs"),
    ("project_requests", "/projectrequests"),
    ("project_request_equipment", "/projectrequestequipment"),
)

LINKED_COLLECTIONS: tuple[tuple[str, str, str, str], ...] = (
    ("equipment_accessories", "/equipment/{}/accessories", "accessories.json", "parent_equipment"),
    ("equipment_alternatives", "/equipment/{}/alternatives", "alternatives.json", "equipment"),
    ("equipment_suppliers", "/equipment/{}/suppliers", "suppliers.json", "equipment"),
    ("stock_location_vehicles", "/stocklocations/{}/vehicles", "stock_locations.json", "id"),
    ("project_costs_of_project", "/projects/{}/costs", "project_costs.json", "project"),
    ("project_crew_of_project", "/projects/{}/projectcrew", "projects.json", "id"),
    ("project_crew_of_subproject", "/subprojects/{}/projectcrew", "subprojects.json", "id"),
    (
        "project_equipment_group_of_project",
        "/projects/{}/projectequipmentgroup",
        "project_equipment_groups.json",
        "project",
    ),
    (
        "project_equipment_group_of_subproject",
        "/subprojects/{}/projectequipmentgroup",
        "project_equipment_groups.json",
        "subproject",
    ),
    (
        "project_function_group_of_project",
        "/projects/{}/projectfunctiongroups",
        "project_function_groups.json",
        "project",
    ),
    (
        "project_function_group_of_subproject",
        "/subprojects/{}/projectfunctiongroups",
        "project_function_groups.json",
        "subproject",
    ),
    (
        "project_functions_of_project",
        "/projects/{}/projectfunctions",
        "project_functions.json",
        "project",
    ),
    (
        "project_functions_of_project_function_group",
        "/projectfunctiongroups/{}/projectfunctions",
        "project_functions.json",
        "group",
    ),
    (
        "project_crew_of_project_function",
        "/projectfunctions/{}/projectcrew",
        "project_crew.json",
        "function",
    ),
    ("project_vehicles_of_project", "/projects/{}/projectvehicles", "projects.json", "id"),
    ("project_vehicles_of_subproject", "/subprojects/{}/projectvehicles", "subprojects.json", "id"),
    (
        "project_vehicles_of_project_function",
        "/projectfunctions/{}/projectvehicles",
        "project_vehicles.json",
        "function",
    ),
    (
        "project_equipment_of_project_equipment_group",
        "/projectequipmentgroup/{}/projectequipment",
        "project_equipment.json",
        "equipment_group",
    ),
    (
        "project_request_equipment_of_project_request",
        "/projectrequests/{}/projectrequestequipment",
        "project_request_equipment.json",
        "project_request",
    ),
)


def load_token() -> str:
    """Resolve the token from the environment or the .env file."""
    for source in (Path(".env"), ENV_FILE):
        if source.is_file():
            for line in source.read_text().splitlines():
                if line.startswith("RENTMAN_TOKEN="):
                    return line.removeprefix("RENTMAN_TOKEN=").strip().strip('"')
    if "RENTMAN_TOKEN" in os.environ:
        return os.environ["RENTMAN_TOKEN"]
    print("Set RENTMAN_TOKEN in the environment or in .env first", file=sys.stderr)
    raise SystemExit(1)


def parent_ids(capture_name: str, field: str) -> list[int]:
    """Read parent ids from one earlier capture, as item ids or as link paths."""
    path = CAPTURES / capture_name
    if not path.is_file():
        return []
    payload = json.loads(path.read_text())
    data = payload.get("data", [])
    if field == "id":
        return list(
            dict.fromkeys(
                item["id"]
                for item in data
                if isinstance(item, dict) and isinstance(item.get("id"), int)
            )
        )
    ids: list[int] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        value = item.get(field)
        if isinstance(value, str):
            tail = value.rsplit("/", 1)[-1]
            if tail.isdigit():
                ids.append(int(tail))
    return list(dict.fromkeys(ids))


async def fetch_page(session: aiohttp.ClientSession, path: str) -> dict[str, Any]:
    """Fetch one page of one collection path."""
    params = urlencode({"limit": PAGE_LIMIT})
    async with session.get(f"{BASE_URL}{path}?{params}") as response:
        response.raise_for_status()
        payload: dict[str, Any] = await response.json()
    return payload


def write_capture(name: str, payload: dict[str, Any]) -> None:
    """Write one captured payload to captures/."""
    CAPTURES.mkdir(exist_ok=True)
    target = CAPTURES / f"{name}.json"
    target.write_text(json.dumps(payload, indent=2))


async def capture(session: aiohttp.ClientSession, name: str, path: str) -> None:
    """Fetch one page of one collection and write it to captures/."""
    payload = await fetch_page(session, path)
    write_capture(name, payload)
    print(f"wrote {name}.json with {len(payload.get('data', []))} items")


async def capture_linked(
    session: aiohttp.ClientSession,
    name: str,
    path_template: str,
    parent_capture: str,
    parent_field: str,
) -> None:
    """Fetch one page per parent id until one parent returns items."""
    ids = parent_ids(parent_capture, parent_field)
    if not ids:
        print(f"skipped {name}: no parent ids in {parent_capture}")
        return
    last: dict[str, Any] | None = None
    for parent_id in ids[:PROBE_LIMIT]:
        try:
            payload = await fetch_page(session, path_template.format(parent_id))
        except aiohttp.ClientResponseError as exc:
            print(f"skipped {name} for parent {parent_id}: {exc}")
            continue
        last = payload
        if payload.get("data"):
            break
    if last is None:
        return
    write_capture(name, last)
    print(f"wrote {name}.json with {len(last.get('data', []))} items")


async def main() -> None:
    """Capture one page of every in-scope collection."""
    token = load_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        for name, path in COLLECTIONS:
            try:
                await capture(session, name, path)
            except aiohttp.ClientResponseError as exc:
                print(f"skipped {name}: {exc}")
        for name, path_template, parent_capture, parent_field in LINKED_COLLECTIONS:
            await capture_linked(session, name, path_template, parent_capture, parent_field)


if __name__ == "__main__":
    asyncio.run(main())
