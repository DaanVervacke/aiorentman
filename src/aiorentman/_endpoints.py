"""The frozen endpoint catalog: one row per wire contract."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .models import (
    Accessory,
    ActualContent,
    Alternative,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
    ExtraInputField,
    Folder,
    Project,
    ProjectEquipment,
    RentmanPage,
    Repair,
    SerialNumber,
    Status,
    StockLocation,
    StockMovement,
    Subproject,
    Supplier,
    Vehicle,
    WarehouseStatus,
)
from .parsers import (
    parse_accessory,
    parse_actual_content,
    parse_alternative,
    parse_envelope_item,
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
)
