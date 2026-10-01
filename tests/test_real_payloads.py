"""Parser tests against real captured payloads, redacted.

Every file in tests/fixtures/redacted/ comes from a live capture of the
account this library is built for, scrubbed by scripts/_redact.py. Running
each one through its parser keeps the library honest against the real wire.
"""

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from aiorentman.models import RentmanLink
from aiorentman.parsers import (
    parse_accessory,
    parse_actual_content,
    parse_alternative,
    parse_contract,
    parse_equipment,
    parse_equipment_assigned_serial,
    parse_equipment_set_content,
    parse_extra_input_field,
    parse_folder,
    parse_invoice,
    parse_invoice_line,
    parse_ledger_code,
    parse_page,
    parse_payment,
    parse_project,
    parse_project_cost,
    parse_project_crew,
    parse_project_equipment,
    parse_project_equipment_group,
    parse_project_function,
    parse_project_function_group,
    parse_project_request,
    parse_project_request_equipment,
    parse_project_status,
    parse_project_type,
    parse_project_vehicle,
    parse_purchase_order,
    parse_purchase_order_cost,
    parse_purchase_order_global_cost,
    parse_quote,
    parse_repair,
    parse_serial_number,
    parse_status,
    parse_stock_location,
    parse_stock_movement,
    parse_subproject,
    parse_subrental,
    parse_subrental_equipment,
    parse_subrental_equipment_group,
    parse_supplier,
    parse_tax_class,
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
    "project_costs.json": parse_project_cost,
    "project_costs_of_project.json": parse_project_cost,
    "project_crew.json": parse_project_crew,
    "project_crew_of_project.json": parse_project_crew,
    "project_crew_of_project_function.json": parse_project_crew,
    "project_crew_of_subproject.json": parse_project_crew,
    "project_equipment_group_of_project.json": parse_project_equipment_group,
    "project_equipment_group_of_subproject.json": parse_project_equipment_group,
    "project_equipment_groups.json": parse_project_equipment_group,
    "project_equipment_of_project_equipment_group.json": parse_project_equipment,
    "project_function_group_of_project.json": parse_project_function_group,
    "project_function_group_of_subproject.json": parse_project_function_group,
    "project_function_groups.json": parse_project_function_group,
    "project_functions.json": parse_project_function,
    "project_functions_of_project.json": parse_project_function,
    "project_functions_of_project_function_group.json": parse_project_function,
    "project_request_equipment.json": parse_project_request_equipment,
    "project_request_equipment_of_project_request.json": parse_project_request_equipment,
    "project_requests.json": parse_project_request,
    "project_statuses.json": parse_project_status,
    "project_types.json": parse_project_type,
    "project_vehicles.json": parse_project_vehicle,
    "project_vehicles_of_project.json": parse_project_vehicle,
    "project_vehicles_of_project_function.json": parse_project_vehicle,
    "project_vehicles_of_subproject.json": parse_project_vehicle,
    "quotes.json": parse_quote,
    "quotes_of_project.json": parse_quote,
    "invoice_lines_of_quote.json": parse_invoice_line,
    "contracts.json": parse_contract,
    "contracts_of_project.json": parse_contract,
    "invoices.json": parse_invoice,
    "invoice_lines_of_invoice.json": parse_invoice_line,
    "payments_of_invoice.json": parse_payment,
    "invoice_lines.json": parse_invoice_line,
    "payments.json": parse_payment,
    "ledger_codes.json": parse_ledger_code,
    "tax_classes.json": parse_tax_class,
    "subrentals.json": parse_subrental,
    "subrental_equipment.json": parse_subrental_equipment,
    "subrental_equipment_groups.json": parse_subrental_equipment_group,
    "subrental_equipment_of_subrental.json": parse_subrental_equipment,
    "subrental_equipment_groups_of_subrental.json": parse_subrental_equipment_group,
    "subrental_equipment_of_subrental_equipment_group.json": parse_subrental_equipment,
    "purchase_orders.json": parse_purchase_order,
    "invoice_lines_of_purchase_order.json": parse_invoice_line,
    "purchase_order_costs.json": parse_purchase_order_cost,
    "purchase_order_costs_of_purchase_order.json": parse_purchase_order_cost,
    "purchase_order_global_costs.json": parse_purchase_order_global_cost,
    "purchase_order_global_costs_of_purchase_order.json": parse_purchase_order_global_cost,
}

EMPTY_CAPTURES = {
    "stock_location_vehicles.json",
    "payments.json",
    "contracts.json",
    "invoice_lines_of_quote.json",
    "payments_of_invoice.json",
    "contracts_of_project.json",
    "invoice_lines_of_purchase_order.json",
    "purchase_order_global_costs.json",
    "purchase_order_global_costs_of_purchase_order.json",
}


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


def test_real_wire_planning_scalars_coerce_to_text() -> None:
    payload = json.loads((REDACTED / "project_functions.json").read_text())
    functions = parse_page(payload, parse_project_function)
    assert all(isinstance(function.order, str) for function in functions.items)
    payload = json.loads((REDACTED / "project_costs.json").read_text())
    costs = parse_page(payload, parse_project_cost)
    assert all(isinstance(cost.order, str) for cost in costs.items)
    payload = json.loads((REDACTED / "project_request_equipment.json").read_text())
    lines = parse_page(payload, parse_project_request_equipment)
    assert all(isinstance(line.factor, str) for line in lines.items)
    assert all(isinstance(line.order, str) for line in lines.items)


def test_real_wire_rate_links_parse_as_links() -> None:
    payload = json.loads((REDACTED / "project_functions.json").read_text())
    functions = parse_page(payload, parse_project_function)
    assert all(isinstance(function.cost_rate, RentmanLink) for function in functions.items)
    payload = json.loads((REDACTED / "project_crew.json").read_text())
    crew = parse_page(payload, parse_project_crew)
    assert all(isinstance(member.cost_rate, RentmanLink) for member in crew.items)
