"""Client tests: token resolution, wire pinning, cursors, and ownership."""

import dataclasses
import inspect
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import aiohttp
import pytest
from aioresponses import aioresponses

from aiorentman import Query, RentmanClient, RentmanPage, Sort, eq, is_null, lt
from aiorentman._endpoints import CATALOG, CreateArgs, DeleteArgs, LinkedCreateArgs, UpdateArgs
from aiorentman.const import BASE_URL, DEFAULT_REQUESTS_PER_SECOND
from aiorentman.exceptions import (
    RentmanAuthenticationError,
    RentmanClientClosedError,
    RentmanInvalidResponseError,
    RentmanNotFoundError,
    RentmanRateLimitError,
    RentmanValidationError,
)
from aiorentman.models import ActualContent, Equipment, RentmanLink, Repair, SerialNumber
from aiorentman.payloads import TaskPayload

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
    (lambda client: client.async_list_accessories(), "/accessories"),
    (
        lambda client: client.async_list_accessories_of_equipment(12),
        "/equipment/12/accessories",
    ),
    (lambda client: client.async_list_alternatives(), "/alternatives"),
    (
        lambda client: client.async_list_alternatives_of_equipment(346),
        "/equipment/346/alternatives",
    ),
    (lambda client: client.async_list_suppliers(), "/suppliers"),
    (
        lambda client: client.async_list_suppliers_of_equipment(354),
        "/equipment/354/suppliers",
    ),
    (lambda client: client.async_list_vehicles(), "/vehicles"),
    (
        lambda client: client.async_list_vehicles_of_stock_location(2),
        "/stocklocations/2/vehicles",
    ),
    (lambda client: client.async_list_extra_input_fields(), "/extrainputfields"),
    (lambda client: client.async_list_project_statuses(), "/projectstatuses"),
    (lambda client: client.async_list_project_types(), "/projecttypes"),
    (
        lambda client: client.async_list_project_function_groups(),
        "/projectfunctiongroups",
    ),
    (
        lambda client: client.async_list_project_function_groups_of_project(80),
        "/projects/80/projectfunctiongroups",
    ),
    (
        lambda client: client.async_list_project_function_groups_of_subproject(80),
        "/subprojects/80/projectfunctiongroups",
    ),
    (lambda client: client.async_list_project_functions(), "/projectfunctions"),
    (
        lambda client: client.async_list_project_functions_of_project(80),
        "/projects/80/projectfunctions",
    ),
    (
        lambda client: client.async_list_project_functions_of_project_function_group(10),
        "/projectfunctiongroups/10/projectfunctions",
    ),
    (lambda client: client.async_list_project_crew(), "/projectcrew"),
    (lambda client: client.async_list_project_crew_of_project(80), "/projects/80/projectcrew"),
    (
        lambda client: client.async_list_project_crew_of_subproject(80),
        "/subprojects/80/projectcrew",
    ),
    (
        lambda client: client.async_list_project_crew_of_project_function(8),
        "/projectfunctions/8/projectcrew",
    ),
    (lambda client: client.async_list_project_vehicles(), "/projectvehicles"),
    (
        lambda client: client.async_list_project_vehicles_of_project(80),
        "/projects/80/projectvehicles",
    ),
    (
        lambda client: client.async_list_project_vehicles_of_subproject(80),
        "/subprojects/80/projectvehicles",
    ),
    (
        lambda client: client.async_list_project_vehicles_of_project_function(43),
        "/projectfunctions/43/projectvehicles",
    ),
    (lambda client: client.async_list_project_equipment_groups(), "/projectequipmentgroup"),
    (
        lambda client: client.async_list_project_equipment_groups_of_project(80),
        "/projects/80/projectequipmentgroup",
    ),
    (
        lambda client: client.async_list_project_equipment_groups_of_subproject(80),
        "/subprojects/80/projectequipmentgroup",
    ),
    (
        lambda client: client.async_list_project_equipment_of_project_equipment_group(150),
        "/projectequipmentgroup/150/projectequipment",
    ),
    (lambda client: client.async_list_project_costs(), "/costs"),
    (lambda client: client.async_list_project_costs_of_project(80), "/projects/80/costs"),
    (lambda client: client.async_list_project_requests(), "/projectrequests"),
    (lambda client: client.async_list_project_request_equipment(), "/projectrequestequipment"),
    (
        lambda client: client.async_list_project_request_equipment_of_project_request(1),
        "/projectrequests/1/projectrequestequipment",
    ),
    (lambda client: client.async_list_quotes(), "/quotes"),
    (lambda client: client.async_list_quotes_of_project(128), "/projects/128/quotes"),
    (lambda client: client.async_list_invoice_lines_of_quote(1), "/quotes/1/invoicelines"),
    (lambda client: client.async_list_contracts(), "/contracts"),
    (lambda client: client.async_list_contracts_of_project(128), "/projects/128/contracts"),
    (lambda client: client.async_list_invoices(), "/invoices"),
    (lambda client: client.async_list_invoice_lines_of_invoice(1), "/invoices/1/invoicelines"),
    (lambda client: client.async_list_payments_of_invoice(1), "/invoices/1/payments"),
    (lambda client: client.async_list_invoice_lines(), "/invoicelines"),
    (lambda client: client.async_list_payments(), "/payments"),
    (lambda client: client.async_list_ledger_codes(), "/ledgercodes"),
    (lambda client: client.async_list_tax_classes(), "/taxclasses"),
    (lambda client: client.async_list_subrentals(), "/subrentals"),
    (lambda client: client.async_list_subrental_equipment(), "/subrentalequipment"),
    (lambda client: client.async_list_subrental_equipment_groups(), "/subrentalequipmentgroup"),
    (
        lambda client: client.async_list_subrental_equipment_of_subrental(17),
        "/subrentals/17/subrentalequipment",
    ),
    (
        lambda client: client.async_list_subrental_equipment_groups_of_subrental(17),
        "/subrentals/17/subrentalequipmentgroup",
    ),
    (
        lambda client: client.async_list_subrental_equipment_of_subrental_equipment_group(2),
        "/subrentalequipmentgroup/2/subrentalequipment",
    ),
    (lambda client: client.async_list_purchase_orders(), "/purchaseorders"),
    (
        lambda client: client.async_list_invoice_lines_of_purchase_order(1),
        "/purchaseorders/1/invoicelines",
    ),
    (
        lambda client: client.async_list_purchase_order_costs_of_purchase_order(1),
        "/purchaseorders/1/purchaseordercosts",
    ),
    (
        lambda client: client.async_list_purchase_order_global_costs_of_purchase_order(1),
        "/purchaseorders/1/purchaseorderglobalcosts",
    ),
    (lambda client: client.async_list_purchase_order_costs(), "/purchaseordercosts"),
    (lambda client: client.async_list_purchase_order_global_costs(), "/purchaseorderglobalcosts"),
    (lambda client: client.async_list_crew(), "/crew"),
    (lambda client: client.async_list_appointments_of_crew(33), "/crew/33/appointments"),
    (lambda client: client.async_list_crew_availability_of_crew(33), "/crew/33/crewavailability"),
    (lambda client: client.async_list_crew_rates_of_crew(33), "/crew/33/crewrates"),
    (lambda client: client.async_list_invitations_of_crew(33), "/crew/33/invitations"),
    (lambda client: client.async_list_crew_availability(), "/crewavailability"),
    (lambda client: client.async_list_crew_rates(), "/crewrates"),
    (lambda client: client.async_list_invitations(), "/invitations"),
    (lambda client: client.async_list_appointments(), "/appointments"),
    (
        lambda client: client.async_list_appointment_crew_of_appointment(28),
        "/appointments/28/appointmentcrew",
    ),
    (lambda client: client.async_list_appointment_crew(), "/appointmentcrew"),
    (lambda client: client.async_list_time_registrations(), "/timeregistration"),
    (
        lambda client: client.async_list_time_registration_activities_of_time_registration(20),
        "/timeregistration/20/timeregistrationactivities",
    ),
    (
        lambda client: client.async_list_time_registration_activities(),
        "/timeregistrationactivities",
    ),
    (lambda client: client.async_list_leave_requests(), "/leaverequest"),
    (
        lambda client: client.async_list_time_registrations_of_leave_request(1),
        "/leaverequest/1/timeregistration",
    ),
    (lambda client: client.async_list_leave_mutations(), "/leavemutation"),
    (lambda client: client.async_list_leave_types(), "/leavetypes"),
    (lambda client: client.async_list_contacts(), "/contacts"),
    (lambda client: client.async_list_contact_persons(), "/contactpersons"),
    (lambda client: client.async_list_rates(), "/rates"),
    (lambda client: client.async_list_rate_factors(), "/ratefactors"),
    (
        lambda client: client.async_list_rate_factors_of_rate(1),
        "/rates/1/ratefactors",
    ),
    (lambda client: client.async_list_factors(), "/factors"),
    (
        lambda client: client.async_list_factors_of_factor_group(1),
        "/factorgroups/1/factors",
    ),
    (lambda client: client.async_list_factor_groups(), "/factorgroups"),
    (
        lambda client: client.async_list_contact_persons_of_contact(3609),
        "/contacts/3609/contactpersons",
    ),
    (lambda client: client.async_list_tasks(), "/tasks"),
    (lambda client: client.async_list_subtasks(), "/subtasks"),
    (lambda client: client.async_list_task_assignments(), "/taskassignments"),
    (lambda client: client.async_list_task_statuses(), "/taskstatuses"),
    (lambda client: client.async_list_files(), "/files"),
    (lambda client: client.async_list_file_folders(), "/file_folders"),
    (
        lambda client: client.async_list_subtasks_of_task(95),
        "/tasks/95/subtasks",
    ),
    (
        lambda client: client.async_list_task_assignments_of_task(95),
        "/tasks/95/taskassignments",
    ),
    (
        lambda client: client.async_list_files_of_task(95),
        "/tasks/95/files",
    ),
    (
        lambda client: client.async_list_file_folders_of_task(95),
        "/tasks/95/file_folders",
    ),
    (
        lambda client: client.async_list_tasks_of_contact_person(8),
        "/contactpersons/8/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_contact(3609),
        "/contacts/3609/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_crew(33),
        "/crew/33/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_equipment(12),
        "/equipment/12/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_invoice(1),
        "/invoices/1/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_project(80),
        "/projects/80/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_purchase_order(1),
        "/purchaseorders/1/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_quote(1),
        "/quotes/1/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_repair(220),
        "/repairs/220/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_serial_number(41),
        "/serialnumbers/41/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_subrental(17),
        "/subrentals/17/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_vehicle(7),
        "/vehicles/7/tasks",
    ),
    (
        lambda client: client.async_list_tasks_of_supplier(1),
        "/suppliers/1/tasks",
    ),
    (
        lambda client: client.async_list_files_of_contact_person(8),
        "/contactpersons/8/files",
    ),
    (
        lambda client: client.async_list_files_of_contact(3609),
        "/contacts/3609/files",
    ),
    (
        lambda client: client.async_list_files_of_crew(33),
        "/crew/33/files",
    ),
    (
        lambda client: client.async_list_files_of_equipment(12),
        "/equipment/12/files",
    ),
    (
        lambda client: client.async_list_files_of_invoice(1),
        "/invoices/1/files",
    ),
    (
        lambda client: client.async_list_files_of_project(80),
        "/projects/80/files",
    ),
    (
        lambda client: client.async_list_files_of_purchase_order(1),
        "/purchaseorders/1/files",
    ),
    (
        lambda client: client.async_list_files_of_quote(1),
        "/quotes/1/files",
    ),
    (
        lambda client: client.async_list_files_of_repair(220),
        "/repairs/220/files",
    ),
    (
        lambda client: client.async_list_files_of_serial_number(41),
        "/serialnumbers/41/files",
    ),
    (
        lambda client: client.async_list_files_of_subrental(17),
        "/subrentals/17/files",
    ),
    (
        lambda client: client.async_list_files_of_time_registration(20),
        "/timeregistration/20/files",
    ),
    (
        lambda client: client.async_list_files_of_vehicle(7),
        "/vehicles/7/files",
    ),
    (
        lambda client: client.async_list_files_of_supplier(1),
        "/suppliers/1/files",
    ),
    (
        lambda client: client.async_list_file_folders_of_contact_person(8),
        "/contactpersons/8/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_contact(3609),
        "/contacts/3609/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_crew(33),
        "/crew/33/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_equipment(12),
        "/equipment/12/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_project(80),
        "/projects/80/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_purchase_order(1),
        "/purchaseorders/1/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_repair(220),
        "/repairs/220/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_serial_number(41),
        "/serialnumbers/41/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_subproject(501),
        "/subprojects/501/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_subrental(17),
        "/subrentals/17/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_supplier(1),
        "/suppliers/1/file_folders",
    ),
    (
        lambda client: client.async_list_file_folders_of_vehicle(7),
        "/vehicles/7/file_folders",
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
    (lambda client: client.async_get_accessory(2), "/accessories/2"),
    (lambda client: client.async_get_alternative(1), "/alternatives/1"),
    (lambda client: client.async_get_supplier(1), "/suppliers/1"),
    (lambda client: client.async_get_vehicle(7), "/vehicles/7"),
    (lambda client: client.async_get_extra_input_field(1), "/extrainputfields/1"),
    (lambda client: client.async_get_project_status(1), "/projectstatuses/1"),
    (lambda client: client.async_get_project_type(104), "/projecttypes/104"),
    (lambda client: client.async_get_project_function_group(3), "/projectfunctiongroups/3"),
    (lambda client: client.async_get_project_function(8), "/projectfunctions/8"),
    (lambda client: client.async_get_project_crew(1), "/projectcrew/1"),
    (lambda client: client.async_get_project_vehicle(11), "/projectvehicles/11"),
    (lambda client: client.async_get_project_equipment_group(150), "/projectequipmentgroup/150"),
    (lambda client: client.async_get_project_cost(7), "/costs/7"),
    (lambda client: client.async_get_project_request(1), "/projectrequests/1"),
    (lambda client: client.async_get_project_request_equipment(1), "/projectrequestequipment/1"),
    (lambda client: client.async_get_quote(1), "/quotes/1"),
    (lambda client: client.async_get_contract(1), "/contracts/1"),
    (lambda client: client.async_get_invoice(1), "/invoices/1"),
    (lambda client: client.async_get_invoice_line(99), "/invoicelines/99"),
    (lambda client: client.async_get_payment(1), "/payments/1"),
    (lambda client: client.async_get_ledger_code(1), "/ledgercodes/1"),
    (lambda client: client.async_get_tax_class(2), "/taxclasses/2"),
    (lambda client: client.async_get_subrental(17), "/subrentals/17"),
    (lambda client: client.async_get_subrental_equipment(1), "/subrentalequipment/1"),
    (lambda client: client.async_get_subrental_equipment_group(1), "/subrentalequipmentgroup/1"),
    (lambda client: client.async_get_purchase_order(1), "/purchaseorders/1"),
    (lambda client: client.async_get_purchase_order_cost(1), "/purchaseordercosts/1"),
    (lambda client: client.async_get_purchase_order_global_cost(1), "/purchaseorderglobalcosts/1"),
    (lambda client: client.async_get_crew(33), "/crew/33"),
    (lambda client: client.async_get_crew_availability(1), "/crewavailability/1"),
    (lambda client: client.async_get_crew_rate(1), "/crewrates/1"),
    (lambda client: client.async_get_invitation(1), "/invitations/1"),
    (lambda client: client.async_get_appointment(25), "/appointments/25"),
    (lambda client: client.async_get_appointment_crew(2), "/appointmentcrew/2"),
    (lambda client: client.async_get_time_registration(20), "/timeregistration/20"),
    (
        lambda client: client.async_get_time_registration_activity(1),
        "/timeregistrationactivities/1",
    ),
    (lambda client: client.async_get_leave_request(1), "/leaverequest/1"),
    (lambda client: client.async_get_leave_mutation(1), "/leavemutation/1"),
    (lambda client: client.async_get_leave_type(1), "/leavetypes/1"),
    (lambda client: client.async_get_contact(3609), "/contacts/3609"),
    (lambda client: client.async_get_contact_person(8), "/contactpersons/8"),
    (lambda client: client.async_get_rate(1), "/rates/1"),
    (lambda client: client.async_get_rate_factor(1), "/ratefactors/1"),
    (lambda client: client.async_get_factor(2), "/factors/2"),
    (lambda client: client.async_get_factor_group(1), "/factorgroups/1"),
    (lambda client: client.async_get_tasks(95), "/tasks/95"),
    (lambda client: client.async_get_subtasks(1), "/subtasks/1"),
    (lambda client: client.async_get_task_assignments(1), "/taskassignments/1"),
    (lambda client: client.async_get_task_statuses(1), "/taskstatuses/1"),
    (lambda client: client.async_get_files(26), "/files/26"),
    (lambda client: client.async_get_file_folders(1), "/file_folders/1"),
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
    (lambda client, query: client.async_iter_accessories(query), "/accessories"),
    (
        lambda client, query: client.async_iter_accessories_of_equipment(12, query),
        "/equipment/12/accessories",
    ),
    (lambda client, query: client.async_iter_alternatives(query), "/alternatives"),
    (
        lambda client, query: client.async_iter_alternatives_of_equipment(346, query),
        "/equipment/346/alternatives",
    ),
    (lambda client, query: client.async_iter_suppliers(query), "/suppliers"),
    (
        lambda client, query: client.async_iter_suppliers_of_equipment(354, query),
        "/equipment/354/suppliers",
    ),
    (lambda client, query: client.async_iter_vehicles(query), "/vehicles"),
    (
        lambda client, query: client.async_iter_vehicles_of_stock_location(2, query),
        "/stocklocations/2/vehicles",
    ),
    (lambda client, query: client.async_iter_extra_input_fields(query), "/extrainputfields"),
    (lambda client, query: client.async_iter_project_statuses(query), "/projectstatuses"),
    (lambda client, query: client.async_iter_project_types(query), "/projecttypes"),
    (
        lambda client, query: client.async_iter_project_function_groups(query),
        "/projectfunctiongroups",
    ),
    (
        lambda client, query: client.async_iter_project_function_groups_of_project(80, query),
        "/projects/80/projectfunctiongroups",
    ),
    (
        lambda client, query: client.async_iter_project_function_groups_of_subproject(80, query),
        "/subprojects/80/projectfunctiongroups",
    ),
    (lambda client, query: client.async_iter_project_functions(query), "/projectfunctions"),
    (
        lambda client, query: client.async_iter_project_functions_of_project(80, query),
        "/projects/80/projectfunctions",
    ),
    (
        lambda client, query: client.async_iter_project_functions_of_project_function_group(
            10, query
        ),
        "/projectfunctiongroups/10/projectfunctions",
    ),
    (lambda client, query: client.async_iter_project_crew(query), "/projectcrew"),
    (
        lambda client, query: client.async_iter_project_crew_of_project(80, query),
        "/projects/80/projectcrew",
    ),
    (
        lambda client, query: client.async_iter_project_crew_of_subproject(80, query),
        "/subprojects/80/projectcrew",
    ),
    (
        lambda client, query: client.async_iter_project_crew_of_project_function(8, query),
        "/projectfunctions/8/projectcrew",
    ),
    (lambda client, query: client.async_iter_project_vehicles(query), "/projectvehicles"),
    (
        lambda client, query: client.async_iter_project_vehicles_of_project(80, query),
        "/projects/80/projectvehicles",
    ),
    (
        lambda client, query: client.async_iter_project_vehicles_of_subproject(80, query),
        "/subprojects/80/projectvehicles",
    ),
    (
        lambda client, query: client.async_iter_project_vehicles_of_project_function(43, query),
        "/projectfunctions/43/projectvehicles",
    ),
    (
        lambda client, query: client.async_iter_project_equipment_groups(query),
        "/projectequipmentgroup",
    ),
    (
        lambda client, query: client.async_iter_project_equipment_groups_of_project(80, query),
        "/projects/80/projectequipmentgroup",
    ),
    (
        lambda client, query: client.async_iter_project_equipment_groups_of_subproject(80, query),
        "/subprojects/80/projectequipmentgroup",
    ),
    (
        lambda client, query: client.async_iter_project_equipment_of_project_equipment_group(
            150, query
        ),
        "/projectequipmentgroup/150/projectequipment",
    ),
    (lambda client, query: client.async_iter_project_costs(query), "/costs"),
    (
        lambda client, query: client.async_iter_project_costs_of_project(80, query),
        "/projects/80/costs",
    ),
    (lambda client, query: client.async_iter_project_requests(query), "/projectrequests"),
    (
        lambda client, query: client.async_iter_project_request_equipment(query),
        "/projectrequestequipment",
    ),
    (
        lambda client, query: client.async_iter_project_request_equipment_of_project_request(
            1, query
        ),
        "/projectrequests/1/projectrequestequipment",
    ),
    (lambda client, query: client.async_iter_quotes(query), "/quotes"),
    (lambda client, query: client.async_iter_quotes_of_project(128, query), "/projects/128/quotes"),
    (
        lambda client, query: client.async_iter_invoice_lines_of_quote(1, query),
        "/quotes/1/invoicelines",
    ),
    (lambda client, query: client.async_iter_contracts(query), "/contracts"),
    (
        lambda client, query: client.async_iter_contracts_of_project(128, query),
        "/projects/128/contracts",
    ),
    (lambda client, query: client.async_iter_invoices(query), "/invoices"),
    (
        lambda client, query: client.async_iter_invoice_lines_of_invoice(1, query),
        "/invoices/1/invoicelines",
    ),
    (
        lambda client, query: client.async_iter_payments_of_invoice(1, query),
        "/invoices/1/payments",
    ),
    (lambda client, query: client.async_iter_invoice_lines(query), "/invoicelines"),
    (lambda client, query: client.async_iter_payments(query), "/payments"),
    (lambda client, query: client.async_iter_ledger_codes(query), "/ledgercodes"),
    (lambda client, query: client.async_iter_tax_classes(query), "/taxclasses"),
    (lambda client, query: client.async_iter_subrentals(query), "/subrentals"),
    (lambda client, query: client.async_iter_subrental_equipment(query), "/subrentalequipment"),
    (
        lambda client, query: client.async_iter_subrental_equipment_groups(query),
        "/subrentalequipmentgroup",
    ),
    (
        lambda client, query: client.async_iter_subrental_equipment_of_subrental(17, query),
        "/subrentals/17/subrentalequipment",
    ),
    (
        lambda client, query: client.async_iter_subrental_equipment_groups_of_subrental(17, query),
        "/subrentals/17/subrentalequipmentgroup",
    ),
    (
        lambda client, query: client.async_iter_subrental_equipment_of_subrental_equipment_group(
            2, query
        ),
        "/subrentalequipmentgroup/2/subrentalequipment",
    ),
    (lambda client, query: client.async_iter_purchase_orders(query), "/purchaseorders"),
    (
        lambda client, query: client.async_iter_invoice_lines_of_purchase_order(1, query),
        "/purchaseorders/1/invoicelines",
    ),
    (
        lambda client, query: client.async_iter_purchase_order_costs_of_purchase_order(1, query),
        "/purchaseorders/1/purchaseordercosts",
    ),
    (
        lambda client, query: client.async_iter_purchase_order_global_costs_of_purchase_order(
            1, query
        ),
        "/purchaseorders/1/purchaseorderglobalcosts",
    ),
    (lambda client, query: client.async_iter_purchase_order_costs(query), "/purchaseordercosts"),
    (
        lambda client, query: client.async_iter_purchase_order_global_costs(query),
        "/purchaseorderglobalcosts",
    ),
    (lambda client, query: client.async_iter_crew(query), "/crew"),
    (
        lambda client, query: client.async_iter_appointments_of_crew(33, query),
        "/crew/33/appointments",
    ),
    (
        lambda client, query: client.async_iter_crew_availability_of_crew(33, query),
        "/crew/33/crewavailability",
    ),
    (lambda client, query: client.async_iter_crew_rates_of_crew(33, query), "/crew/33/crewrates"),
    (
        lambda client, query: client.async_iter_invitations_of_crew(33, query),
        "/crew/33/invitations",
    ),
    (lambda client, query: client.async_iter_crew_availability(query), "/crewavailability"),
    (lambda client, query: client.async_iter_crew_rates(query), "/crewrates"),
    (lambda client, query: client.async_iter_invitations(query), "/invitations"),
    (lambda client, query: client.async_iter_appointments(query), "/appointments"),
    (
        lambda client, query: client.async_iter_appointment_crew_of_appointment(28, query),
        "/appointments/28/appointmentcrew",
    ),
    (lambda client, query: client.async_iter_appointment_crew(query), "/appointmentcrew"),
    (lambda client, query: client.async_iter_time_registrations(query), "/timeregistration"),
    (
        lambda client, query: client.async_iter_time_registration_activities_of_time_registration(
            20, query
        ),
        "/timeregistration/20/timeregistrationactivities",
    ),
    (
        lambda client, query: client.async_iter_time_registration_activities(query),
        "/timeregistrationactivities",
    ),
    (lambda client, query: client.async_iter_leave_requests(query), "/leaverequest"),
    (
        lambda client, query: client.async_iter_time_registrations_of_leave_request(1, query),
        "/leaverequest/1/timeregistration",
    ),
    (lambda client, query: client.async_iter_leave_mutations(query), "/leavemutation"),
    (lambda client, query: client.async_iter_leave_types(query), "/leavetypes"),
    (lambda client, query: client.async_iter_contacts(query), "/contacts"),
    (lambda client, query: client.async_iter_contact_persons(query), "/contactpersons"),
    (lambda client, query: client.async_iter_rates(query), "/rates"),
    (lambda client, query: client.async_iter_rate_factors(query), "/ratefactors"),
    (
        lambda client, query: client.async_iter_rate_factors_of_rate(1, query),
        "/rates/1/ratefactors",
    ),
    (lambda client, query: client.async_iter_factors(query), "/factors"),
    (
        lambda client, query: client.async_iter_factors_of_factor_group(1, query),
        "/factorgroups/1/factors",
    ),
    (
        lambda client, query: client.async_iter_factor_groups(query),
        "/factorgroups",
    ),
    (
        lambda client, query: client.async_iter_contact_persons_of_contact(3609, query),
        "/contacts/3609/contactpersons",
    ),
    (lambda client, query: client.async_iter_tasks(query), "/tasks"),
    (lambda client, query: client.async_iter_subtasks(query), "/subtasks"),
    (lambda client, query: client.async_iter_task_assignments(query), "/taskassignments"),
    (lambda client, query: client.async_iter_task_statuses(query), "/taskstatuses"),
    (lambda client, query: client.async_iter_files(query), "/files"),
    (lambda client, query: client.async_iter_file_folders(query), "/file_folders"),
    (
        lambda client, query: client.async_iter_subtasks_of_task(95, query),
        "/tasks/95/subtasks",
    ),
    (
        lambda client, query: client.async_iter_task_assignments_of_task(95, query),
        "/tasks/95/taskassignments",
    ),
    (
        lambda client, query: client.async_iter_files_of_task(95, query),
        "/tasks/95/files",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_task(95, query),
        "/tasks/95/file_folders",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_contact_person(8, query),
        "/contactpersons/8/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_contact(3609, query),
        "/contacts/3609/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_crew(33, query),
        "/crew/33/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_equipment(12, query),
        "/equipment/12/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_invoice(1, query),
        "/invoices/1/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_project(80, query),
        "/projects/80/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_purchase_order(1, query),
        "/purchaseorders/1/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_quote(1, query),
        "/quotes/1/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_repair(220, query),
        "/repairs/220/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_serial_number(41, query),
        "/serialnumbers/41/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_subrental(17, query),
        "/subrentals/17/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_vehicle(7, query),
        "/vehicles/7/tasks",
    ),
    (
        lambda client, query: client.async_iter_tasks_of_supplier(1, query),
        "/suppliers/1/tasks",
    ),
    (
        lambda client, query: client.async_iter_files_of_contact_person(8, query),
        "/contactpersons/8/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_contact(3609, query),
        "/contacts/3609/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_crew(33, query),
        "/crew/33/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_equipment(12, query),
        "/equipment/12/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_invoice(1, query),
        "/invoices/1/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_project(80, query),
        "/projects/80/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_purchase_order(1, query),
        "/purchaseorders/1/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_quote(1, query),
        "/quotes/1/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_repair(220, query),
        "/repairs/220/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_serial_number(41, query),
        "/serialnumbers/41/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_subrental(17, query),
        "/subrentals/17/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_time_registration(20, query),
        "/timeregistration/20/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_vehicle(7, query),
        "/vehicles/7/files",
    ),
    (
        lambda client, query: client.async_iter_files_of_supplier(1, query),
        "/suppliers/1/files",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_contact_person(8, query),
        "/contactpersons/8/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_contact(3609, query),
        "/contacts/3609/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_crew(33, query),
        "/crew/33/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_equipment(12, query),
        "/equipment/12/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_project(80, query),
        "/projects/80/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_purchase_order(1, query),
        "/purchaseorders/1/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_repair(220, query),
        "/repairs/220/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_serial_number(41, query),
        "/serialnumbers/41/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_subproject(501, query),
        "/subprojects/501/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_subrental(17, query),
        "/subrentals/17/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_supplier(1, query),
        "/suppliers/1/file_folders",
    ),
    (
        lambda client, query: client.async_iter_file_folders_of_vehicle(7, query),
        "/vehicles/7/file_folders",
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


SAMPLE_MOMENT = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
SAMPLE_LINK = RentmanLink(path="/crew/1")


def minimal_payload(payload_cls: type) -> Any:
    """Build one payload of one class with a sample value for every required field."""
    samples: dict[Any, Any] = {
        str: "sample",
        int: 1,
        float: 1.0,
        bool: True,
        datetime: SAMPLE_MOMENT,
        RentmanLink: SAMPLE_LINK,
    }
    kwargs: dict[str, Any] = {}
    for field in dataclasses.fields(payload_cls):
        if field.default is not dataclasses.MISSING:
            continue
        base = field.type
        if isinstance(base, str):
            continue
        for candidate in getattr(base, "__args__", ()):
            if candidate is not type(None):
                base = candidate
        if isinstance(base, type):
            kwargs[field.name] = samples[base]
    return payload_cls(**kwargs)


def write_case(endpoint: Any) -> tuple[str, tuple[Any, ...], str, str]:
    """Derive one facade call, its arguments, its path, and its HTTP method."""
    name = f"async_{endpoint.name}"
    method = getattr(RentmanClient, name, None)
    assert method is not None, f"the facade is missing {name}"
    if endpoint.method == "DELETE":
        return name, (1,), endpoint.path(DeleteArgs(item_id=1)), "DELETE"
    if endpoint.method == "PUT":
        payload_cls = inspect.signature(method).parameters["payload"].annotation
        update = UpdateArgs(item_id=1, payload=None)
        return name, (1, minimal_payload(payload_cls)), endpoint.path(update), "PUT"
    payload_cls = inspect.signature(method).parameters["payload"].annotation
    if "_of_" in endpoint.name:
        linked = LinkedCreateArgs(parent_id=1, payload=None)
        return name, (1, minimal_payload(payload_cls)), endpoint.path(linked), "POST"
    return name, (minimal_payload(payload_cls),), endpoint.path(CreateArgs(payload=None)), "POST"


WRITE_CASES: tuple[tuple[str, tuple[Any, ...], str, str], ...] = tuple(
    write_case(endpoint) for endpoint in CATALOG if endpoint.method != "GET"
)


async def test_write_methods_hit_their_paths() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            for _, _, path, http_method in WRITE_CASES:
                if http_method == "DELETE":
                    m.delete(api_url(path))
                elif http_method == "POST":
                    m.post(api_url(path), payload=EMPTY_ITEM)
                else:
                    m.put(api_url(path), payload=EMPTY_ITEM)
            client = make_client(session)
            for method_name, args, path, http_method in WRITE_CASES:
                result = await getattr(client, method_name)(*args)
                if http_method == "DELETE":
                    assert result is None, path
                else:
                    assert result is not None, path


async def test_create_task_pins_the_wire_body() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.post(api_url("/tasks"), payload=EMPTY_ITEM)
            client = make_client(session)
            await client.async_create_task(
                TaskPayload(
                    color="#ffffff",
                    name="sample",
                    deadline=SAMPLE_MOMENT,
                    status=RentmanLink(path="/taskstatuses/3"),
                    custom={"custom_1": "value"},
                )
            )
            call = recorded_call(m.requests, "POST", f"{BASE_URL}/tasks")
    assert call.kwargs["json"] == {
        "color": "#ffffff",
        "name": "sample",
        "deadline": "2026-10-02T12:00:00+00:00",
        "status": "/taskstatuses/3",
        "custom": {"custom_1": "value"},
    }


async def test_update_task_sends_only_set_fields() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.put(api_url("/tasks/1"), payload=EMPTY_ITEM)
            client = make_client(session)
            await client.async_update_task(1, TaskPayload(color="#ffffff", name="renamed"))
            call = recorded_call(m.requests, "PUT", f"{BASE_URL}/tasks/1")
    assert call.kwargs["json"] == {"color": "#ffffff", "name": "renamed"}


async def test_create_maps_400_to_validation_error() -> None:
    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.post(api_url("/tasks"), status=400, body="color is required")
            client = make_client(session)
            with pytest.raises(RentmanValidationError, match="color is required") as info:
                await client.async_create_task(TaskPayload(color="#ffffff"))
    assert info.value.status == 400


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
