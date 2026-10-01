"""Parser tests against real captured payloads, redacted.

Every file in tests/fixtures/redacted/ comes from a live capture of the
account this library is built for, scrubbed by scripts/_redact.py. Running
each one through its parser keeps the library honest against the real wire.
"""

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from aiorentman.parsers import (
    parse_accessory,
    parse_actual_content,
    parse_alternative,
    parse_equipment,
    parse_equipment_assigned_serial,
    parse_equipment_set_content,
    parse_extra_input_field,
    parse_folder,
    parse_page,
    parse_project,
    parse_project_equipment,
    parse_repair,
    parse_serial_number,
    parse_status,
    parse_stock_location,
    parse_stock_movement,
    parse_subproject,
    parse_supplier,
    parse_vehicle,
    parse_warehouse_status,
)

REDACTED = Path(__file__).parent / "fixtures" / "redacted"

PARSERS: dict[str, Callable[[Mapping[str, Any]], Any]] = {
    "accessories.json": parse_accessory,
    "actual_content.json": parse_actual_content,
    "alternatives.json": parse_alternative,
    "equipment.json": parse_equipment,
    "equipment_accessories.json": parse_accessory,
    "equipment_alternatives.json": parse_alternative,
    "equipment_assigned_serials.json": parse_equipment_assigned_serial,
    "equipment_set_content.json": parse_equipment_set_content,
    "equipment_suppliers.json": parse_supplier,
    "extra_input_fields.json": parse_extra_input_field,
    "folders.json": parse_folder,
    "project_equipment.json": parse_project_equipment,
    "projects.json": parse_project,
    "repairs.json": parse_repair,
    "serial_numbers.json": parse_serial_number,
    "statuses.json": parse_status,
    "stock_location_vehicles.json": parse_vehicle,
    "stock_locations.json": parse_stock_location,
    "stock_movements.json": parse_stock_movement,
    "subprojects.json": parse_subproject,
    "suppliers.json": parse_supplier,
    "vehicles.json": parse_vehicle,
    "warehouse_statuses.json": parse_warehouse_status,
}

EMPTY_CAPTURES = {"stock_location_vehicles.json"}


def test_every_redacted_capture_parses() -> None:
    for name, parse_item in PARSERS.items():
        payload = json.loads((REDACTED / name).read_text())
        page = parse_page(payload, parse_item)
        assert page.items or name in EMPTY_CAPTURES, name
        assert page.item_count >= len(page.items), name
        for item in page.items:
            assert isinstance(item.id, int), name
            assert isinstance(item.update_hash, str), name
            assert item.update_hash, name


def test_empty_real_collection_parses_to_no_items() -> None:
    payload = json.loads((REDACTED / "stock_location_vehicles.json").read_text())
    page = parse_page(payload, parse_vehicle)
    assert page.items == ()
    assert page.item_count == 0
    assert page.next_page_url is None


def test_redacted_covers_every_in_scope_collection() -> None:
    captured = {path.name for path in REDACTED.glob("*.json")}
    assert captured == set(PARSERS)


def test_real_wire_qrcodes_stay_comma_separated() -> None:
    payload = json.loads((REDACTED / "serial_numbers.json").read_text())
    page = parse_page(payload, parse_serial_number)
    multi = [serial for serial in page.items if len(serial.qrcodes) > 1]
    assert multi, "no serial with multiple codes captured"
    for serial in multi:
        assert all(code.startswith("SYN-") for code in serial.qrcodes)


def test_real_wire_quantities_coerce_to_text() -> None:
    payload = json.loads((REDACTED / "project_equipment.json").read_text())
    page = parse_page(payload, parse_project_equipment)
    assert all(isinstance(line.quantity, str) for line in page.items)
    assert all(line.quantity.isdigit() for line in page.items)


def test_real_wire_accessory_orders_coerce_to_text() -> None:
    payload = json.loads((REDACTED / "accessories.json").read_text())
    page = parse_page(payload, parse_accessory)
    assert all(isinstance(accessory.order, str) for accessory in page.items)
