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
