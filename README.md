# aiorentman

[![Check](https://github.com/DaanVervacke/aiorentman/actions/workflows/check.yml/badge.svg)](https://github.com/DaanVervacke/aiorentman/actions/workflows/check.yml)
[![PyPI version](https://img.shields.io/pypi/v/aiorentman.svg)](https://pypi.org/project/aiorentman/)
[![Python versions](https://img.shields.io/pypi/pyversions/aiorentman.svg)](https://pypi.org/project/aiorentman/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unofficial asynchronous Python library to interact with the Rentman API. Requires Python >= 3.14.

This is a client for a documented public API, but it is not affiliated with or endorsed by Rentman B.V. Rentman runs one rolling API version and migrates integrations automatically, so the library pins its contract to the OpenAPI document it ships with and validates every endpoint against it.

## Install

```bash
pip install aiorentman
```

## Scope

The library covers the resources an RFID and materials project needs, read only:

| Resource | List | Iterate | Get |
| --- | --- | --- | --- |
| Equipment (materials) | `async_list_equipment` | `async_iter_equipment` | `async_get_equipment` |
| Serial numbers | `async_list_serial_numbers` | `async_iter_serial_numbers` | `async_get_serial_number` |
| Serial numbers of a material | `async_list_serial_numbers_of_equipment` | `async_iter_serial_numbers_of_equipment` | |
| Actual content | `async_list_actual_content` | `async_iter_actual_content` | `async_get_actual_content` |
| Actual content of a serial | `async_list_actual_content_of_serial_number` | `async_iter_actual_content_of_serial_number` | |
| Assigned serials | `async_list_equipment_assigned_serials` | `async_iter_equipment_assigned_serials` | `async_get_equipment_assigned_serial` |
| Assigned serials of a serial | `async_list_equipment_assigned_serials_of_serial_number` | `async_iter_equipment_assigned_serials_of_serial_number` | |
| Set content | `async_list_equipment_set_content` | `async_iter_equipment_set_content` | `async_get_equipment_set_content` |
| Set content of a material | `async_list_equipment_set_content_of_equipment` | `async_iter_equipment_set_content_of_equipment` | |
| Folders | `async_list_folders` | `async_iter_folders` | `async_get_folder` |
| Stock locations | `async_list_stock_locations` | `async_iter_stock_locations` | `async_get_stock_location` |
| Warehouse statuses | `async_list_warehouse_statuses` | `async_iter_warehouse_statuses` | `async_get_warehouse_status` |
| Statuses | `async_list_statuses` | `async_iter_statuses` | `async_get_status` |
| Stock movements | `async_list_stock_movements` | `async_iter_stock_movements` | `async_get_stock_movement` |
| Stock movements of a material | `async_list_stock_movements_of_equipment` | `async_iter_stock_movements_of_equipment` | |
| Repairs | `async_list_repairs` | `async_iter_repairs` | `async_get_repair` |
| Repairs of a material | `async_list_repairs_of_equipment` | `async_iter_repairs_of_equipment` | |
| Projects | `async_list_projects` | `async_iter_projects` | `async_get_project` |
| Subprojects | `async_list_subprojects` | `async_iter_subprojects` | `async_get_subproject` |
| Subprojects of a project | `async_list_subprojects_of_project` | `async_iter_subprojects_of_project` | |
| Project equipment | `async_list_project_equipment` | `async_iter_project_equipment` | `async_get_project_equipment` |
| Project equipment of a project | `async_list_project_equipment_of_project` | `async_iter_project_equipment_of_project` | |
| Project equipment of a subproject | `async_list_project_equipment_of_subproject` | `async_iter_project_equipment_of_subproject` | |
| Accessories | `async_list_accessories` | `async_iter_accessories` | `async_get_accessory` |
| Accessories of a material | `async_list_accessories_of_equipment` | `async_iter_accessories_of_equipment` | |
| Alternatives | `async_list_alternatives` | `async_iter_alternatives` | `async_get_alternative` |
| Alternatives of a material | `async_list_alternatives_of_equipment` | `async_iter_alternatives_of_equipment` | |
| Suppliers | `async_list_suppliers` | `async_iter_suppliers` | `async_get_supplier` |
| Suppliers of a material | `async_list_suppliers_of_equipment` | `async_iter_suppliers_of_equipment` | |
| Vehicles | `async_list_vehicles` | `async_iter_vehicles` | `async_get_vehicle` |
| Vehicles of a stock location | `async_list_vehicles_of_stock_location` | `async_iter_vehicles_of_stock_location` | |
| Extra input fields | `async_list_extra_input_fields` | `async_iter_extra_input_fields` | `async_get_extra_input_field` |
| Project statuses | `async_list_project_statuses` | `async_iter_project_statuses` | `async_get_project_status` |
| Project types | `async_list_project_types` | `async_iter_project_types` | `async_get_project_type` |
| Project function groups | `async_list_project_function_groups` | `async_iter_project_function_groups` | `async_get_project_function_group` |
| Function groups of a project | `async_list_project_function_groups_of_project` | `async_iter_project_function_groups_of_project` | |
| Function groups of a subproject | `async_list_project_function_groups_of_subproject` | `async_iter_project_function_groups_of_subproject` | |
| Project functions | `async_list_project_functions` | `async_iter_project_functions` | `async_get_project_function` |
| Functions of a project | `async_list_project_functions_of_project` | `async_iter_project_functions_of_project` | |
| Functions of a function group | `async_list_project_functions_of_project_function_group` | `async_iter_project_functions_of_project_function_group` | |
| Project crew | `async_list_project_crew` | `async_iter_project_crew` | `async_get_project_crew` |
| Crew of a project | `async_list_project_crew_of_project` | `async_iter_project_crew_of_project` | |
| Crew of a subproject | `async_list_project_crew_of_subproject` | `async_iter_project_crew_of_subproject` | |
| Crew of a project function | `async_list_project_crew_of_project_function` | `async_iter_project_crew_of_project_function` | |
| Project vehicles | `async_list_project_vehicles` | `async_iter_project_vehicles` | `async_get_project_vehicle` |
| Vehicles of a project | `async_list_project_vehicles_of_project` | `async_iter_project_vehicles_of_project` | |
| Vehicles of a subproject | `async_list_project_vehicles_of_subproject` | `async_iter_project_vehicles_of_subproject` | |
| Vehicles of a project function | `async_list_project_vehicles_of_project_function` | `async_iter_project_vehicles_of_project_function` | |
| Project equipment groups | `async_list_project_equipment_groups` | `async_iter_project_equipment_groups` | `async_get_project_equipment_group` |
| Equipment groups of a project | `async_list_project_equipment_groups_of_project` | `async_iter_project_equipment_groups_of_project` | |
| Equipment groups of a subproject | `async_list_project_equipment_groups_of_subproject` | `async_iter_project_equipment_groups_of_subproject` | |
| Project equipment of an equipment group | `async_list_project_equipment_of_project_equipment_group` | `async_iter_project_equipment_of_project_equipment_group` | |
| Project costs | `async_list_project_costs` | `async_iter_project_costs` | `async_get_project_cost` |
| Costs of a project | `async_list_project_costs_of_project` | `async_iter_project_costs_of_project` | |
| Project requests | `async_list_project_requests` | `async_iter_project_requests` | `async_get_project_request` |
| Project request equipment | `async_list_project_request_equipment` | `async_iter_project_request_equipment` | `async_get_project_request_equipment` |
| Request equipment of a project request | `async_list_project_request_equipment_of_project_request` | `async_iter_project_request_equipment_of_project_request` | |
| Quotes | `async_list_quotes` | `async_iter_quotes` | `async_get_quote` |
| Quotes of a project | `async_list_quotes_of_project` | `async_iter_quotes_of_project` | |
| Invoice lines of a quote | `async_list_invoice_lines_of_quote` | `async_iter_invoice_lines_of_quote` | |
| Contracts | `async_list_contracts` | `async_iter_contracts` | `async_get_contract` |
| Contracts of a project | `async_list_contracts_of_project` | `async_iter_contracts_of_project` | |
| Invoices | `async_list_invoices` | `async_iter_invoices` | `async_get_invoice` |
| Invoice lines of an invoice | `async_list_invoice_lines_of_invoice` | `async_iter_invoice_lines_of_invoice` | |
| Payments of an invoice | `async_list_payments_of_invoice` | `async_iter_payments_of_invoice` | |
| Invoice lines | `async_list_invoice_lines` | `async_iter_invoice_lines` | `async_get_invoice_line` |
| Payments | `async_list_payments` | `async_iter_payments` | `async_get_payment` |
| Ledger codes | `async_list_ledger_codes` | `async_iter_ledger_codes` | `async_get_ledger_code` |
| Tax classes | `async_list_tax_classes` | `async_iter_tax_classes` | `async_get_tax_class` |
| Subrentals | `async_list_subrentals` | `async_iter_subrentals` | `async_get_subrental` |
| Subrental equipment | `async_list_subrental_equipment` | `async_iter_subrental_equipment` | `async_get_subrental_equipment` |
| Subrental equipment of a subrental | `async_list_subrental_equipment_of_subrental` | `async_iter_subrental_equipment_of_subrental` | |
| Subrental equipment of a group | `async_list_subrental_equipment_of_subrental_equipment_group` | `async_iter_subrental_equipment_of_subrental_equipment_group` | |
| Subrental equipment groups | `async_list_subrental_equipment_groups` | `async_iter_subrental_equipment_groups` | `async_get_subrental_equipment_group` |
| Equipment groups of a subrental | `async_list_subrental_equipment_groups_of_subrental` | `async_iter_subrental_equipment_groups_of_subrental` | |
| Purchase orders | `async_list_purchase_orders` | `async_iter_purchase_orders` | `async_get_purchase_order` |
| Invoice lines of a purchase order | `async_list_invoice_lines_of_purchase_order` | `async_iter_invoice_lines_of_purchase_order` | |
| Purchase order costs | `async_list_purchase_order_costs` | `async_iter_purchase_order_costs` | `async_get_purchase_order_cost` |
| Costs of a purchase order | `async_list_purchase_order_costs_of_purchase_order` | `async_iter_purchase_order_costs_of_purchase_order` | |
| Purchase order global costs | `async_list_purchase_order_global_costs` | `async_iter_purchase_order_global_costs` | `async_get_purchase_order_global_cost` |
| Global costs of a purchase order | `async_list_purchase_order_global_costs_of_purchase_order` | `async_iter_purchase_order_global_costs_of_purchase_order` | |
| Crew | `async_list_crew` | `async_iter_crew` | `async_get_crew` |
| Appointments of a crew member | `async_list_appointments_of_crew` | `async_iter_appointments_of_crew` | |
| Crew availability | `async_list_crew_availability` | `async_iter_crew_availability` | `async_get_crew_availability` |
| Availability of a crew member | `async_list_crew_availability_of_crew` | `async_iter_crew_availability_of_crew` | |
| Crew rates | `async_list_crew_rates` | `async_iter_crew_rates` | `async_get_crew_rate` |
| Rates of a crew member | `async_list_crew_rates_of_crew` | `async_iter_crew_rates_of_crew` | |
| Invitations | `async_list_invitations` | `async_iter_invitations` | `async_get_invitation` |
| Invitations of a crew member | `async_list_invitations_of_crew` | `async_iter_invitations_of_crew` | |
| Appointments | `async_list_appointments` | `async_iter_appointments` | `async_get_appointment` |
| Appointment crew | `async_list_appointment_crew` | `async_iter_appointment_crew` | `async_get_appointment_crew` |
| Crew of an appointment | `async_list_appointment_crew_of_appointment` | `async_iter_appointment_crew_of_appointment` | |
| Time registrations | `async_list_time_registrations` | `async_iter_time_registrations` | `async_get_time_registration` |
| Time registration activities | `async_list_time_registration_activities` | `async_iter_time_registration_activities` | `async_get_time_registration_activity` |
| Activities of a time registration | `async_list_time_registration_activities_of_time_registration` | `async_iter_time_registration_activities_of_time_registration` | |
| Leave requests | `async_list_leave_requests` | `async_iter_leave_requests` | `async_get_leave_request` |
| Time registrations of a leave request | `async_list_time_registrations_of_leave_request` | `async_iter_time_registrations_of_leave_request` | |
| Leave mutations | `async_list_leave_mutations` | `async_iter_leave_mutations` | `async_get_leave_mutation` |
| Leave types | `async_list_leave_types` | `async_iter_leave_types` | `async_get_leave_type` |
| Contacts | `async_list_contacts` | `async_iter_contacts` | `async_get_contact` |
| Contact persons | `async_list_contact_persons` | `async_iter_contact_persons` | `async_get_contact_person` |
| Contact persons of a contact | `async_list_contact_persons_of_contact` | `async_iter_contact_persons_of_contact` | |
| Tasks | `async_list_tasks` | `async_iter_tasks` | `async_get_tasks` |
| Subtasks | `async_list_subtasks` | `async_iter_subtasks` | `async_get_subtasks` |
| Task assignments | `async_list_task_assignments` | `async_iter_task_assignments` | `async_get_task_assignments` |
| Task statuses | `async_list_task_statuses` | `async_iter_task_statuses` | `async_get_task_statuses` |
| Files | `async_list_files` | `async_iter_files` | `async_get_files` |
| File folders | `async_list_file_folders` | `async_iter_file_folders` | `async_get_file_folders` |
| Subtasks of a task | `async_list_subtasks_of_task` | `async_iter_subtasks_of_task` |  |
| Task assignments of a task | `async_list_task_assignments_of_task` | `async_iter_task_assignments_of_task` |  |
| Files of a task | `async_list_files_of_task` | `async_iter_files_of_task` |  |
| File folders of a task | `async_list_file_folders_of_task` | `async_iter_file_folders_of_task` |  |
| Tasks of a contact person | `async_list_tasks_of_contact_person` | `async_iter_tasks_of_contact_person` |  |
| Tasks of a contact | `async_list_tasks_of_contact` | `async_iter_tasks_of_contact` |  |
| Tasks of a crew member | `async_list_tasks_of_crew` | `async_iter_tasks_of_crew` |  |
| Tasks of a material | `async_list_tasks_of_equipment` | `async_iter_tasks_of_equipment` |  |
| Tasks of an invoice | `async_list_tasks_of_invoice` | `async_iter_tasks_of_invoice` |  |
| Tasks of a project | `async_list_tasks_of_project` | `async_iter_tasks_of_project` |  |
| Tasks of a purchase order | `async_list_tasks_of_purchase_order` | `async_iter_tasks_of_purchase_order` |  |
| Tasks of a quote | `async_list_tasks_of_quote` | `async_iter_tasks_of_quote` |  |
| Tasks of a repair | `async_list_tasks_of_repair` | `async_iter_tasks_of_repair` |  |
| Tasks of a serial number | `async_list_tasks_of_serial_number` | `async_iter_tasks_of_serial_number` |  |
| Tasks of a subrental | `async_list_tasks_of_subrental` | `async_iter_tasks_of_subrental` |  |
| Tasks of a vehicle | `async_list_tasks_of_vehicle` | `async_iter_tasks_of_vehicle` |  |
| Tasks of a supplier | `async_list_tasks_of_supplier` | `async_iter_tasks_of_supplier` |  |
| Files of a contact person | `async_list_files_of_contact_person` | `async_iter_files_of_contact_person` |  |
| Files of a contact | `async_list_files_of_contact` | `async_iter_files_of_contact` |  |
| Files of a crew member | `async_list_files_of_crew` | `async_iter_files_of_crew` |  |
| Files of a material | `async_list_files_of_equipment` | `async_iter_files_of_equipment` |  |
| Files of an invoice | `async_list_files_of_invoice` | `async_iter_files_of_invoice` |  |
| Files of a project | `async_list_files_of_project` | `async_iter_files_of_project` |  |
| Files of a purchase order | `async_list_files_of_purchase_order` | `async_iter_files_of_purchase_order` |  |
| Files of a quote | `async_list_files_of_quote` | `async_iter_files_of_quote` |  |
| Files of a repair | `async_list_files_of_repair` | `async_iter_files_of_repair` |  |
| Files of a serial number | `async_list_files_of_serial_number` | `async_iter_files_of_serial_number` |  |
| Files of a subrental | `async_list_files_of_subrental` | `async_iter_files_of_subrental` |  |
| Files of a time registration | `async_list_files_of_time_registration` | `async_iter_files_of_time_registration` |  |
| Files of a vehicle | `async_list_files_of_vehicle` | `async_iter_files_of_vehicle` |  |
| Files of a supplier | `async_list_files_of_supplier` | `async_iter_files_of_supplier` |  |
| File folders of a contact person | `async_list_file_folders_of_contact_person` | `async_iter_file_folders_of_contact_person` |  |
| File folders of a contact | `async_list_file_folders_of_contact` | `async_iter_file_folders_of_contact` |  |
| File folders of a crew member | `async_list_file_folders_of_crew` | `async_iter_file_folders_of_crew` |  |
| File folders of a material | `async_list_file_folders_of_equipment` | `async_iter_file_folders_of_equipment` |  |
| File folders of a project | `async_list_file_folders_of_project` | `async_iter_file_folders_of_project` |  |
| File folders of a purchase order | `async_list_file_folders_of_purchase_order` | `async_iter_file_folders_of_purchase_order` |  |
| File folders of a repair | `async_list_file_folders_of_repair` | `async_iter_file_folders_of_repair` |  |
| File folders of a serial number | `async_list_file_folders_of_serial_number` | `async_iter_file_folders_of_serial_number` |  |
| File folders of a subproject | `async_list_file_folders_of_subproject` | `async_iter_file_folders_of_subproject` |  |
| File folders of a subrental | `async_list_file_folders_of_subrental` | `async_iter_file_folders_of_subrental` |  |
| File folders of a supplier | `async_list_file_folders_of_supplier` | `async_iter_file_folders_of_supplier` |  |
| File folders of a vehicle | `async_list_file_folders_of_vehicle` | `async_iter_file_folders_of_vehicle` |  |
| Rates | `async_list_rates` | `async_iter_rates` | `async_get_rate` |
| Rate factors | `async_list_rate_factors` | `async_iter_rate_factors` | `async_get_rate_factor` |
| Rate factors of a rate | `async_list_rate_factors_of_rate` | `async_iter_rate_factors_of_rate` |  |
| Factors | `async_list_factors` | `async_iter_factors` | `async_get_factor` |
| Factors of a factor group | `async_list_factors_of_factor_group` | `async_iter_factors_of_factor_group` |  |
| Factor groups | `async_list_factor_groups` | `async_iter_factor_groups` | `async_get_factor_group` |

## Token

Rentman issues one static token per user, generated in the application under Configuration, Integrations. Only the last generated token is valid. Pass it explicitly or set `RENTMAN_TOKEN`:

```python
import asyncio

from aiorentman import RentmanClient


async def main() -> None:
    async with RentmanClient(token="your-api-token") as client:
        page = await client.async_list_equipment()
        print(page.item_count, "materials on this page")


asyncio.run(main())
```

## Querying

Every list method takes a `Query` with the field selection, sorting, filters, expansion, and paging that the API supports:

```python
from aiorentman import Query, Sort, eq, lt

query = Query(
    fields=("name", "code", "price"),
    sort=(Sort("name"),),
    expand=("folder",),
    filters=(eq("code", "AUD-001"), lt("price", 200)),
    limit=100,
)
page = await client.async_list_equipment(query)
```

Filters support the relational operators the API documents: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, and `is_null`. Field names come straight from the API schema, including `custom_<number>` custom fields.

Linked fields such as `equipment.folder` hold a `RentmanLink` with the API path of the linked resource. Expand a field and the parser returns the full typed model instead.

## RFID and materials

Rentman links every RFID tag to exactly one serial number, and the tag identifier lands in the `qrcodes` field of that serial number. The library exposes `qrcodes` as a parsed tuple. That field is generated by the Rentman backend, and the API can neither filter nor sort on it, so an RFID scan resolves against a local index built from a serial number sync:

```python
index: dict[str, int] = {}
query = Query(fields=("serial", "qrcodes", "equipment"), limit=1500)
async for serial in client.async_iter_serial_numbers(query):
    for tag in serial.qrcodes:
        index[tag] = serial.id
```

The docs describe the full workflow, including expansion and availability checks: see `docs/serial-numbers.rst`.

## Rate limits

Rentman allows 10 requests per second, at most 20 concurrent requests, and 50.000 requests per day. The client enforces the first two by default. Pass `requests_per_second=None` to disable pacing, or lower it when several consumers share one account. Exceeding the server-side limits raises `RentmanRateLimitError`.

## Errors

| Exception | Meaning |
| --- | --- |
| `RentmanAuthenticationError` | The token is missing or was rejected |
| `RentmanAuthorizationError` | The token does not grant access to a resource |
| `RentmanRateLimitError` | The request exceeded the rate limits |
| `RentmanCommunicationError` | The API is unreachable or answered with a failure |
| `RentmanTimeoutError` | A request exceeded the configured timeout |
| `RentmanInvalidResponseError` | A response payload was unusable |
| `RentmanNotFoundError` | The requested object does not exist |
| `RentmanClientClosedError` | The client was closed |

## Development

```bash
uv sync
uv run python -m scripts.check
```

## License

MIT. See [LICENSE](LICENSE).
