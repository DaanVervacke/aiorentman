"""Capture live payloads from the Rentman API into the captures directory.

Reads the API token from the RENTMAN_TOKEN variable in the environment or a
.env file next to the repository root, then dumps one page of every in-scope
collection plus a few single items into captures/. Raw captures stay
untracked. Run scripts/_redact.py before committing any of them as fixtures.
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


async def capture(session: aiohttp.ClientSession, name: str, path: str) -> None:
    """Fetch one page of one collection and write it to captures/."""
    params = urlencode({"limit": PAGE_LIMIT})
    async with session.get(f"{BASE_URL}{path}?{params}") as response:
        response.raise_for_status()
        payload: dict[str, Any] = await response.json()
    CAPTURES.mkdir(exist_ok=True)
    target = CAPTURES / f"{name}.json"
    target.write_text(json.dumps(payload, indent=2))
    count = len(payload.get("data", []))
    print(f"wrote {target.name} with {count} items")


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


if __name__ == "__main__":
    asyncio.run(main())
