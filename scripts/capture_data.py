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
    ("quotes", "/quotes"),
    ("contracts", "/contracts"),
    ("invoices", "/invoices"),
    ("invoice_lines", "/invoicelines"),
    ("payments", "/payments"),
    ("ledger_codes", "/ledgercodes"),
    ("tax_classes", "/taxclasses"),
    ("subrentals", "/subrentals"),
    ("subrental_equipment", "/subrentalequipment"),
    ("subrental_equipment_groups", "/subrentalequipmentgroup"),
    ("purchase_orders", "/purchaseorders"),
    ("purchase_order_costs", "/purchaseordercosts"),
    ("purchase_order_global_costs", "/purchaseorderglobalcosts"),
    ("crew", "/crew"),
    ("crew_availability", "/crewavailability"),
    ("crew_rates", "/crewrates"),
    ("invitations", "/invitations"),
    ("appointments", "/appointments"),
    ("appointment_crew", "/appointmentcrew"),
    ("time_registrations", "/timeregistration"),
    ("time_registration_activities", "/timeregistrationactivities"),
    ("leave_requests", "/leaverequest"),
    ("leave_mutations", "/leavemutation"),
    ("leave_types", "/leavetypes"),
    ("contacts", "/contacts"),
    ("contact_persons", "/contactpersons"),
    ("tasks", "/tasks"),
    ("subtasks", "/subtasks"),
    ("task_assignments", "/taskassignments"),
    ("task_statuses", "/taskstatuses"),
    ("files", "/files"),
    ("file_folders", "/file_folders"),
    ("rates", "/rates"),
    ("rate_factors", "/ratefactors"),
    ("factors", "/factors"),
    ("factor_groups", "/factorgroups"),
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
    ("invoice_lines_of_quote", "/quotes/{}/invoicelines", "quotes.json", "id"),
    ("invoice_lines_of_contract", "/contracts/{}/invoicelines", "contracts.json", "id"),
    ("invoice_lines_of_invoice", "/invoices/{}/invoicelines", "invoices.json", "id"),
    ("payments_of_invoice", "/invoices/{}/payments", "invoices.json", "id"),
    ("quotes_of_project", "/projects/{}/quotes", "quotes.json", "project"),
    ("contracts_of_project", "/projects/{}/contracts", "projects.json", "id"),
    (
        "subrental_equipment_of_subrental",
        "/subrentals/{}/subrentalequipment",
        "subrentals.json",
        "id",
    ),
    (
        "subrental_equipment_groups_of_subrental",
        "/subrentals/{}/subrentalequipmentgroup",
        "subrental_equipment_groups.json",
        "subrental",
    ),
    (
        "subrental_equipment_of_subrental_equipment_group",
        "/subrentalequipmentgroup/{}/subrentalequipment",
        "subrental_equipment.json",
        "subrental_group",
    ),
    (
        "invoice_lines_of_purchase_order",
        "/purchaseorders/{}/invoicelines",
        "purchase_orders.json",
        "id",
    ),
    (
        "purchase_order_costs_of_purchase_order",
        "/purchaseorders/{}/purchaseordercosts",
        "purchase_order_costs.json",
        "purchase_order",
    ),
    (
        "purchase_order_global_costs_of_purchase_order",
        "/purchaseorders/{}/purchaseorderglobalcosts",
        "purchase_orders.json",
        "id",
    ),
    ("appointments_of_crew", "/crew/{}/appointments", "crew.json", "id"),
    (
        "crew_availability_of_crew",
        "/crew/{}/crewavailability",
        "crew_availability.json",
        "crewmember",
    ),
    ("crew_rates_of_crew", "/crew/{}/crewrates", "crew_rates.json", "medewerker"),
    ("invitations_of_crew", "/crew/{}/invitations", "invitations.json", "crewmember"),
    (
        "appointment_crew_of_appointment",
        "/appointments/{}/appointmentcrew",
        "appointment_crew.json",
        "appointment",
    ),
    (
        "time_registration_activities_of_time_registration",
        "/timeregistration/{}/timeregistrationactivities",
        "time_registration_activities.json",
        "time_registration",
    ),
    (
        "time_registrations_of_leave_request",
        "/leaverequest/{}/timeregistration",
        "time_registrations.json",
        "leaverequest",
    ),
    (
        "contact_persons_of_contact",
        "/contacts/{}/contactpersons",
        "contact_persons.json",
        "contact",
    ),
    ("subtasks_of_task", "/tasks/{}/subtasks", "tasks.json", "id"),
    ("task_assignments_of_task", "/tasks/{}/taskassignments", "tasks.json", "id"),
    ("tasks_of_contact_person", "/contactpersons/{}/tasks", "contact_persons.json", "id"),
    ("tasks_of_contact", "/contacts/{}/tasks", "contacts.json", "id"),
    ("tasks_of_crew", "/crew/{}/tasks", "crew.json", "id"),
    ("tasks_of_equipment", "/equipment/{}/tasks", "equipment.json", "id"),
    ("tasks_of_invoice", "/invoices/{}/tasks", "invoices.json", "id"),
    ("tasks_of_project", "/projects/{}/tasks", "projects.json", "id"),
    ("tasks_of_purchase_order", "/purchaseorders/{}/tasks", "purchase_orders.json", "id"),
    ("tasks_of_quote", "/quotes/{}/tasks", "quotes.json", "id"),
    ("tasks_of_repair", "/repairs/{}/tasks", "repairs.json", "id"),
    ("tasks_of_serial_number", "/serialnumbers/{}/tasks", "serial_numbers.json", "id"),
    ("tasks_of_subrental", "/subrentals/{}/tasks", "subrentals.json", "id"),
    ("tasks_of_vehicle", "/vehicles/{}/tasks", "vehicles.json", "id"),
    ("tasks_of_supplier", "/suppliers/{}/tasks", "suppliers.json", "id"),
    ("files_of_contact_person", "/contactpersons/{}/files", "contact_persons.json", "id"),
    ("files_of_contact", "/contacts/{}/files", "contacts.json", "id"),
    ("files_of_crew", "/crew/{}/files", "crew.json", "id"),
    ("files_of_equipment", "/equipment/{}/files", "equipment.json", "id"),
    ("files_of_invoice", "/invoices/{}/files", "invoices.json", "id"),
    ("files_of_project", "/projects/{}/files", "projects.json", "id"),
    ("files_of_purchase_order", "/purchaseorders/{}/files", "purchase_orders.json", "id"),
    ("files_of_quote", "/quotes/{}/files", "quotes.json", "id"),
    ("files_of_repair", "/repairs/{}/files", "repairs.json", "id"),
    ("files_of_serial_number", "/serialnumbers/{}/files", "serial_numbers.json", "id"),
    ("files_of_subrental", "/subrentals/{}/files", "subrentals.json", "id"),
    ("files_of_task", "/tasks/{}/files", "tasks.json", "id"),
    ("files_of_time_registration", "/timeregistration/{}/files", "time_registrations.json", "id"),
    ("files_of_vehicle", "/vehicles/{}/files", "vehicles.json", "id"),
    ("files_of_supplier", "/suppliers/{}/files", "suppliers.json", "id"),
    (
        "file_folders_of_contact_person",
        "/contactpersons/{}/file_folders",
        "contact_persons.json",
        "id",
    ),
    ("file_folders_of_contact", "/contacts/{}/file_folders", "contacts.json", "id"),
    ("file_folders_of_crew", "/crew/{}/file_folders", "crew.json", "id"),
    ("file_folders_of_equipment", "/equipment/{}/file_folders", "equipment.json", "id"),
    ("file_folders_of_project", "/projects/{}/file_folders", "projects.json", "id"),
    (
        "file_folders_of_purchase_order",
        "/purchaseorders/{}/file_folders",
        "purchase_orders.json",
        "id",
    ),
    ("file_folders_of_repair", "/repairs/{}/file_folders", "repairs.json", "id"),
    (
        "file_folders_of_serial_number",
        "/serialnumbers/{}/file_folders",
        "serial_numbers.json",
        "id",
    ),
    ("file_folders_of_subproject", "/subprojects/{}/file_folders", "subprojects.json", "id"),
    ("file_folders_of_subrental", "/subrentals/{}/file_folders", "subrentals.json", "id"),
    ("file_folders_of_supplier", "/suppliers/{}/file_folders", "suppliers.json", "id"),
    ("file_folders_of_task", "/tasks/{}/file_folders", "tasks.json", "id"),
    ("file_folders_of_vehicle", "/vehicles/{}/file_folders", "vehicles.json", "id"),
    ("rate_factors_of_rate", "/rates/{}/ratefactors", "rate_factors.json", "rate_id"),
    ("factors_of_factor_group", "/factorgroups/{}/factors", "factors.json", "factor_group"),
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
