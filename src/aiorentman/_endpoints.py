"""The frozen endpoint catalog: one row per wire contract."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .models import (
    Accessory,
    ActualContent,
    Alternative,
    Appointment,
    AppointmentCrew,
    Contact,
    ContactPerson,
    Contract,
    Crew,
    CrewAvailability,
    CrewRate,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
    ExtraInputField,
    Factor,
    FactorGroup,
    File,
    FileFolder,
    Folder,
    Invitation,
    Invoice,
    InvoiceLine,
    LeaveMutation,
    LeaveRequest,
    LeaveType,
    LedgerCode,
    Payment,
    Project,
    ProjectCost,
    ProjectCrew,
    ProjectEquipment,
    ProjectEquipmentGroup,
    ProjectFunction,
    ProjectFunctionGroup,
    ProjectRequest,
    ProjectRequestEquipment,
    ProjectStatus,
    ProjectType,
    ProjectVehicle,
    PurchaseOrder,
    PurchaseOrderCost,
    PurchaseOrderGlobalCost,
    Quote,
    Rate,
    RateFactor,
    RentmanPage,
    Repair,
    SerialNumber,
    Status,
    StockLocation,
    StockMovement,
    Subproject,
    Subrental,
    SubrentalEquipment,
    SubrentalEquipmentGroup,
    Subtask,
    Supplier,
    Task,
    TaskAssignment,
    TaskStatus,
    TaxClass,
    TimeRegistration,
    TimeRegistrationActivity,
    Vehicle,
    WarehouseStatus,
)
from .parsers import (
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
    parse_envelope_item,
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
from .query import Query


@dataclass(frozen=True, slots=True)
class CollectionArgs:
    """One top-level collection page with its query."""

    query: Query | None = None


@dataclass(frozen=True, slots=True)
class ItemArgs:
    """One item, addressed by its numeric id."""

    item_id: int

    def __post_init__(self) -> None:
        if self.item_id < 1:
            msg = "item_id must be a positive id"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ParentCollectionArgs:
    """One linked collection page: the parent id and its query."""

    parent_id: int
    query: Query | None = None

    def __post_init__(self) -> None:
        if self.parent_id < 1:
            msg = "parent_id must be a positive id"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Endpoint[ArgsT, ModelT]:
    """One wire contract: method, path, params, the parse step, and schema."""

    name: str
    method: str
    path: Callable[[ArgsT], str]
    parse: Callable[[Any, ArgsT], ModelT]
    params: Callable[[ArgsT], dict[str, str]]
    response_schema: str


def _collection_params(args: CollectionArgs) -> dict[str, str]:
    return {} if args.query is None else args.query.params()


def _linked_collection_params(args: ParentCollectionArgs) -> dict[str, str]:
    return {} if args.query is None else args.query.params()


ACTUAL_CONTENT: Endpoint[CollectionArgs, RentmanPage[ActualContent]] = Endpoint(
    name="actual_content",
    method="GET",
    path=lambda _args: "/actualcontent",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_actual_content),
    response_schema="ActualContentResponse",
)

ACTUAL_CONTENT_ITEM: Endpoint[ItemArgs, ActualContent | None] = Endpoint(
    name="actual_content_item",
    method="GET",
    path=lambda args: f"/actualcontent/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_actual_content),
    response_schema="ActualContentResponse",
)

ACTUAL_CONTENT_OF_SERIAL_NUMBER: Endpoint[ParentCollectionArgs, RentmanPage[ActualContent]] = (
    Endpoint(
        name="actual_content_of_serial_number",
        method="GET",
        path=lambda args: f"/serialnumbers/{args.parent_id}/actualcontent",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_actual_content),
        response_schema="ActualContentResponse",
    )
)

EQUIPMENT: Endpoint[CollectionArgs, RentmanPage[Equipment]] = Endpoint(
    name="equipment",
    method="GET",
    path=lambda _args: "/equipment",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_equipment),
    response_schema="EquipmentResponse",
)

EQUIPMENT_ITEM: Endpoint[ItemArgs, Equipment | None] = Endpoint(
    name="equipment_item",
    method="GET",
    path=lambda args: f"/equipment/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_equipment),
    response_schema="EquipmentResponse",
)

EQUIPMENT_SET_CONTENT_OF_EQUIPMENT: Endpoint[
    ParentCollectionArgs, RentmanPage[EquipmentSetContent]
] = Endpoint(
    name="equipment_set_content_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/equipmentsetscontent",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_equipment_set_content),
    response_schema="EquipmentSetContentResponse",
)

REPAIRS_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[Repair]] = Endpoint(
    name="repairs_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/repairs",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_repair),
    response_schema="RepairResponse",
)

SERIAL_NUMBERS_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[SerialNumber]] = Endpoint(
    name="serial_numbers_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/serialnumbers",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_serial_number),
    response_schema="SerialNumberResponse",
)

STOCK_MOVEMENTS_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[StockMovement]] = Endpoint(
    name="stock_movements_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/stockmovements",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_stock_movement),
    response_schema="StockMovementResponse",
)

SERIAL_NUMBERS: Endpoint[CollectionArgs, RentmanPage[SerialNumber]] = Endpoint(
    name="serial_numbers",
    method="GET",
    path=lambda _args: "/serialnumbers",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_serial_number),
    response_schema="SerialNumberResponse",
)

SERIAL_NUMBERS_ITEM: Endpoint[ItemArgs, SerialNumber | None] = Endpoint(
    name="serial_numbers_item",
    method="GET",
    path=lambda args: f"/serialnumbers/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_serial_number),
    response_schema="SerialNumberResponse",
)

EQUIPMENT_ASSIGNED_SERIALS: Endpoint[CollectionArgs, RentmanPage[EquipmentAssignedSerial]] = (
    Endpoint(
        name="equipment_assigned_serials",
        method="GET",
        path=lambda _args: "/equipmentassignedserials",
        params=_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_equipment_assigned_serial),
        response_schema="EquipmentAssignedSerialsResponse",
    )
)

EQUIPMENT_ASSIGNED_SERIALS_ITEM: Endpoint[ItemArgs, EquipmentAssignedSerial | None] = Endpoint(
    name="equipment_assigned_serials_item",
    method="GET",
    path=lambda args: f"/equipmentassignedserials/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_equipment_assigned_serial),
    response_schema="EquipmentAssignedSerialsResponse",
)

EQUIPMENT_ASSIGNED_SERIALS_OF_SERIAL_NUMBER: Endpoint[
    ParentCollectionArgs, RentmanPage[EquipmentAssignedSerial]
] = Endpoint(
    name="equipment_assigned_serials_of_serial_number",
    method="GET",
    path=lambda args: f"/serialnumbers/{args.parent_id}/equipmentassignedserials",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_equipment_assigned_serial),
    response_schema="EquipmentAssignedSerialsResponse",
)

EQUIPMENT_SET_CONTENT: Endpoint[CollectionArgs, RentmanPage[EquipmentSetContent]] = Endpoint(
    name="equipment_set_content",
    method="GET",
    path=lambda _args: "/equipmentsetscontent",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_equipment_set_content),
    response_schema="EquipmentSetContentResponse",
)

EQUIPMENT_SET_CONTENT_ITEM: Endpoint[ItemArgs, EquipmentSetContent | None] = Endpoint(
    name="equipment_set_content_item",
    method="GET",
    path=lambda args: f"/equipmentsetscontent/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_equipment_set_content),
    response_schema="EquipmentSetContentResponse",
)

FOLDERS: Endpoint[CollectionArgs, RentmanPage[Folder]] = Endpoint(
    name="folders",
    method="GET",
    path=lambda _args: "/folders",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_folder),
    response_schema="FolderResponse",
)

FOLDERS_ITEM: Endpoint[ItemArgs, Folder | None] = Endpoint(
    name="folders_item",
    method="GET",
    path=lambda args: f"/folders/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_folder),
    response_schema="FolderResponse",
)

STOCK_LOCATIONS: Endpoint[CollectionArgs, RentmanPage[StockLocation]] = Endpoint(
    name="stock_locations",
    method="GET",
    path=lambda _args: "/stocklocations",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_stock_location),
    response_schema="StockLocationResponse",
)

STOCK_LOCATIONS_ITEM: Endpoint[ItemArgs, StockLocation | None] = Endpoint(
    name="stock_locations_item",
    method="GET",
    path=lambda args: f"/stocklocations/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_stock_location),
    response_schema="StockLocationResponse",
)

WAREHOUSE_STATUSES: Endpoint[CollectionArgs, RentmanPage[WarehouseStatus]] = Endpoint(
    name="warehouse_statuses",
    method="GET",
    path=lambda _args: "/warehousestatuses",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_warehouse_status),
    response_schema="WarehouseStatusResponse",
)

WAREHOUSE_STATUSES_ITEM: Endpoint[ItemArgs, WarehouseStatus | None] = Endpoint(
    name="warehouse_statuses_item",
    method="GET",
    path=lambda args: f"/warehousestatuses/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_warehouse_status),
    response_schema="WarehouseStatusResponse",
)

STATUSES: Endpoint[CollectionArgs, RentmanPage[Status]] = Endpoint(
    name="statuses",
    method="GET",
    path=lambda _args: "/statuses",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_status),
    response_schema="StatusResponse",
)

STATUSES_ITEM: Endpoint[ItemArgs, Status | None] = Endpoint(
    name="statuses_item",
    method="GET",
    path=lambda args: f"/statuses/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_status),
    response_schema="StatusResponse",
)

STOCK_MOVEMENTS: Endpoint[CollectionArgs, RentmanPage[StockMovement]] = Endpoint(
    name="stock_movements",
    method="GET",
    path=lambda _args: "/stockmovements",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_stock_movement),
    response_schema="StockMovementResponse",
)

STOCK_MOVEMENTS_ITEM: Endpoint[ItemArgs, StockMovement | None] = Endpoint(
    name="stock_movements_item",
    method="GET",
    path=lambda args: f"/stockmovements/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_stock_movement),
    response_schema="StockMovementResponse",
)

REPAIRS: Endpoint[CollectionArgs, RentmanPage[Repair]] = Endpoint(
    name="repairs",
    method="GET",
    path=lambda _args: "/repairs",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_repair),
    response_schema="RepairResponse",
)

REPAIRS_ITEM: Endpoint[ItemArgs, Repair | None] = Endpoint(
    name="repairs_item",
    method="GET",
    path=lambda args: f"/repairs/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_repair),
    response_schema="RepairResponse",
)

PROJECTS: Endpoint[CollectionArgs, RentmanPage[Project]] = Endpoint(
    name="projects",
    method="GET",
    path=lambda _args: "/projects",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project),
    response_schema="ProjectResponse",
)

PROJECTS_ITEM: Endpoint[ItemArgs, Project | None] = Endpoint(
    name="projects_item",
    method="GET",
    path=lambda args: f"/projects/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project),
    response_schema="ProjectResponse",
)

PROJECT_EQUIPMENT_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectEquipment]] = (
    Endpoint(
        name="project_equipment_of_project",
        method="GET",
        path=lambda args: f"/projects/{args.parent_id}/projectequipment",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_project_equipment),
        response_schema="ProjectEquipmentResponse",
    )
)

SUBPROJECTS_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[Subproject]] = Endpoint(
    name="subprojects_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/subprojects",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subproject),
    response_schema="SubprojectResponse",
)

SUBPROJECTS: Endpoint[CollectionArgs, RentmanPage[Subproject]] = Endpoint(
    name="subprojects",
    method="GET",
    path=lambda _args: "/subprojects",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subproject),
    response_schema="SubprojectResponse",
)

SUBPROJECTS_ITEM: Endpoint[ItemArgs, Subproject | None] = Endpoint(
    name="subprojects_item",
    method="GET",
    path=lambda args: f"/subprojects/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_subproject),
    response_schema="SubprojectResponse",
)

PROJECT_EQUIPMENT_OF_SUBPROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectEquipment]] = (
    Endpoint(
        name="project_equipment_of_subproject",
        method="GET",
        path=lambda args: f"/subprojects/{args.parent_id}/projectequipment",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_project_equipment),
        response_schema="ProjectEquipmentResponse",
    )
)

PROJECT_EQUIPMENT: Endpoint[CollectionArgs, RentmanPage[ProjectEquipment]] = Endpoint(
    name="project_equipment",
    method="GET",
    path=lambda _args: "/projectequipment",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_equipment),
    response_schema="ProjectEquipmentResponse",
)

PROJECT_EQUIPMENT_ITEM: Endpoint[ItemArgs, ProjectEquipment | None] = Endpoint(
    name="project_equipment_item",
    method="GET",
    path=lambda args: f"/projectequipment/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_equipment),
    response_schema="ProjectEquipmentResponse",
)

ACCESSORIES: Endpoint[CollectionArgs, RentmanPage[Accessory]] = Endpoint(
    name="accessories",
    method="GET",
    path=lambda _args: "/accessories",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_accessory),
    response_schema="AccessoryResponse",
)

ACCESSORIES_ITEM: Endpoint[ItemArgs, Accessory | None] = Endpoint(
    name="accessories_item",
    method="GET",
    path=lambda args: f"/accessories/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_accessory),
    response_schema="AccessoryResponse",
)

ACCESSORIES_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[Accessory]] = Endpoint(
    name="accessories_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/accessories",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_accessory),
    response_schema="AccessoryResponse",
)

ALTERNATIVES: Endpoint[CollectionArgs, RentmanPage[Alternative]] = Endpoint(
    name="alternatives",
    method="GET",
    path=lambda _args: "/alternatives",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_alternative),
    response_schema="AlternativeResponse",
)

ALTERNATIVES_ITEM: Endpoint[ItemArgs, Alternative | None] = Endpoint(
    name="alternatives_item",
    method="GET",
    path=lambda args: f"/alternatives/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_alternative),
    response_schema="AlternativeResponse",
)

ALTERNATIVES_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[Alternative]] = Endpoint(
    name="alternatives_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/alternatives",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_alternative),
    response_schema="AlternativeResponse",
)

SUPPLIERS: Endpoint[CollectionArgs, RentmanPage[Supplier]] = Endpoint(
    name="suppliers",
    method="GET",
    path=lambda _args: "/suppliers",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_supplier),
    response_schema="SupplierResponse",
)

SUPPLIERS_ITEM: Endpoint[ItemArgs, Supplier | None] = Endpoint(
    name="suppliers_item",
    method="GET",
    path=lambda args: f"/suppliers/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_supplier),
    response_schema="SupplierResponse",
)

SUPPLIERS_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[Supplier]] = Endpoint(
    name="suppliers_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/suppliers",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_supplier),
    response_schema="SupplierResponse",
)

VEHICLES: Endpoint[CollectionArgs, RentmanPage[Vehicle]] = Endpoint(
    name="vehicles",
    method="GET",
    path=lambda _args: "/vehicles",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_vehicle),
    response_schema="VehicleResponse",
)

VEHICLES_ITEM: Endpoint[ItemArgs, Vehicle | None] = Endpoint(
    name="vehicles_item",
    method="GET",
    path=lambda args: f"/vehicles/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_vehicle),
    response_schema="VehicleResponse",
)

VEHICLES_OF_STOCK_LOCATION: Endpoint[ParentCollectionArgs, RentmanPage[Vehicle]] = Endpoint(
    name="vehicles_of_stock_location",
    method="GET",
    path=lambda args: f"/stocklocations/{args.parent_id}/vehicles",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_vehicle),
    response_schema="VehicleResponse",
)

EXTRA_INPUT_FIELDS: Endpoint[CollectionArgs, RentmanPage[ExtraInputField]] = Endpoint(
    name="extra_input_fields",
    method="GET",
    path=lambda _args: "/extrainputfields",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_extra_input_field),
    response_schema="ExtraInputFieldResponse",
)

EXTRA_INPUT_FIELDS_ITEM: Endpoint[ItemArgs, ExtraInputField | None] = Endpoint(
    name="extra_input_fields_item",
    method="GET",
    path=lambda args: f"/extrainputfields/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_extra_input_field),
    response_schema="ExtraInputFieldResponse",
)

PROJECT_STATUSES: Endpoint[CollectionArgs, RentmanPage[ProjectStatus]] = Endpoint(
    name="project_statuses",
    method="GET",
    path=lambda _args: "/projectstatuses",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_status),
    response_schema="ProjectStatusResponse",
)

PROJECT_STATUSES_ITEM: Endpoint[ItemArgs, ProjectStatus | None] = Endpoint(
    name="project_statuses_item",
    method="GET",
    path=lambda args: f"/projectstatuses/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_status),
    response_schema="ProjectStatusResponse",
)

PROJECT_TYPES: Endpoint[CollectionArgs, RentmanPage[ProjectType]] = Endpoint(
    name="project_types",
    method="GET",
    path=lambda _args: "/projecttypes",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_type),
    response_schema="ProjectTypeResponse",
)

PROJECT_TYPES_ITEM: Endpoint[ItemArgs, ProjectType | None] = Endpoint(
    name="project_types_item",
    method="GET",
    path=lambda args: f"/projecttypes/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_type),
    response_schema="ProjectTypeResponse",
)

PROJECT_FUNCTION_GROUPS: Endpoint[CollectionArgs, RentmanPage[ProjectFunctionGroup]] = Endpoint(
    name="project_function_groups",
    method="GET",
    path=lambda _args: "/projectfunctiongroups",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_function_group),
    response_schema="ProjectFunctionGroupResponse",
)

PROJECT_FUNCTION_GROUPS_ITEM: Endpoint[ItemArgs, ProjectFunctionGroup | None] = Endpoint(
    name="project_function_groups_item",
    method="GET",
    path=lambda args: f"/projectfunctiongroups/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_function_group),
    response_schema="ProjectFunctionGroupResponse",
)

PROJECT_FUNCTION_GROUPS_OF_PROJECT: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectFunctionGroup]
] = Endpoint(
    name="project_function_groups_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/projectfunctiongroups",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_function_group),
    response_schema="ProjectFunctionGroupResponse",
)

PROJECT_FUNCTION_GROUPS_OF_SUBPROJECT: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectFunctionGroup]
] = Endpoint(
    name="project_function_groups_of_subproject",
    method="GET",
    path=lambda args: f"/subprojects/{args.parent_id}/projectfunctiongroups",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_function_group),
    response_schema="ProjectFunctionGroupResponse",
)

PROJECT_FUNCTIONS: Endpoint[CollectionArgs, RentmanPage[ProjectFunction]] = Endpoint(
    name="project_functions",
    method="GET",
    path=lambda _args: "/projectfunctions",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_function),
    response_schema="ProjectFunctionResponse",
)

PROJECT_FUNCTIONS_ITEM: Endpoint[ItemArgs, ProjectFunction | None] = Endpoint(
    name="project_functions_item",
    method="GET",
    path=lambda args: f"/projectfunctions/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_function),
    response_schema="ProjectFunctionResponse",
)

PROJECT_FUNCTIONS_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectFunction]] = (
    Endpoint(
        name="project_functions_of_project",
        method="GET",
        path=lambda args: f"/projects/{args.parent_id}/projectfunctions",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_project_function),
        response_schema="ProjectFunctionResponse",
    )
)

PROJECT_FUNCTIONS_OF_PROJECT_FUNCTION_GROUP: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectFunction]
] = Endpoint(
    name="project_functions_of_project_function_group",
    method="GET",
    path=lambda args: f"/projectfunctiongroups/{args.parent_id}/projectfunctions",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_function),
    response_schema="ProjectFunctionResponse",
)

PROJECT_CREW: Endpoint[CollectionArgs, RentmanPage[ProjectCrew]] = Endpoint(
    name="project_crew",
    method="GET",
    path=lambda _args: "/projectcrew",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_crew),
    response_schema="ProjectCrewResponse",
)

PROJECT_CREW_ITEM: Endpoint[ItemArgs, ProjectCrew | None] = Endpoint(
    name="project_crew_item",
    method="GET",
    path=lambda args: f"/projectcrew/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_crew),
    response_schema="ProjectCrewResponse",
)

PROJECT_CREW_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectCrew]] = Endpoint(
    name="project_crew_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/projectcrew",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_crew),
    response_schema="ProjectCrewResponse",
)

PROJECT_CREW_OF_SUBPROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectCrew]] = Endpoint(
    name="project_crew_of_subproject",
    method="GET",
    path=lambda args: f"/subprojects/{args.parent_id}/projectcrew",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_crew),
    response_schema="ProjectCrewResponse",
)

PROJECT_CREW_OF_PROJECT_FUNCTION: Endpoint[ParentCollectionArgs, RentmanPage[ProjectCrew]] = (
    Endpoint(
        name="project_crew_of_project_function",
        method="GET",
        path=lambda args: f"/projectfunctions/{args.parent_id}/projectcrew",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_project_crew),
        response_schema="ProjectCrewResponse",
    )
)

PROJECT_VEHICLES: Endpoint[CollectionArgs, RentmanPage[ProjectVehicle]] = Endpoint(
    name="project_vehicles",
    method="GET",
    path=lambda _args: "/projectvehicles",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_vehicle),
    response_schema="ProjectVehicleResponse",
)

PROJECT_VEHICLES_ITEM: Endpoint[ItemArgs, ProjectVehicle | None] = Endpoint(
    name="project_vehicles_item",
    method="GET",
    path=lambda args: f"/projectvehicles/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_vehicle),
    response_schema="ProjectVehicleResponse",
)

PROJECT_VEHICLES_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectVehicle]] = Endpoint(
    name="project_vehicles_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/projectvehicles",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_vehicle),
    response_schema="ProjectVehicleResponse",
)

PROJECT_VEHICLES_OF_SUBPROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectVehicle]] = (
    Endpoint(
        name="project_vehicles_of_subproject",
        method="GET",
        path=lambda args: f"/subprojects/{args.parent_id}/projectvehicles",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_project_vehicle),
        response_schema="ProjectVehicleResponse",
    )
)

PROJECT_VEHICLES_OF_PROJECT_FUNCTION: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectVehicle]
] = Endpoint(
    name="project_vehicles_of_project_function",
    method="GET",
    path=lambda args: f"/projectfunctions/{args.parent_id}/projectvehicles",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_vehicle),
    response_schema="ProjectVehicleResponse",
)

PROJECT_EQUIPMENT_GROUPS: Endpoint[CollectionArgs, RentmanPage[ProjectEquipmentGroup]] = Endpoint(
    name="project_equipment_groups",
    method="GET",
    path=lambda _args: "/projectequipmentgroup",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_equipment_group),
    response_schema="ProjectEquipmentGroupResponse",
)

PROJECT_EQUIPMENT_GROUPS_ITEM: Endpoint[ItemArgs, ProjectEquipmentGroup | None] = Endpoint(
    name="project_equipment_groups_item",
    method="GET",
    path=lambda args: f"/projectequipmentgroup/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_equipment_group),
    response_schema="ProjectEquipmentGroupResponse",
)

PROJECT_EQUIPMENT_GROUPS_OF_PROJECT: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectEquipmentGroup]
] = Endpoint(
    name="project_equipment_groups_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/projectequipmentgroup",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_equipment_group),
    response_schema="ProjectEquipmentGroupResponse",
)

PROJECT_EQUIPMENT_GROUPS_OF_SUBPROJECT: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectEquipmentGroup]
] = Endpoint(
    name="project_equipment_groups_of_subproject",
    method="GET",
    path=lambda args: f"/subprojects/{args.parent_id}/projectequipmentgroup",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_equipment_group),
    response_schema="ProjectEquipmentGroupResponse",
)

PROJECT_EQUIPMENT_OF_PROJECT_EQUIPMENT_GROUP: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectEquipment]
] = Endpoint(
    name="project_equipment_of_project_equipment_group",
    method="GET",
    path=lambda args: f"/projectequipmentgroup/{args.parent_id}/projectequipment",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_equipment),
    response_schema="ProjectEquipmentResponse",
)

PROJECT_COSTS: Endpoint[CollectionArgs, RentmanPage[ProjectCost]] = Endpoint(
    name="project_costs",
    method="GET",
    path=lambda _args: "/costs",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_cost),
    response_schema="ProjectCostResponse",
)

PROJECT_COSTS_ITEM: Endpoint[ItemArgs, ProjectCost | None] = Endpoint(
    name="project_costs_item",
    method="GET",
    path=lambda args: f"/costs/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_cost),
    response_schema="ProjectCostResponse",
)

PROJECT_COSTS_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[ProjectCost]] = Endpoint(
    name="project_costs_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/costs",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_cost),
    response_schema="ProjectCostResponse",
)

PROJECT_REQUESTS: Endpoint[CollectionArgs, RentmanPage[ProjectRequest]] = Endpoint(
    name="project_requests",
    method="GET",
    path=lambda _args: "/projectrequests",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_request),
    response_schema="ProjectRequestResponse",
)

PROJECT_REQUESTS_ITEM: Endpoint[ItemArgs, ProjectRequest | None] = Endpoint(
    name="project_requests_item",
    method="GET",
    path=lambda args: f"/projectrequests/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_request),
    response_schema="ProjectRequestResponse",
)

PROJECT_REQUEST_EQUIPMENT: Endpoint[CollectionArgs, RentmanPage[ProjectRequestEquipment]] = (
    Endpoint(
        name="project_request_equipment",
        method="GET",
        path=lambda _args: "/projectrequestequipment",
        params=_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_project_request_equipment),
        response_schema="ProjectRequestEquipmentResponse",
    )
)

PROJECT_REQUEST_EQUIPMENT_ITEM: Endpoint[ItemArgs, ProjectRequestEquipment | None] = Endpoint(
    name="project_request_equipment_item",
    method="GET",
    path=lambda args: f"/projectrequestequipment/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_project_request_equipment),
    response_schema="ProjectRequestEquipmentResponse",
)

PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST: Endpoint[
    ParentCollectionArgs, RentmanPage[ProjectRequestEquipment]
] = Endpoint(
    name="project_request_equipment_of_project_request",
    method="GET",
    path=lambda args: f"/projectrequests/{args.parent_id}/projectrequestequipment",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_project_request_equipment),
    response_schema="ProjectRequestEquipmentResponse",
)

QUOTES: Endpoint[CollectionArgs, RentmanPage[Quote]] = Endpoint(
    name="quotes",
    method="GET",
    path=lambda _args: "/quotes",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_quote),
    response_schema="QuotationResponse",
)

QUOTES_ITEM: Endpoint[ItemArgs, Quote | None] = Endpoint(
    name="quotes_item",
    method="GET",
    path=lambda args: f"/quotes/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_quote),
    response_schema="QuotationResponse",
)

QUOTES_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[Quote]] = Endpoint(
    name="quotes_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/quotes",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_quote),
    response_schema="QuotationResponse",
)

INVOICE_LINES_OF_QUOTE: Endpoint[ParentCollectionArgs, RentmanPage[InvoiceLine]] = Endpoint(
    name="invoice_lines_of_quote",
    method="GET",
    path=lambda args: f"/quotes/{args.parent_id}/invoicelines",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_invoice_line),
    response_schema="InvoiceLineResponse",
)

CONTRACTS: Endpoint[CollectionArgs, RentmanPage[Contract]] = Endpoint(
    name="contracts",
    method="GET",
    path=lambda _args: "/contracts",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_contract),
    response_schema="ContractResponse",
)

CONTRACTS_ITEM: Endpoint[ItemArgs, Contract | None] = Endpoint(
    name="contracts_item",
    method="GET",
    path=lambda args: f"/contracts/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_contract),
    response_schema="ContractResponse",
)

CONTRACTS_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[Contract]] = Endpoint(
    name="contracts_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/contracts",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_contract),
    response_schema="ContractResponse",
)

INVOICES: Endpoint[CollectionArgs, RentmanPage[Invoice]] = Endpoint(
    name="invoices",
    method="GET",
    path=lambda _args: "/invoices",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_invoice),
    response_schema="FactuurResponse",
)

INVOICES_ITEM: Endpoint[ItemArgs, Invoice | None] = Endpoint(
    name="invoices_item",
    method="GET",
    path=lambda args: f"/invoices/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_invoice),
    response_schema="FactuurResponse",
)

INVOICE_LINES_OF_INVOICE: Endpoint[ParentCollectionArgs, RentmanPage[InvoiceLine]] = Endpoint(
    name="invoice_lines_of_invoice",
    method="GET",
    path=lambda args: f"/invoices/{args.parent_id}/invoicelines",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_invoice_line),
    response_schema="InvoiceLineResponse",
)

PAYMENTS_OF_INVOICE: Endpoint[ParentCollectionArgs, RentmanPage[Payment]] = Endpoint(
    name="payments_of_invoice",
    method="GET",
    path=lambda args: f"/invoices/{args.parent_id}/payments",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_payment),
    response_schema="PaymentResponse",
)

INVOICE_LINES: Endpoint[CollectionArgs, RentmanPage[InvoiceLine]] = Endpoint(
    name="invoice_lines",
    method="GET",
    path=lambda _args: "/invoicelines",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_invoice_line),
    response_schema="InvoiceLineResponse",
)

INVOICE_LINES_ITEM: Endpoint[ItemArgs, InvoiceLine | None] = Endpoint(
    name="invoice_lines_item",
    method="GET",
    path=lambda args: f"/invoicelines/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_invoice_line),
    response_schema="InvoiceLineResponse",
)

PAYMENTS: Endpoint[CollectionArgs, RentmanPage[Payment]] = Endpoint(
    name="payments",
    method="GET",
    path=lambda _args: "/payments",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_payment),
    response_schema="PaymentResponse",
)

PAYMENTS_ITEM: Endpoint[ItemArgs, Payment | None] = Endpoint(
    name="payments_item",
    method="GET",
    path=lambda args: f"/payments/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_payment),
    response_schema="PaymentResponse",
)

LEDGER_CODES: Endpoint[CollectionArgs, RentmanPage[LedgerCode]] = Endpoint(
    name="ledger_codes",
    method="GET",
    path=lambda _args: "/ledgercodes",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_ledger_code),
    response_schema="LedgerResponse",
)

LEDGER_CODES_ITEM: Endpoint[ItemArgs, LedgerCode | None] = Endpoint(
    name="ledger_codes_item",
    method="GET",
    path=lambda args: f"/ledgercodes/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_ledger_code),
    response_schema="LedgerResponse",
)

TAX_CLASSES: Endpoint[CollectionArgs, RentmanPage[TaxClass]] = Endpoint(
    name="tax_classes",
    method="GET",
    path=lambda _args: "/taxclasses",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_tax_class),
    response_schema="TaxClassResponse",
)

TAX_CLASSES_ITEM: Endpoint[ItemArgs, TaxClass | None] = Endpoint(
    name="tax_classes_item",
    method="GET",
    path=lambda args: f"/taxclasses/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_tax_class),
    response_schema="TaxClassResponse",
)

SUBRENTALS: Endpoint[CollectionArgs, RentmanPage[Subrental]] = Endpoint(
    name="subrentals",
    method="GET",
    path=lambda _args: "/subrentals",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subrental),
    response_schema="SubrentalResponse",
)

SUBRENTALS_ITEM: Endpoint[ItemArgs, Subrental | None] = Endpoint(
    name="subrentals_item",
    method="GET",
    path=lambda args: f"/subrentals/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_subrental),
    response_schema="SubrentalResponse",
)

SUBRENTAL_EQUIPMENT_OF_SUBRENTAL: Endpoint[
    ParentCollectionArgs, RentmanPage[SubrentalEquipment]
] = Endpoint(
    name="subrental_equipment_of_subrental",
    method="GET",
    path=lambda args: f"/subrentals/{args.parent_id}/subrentalequipment",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subrental_equipment),
    response_schema="SubrentalEquipmentResponse",
)

SUBRENTAL_EQUIPMENT_GROUPS_OF_SUBRENTAL: Endpoint[
    ParentCollectionArgs, RentmanPage[SubrentalEquipmentGroup]
] = Endpoint(
    name="subrental_equipment_groups_of_subrental",
    method="GET",
    path=lambda args: f"/subrentals/{args.parent_id}/subrentalequipmentgroup",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subrental_equipment_group),
    response_schema="SubrentalEquipmentGroupResponse",
)

SUBRENTAL_EQUIPMENT: Endpoint[CollectionArgs, RentmanPage[SubrentalEquipment]] = Endpoint(
    name="subrental_equipment",
    method="GET",
    path=lambda _args: "/subrentalequipment",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subrental_equipment),
    response_schema="SubrentalEquipmentResponse",
)

SUBRENTAL_EQUIPMENT_ITEM: Endpoint[ItemArgs, SubrentalEquipment | None] = Endpoint(
    name="subrental_equipment_item",
    method="GET",
    path=lambda args: f"/subrentalequipment/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_subrental_equipment),
    response_schema="SubrentalEquipmentResponse",
)

SUBRENTAL_EQUIPMENT_OF_SUBRENTAL_EQUIPMENT_GROUP: Endpoint[
    ParentCollectionArgs, RentmanPage[SubrentalEquipment]
] = Endpoint(
    name="subrental_equipment_of_subrental_equipment_group",
    method="GET",
    path=lambda args: f"/subrentalequipmentgroup/{args.parent_id}/subrentalequipment",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subrental_equipment),
    response_schema="SubrentalEquipmentResponse",
)

SUBRENTAL_EQUIPMENT_GROUPS: Endpoint[CollectionArgs, RentmanPage[SubrentalEquipmentGroup]] = (
    Endpoint(
        name="subrental_equipment_groups",
        method="GET",
        path=lambda _args: "/subrentalequipmentgroup",
        params=_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_subrental_equipment_group),
        response_schema="SubrentalEquipmentGroupResponse",
    )
)

SUBRENTAL_EQUIPMENT_GROUPS_ITEM: Endpoint[ItemArgs, SubrentalEquipmentGroup | None] = Endpoint(
    name="subrental_equipment_groups_item",
    method="GET",
    path=lambda args: f"/subrentalequipmentgroup/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_subrental_equipment_group),
    response_schema="SubrentalEquipmentGroupResponse",
)

PURCHASE_ORDERS: Endpoint[CollectionArgs, RentmanPage[PurchaseOrder]] = Endpoint(
    name="purchase_orders",
    method="GET",
    path=lambda _args: "/purchaseorders",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_purchase_order),
    response_schema="PurchaseOrderResponse",
)

PURCHASE_ORDERS_ITEM: Endpoint[ItemArgs, PurchaseOrder | None] = Endpoint(
    name="purchase_orders_item",
    method="GET",
    path=lambda args: f"/purchaseorders/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_purchase_order),
    response_schema="PurchaseOrderResponse",
)

INVOICE_LINES_OF_PURCHASE_ORDER: Endpoint[ParentCollectionArgs, RentmanPage[InvoiceLine]] = (
    Endpoint(
        name="invoice_lines_of_purchase_order",
        method="GET",
        path=lambda args: f"/purchaseorders/{args.parent_id}/invoicelines",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_invoice_line),
        response_schema="InvoiceLineResponse",
    )
)

PURCHASE_ORDER_COSTS_OF_PURCHASE_ORDER: Endpoint[
    ParentCollectionArgs, RentmanPage[PurchaseOrderCost]
] = Endpoint(
    name="purchase_order_costs_of_purchase_order",
    method="GET",
    path=lambda args: f"/purchaseorders/{args.parent_id}/purchaseordercosts",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_purchase_order_cost),
    response_schema="PurchaseOrderCostResponse",
)

PURCHASE_ORDER_GLOBAL_COSTS_OF_PURCHASE_ORDER: Endpoint[
    ParentCollectionArgs, RentmanPage[PurchaseOrderGlobalCost]
] = Endpoint(
    name="purchase_order_global_costs_of_purchase_order",
    method="GET",
    path=lambda args: f"/purchaseorders/{args.parent_id}/purchaseorderglobalcosts",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_purchase_order_global_cost),
    response_schema="PurchaseOrderGlobalCostResponse",
)

PURCHASE_ORDER_COSTS: Endpoint[CollectionArgs, RentmanPage[PurchaseOrderCost]] = Endpoint(
    name="purchase_order_costs",
    method="GET",
    path=lambda _args: "/purchaseordercosts",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_purchase_order_cost),
    response_schema="PurchaseOrderCostResponse",
)

PURCHASE_ORDER_COSTS_ITEM: Endpoint[ItemArgs, PurchaseOrderCost | None] = Endpoint(
    name="purchase_order_costs_item",
    method="GET",
    path=lambda args: f"/purchaseordercosts/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_purchase_order_cost),
    response_schema="PurchaseOrderCostResponse",
)

PURCHASE_ORDER_GLOBAL_COSTS: Endpoint[CollectionArgs, RentmanPage[PurchaseOrderGlobalCost]] = (
    Endpoint(
        name="purchase_order_global_costs",
        method="GET",
        path=lambda _args: "/purchaseorderglobalcosts",
        params=_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_purchase_order_global_cost),
        response_schema="PurchaseOrderGlobalCostResponse",
    )
)

PURCHASE_ORDER_GLOBAL_COSTS_ITEM: Endpoint[ItemArgs, PurchaseOrderGlobalCost | None] = Endpoint(
    name="purchase_order_global_costs_item",
    method="GET",
    path=lambda args: f"/purchaseorderglobalcosts/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_purchase_order_global_cost),
    response_schema="PurchaseOrderGlobalCostResponse",
)

CREW: Endpoint[CollectionArgs, RentmanPage[Crew]] = Endpoint(
    name="crew",
    method="GET",
    path=lambda _args: "/crew",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_crew),
    response_schema="CrewResponse",
)

CREW_ITEM: Endpoint[ItemArgs, Crew | None] = Endpoint(
    name="crew_item",
    method="GET",
    path=lambda args: f"/crew/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_crew),
    response_schema="CrewResponse",
)

APPOINTMENTS_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[Appointment]] = Endpoint(
    name="appointments_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/appointments",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_appointment),
    response_schema="AppointmentResponse",
)

CREW_AVAILABILITY_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[CrewAvailability]] = Endpoint(
    name="crew_availability_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/crewavailability",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_crew_availability),
    response_schema="CrewAvailabilityResponse",
)

CREW_RATES_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[CrewRate]] = Endpoint(
    name="crew_rates_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/crewrates",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_crew_rate),
    response_schema="CrewRatesResponse",
)

INVITATIONS_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[Invitation]] = Endpoint(
    name="invitations_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/invitations",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_invitation),
    response_schema="InvitationsResponse",
)

CREW_AVAILABILITY: Endpoint[CollectionArgs, RentmanPage[CrewAvailability]] = Endpoint(
    name="crew_availability",
    method="GET",
    path=lambda _args: "/crewavailability",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_crew_availability),
    response_schema="CrewAvailabilityResponse",
)

CREW_AVAILABILITY_ITEM: Endpoint[ItemArgs, CrewAvailability | None] = Endpoint(
    name="crew_availability_item",
    method="GET",
    path=lambda args: f"/crewavailability/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_crew_availability),
    response_schema="CrewAvailabilityResponse",
)

CREW_RATES: Endpoint[CollectionArgs, RentmanPage[CrewRate]] = Endpoint(
    name="crew_rates",
    method="GET",
    path=lambda _args: "/crewrates",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_crew_rate),
    response_schema="CrewRatesResponse",
)

CREW_RATES_ITEM: Endpoint[ItemArgs, CrewRate | None] = Endpoint(
    name="crew_rates_item",
    method="GET",
    path=lambda args: f"/crewrates/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_crew_rate),
    response_schema="CrewRatesResponse",
)

INVITATIONS: Endpoint[CollectionArgs, RentmanPage[Invitation]] = Endpoint(
    name="invitations",
    method="GET",
    path=lambda _args: "/invitations",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_invitation),
    response_schema="InvitationsResponse",
)

INVITATIONS_ITEM: Endpoint[ItemArgs, Invitation | None] = Endpoint(
    name="invitations_item",
    method="GET",
    path=lambda args: f"/invitations/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_invitation),
    response_schema="InvitationsResponse",
)

APPOINTMENTS: Endpoint[CollectionArgs, RentmanPage[Appointment]] = Endpoint(
    name="appointments",
    method="GET",
    path=lambda _args: "/appointments",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_appointment),
    response_schema="AppointmentResponse",
)

APPOINTMENTS_ITEM: Endpoint[ItemArgs, Appointment | None] = Endpoint(
    name="appointments_item",
    method="GET",
    path=lambda args: f"/appointments/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_appointment),
    response_schema="AppointmentResponse",
)

APPOINTMENT_CREW_OF_APPOINTMENT: Endpoint[ParentCollectionArgs, RentmanPage[AppointmentCrew]] = (
    Endpoint(
        name="appointment_crew_of_appointment",
        method="GET",
        path=lambda args: f"/appointments/{args.parent_id}/appointmentcrew",
        params=_linked_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_appointment_crew),
        response_schema="AppointmentCrewResponse",
    )
)

APPOINTMENT_CREW: Endpoint[CollectionArgs, RentmanPage[AppointmentCrew]] = Endpoint(
    name="appointment_crew",
    method="GET",
    path=lambda _args: "/appointmentcrew",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_appointment_crew),
    response_schema="AppointmentCrewResponse",
)

APPOINTMENT_CREW_ITEM: Endpoint[ItemArgs, AppointmentCrew | None] = Endpoint(
    name="appointment_crew_item",
    method="GET",
    path=lambda args: f"/appointmentcrew/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_appointment_crew),
    response_schema="AppointmentCrewResponse",
)

TIME_REGISTRATIONS: Endpoint[CollectionArgs, RentmanPage[TimeRegistration]] = Endpoint(
    name="time_registrations",
    method="GET",
    path=lambda _args: "/timeregistration",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_time_registration),
    response_schema="TimeRegistrationResponse",
)

TIME_REGISTRATIONS_ITEM: Endpoint[ItemArgs, TimeRegistration | None] = Endpoint(
    name="time_registrations_item",
    method="GET",
    path=lambda args: f"/timeregistration/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_time_registration),
    response_schema="TimeRegistrationResponse",
)

TIME_REGISTRATION_ACTIVITIES_OF_TIME_REGISTRATION: Endpoint[
    ParentCollectionArgs, RentmanPage[TimeRegistrationActivity]
] = Endpoint(
    name="time_registration_activities_of_time_registration",
    method="GET",
    path=lambda args: f"/timeregistration/{args.parent_id}/timeregistrationactivities",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_time_registration_activity),
    response_schema="TimeRegistrationActivityResponse",
)

TIME_REGISTRATION_ACTIVITIES: Endpoint[CollectionArgs, RentmanPage[TimeRegistrationActivity]] = (
    Endpoint(
        name="time_registration_activities",
        method="GET",
        path=lambda _args: "/timeregistrationactivities",
        params=_collection_params,
        parse=lambda payload, _args: parse_page(payload, parse_time_registration_activity),
        response_schema="TimeRegistrationActivityResponse",
    )
)

TIME_REGISTRATION_ACTIVITIES_ITEM: Endpoint[ItemArgs, TimeRegistrationActivity | None] = Endpoint(
    name="time_registration_activities_item",
    method="GET",
    path=lambda args: f"/timeregistrationactivities/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_time_registration_activity),
    response_schema="TimeRegistrationActivityResponse",
)

LEAVE_REQUESTS: Endpoint[CollectionArgs, RentmanPage[LeaveRequest]] = Endpoint(
    name="leave_requests",
    method="GET",
    path=lambda _args: "/leaverequest",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_leave_request),
    response_schema="LeaveRequestResponse",
)

LEAVE_REQUESTS_ITEM: Endpoint[ItemArgs, LeaveRequest | None] = Endpoint(
    name="leave_requests_item",
    method="GET",
    path=lambda args: f"/leaverequest/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_leave_request),
    response_schema="LeaveRequestResponse",
)

TIME_REGISTRATIONS_OF_LEAVE_REQUEST: Endpoint[
    ParentCollectionArgs, RentmanPage[TimeRegistration]
] = Endpoint(
    name="time_registrations_of_leave_request",
    method="GET",
    path=lambda args: f"/leaverequest/{args.parent_id}/timeregistration",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_time_registration),
    response_schema="TimeRegistrationResponse",
)

LEAVE_MUTATIONS: Endpoint[CollectionArgs, RentmanPage[LeaveMutation]] = Endpoint(
    name="leave_mutations",
    method="GET",
    path=lambda _args: "/leavemutation",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_leave_mutation),
    response_schema="LeaveMutationsResponse",
)

LEAVE_MUTATIONS_ITEM: Endpoint[ItemArgs, LeaveMutation | None] = Endpoint(
    name="leave_mutations_item",
    method="GET",
    path=lambda args: f"/leavemutation/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_leave_mutation),
    response_schema="LeaveMutationsResponse",
)

LEAVE_TYPES: Endpoint[CollectionArgs, RentmanPage[LeaveType]] = Endpoint(
    name="leave_types",
    method="GET",
    path=lambda _args: "/leavetypes",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_leave_type),
    response_schema="LeaveTypesResponse",
)

LEAVE_TYPES_ITEM: Endpoint[ItemArgs, LeaveType | None] = Endpoint(
    name="leave_types_item",
    method="GET",
    path=lambda args: f"/leavetypes/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_leave_type),
    response_schema="LeaveTypesResponse",
)

CONTACTS: Endpoint[CollectionArgs, RentmanPage[Contact]] = Endpoint(
    name="contacts",
    method="GET",
    path=lambda _args: "/contacts",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_contact),
    response_schema="ContactResponse",
)

CONTACTS_ITEM: Endpoint[ItemArgs, Contact | None] = Endpoint(
    name="contacts_item",
    method="GET",
    path=lambda args: f"/contacts/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_contact),
    response_schema="ContactResponse",
)

CONTACT_PERSONS_OF_CONTACT: Endpoint[ParentCollectionArgs, RentmanPage[ContactPerson]] = Endpoint(
    name="contact_persons_of_contact",
    method="GET",
    path=lambda args: f"/contacts/{args.parent_id}/contactpersons",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_contact_person),
    response_schema="ContactPersonResponse",
)

CONTACT_PERSONS: Endpoint[CollectionArgs, RentmanPage[ContactPerson]] = Endpoint(
    name="contact_persons",
    method="GET",
    path=lambda _args: "/contactpersons",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_contact_person),
    response_schema="ContactPersonResponse",
)

CONTACT_PERSONS_ITEM: Endpoint[ItemArgs, ContactPerson | None] = Endpoint(
    name="contact_persons_item",
    method="GET",
    path=lambda args: f"/contactpersons/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_contact_person),
    response_schema="ContactPersonResponse",
)

TASKS: Endpoint[CollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks",
    method="GET",
    path=lambda _args: "/tasks",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

SUBTASKS: Endpoint[CollectionArgs, RentmanPage[Subtask]] = Endpoint(
    name="subtasks",
    method="GET",
    path=lambda _args: "/subtasks",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subtask),
    response_schema="SubtaskResponse",
)

TASK_ASSIGNMENTS: Endpoint[CollectionArgs, RentmanPage[TaskAssignment]] = Endpoint(
    name="task_assignments",
    method="GET",
    path=lambda _args: "/taskassignments",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task_assignment),
    response_schema="TaskAssignmentResponse",
)

TASK_STATUSES: Endpoint[CollectionArgs, RentmanPage[TaskStatus]] = Endpoint(
    name="task_statuses",
    method="GET",
    path=lambda _args: "/taskstatuses",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task_status),
    response_schema="TaskStatusResponse",
)

FILES: Endpoint[CollectionArgs, RentmanPage[File]] = Endpoint(
    name="files",
    method="GET",
    path=lambda _args: "/files",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILE_FOLDERS: Endpoint[CollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders",
    method="GET",
    path=lambda _args: "/file_folders",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

TASKS_ITEM: Endpoint[ItemArgs, Task | None] = Endpoint(
    name="tasks_item",
    method="GET",
    path=lambda args: f"/tasks/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_task),
    response_schema="TaskResponse",
)

SUBTASKS_ITEM: Endpoint[ItemArgs, Subtask | None] = Endpoint(
    name="subtasks_item",
    method="GET",
    path=lambda args: f"/subtasks/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_subtask),
    response_schema="SubtaskResponse",
)

TASK_ASSIGNMENTS_ITEM: Endpoint[ItemArgs, TaskAssignment | None] = Endpoint(
    name="task_assignments_item",
    method="GET",
    path=lambda args: f"/taskassignments/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_task_assignment),
    response_schema="TaskAssignmentResponse",
)

TASK_STATUSES_ITEM: Endpoint[ItemArgs, TaskStatus | None] = Endpoint(
    name="task_statuses_item",
    method="GET",
    path=lambda args: f"/taskstatuses/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_task_status),
    response_schema="TaskStatusResponse",
)

FILES_ITEM: Endpoint[ItemArgs, File | None] = Endpoint(
    name="files_item",
    method="GET",
    path=lambda args: f"/files/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_file),
    response_schema="FileResponse",
)

FILE_FOLDERS_ITEM: Endpoint[ItemArgs, FileFolder | None] = Endpoint(
    name="file_folders_item",
    method="GET",
    path=lambda args: f"/file_folders/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

SUBTASKS_OF_TASK: Endpoint[ParentCollectionArgs, RentmanPage[Subtask]] = Endpoint(
    name="subtasks_of_task",
    method="GET",
    path=lambda args: f"/tasks/{args.parent_id}/subtasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_subtask),
    response_schema="SubtaskResponse",
)

TASK_ASSIGNMENTS_OF_TASK: Endpoint[ParentCollectionArgs, RentmanPage[TaskAssignment]] = Endpoint(
    name="task_assignments_of_task",
    method="GET",
    path=lambda args: f"/tasks/{args.parent_id}/taskassignments",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task_assignment),
    response_schema="TaskAssignmentResponse",
)

FILES_OF_TASK: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_task",
    method="GET",
    path=lambda args: f"/tasks/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILE_FOLDERS_OF_TASK: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_task",
    method="GET",
    path=lambda args: f"/tasks/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

TASKS_OF_CONTACT_PERSON: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_contact_person",
    method="GET",
    path=lambda args: f"/contactpersons/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_CONTACT: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_contact",
    method="GET",
    path=lambda args: f"/contacts/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_INVOICE: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_invoice",
    method="GET",
    path=lambda args: f"/invoices/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_PURCHASE_ORDER: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_purchase_order",
    method="GET",
    path=lambda args: f"/purchaseorders/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_QUOTE: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_quote",
    method="GET",
    path=lambda args: f"/quotes/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_REPAIR: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_repair",
    method="GET",
    path=lambda args: f"/repairs/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_SERIAL_NUMBER: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_serial_number",
    method="GET",
    path=lambda args: f"/serialnumbers/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_SUBRENTAL: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_subrental",
    method="GET",
    path=lambda args: f"/subrentals/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_VEHICLE: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_vehicle",
    method="GET",
    path=lambda args: f"/vehicles/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

TASKS_OF_SUPPLIER: Endpoint[ParentCollectionArgs, RentmanPage[Task]] = Endpoint(
    name="tasks_of_supplier",
    method="GET",
    path=lambda args: f"/suppliers/{args.parent_id}/tasks",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_task),
    response_schema="TaskResponse",
)

FILES_OF_CONTACT_PERSON: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_contact_person",
    method="GET",
    path=lambda args: f"/contactpersons/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_CONTACT: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_contact",
    method="GET",
    path=lambda args: f"/contacts/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_INVOICE: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_invoice",
    method="GET",
    path=lambda args: f"/invoices/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_PURCHASE_ORDER: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_purchase_order",
    method="GET",
    path=lambda args: f"/purchaseorders/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_QUOTE: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_quote",
    method="GET",
    path=lambda args: f"/quotes/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_REPAIR: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_repair",
    method="GET",
    path=lambda args: f"/repairs/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_SERIAL_NUMBER: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_serial_number",
    method="GET",
    path=lambda args: f"/serialnumbers/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_SUBRENTAL: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_subrental",
    method="GET",
    path=lambda args: f"/subrentals/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_TIME_REGISTRATION: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_time_registration",
    method="GET",
    path=lambda args: f"/timeregistration/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_VEHICLE: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_vehicle",
    method="GET",
    path=lambda args: f"/vehicles/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILES_OF_SUPPLIER: Endpoint[ParentCollectionArgs, RentmanPage[File]] = Endpoint(
    name="files_of_supplier",
    method="GET",
    path=lambda args: f"/suppliers/{args.parent_id}/files",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file),
    response_schema="FileResponse",
)

FILE_FOLDERS_OF_CONTACT_PERSON: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_contact_person",
    method="GET",
    path=lambda args: f"/contactpersons/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_CONTACT: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_contact",
    method="GET",
    path=lambda args: f"/contacts/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_CREW: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_crew",
    method="GET",
    path=lambda args: f"/crew/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_EQUIPMENT: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_equipment",
    method="GET",
    path=lambda args: f"/equipment/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_PROJECT: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_project",
    method="GET",
    path=lambda args: f"/projects/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_PURCHASE_ORDER: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_purchase_order",
    method="GET",
    path=lambda args: f"/purchaseorders/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_REPAIR: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_repair",
    method="GET",
    path=lambda args: f"/repairs/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_SERIAL_NUMBER: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_serial_number",
    method="GET",
    path=lambda args: f"/serialnumbers/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_SUBPROJECT: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_subproject",
    method="GET",
    path=lambda args: f"/subprojects/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_SUBRENTAL: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_subrental",
    method="GET",
    path=lambda args: f"/subrentals/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_SUPPLIER: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_supplier",
    method="GET",
    path=lambda args: f"/suppliers/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)

FILE_FOLDERS_OF_VEHICLE: Endpoint[ParentCollectionArgs, RentmanPage[FileFolder]] = Endpoint(
    name="file_folders_of_vehicle",
    method="GET",
    path=lambda args: f"/vehicles/{args.parent_id}/file_folders",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_file_folder),
    response_schema="FileFolderResponse",
)


RATES: Endpoint[CollectionArgs, RentmanPage[Rate]] = Endpoint(
    name="rates",
    method="GET",
    path=lambda _args: "/rates",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_rate),
    response_schema="CrewRateResponse",
)

RATES_ITEM: Endpoint[ItemArgs, Rate | None] = Endpoint(
    name="rates_item",
    method="GET",
    path=lambda args: f"/rates/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_rate),
    response_schema="CrewRateResponse",
)

RATE_FACTORS: Endpoint[CollectionArgs, RentmanPage[RateFactor]] = Endpoint(
    name="rate_factors",
    method="GET",
    path=lambda _args: "/ratefactors",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_rate_factor),
    response_schema="CrewRateFactorResponse",
)

RATE_FACTORS_ITEM: Endpoint[ItemArgs, RateFactor | None] = Endpoint(
    name="rate_factors_item",
    method="GET",
    path=lambda args: f"/ratefactors/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_rate_factor),
    response_schema="CrewRateFactorResponse",
)

RATE_FACTORS_OF_RATE: Endpoint[ParentCollectionArgs, RentmanPage[RateFactor]] = Endpoint(
    name="rate_factors_of_rate",
    method="GET",
    path=lambda args: f"/rates/{args.parent_id}/ratefactors",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_rate_factor),
    response_schema="CrewRateFactorResponse",
)

FACTORS: Endpoint[CollectionArgs, RentmanPage[Factor]] = Endpoint(
    name="factors",
    method="GET",
    path=lambda _args: "/factors",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_factor),
    response_schema="FactorsResponse",
)

FACTORS_ITEM: Endpoint[ItemArgs, Factor | None] = Endpoint(
    name="factors_item",
    method="GET",
    path=lambda args: f"/factors/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_factor),
    response_schema="FactorsResponse",
)

FACTORS_OF_FACTOR_GROUP: Endpoint[ParentCollectionArgs, RentmanPage[Factor]] = Endpoint(
    name="factors_of_factor_group",
    method="GET",
    path=lambda args: f"/factorgroups/{args.parent_id}/factors",
    params=_linked_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_factor),
    response_schema="FactorsResponse",
)

FACTOR_GROUPS: Endpoint[CollectionArgs, RentmanPage[FactorGroup]] = Endpoint(
    name="factor_groups",
    method="GET",
    path=lambda _args: "/factorgroups",
    params=_collection_params,
    parse=lambda payload, _args: parse_page(payload, parse_factor_group),
    response_schema="FactorGroupsResponse",
)

FACTOR_GROUPS_ITEM: Endpoint[ItemArgs, FactorGroup | None] = Endpoint(
    name="factor_groups_item",
    method="GET",
    path=lambda args: f"/factorgroups/{args.item_id}",
    params=lambda _args: {},
    parse=lambda payload, _args: parse_envelope_item(payload, parse_factor_group),
    response_schema="FactorGroupsResponse",
)

CATALOG: tuple[Endpoint[Any, Any], ...] = (
    ACTUAL_CONTENT,
    ACTUAL_CONTENT_ITEM,
    ACTUAL_CONTENT_OF_SERIAL_NUMBER,
    EQUIPMENT,
    EQUIPMENT_ITEM,
    EQUIPMENT_SET_CONTENT_OF_EQUIPMENT,
    REPAIRS_OF_EQUIPMENT,
    SERIAL_NUMBERS_OF_EQUIPMENT,
    STOCK_MOVEMENTS_OF_EQUIPMENT,
    SERIAL_NUMBERS,
    SERIAL_NUMBERS_ITEM,
    EQUIPMENT_ASSIGNED_SERIALS,
    EQUIPMENT_ASSIGNED_SERIALS_ITEM,
    EQUIPMENT_ASSIGNED_SERIALS_OF_SERIAL_NUMBER,
    EQUIPMENT_SET_CONTENT,
    EQUIPMENT_SET_CONTENT_ITEM,
    FOLDERS,
    FOLDERS_ITEM,
    STOCK_LOCATIONS,
    STOCK_LOCATIONS_ITEM,
    WAREHOUSE_STATUSES,
    WAREHOUSE_STATUSES_ITEM,
    STATUSES,
    STATUSES_ITEM,
    STOCK_MOVEMENTS,
    STOCK_MOVEMENTS_ITEM,
    REPAIRS,
    REPAIRS_ITEM,
    PROJECTS,
    PROJECTS_ITEM,
    PROJECT_EQUIPMENT_OF_PROJECT,
    SUBPROJECTS_OF_PROJECT,
    SUBPROJECTS,
    SUBPROJECTS_ITEM,
    PROJECT_EQUIPMENT_OF_SUBPROJECT,
    PROJECT_EQUIPMENT,
    PROJECT_EQUIPMENT_ITEM,
    ACCESSORIES,
    ACCESSORIES_ITEM,
    ACCESSORIES_OF_EQUIPMENT,
    ALTERNATIVES,
    ALTERNATIVES_ITEM,
    ALTERNATIVES_OF_EQUIPMENT,
    SUPPLIERS,
    SUPPLIERS_ITEM,
    SUPPLIERS_OF_EQUIPMENT,
    VEHICLES,
    VEHICLES_ITEM,
    VEHICLES_OF_STOCK_LOCATION,
    EXTRA_INPUT_FIELDS,
    EXTRA_INPUT_FIELDS_ITEM,
    PROJECT_STATUSES,
    PROJECT_STATUSES_ITEM,
    PROJECT_TYPES,
    PROJECT_TYPES_ITEM,
    PROJECT_FUNCTION_GROUPS,
    PROJECT_FUNCTION_GROUPS_ITEM,
    PROJECT_FUNCTION_GROUPS_OF_PROJECT,
    PROJECT_FUNCTION_GROUPS_OF_SUBPROJECT,
    PROJECT_FUNCTIONS,
    PROJECT_FUNCTIONS_ITEM,
    PROJECT_FUNCTIONS_OF_PROJECT,
    PROJECT_FUNCTIONS_OF_PROJECT_FUNCTION_GROUP,
    PROJECT_CREW,
    PROJECT_CREW_ITEM,
    PROJECT_CREW_OF_PROJECT,
    PROJECT_CREW_OF_SUBPROJECT,
    PROJECT_CREW_OF_PROJECT_FUNCTION,
    PROJECT_VEHICLES,
    PROJECT_VEHICLES_ITEM,
    PROJECT_VEHICLES_OF_PROJECT,
    PROJECT_VEHICLES_OF_SUBPROJECT,
    PROJECT_VEHICLES_OF_PROJECT_FUNCTION,
    PROJECT_EQUIPMENT_GROUPS,
    PROJECT_EQUIPMENT_GROUPS_ITEM,
    PROJECT_EQUIPMENT_GROUPS_OF_PROJECT,
    PROJECT_EQUIPMENT_GROUPS_OF_SUBPROJECT,
    PROJECT_EQUIPMENT_OF_PROJECT_EQUIPMENT_GROUP,
    PROJECT_COSTS,
    PROJECT_COSTS_ITEM,
    PROJECT_COSTS_OF_PROJECT,
    PROJECT_REQUESTS,
    PROJECT_REQUESTS_ITEM,
    PROJECT_REQUEST_EQUIPMENT,
    PROJECT_REQUEST_EQUIPMENT_ITEM,
    PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST,
    QUOTES,
    QUOTES_ITEM,
    QUOTES_OF_PROJECT,
    INVOICE_LINES_OF_QUOTE,
    CONTRACTS,
    CONTRACTS_ITEM,
    CONTRACTS_OF_PROJECT,
    INVOICES,
    INVOICES_ITEM,
    INVOICE_LINES_OF_INVOICE,
    PAYMENTS_OF_INVOICE,
    INVOICE_LINES,
    INVOICE_LINES_ITEM,
    PAYMENTS,
    PAYMENTS_ITEM,
    LEDGER_CODES,
    LEDGER_CODES_ITEM,
    TAX_CLASSES,
    TAX_CLASSES_ITEM,
    SUBRENTALS,
    SUBRENTALS_ITEM,
    SUBRENTAL_EQUIPMENT_OF_SUBRENTAL,
    SUBRENTAL_EQUIPMENT_GROUPS_OF_SUBRENTAL,
    SUBRENTAL_EQUIPMENT,
    SUBRENTAL_EQUIPMENT_ITEM,
    SUBRENTAL_EQUIPMENT_OF_SUBRENTAL_EQUIPMENT_GROUP,
    SUBRENTAL_EQUIPMENT_GROUPS,
    SUBRENTAL_EQUIPMENT_GROUPS_ITEM,
    PURCHASE_ORDERS,
    PURCHASE_ORDERS_ITEM,
    INVOICE_LINES_OF_PURCHASE_ORDER,
    PURCHASE_ORDER_COSTS_OF_PURCHASE_ORDER,
    PURCHASE_ORDER_GLOBAL_COSTS_OF_PURCHASE_ORDER,
    PURCHASE_ORDER_COSTS,
    PURCHASE_ORDER_COSTS_ITEM,
    PURCHASE_ORDER_GLOBAL_COSTS,
    PURCHASE_ORDER_GLOBAL_COSTS_ITEM,
    CREW,
    CREW_ITEM,
    APPOINTMENTS_OF_CREW,
    CREW_AVAILABILITY_OF_CREW,
    CREW_RATES_OF_CREW,
    INVITATIONS_OF_CREW,
    CREW_AVAILABILITY,
    CREW_AVAILABILITY_ITEM,
    CREW_RATES,
    CREW_RATES_ITEM,
    INVITATIONS,
    INVITATIONS_ITEM,
    APPOINTMENTS,
    APPOINTMENTS_ITEM,
    APPOINTMENT_CREW_OF_APPOINTMENT,
    APPOINTMENT_CREW,
    APPOINTMENT_CREW_ITEM,
    TIME_REGISTRATIONS,
    TIME_REGISTRATIONS_ITEM,
    TIME_REGISTRATION_ACTIVITIES_OF_TIME_REGISTRATION,
    TIME_REGISTRATION_ACTIVITIES,
    TIME_REGISTRATION_ACTIVITIES_ITEM,
    LEAVE_REQUESTS,
    LEAVE_REQUESTS_ITEM,
    TIME_REGISTRATIONS_OF_LEAVE_REQUEST,
    LEAVE_MUTATIONS,
    LEAVE_MUTATIONS_ITEM,
    LEAVE_TYPES,
    LEAVE_TYPES_ITEM,
    CONTACTS,
    CONTACTS_ITEM,
    CONTACT_PERSONS_OF_CONTACT,
    CONTACT_PERSONS,
    CONTACT_PERSONS_ITEM,
    RATES,
    RATES_ITEM,
    RATE_FACTORS,
    RATE_FACTORS_ITEM,
    RATE_FACTORS_OF_RATE,
    FACTORS,
    FACTORS_ITEM,
    FACTORS_OF_FACTOR_GROUP,
    FACTOR_GROUPS,
    FACTOR_GROUPS_ITEM,
    TASKS,
    SUBTASKS,
    TASK_ASSIGNMENTS,
    TASK_STATUSES,
    FILES,
    FILE_FOLDERS,
    TASKS_ITEM,
    SUBTASKS_ITEM,
    TASK_ASSIGNMENTS_ITEM,
    TASK_STATUSES_ITEM,
    FILES_ITEM,
    FILE_FOLDERS_ITEM,
    SUBTASKS_OF_TASK,
    TASK_ASSIGNMENTS_OF_TASK,
    FILES_OF_TASK,
    FILE_FOLDERS_OF_TASK,
    TASKS_OF_CONTACT_PERSON,
    TASKS_OF_CONTACT,
    TASKS_OF_CREW,
    TASKS_OF_EQUIPMENT,
    TASKS_OF_INVOICE,
    TASKS_OF_PROJECT,
    TASKS_OF_PURCHASE_ORDER,
    TASKS_OF_QUOTE,
    TASKS_OF_REPAIR,
    TASKS_OF_SERIAL_NUMBER,
    TASKS_OF_SUBRENTAL,
    TASKS_OF_VEHICLE,
    TASKS_OF_SUPPLIER,
    FILES_OF_CONTACT_PERSON,
    FILES_OF_CONTACT,
    FILES_OF_CREW,
    FILES_OF_EQUIPMENT,
    FILES_OF_INVOICE,
    FILES_OF_PROJECT,
    FILES_OF_PURCHASE_ORDER,
    FILES_OF_QUOTE,
    FILES_OF_REPAIR,
    FILES_OF_SERIAL_NUMBER,
    FILES_OF_SUBRENTAL,
    FILES_OF_TIME_REGISTRATION,
    FILES_OF_VEHICLE,
    FILES_OF_SUPPLIER,
    FILE_FOLDERS_OF_CONTACT_PERSON,
    FILE_FOLDERS_OF_CONTACT,
    FILE_FOLDERS_OF_CREW,
    FILE_FOLDERS_OF_EQUIPMENT,
    FILE_FOLDERS_OF_PROJECT,
    FILE_FOLDERS_OF_PURCHASE_ORDER,
    FILE_FOLDERS_OF_REPAIR,
    FILE_FOLDERS_OF_SERIAL_NUMBER,
    FILE_FOLDERS_OF_SUBPROJECT,
    FILE_FOLDERS_OF_SUBRENTAL,
    FILE_FOLDERS_OF_SUPPLIER,
    FILE_FOLDERS_OF_VEHICLE,
)
