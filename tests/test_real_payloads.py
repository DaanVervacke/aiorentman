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
    parse_appointment,
    parse_appointment_crew,
    parse_contact,
    parse_contact_person,
    parse_contract,
    parse_crew,
    parse_crew_availability,
    parse_crew_rate,
    parse_equipment,
    parse_equipment_assigned_serial,
    parse_equipment_set_content,
    parse_extra_input_field,
    parse_factor,
    parse_factor_group,
    parse_file,
    parse_file_folder,
    parse_folder,
    parse_invitation,
    parse_invoice,
    parse_invoice_line,
    parse_leave_mutation,
    parse_leave_request,
    parse_leave_type,
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
    parse_rate,
    parse_rate_factor,
    parse_repair,
    parse_serial_number,
    parse_status,
    parse_stock_location,
    parse_stock_movement,
    parse_subproject,
    parse_subrental,
    parse_subrental_equipment,
    parse_subrental_equipment_group,
    parse_subtask,
    parse_supplier,
    parse_task,
    parse_task_assignment,
    parse_task_status,
    parse_tax_class,
    parse_time_registration,
    parse_time_registration_activity,
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
    "crew.json": parse_crew,
    "appointments_of_crew.json": parse_appointment,
    "crew_availability.json": parse_crew_availability,
    "crew_availability_of_crew.json": parse_crew_availability,
    "crew_rates.json": parse_crew_rate,
    "crew_rates_of_crew.json": parse_crew_rate,
    "invitations.json": parse_invitation,
    "invitations_of_crew.json": parse_invitation,
    "appointments.json": parse_appointment,
    "appointment_crew.json": parse_appointment_crew,
    "appointment_crew_of_appointment.json": parse_appointment_crew,
    "time_registrations.json": parse_time_registration,
    "time_registrations_of_leave_request.json": parse_time_registration,
    "time_registration_activities.json": parse_time_registration_activity,
    "time_registration_activities_of_time_registration.json": parse_time_registration_activity,
    "leave_requests.json": parse_leave_request,
    "leave_mutations.json": parse_leave_mutation,
    "leave_types.json": parse_leave_type,
    "contacts.json": parse_contact,
    "contact_persons.json": parse_contact_person,
    "contact_persons_of_contact.json": parse_contact_person,
    "rates.json": parse_rate,
    "rate_factors.json": parse_rate_factor,
    "rate_factors_of_rate.json": parse_rate_factor,
    "factors.json": parse_factor,
    "factors_of_factor_group.json": parse_factor,
    "factor_groups.json": parse_factor_group,
    "tasks.json": parse_task,
    "subtasks.json": parse_subtask,
    "task_assignments.json": parse_task_assignment,
    "task_statuses.json": parse_task_status,
    "files.json": parse_file,
    "file_folders.json": parse_file_folder,
    "subtasks_of_task.json": parse_subtask,
    "task_assignments_of_task.json": parse_task_assignment,
    "files_of_task.json": parse_file,
    "file_folders_of_task.json": parse_file_folder,
    "tasks_of_contact_person.json": parse_task,
    "tasks_of_contact.json": parse_task,
    "tasks_of_crew.json": parse_task,
    "tasks_of_equipment.json": parse_task,
    "tasks_of_invoice.json": parse_task,
    "tasks_of_project.json": parse_task,
    "tasks_of_purchase_order.json": parse_task,
    "tasks_of_quote.json": parse_task,
    "tasks_of_repair.json": parse_task,
    "tasks_of_serial_number.json": parse_task,
    "tasks_of_subrental.json": parse_task,
    "tasks_of_vehicle.json": parse_task,
    "tasks_of_supplier.json": parse_task,
    "files_of_contact_person.json": parse_file,
    "files_of_contact.json": parse_file,
    "files_of_crew.json": parse_file,
    "files_of_equipment.json": parse_file,
    "files_of_invoice.json": parse_file,
    "files_of_project.json": parse_file,
    "files_of_purchase_order.json": parse_file,
    "files_of_quote.json": parse_file,
    "files_of_repair.json": parse_file,
    "files_of_serial_number.json": parse_file,
    "files_of_subrental.json": parse_file,
    "files_of_time_registration.json": parse_file,
    "files_of_vehicle.json": parse_file,
    "files_of_supplier.json": parse_file,
    "file_folders_of_contact_person.json": parse_file_folder,
    "file_folders_of_contact.json": parse_file_folder,
    "file_folders_of_crew.json": parse_file_folder,
    "file_folders_of_equipment.json": parse_file_folder,
    "file_folders_of_project.json": parse_file_folder,
    "file_folders_of_purchase_order.json": parse_file_folder,
    "file_folders_of_repair.json": parse_file_folder,
    "file_folders_of_serial_number.json": parse_file_folder,
    "file_folders_of_subproject.json": parse_file_folder,
    "file_folders_of_subrental.json": parse_file_folder,
    "file_folders_of_supplier.json": parse_file_folder,
    "file_folders_of_vehicle.json": parse_file_folder,
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
    "subtasks.json",
    "subtasks_of_task.json",
    "files_of_task.json",
    "file_folders_of_task.json",
    "tasks_of_contact_person.json",
    "tasks_of_contact.json",
    "tasks_of_crew.json",
    "tasks_of_equipment.json",
    "tasks_of_invoice.json",
    "tasks_of_purchase_order.json",
    "tasks_of_quote.json",
    "tasks_of_serial_number.json",
    "tasks_of_subrental.json",
    "tasks_of_vehicle.json",
    "tasks_of_supplier.json",
    "files_of_contact_person.json",
    "files_of_contact.json",
    "files_of_crew.json",
    "files_of_invoice.json",
    "files_of_purchase_order.json",
    "files_of_quote.json",
    "files_of_repair.json",
    "files_of_serial_number.json",
    "files_of_subrental.json",
    "files_of_time_registration.json",
    "files_of_vehicle.json",
    "files_of_supplier.json",
    "file_folders_of_contact_person.json",
    "file_folders_of_contact.json",
    "file_folders_of_crew.json",
    "file_folders_of_equipment.json",
    "file_folders_of_project.json",
    "file_folders_of_purchase_order.json",
    "file_folders_of_repair.json",
    "file_folders_of_serial_number.json",
    "file_folders_of_subrental.json",
    "file_folders_of_supplier.json",
    "file_folders_of_vehicle.json",
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
