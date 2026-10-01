"""The RentmanClient facade: one typed method per endpoint."""

import logging
import os
from collections.abc import AsyncIterator
from typing import Self
from urllib.parse import parse_qsl, urlsplit

import aiohttp

from ._endpoints import (
    ACCESSORIES,
    ACCESSORIES_ITEM,
    ACCESSORIES_OF_EQUIPMENT,
    ACTUAL_CONTENT,
    ACTUAL_CONTENT_ITEM,
    ACTUAL_CONTENT_OF_SERIAL_NUMBER,
    ALTERNATIVES,
    ALTERNATIVES_ITEM,
    ALTERNATIVES_OF_EQUIPMENT,
    EQUIPMENT,
    EQUIPMENT_ASSIGNED_SERIALS,
    EQUIPMENT_ASSIGNED_SERIALS_ITEM,
    EQUIPMENT_ASSIGNED_SERIALS_OF_SERIAL_NUMBER,
    EQUIPMENT_ITEM,
    EQUIPMENT_SET_CONTENT,
    EQUIPMENT_SET_CONTENT_ITEM,
    EQUIPMENT_SET_CONTENT_OF_EQUIPMENT,
    EXTRA_INPUT_FIELDS,
    EXTRA_INPUT_FIELDS_ITEM,
    FOLDERS,
    FOLDERS_ITEM,
    PROJECT_COSTS,
    PROJECT_COSTS_ITEM,
    PROJECT_COSTS_OF_PROJECT,
    PROJECT_CREW,
    PROJECT_CREW_ITEM,
    PROJECT_CREW_OF_PROJECT,
    PROJECT_CREW_OF_PROJECT_FUNCTION,
    PROJECT_CREW_OF_SUBPROJECT,
    PROJECT_EQUIPMENT,
    PROJECT_EQUIPMENT_GROUPS,
    PROJECT_EQUIPMENT_GROUPS_ITEM,
    PROJECT_EQUIPMENT_GROUPS_OF_PROJECT,
    PROJECT_EQUIPMENT_GROUPS_OF_SUBPROJECT,
    PROJECT_EQUIPMENT_ITEM,
    PROJECT_EQUIPMENT_OF_PROJECT,
    PROJECT_EQUIPMENT_OF_PROJECT_EQUIPMENT_GROUP,
    PROJECT_EQUIPMENT_OF_SUBPROJECT,
    PROJECT_FUNCTION_GROUPS,
    PROJECT_FUNCTION_GROUPS_ITEM,
    PROJECT_FUNCTION_GROUPS_OF_PROJECT,
    PROJECT_FUNCTION_GROUPS_OF_SUBPROJECT,
    PROJECT_FUNCTIONS,
    PROJECT_FUNCTIONS_ITEM,
    PROJECT_FUNCTIONS_OF_PROJECT,
    PROJECT_FUNCTIONS_OF_PROJECT_FUNCTION_GROUP,
    PROJECT_REQUEST_EQUIPMENT,
    PROJECT_REQUEST_EQUIPMENT_ITEM,
    PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST,
    PROJECT_REQUESTS,
    PROJECT_REQUESTS_ITEM,
    PROJECT_STATUSES,
    PROJECT_STATUSES_ITEM,
    PROJECT_TYPES,
    PROJECT_TYPES_ITEM,
    PROJECT_VEHICLES,
    PROJECT_VEHICLES_ITEM,
    PROJECT_VEHICLES_OF_PROJECT,
    PROJECT_VEHICLES_OF_PROJECT_FUNCTION,
    PROJECT_VEHICLES_OF_SUBPROJECT,
    PROJECTS,
    PROJECTS_ITEM,
    REPAIRS,
    REPAIRS_ITEM,
    REPAIRS_OF_EQUIPMENT,
    SERIAL_NUMBERS,
    SERIAL_NUMBERS_ITEM,
    SERIAL_NUMBERS_OF_EQUIPMENT,
    STATUSES,
    STATUSES_ITEM,
    STOCK_LOCATIONS,
    STOCK_LOCATIONS_ITEM,
    STOCK_MOVEMENTS,
    STOCK_MOVEMENTS_ITEM,
    STOCK_MOVEMENTS_OF_EQUIPMENT,
    SUBPROJECTS,
    SUBPROJECTS_ITEM,
    SUBPROJECTS_OF_PROJECT,
    SUPPLIERS,
    SUPPLIERS_ITEM,
    SUPPLIERS_OF_EQUIPMENT,
    VEHICLES,
    VEHICLES_ITEM,
    VEHICLES_OF_STOCK_LOCATION,
    WAREHOUSE_STATUSES,
    WAREHOUSE_STATUSES_ITEM,
    CollectionArgs,
    Endpoint,
    ItemArgs,
    ParentCollectionArgs,
)
from ._ratelimit import RequestPacer
from ._transport import OwnedSession, request_json
from .const import (
    BASE_URL,
    DEFAULT_MAX_CONCURRENT_REQUESTS,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_REQUESTS_PER_SECOND,
    TOKEN_ENV_VAR,
    USER_AGENT,
)
from .exceptions import (
    RentmanAuthenticationError,
    RentmanClientClosedError,
    RentmanInvalidResponseError,
)
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
from .query import Query

_LOGGER = logging.getLogger(__name__)


class RentmanClient:
    """Asynchronous read-only client for the Rentman API.

    The client covers the inventory and planning resources an RFID and
    materials project needs. Every request is paced against the documented
    rate limits unless pacing is disabled with ``requests_per_second=None``.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession | None = None,
        *,
        token: str | None = None,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        requests_per_second: float | None = DEFAULT_REQUESTS_PER_SECOND,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
    ) -> None:
        """Create a client from a session and an API token.

        The token comes from the argument or from the RENTMAN_TOKEN
        environment variable. Regenerating the token in Rentman invalidates
        the previous one.
        """
        resolved = token or os.environ.get(TOKEN_ENV_VAR)
        if not resolved:
            msg = f"A token is required: pass token or set the {TOKEN_ENV_VAR} environment variable"
            raise RentmanAuthenticationError(msg)
        self._owned_session = OwnedSession(
            session=aiohttp.ClientSession() if session is None else session,
            owned=session is None,
        )
        self._token = resolved
        self._request_timeout = request_timeout
        self._pacer = RequestPacer(
            requests_per_second=requests_per_second,
            max_concurrent=max_concurrent,
        )
        self._closed = False

    async def async_list_actual_content(
        self, query: Query | None = None
    ) -> RentmanPage[ActualContent]:
        """Fetch one page of recorded combination contents."""
        return await self._call(ACTUAL_CONTENT, CollectionArgs(query=query))

    def async_iter_actual_content(self, query: Query | None = None) -> AsyncIterator[ActualContent]:
        """Yield every recorded combination content, following the cursor."""
        return self._iter_collection(ACTUAL_CONTENT, CollectionArgs(query=query))

    async def async_get_actual_content(self, actual_content_id: int) -> ActualContent | None:
        """Fetch one recorded combination content by its id."""
        return await self._call(ACTUAL_CONTENT_ITEM, ItemArgs(item_id=actual_content_id))

    async def async_list_actual_content_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> RentmanPage[ActualContent]:
        """Fetch one page of contents recorded inside one combination serial."""
        return await self._call(
            ACTUAL_CONTENT_OF_SERIAL_NUMBER,
            ParentCollectionArgs(parent_id=serial_number_id, query=query),
        )

    def async_iter_actual_content_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> AsyncIterator[ActualContent]:
        """Yield every content of one combination serial, following the cursor."""
        return self._iter_collection(
            ACTUAL_CONTENT_OF_SERIAL_NUMBER,
            ParentCollectionArgs(parent_id=serial_number_id, query=query),
        )

    async def async_list_equipment(self, query: Query | None = None) -> RentmanPage[Equipment]:
        """Fetch one page of materials."""
        return await self._call(EQUIPMENT, CollectionArgs(query=query))

    def async_iter_equipment(self, query: Query | None = None) -> AsyncIterator[Equipment]:
        """Yield every material, following the cursor across pages."""
        return self._iter_collection(EQUIPMENT, CollectionArgs(query=query))

    async def async_get_equipment(self, equipment_id: int) -> Equipment | None:
        """Fetch one material by its id."""
        return await self._call(EQUIPMENT_ITEM, ItemArgs(item_id=equipment_id))

    async def async_list_serial_numbers_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[SerialNumber]:
        """Fetch one page of serial numbers of one material."""
        return await self._call(
            SERIAL_NUMBERS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_serial_numbers_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[SerialNumber]:
        """Yield every serial number of one material, following the cursor."""
        return self._iter_collection(
            SERIAL_NUMBERS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_stock_movements_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[StockMovement]:
        """Fetch one page of stock movements of one material."""
        return await self._call(
            STOCK_MOVEMENTS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_stock_movements_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[StockMovement]:
        """Yield every stock movement of one material, following the cursor."""
        return self._iter_collection(
            STOCK_MOVEMENTS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_repairs_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[Repair]:
        """Fetch one page of repairs of one material."""
        return await self._call(
            REPAIRS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_repairs_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Repair]:
        """Yield every repair of one material, following the cursor."""
        return self._iter_collection(
            REPAIRS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_equipment_set_content_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[EquipmentSetContent]:
        """Fetch one page of set contents of one combination material."""
        return await self._call(
            EQUIPMENT_SET_CONTENT_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_equipment_set_content_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[EquipmentSetContent]:
        """Yield every set content of one combination material, following the cursor."""
        return self._iter_collection(
            EQUIPMENT_SET_CONTENT_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_serial_numbers(
        self, query: Query | None = None
    ) -> RentmanPage[SerialNumber]:
        """Fetch one page of serial numbers."""
        return await self._call(SERIAL_NUMBERS, CollectionArgs(query=query))

    def async_iter_serial_numbers(self, query: Query | None = None) -> AsyncIterator[SerialNumber]:
        """Yield every serial number, following the cursor across pages."""
        return self._iter_collection(SERIAL_NUMBERS, CollectionArgs(query=query))

    async def async_get_serial_number(self, serial_number_id: int) -> SerialNumber | None:
        """Fetch one serial number by its id."""
        return await self._call(SERIAL_NUMBERS_ITEM, ItemArgs(item_id=serial_number_id))

    async def async_list_equipment_assigned_serials(
        self, query: Query | None = None
    ) -> RentmanPage[EquipmentAssignedSerial]:
        """Fetch one page of serial numbers assigned to combinations."""
        return await self._call(EQUIPMENT_ASSIGNED_SERIALS, CollectionArgs(query=query))

    def async_iter_equipment_assigned_serials(
        self, query: Query | None = None
    ) -> AsyncIterator[EquipmentAssignedSerial]:
        """Yield every combination assignment, following the cursor."""
        return self._iter_collection(EQUIPMENT_ASSIGNED_SERIALS, CollectionArgs(query=query))

    async def async_get_equipment_assigned_serial(
        self, assigned_serial_id: int
    ) -> EquipmentAssignedSerial | None:
        """Fetch one combination assignment by its id."""
        return await self._call(
            EQUIPMENT_ASSIGNED_SERIALS_ITEM, ItemArgs(item_id=assigned_serial_id)
        )

    async def async_list_equipment_assigned_serials_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> RentmanPage[EquipmentAssignedSerial]:
        """Fetch one page of assignments recorded inside one combination serial."""
        return await self._call(
            EQUIPMENT_ASSIGNED_SERIALS_OF_SERIAL_NUMBER,
            ParentCollectionArgs(parent_id=serial_number_id, query=query),
        )

    def async_iter_equipment_assigned_serials_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> AsyncIterator[EquipmentAssignedSerial]:
        """Yield every assignment of one combination serial, following the cursor."""
        return self._iter_collection(
            EQUIPMENT_ASSIGNED_SERIALS_OF_SERIAL_NUMBER,
            ParentCollectionArgs(parent_id=serial_number_id, query=query),
        )

    async def async_list_equipment_set_content(
        self, query: Query | None = None
    ) -> RentmanPage[EquipmentSetContent]:
        """Fetch one page of equipment set contents."""
        return await self._call(EQUIPMENT_SET_CONTENT, CollectionArgs(query=query))

    def async_iter_equipment_set_content(
        self, query: Query | None = None
    ) -> AsyncIterator[EquipmentSetContent]:
        """Yield every equipment set content, following the cursor."""
        return self._iter_collection(EQUIPMENT_SET_CONTENT, CollectionArgs(query=query))

    async def async_get_equipment_set_content(
        self, equipment_set_content_id: int
    ) -> EquipmentSetContent | None:
        """Fetch one equipment set content by its id."""
        return await self._call(
            EQUIPMENT_SET_CONTENT_ITEM, ItemArgs(item_id=equipment_set_content_id)
        )

    async def async_list_folders(self, query: Query | None = None) -> RentmanPage[Folder]:
        """Fetch one page of folders."""
        return await self._call(FOLDERS, CollectionArgs(query=query))

    def async_iter_folders(self, query: Query | None = None) -> AsyncIterator[Folder]:
        """Yield every folder, following the cursor across pages."""
        return self._iter_collection(FOLDERS, CollectionArgs(query=query))

    async def async_get_folder(self, folder_id: int) -> Folder | None:
        """Fetch one folder by its id."""
        return await self._call(FOLDERS_ITEM, ItemArgs(item_id=folder_id))

    async def async_list_stock_locations(
        self, query: Query | None = None
    ) -> RentmanPage[StockLocation]:
        """Fetch one page of stock locations."""
        return await self._call(STOCK_LOCATIONS, CollectionArgs(query=query))

    def async_iter_stock_locations(
        self, query: Query | None = None
    ) -> AsyncIterator[StockLocation]:
        """Yield every stock location, following the cursor across pages."""
        return self._iter_collection(STOCK_LOCATIONS, CollectionArgs(query=query))

    async def async_get_stock_location(self, stock_location_id: int) -> StockLocation | None:
        """Fetch one stock location by its id."""
        return await self._call(STOCK_LOCATIONS_ITEM, ItemArgs(item_id=stock_location_id))

    async def async_list_warehouse_statuses(
        self, query: Query | None = None
    ) -> RentmanPage[WarehouseStatus]:
        """Fetch one page of warehouse statuses."""
        return await self._call(WAREHOUSE_STATUSES, CollectionArgs(query=query))

    def async_iter_warehouse_statuses(
        self, query: Query | None = None
    ) -> AsyncIterator[WarehouseStatus]:
        """Yield every warehouse status, following the cursor across pages."""
        return self._iter_collection(WAREHOUSE_STATUSES, CollectionArgs(query=query))

    async def async_get_warehouse_status(self, warehouse_status_id: int) -> WarehouseStatus | None:
        """Fetch one warehouse status by its id."""
        return await self._call(WAREHOUSE_STATUSES_ITEM, ItemArgs(item_id=warehouse_status_id))

    async def async_list_statuses(self, query: Query | None = None) -> RentmanPage[Status]:
        """Fetch one page of planning statuses."""
        return await self._call(STATUSES, CollectionArgs(query=query))

    def async_iter_statuses(self, query: Query | None = None) -> AsyncIterator[Status]:
        """Yield every planning status, following the cursor across pages."""
        return self._iter_collection(STATUSES, CollectionArgs(query=query))

    async def async_get_status(self, status_id: int) -> Status | None:
        """Fetch one planning status by its id."""
        return await self._call(STATUSES_ITEM, ItemArgs(item_id=status_id))

    async def async_list_stock_movements(
        self, query: Query | None = None
    ) -> RentmanPage[StockMovement]:
        """Fetch one page of stock movements."""
        return await self._call(STOCK_MOVEMENTS, CollectionArgs(query=query))

    def async_iter_stock_movements(
        self, query: Query | None = None
    ) -> AsyncIterator[StockMovement]:
        """Yield every stock movement, following the cursor across pages."""
        return self._iter_collection(STOCK_MOVEMENTS, CollectionArgs(query=query))

    async def async_get_stock_movement(self, stock_movement_id: int) -> StockMovement | None:
        """Fetch one stock movement by its id."""
        return await self._call(STOCK_MOVEMENTS_ITEM, ItemArgs(item_id=stock_movement_id))

    async def async_list_repairs(self, query: Query | None = None) -> RentmanPage[Repair]:
        """Fetch one page of repairs."""
        return await self._call(REPAIRS, CollectionArgs(query=query))

    def async_iter_repairs(self, query: Query | None = None) -> AsyncIterator[Repair]:
        """Yield every repair, following the cursor across pages."""
        return self._iter_collection(REPAIRS, CollectionArgs(query=query))

    async def async_get_repair(self, repair_id: int) -> Repair | None:
        """Fetch one repair by its id."""
        return await self._call(REPAIRS_ITEM, ItemArgs(item_id=repair_id))

    async def async_list_projects(self, query: Query | None = None) -> RentmanPage[Project]:
        """Fetch one page of projects."""
        return await self._call(PROJECTS, CollectionArgs(query=query))

    def async_iter_projects(self, query: Query | None = None) -> AsyncIterator[Project]:
        """Yield every project, following the cursor across pages."""
        return self._iter_collection(PROJECTS, CollectionArgs(query=query))

    async def async_get_project(self, project_id: int) -> Project | None:
        """Fetch one project by its id."""
        return await self._call(PROJECTS_ITEM, ItemArgs(item_id=project_id))

    async def async_list_subprojects_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[Subproject]:
        """Fetch one page of subprojects of one project."""
        return await self._call(
            SUBPROJECTS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_subprojects_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[Subproject]:
        """Yield every subproject of one project, following the cursor."""
        return self._iter_collection(
            SUBPROJECTS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_subprojects(self, query: Query | None = None) -> RentmanPage[Subproject]:
        """Fetch one page of subprojects."""
        return await self._call(SUBPROJECTS, CollectionArgs(query=query))

    def async_iter_subprojects(self, query: Query | None = None) -> AsyncIterator[Subproject]:
        """Yield every subproject, following the cursor across pages."""
        return self._iter_collection(SUBPROJECTS, CollectionArgs(query=query))

    async def async_get_subproject(self, subproject_id: int) -> Subproject | None:
        """Fetch one subproject by its id."""
        return await self._call(SUBPROJECTS_ITEM, ItemArgs(item_id=subproject_id))

    async def async_list_project_equipment(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectEquipment]:
        """Fetch one page of planned equipment lines."""
        return await self._call(PROJECT_EQUIPMENT, CollectionArgs(query=query))

    def async_iter_project_equipment(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipment]:
        """Yield every planned equipment line, following the cursor."""
        return self._iter_collection(PROJECT_EQUIPMENT, CollectionArgs(query=query))

    async def async_get_project_equipment(
        self, project_equipment_id: int
    ) -> ProjectEquipment | None:
        """Fetch one planned equipment line by its id."""
        return await self._call(PROJECT_EQUIPMENT_ITEM, ItemArgs(item_id=project_equipment_id))

    async def async_list_project_equipment_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectEquipment]:
        """Fetch one page of planned equipment lines of one project."""
        return await self._call(
            PROJECT_EQUIPMENT_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_equipment_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipment]:
        """Yield every planned equipment line of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_EQUIPMENT_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_equipment_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectEquipment]:
        """Fetch one page of planned equipment lines of one subproject."""
        return await self._call(
            PROJECT_EQUIPMENT_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    def async_iter_project_equipment_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipment]:
        """Yield every planned equipment line of one subproject, following the cursor."""
        return self._iter_collection(
            PROJECT_EQUIPMENT_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    async def async_list_accessories(self, query: Query | None = None) -> RentmanPage[Accessory]:
        """Fetch one page of accessories."""
        return await self._call(ACCESSORIES, CollectionArgs(query=query))

    def async_iter_accessories(self, query: Query | None = None) -> AsyncIterator[Accessory]:
        """Yield every accessory, following the cursor across pages."""
        return self._iter_collection(ACCESSORIES, CollectionArgs(query=query))

    async def async_get_accessory(self, accessory_id: int) -> Accessory | None:
        """Fetch one accessory by its id."""
        return await self._call(ACCESSORIES_ITEM, ItemArgs(item_id=accessory_id))

    async def async_list_accessories_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[Accessory]:
        """Fetch one page of accessories of one material."""
        return await self._call(
            ACCESSORIES_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_accessories_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Accessory]:
        """Yield every accessory of one material, following the cursor."""
        return self._iter_collection(
            ACCESSORIES_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_alternatives(self, query: Query | None = None) -> RentmanPage[Alternative]:
        """Fetch one page of alternatives."""
        return await self._call(ALTERNATIVES, CollectionArgs(query=query))

    def async_iter_alternatives(self, query: Query | None = None) -> AsyncIterator[Alternative]:
        """Yield every alternative, following the cursor across pages."""
        return self._iter_collection(ALTERNATIVES, CollectionArgs(query=query))

    async def async_get_alternative(self, alternative_id: int) -> Alternative | None:
        """Fetch one alternative by its id."""
        return await self._call(ALTERNATIVES_ITEM, ItemArgs(item_id=alternative_id))

    async def async_list_alternatives_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[Alternative]:
        """Fetch one page of alternatives of one material."""
        return await self._call(
            ALTERNATIVES_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_alternatives_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Alternative]:
        """Yield every alternative of one material, following the cursor."""
        return self._iter_collection(
            ALTERNATIVES_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_suppliers(self, query: Query | None = None) -> RentmanPage[Supplier]:
        """Fetch one page of suppliers."""
        return await self._call(SUPPLIERS, CollectionArgs(query=query))

    def async_iter_suppliers(self, query: Query | None = None) -> AsyncIterator[Supplier]:
        """Yield every supplier, following the cursor across pages."""
        return self._iter_collection(SUPPLIERS, CollectionArgs(query=query))

    async def async_get_supplier(self, supplier_id: int) -> Supplier | None:
        """Fetch one supplier by its id."""
        return await self._call(SUPPLIERS_ITEM, ItemArgs(item_id=supplier_id))

    async def async_list_suppliers_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[Supplier]:
        """Fetch one page of suppliers of one material."""
        return await self._call(
            SUPPLIERS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    def async_iter_suppliers_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Supplier]:
        """Yield every supplier of one material, following the cursor."""
        return self._iter_collection(
            SUPPLIERS_OF_EQUIPMENT,
            ParentCollectionArgs(parent_id=equipment_id, query=query),
        )

    async def async_list_vehicles(self, query: Query | None = None) -> RentmanPage[Vehicle]:
        """Fetch one page of vehicles."""
        return await self._call(VEHICLES, CollectionArgs(query=query))

    def async_iter_vehicles(self, query: Query | None = None) -> AsyncIterator[Vehicle]:
        """Yield every vehicle, following the cursor across pages."""
        return self._iter_collection(VEHICLES, CollectionArgs(query=query))

    async def async_get_vehicle(self, vehicle_id: int) -> Vehicle | None:
        """Fetch one vehicle by its id."""
        return await self._call(VEHICLES_ITEM, ItemArgs(item_id=vehicle_id))

    async def async_list_vehicles_of_stock_location(
        self, stock_location_id: int, query: Query | None = None
    ) -> RentmanPage[Vehicle]:
        """Fetch one page of vehicles of one stock location."""
        return await self._call(
            VEHICLES_OF_STOCK_LOCATION,
            ParentCollectionArgs(parent_id=stock_location_id, query=query),
        )

    def async_iter_vehicles_of_stock_location(
        self, stock_location_id: int, query: Query | None = None
    ) -> AsyncIterator[Vehicle]:
        """Yield every vehicle of one stock location, following the cursor."""
        return self._iter_collection(
            VEHICLES_OF_STOCK_LOCATION,
            ParentCollectionArgs(parent_id=stock_location_id, query=query),
        )

    async def async_list_extra_input_fields(
        self, query: Query | None = None
    ) -> RentmanPage[ExtraInputField]:
        """Fetch one page of custom field definitions."""
        return await self._call(EXTRA_INPUT_FIELDS, CollectionArgs(query=query))

    def async_iter_extra_input_fields(
        self, query: Query | None = None
    ) -> AsyncIterator[ExtraInputField]:
        """Yield every custom field definition, following the cursor across pages."""
        return self._iter_collection(EXTRA_INPUT_FIELDS, CollectionArgs(query=query))

    async def async_get_extra_input_field(
        self, extra_input_field_id: int
    ) -> ExtraInputField | None:
        """Fetch one custom field definition by its id."""
        return await self._call(
            EXTRA_INPUT_FIELDS_ITEM,
            ItemArgs(item_id=extra_input_field_id),
        )

    async def async_list_project_statuses(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectStatus]:
        """Fetch one page of project statuses."""
        return await self._call(PROJECT_STATUSES, CollectionArgs(query=query))

    def async_iter_project_statuses(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectStatus]:
        """Yield every project status, following the cursor across pages."""
        return self._iter_collection(PROJECT_STATUSES, CollectionArgs(query=query))

    async def async_get_project_status(self, project_status_id: int) -> ProjectStatus | None:
        """Fetch one project status by its id."""
        return await self._call(PROJECT_STATUSES_ITEM, ItemArgs(item_id=project_status_id))

    async def async_list_project_types(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectType]:
        """Fetch one page of project types."""
        return await self._call(PROJECT_TYPES, CollectionArgs(query=query))

    def async_iter_project_types(self, query: Query | None = None) -> AsyncIterator[ProjectType]:
        """Yield every project type, following the cursor across pages."""
        return self._iter_collection(PROJECT_TYPES, CollectionArgs(query=query))

    async def async_get_project_type(self, project_type_id: int) -> ProjectType | None:
        """Fetch one project type by its id."""
        return await self._call(PROJECT_TYPES_ITEM, ItemArgs(item_id=project_type_id))

    async def async_list_project_function_groups(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectFunctionGroup]:
        """Fetch one page of project function groups."""
        return await self._call(PROJECT_FUNCTION_GROUPS, CollectionArgs(query=query))

    def async_iter_project_function_groups(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectFunctionGroup]:
        """Yield every project function group, following the cursor across pages."""
        return self._iter_collection(PROJECT_FUNCTION_GROUPS, CollectionArgs(query=query))

    async def async_get_project_function_group(self, group_id: int) -> ProjectFunctionGroup | None:
        """Fetch one project function group by its id."""
        return await self._call(PROJECT_FUNCTION_GROUPS_ITEM, ItemArgs(item_id=group_id))

    async def async_list_project_function_groups_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectFunctionGroup]:
        """Fetch one page of function groups of one project."""
        return await self._call(
            PROJECT_FUNCTION_GROUPS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_function_groups_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectFunctionGroup]:
        """Yield every function group of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_FUNCTION_GROUPS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_function_groups_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectFunctionGroup]:
        """Fetch one page of function groups of one subproject."""
        return await self._call(
            PROJECT_FUNCTION_GROUPS_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    def async_iter_project_function_groups_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectFunctionGroup]:
        """Yield every function group of one subproject, following the cursor."""
        return self._iter_collection(
            PROJECT_FUNCTION_GROUPS_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    async def async_list_project_functions(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectFunction]:
        """Fetch one page of project functions."""
        return await self._call(PROJECT_FUNCTIONS, CollectionArgs(query=query))

    def async_iter_project_functions(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectFunction]:
        """Yield every project function, following the cursor across pages."""
        return self._iter_collection(PROJECT_FUNCTIONS, CollectionArgs(query=query))

    async def async_get_project_function(self, function_id: int) -> ProjectFunction | None:
        """Fetch one project function by its id."""
        return await self._call(PROJECT_FUNCTIONS_ITEM, ItemArgs(item_id=function_id))

    async def async_list_project_functions_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectFunction]:
        """Fetch one page of functions of one project."""
        return await self._call(
            PROJECT_FUNCTIONS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_functions_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectFunction]:
        """Yield every function of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_FUNCTIONS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_functions_of_project_function_group(
        self, group_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectFunction]:
        """Fetch one page of functions of one function group."""
        return await self._call(
            PROJECT_FUNCTIONS_OF_PROJECT_FUNCTION_GROUP,
            ParentCollectionArgs(parent_id=group_id, query=query),
        )

    def async_iter_project_functions_of_project_function_group(
        self, group_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectFunction]:
        """Yield every function of one function group, following the cursor."""
        return self._iter_collection(
            PROJECT_FUNCTIONS_OF_PROJECT_FUNCTION_GROUP,
            ParentCollectionArgs(parent_id=group_id, query=query),
        )

    async def async_list_project_crew(self, query: Query | None = None) -> RentmanPage[ProjectCrew]:
        """Fetch one page of planned crew."""
        return await self._call(PROJECT_CREW, CollectionArgs(query=query))

    def async_iter_project_crew(self, query: Query | None = None) -> AsyncIterator[ProjectCrew]:
        """Yield every planned crew member, following the cursor across pages."""
        return self._iter_collection(PROJECT_CREW, CollectionArgs(query=query))

    async def async_get_project_crew(self, project_crew_id: int) -> ProjectCrew | None:
        """Fetch one planned crew member by its id."""
        return await self._call(PROJECT_CREW_ITEM, ItemArgs(item_id=project_crew_id))

    async def async_list_project_crew_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectCrew]:
        """Fetch one page of planned crew of one project."""
        return await self._call(
            PROJECT_CREW_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_crew_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCrew]:
        """Yield every planned crew member of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_CREW_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_crew_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectCrew]:
        """Fetch one page of planned crew of one subproject."""
        return await self._call(
            PROJECT_CREW_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    def async_iter_project_crew_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCrew]:
        """Yield every planned crew member of one subproject, following the cursor."""
        return self._iter_collection(
            PROJECT_CREW_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    async def async_list_project_crew_of_project_function(
        self, function_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectCrew]:
        """Fetch one page of crew planned on one function."""
        return await self._call(
            PROJECT_CREW_OF_PROJECT_FUNCTION,
            ParentCollectionArgs(parent_id=function_id, query=query),
        )

    def async_iter_project_crew_of_project_function(
        self, function_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCrew]:
        """Yield every crew member planned on one function, following the cursor."""
        return self._iter_collection(
            PROJECT_CREW_OF_PROJECT_FUNCTION,
            ParentCollectionArgs(parent_id=function_id, query=query),
        )

    async def async_list_project_vehicles(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectVehicle]:
        """Fetch one page of planned vehicles."""
        return await self._call(PROJECT_VEHICLES, CollectionArgs(query=query))

    def async_iter_project_vehicles(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectVehicle]:
        """Yield every planned vehicle, following the cursor across pages."""
        return self._iter_collection(PROJECT_VEHICLES, CollectionArgs(query=query))

    async def async_get_project_vehicle(self, project_vehicle_id: int) -> ProjectVehicle | None:
        """Fetch one planned vehicle by its id."""
        return await self._call(PROJECT_VEHICLES_ITEM, ItemArgs(item_id=project_vehicle_id))

    async def async_list_project_vehicles_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectVehicle]:
        """Fetch one page of planned vehicles of one project."""
        return await self._call(
            PROJECT_VEHICLES_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_vehicles_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectVehicle]:
        """Yield every planned vehicle of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_VEHICLES_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_vehicles_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectVehicle]:
        """Fetch one page of planned vehicles of one subproject."""
        return await self._call(
            PROJECT_VEHICLES_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    def async_iter_project_vehicles_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectVehicle]:
        """Yield every planned vehicle of one subproject, following the cursor."""
        return self._iter_collection(
            PROJECT_VEHICLES_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    async def async_list_project_vehicles_of_project_function(
        self, function_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectVehicle]:
        """Fetch one page of vehicles planned on one function."""
        return await self._call(
            PROJECT_VEHICLES_OF_PROJECT_FUNCTION,
            ParentCollectionArgs(parent_id=function_id, query=query),
        )

    def async_iter_project_vehicles_of_project_function(
        self, function_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectVehicle]:
        """Yield every vehicle planned on one function, following the cursor."""
        return self._iter_collection(
            PROJECT_VEHICLES_OF_PROJECT_FUNCTION,
            ParentCollectionArgs(parent_id=function_id, query=query),
        )

    async def async_list_project_equipment_groups(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectEquipmentGroup]:
        """Fetch one page of project equipment groups."""
        return await self._call(PROJECT_EQUIPMENT_GROUPS, CollectionArgs(query=query))

    def async_iter_project_equipment_groups(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipmentGroup]:
        """Yield every project equipment group, following the cursor across pages."""
        return self._iter_collection(PROJECT_EQUIPMENT_GROUPS, CollectionArgs(query=query))

    async def async_get_project_equipment_group(
        self, group_id: int
    ) -> ProjectEquipmentGroup | None:
        """Fetch one project equipment group by its id."""
        return await self._call(PROJECT_EQUIPMENT_GROUPS_ITEM, ItemArgs(item_id=group_id))

    async def async_list_project_equipment_groups_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectEquipmentGroup]:
        """Fetch one page of equipment groups of one project."""
        return await self._call(
            PROJECT_EQUIPMENT_GROUPS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_equipment_groups_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipmentGroup]:
        """Yield every equipment group of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_EQUIPMENT_GROUPS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_equipment_groups_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectEquipmentGroup]:
        """Fetch one page of equipment groups of one subproject."""
        return await self._call(
            PROJECT_EQUIPMENT_GROUPS_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    def async_iter_project_equipment_groups_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipmentGroup]:
        """Yield every equipment group of one subproject, following the cursor."""
        return self._iter_collection(
            PROJECT_EQUIPMENT_GROUPS_OF_SUBPROJECT,
            ParentCollectionArgs(parent_id=subproject_id, query=query),
        )

    async def async_list_project_equipment_of_project_equipment_group(
        self, group_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectEquipment]:
        """Fetch one page of planned equipment of one equipment group."""
        return await self._call(
            PROJECT_EQUIPMENT_OF_PROJECT_EQUIPMENT_GROUP,
            ParentCollectionArgs(parent_id=group_id, query=query),
        )

    def async_iter_project_equipment_of_project_equipment_group(
        self, group_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipment]:
        """Yield every planned equipment line of one equipment group, following the cursor."""
        return self._iter_collection(
            PROJECT_EQUIPMENT_OF_PROJECT_EQUIPMENT_GROUP,
            ParentCollectionArgs(parent_id=group_id, query=query),
        )

    async def async_list_project_costs(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectCost]:
        """Fetch one page of project cost lines."""
        return await self._call(PROJECT_COSTS, CollectionArgs(query=query))

    def async_iter_project_costs(self, query: Query | None = None) -> AsyncIterator[ProjectCost]:
        """Yield every project cost line, following the cursor across pages."""
        return self._iter_collection(PROJECT_COSTS, CollectionArgs(query=query))

    async def async_get_project_cost(self, project_cost_id: int) -> ProjectCost | None:
        """Fetch one project cost line by its id."""
        return await self._call(PROJECT_COSTS_ITEM, ItemArgs(item_id=project_cost_id))

    async def async_list_project_costs_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectCost]:
        """Fetch one page of cost lines of one project."""
        return await self._call(
            PROJECT_COSTS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    def async_iter_project_costs_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCost]:
        """Yield every cost line of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_COSTS_OF_PROJECT,
            ParentCollectionArgs(parent_id=project_id, query=query),
        )

    async def async_list_project_requests(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectRequest]:
        """Fetch one page of project requests."""
        return await self._call(PROJECT_REQUESTS, CollectionArgs(query=query))

    def async_iter_project_requests(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectRequest]:
        """Yield every project request, following the cursor across pages."""
        return self._iter_collection(PROJECT_REQUESTS, CollectionArgs(query=query))

    async def async_get_project_request(self, project_request_id: int) -> ProjectRequest | None:
        """Fetch one project request by its id."""
        return await self._call(PROJECT_REQUESTS_ITEM, ItemArgs(item_id=project_request_id))

    async def async_list_project_request_equipment(
        self, query: Query | None = None
    ) -> RentmanPage[ProjectRequestEquipment]:
        """Fetch one page of requested equipment lines."""
        return await self._call(PROJECT_REQUEST_EQUIPMENT, CollectionArgs(query=query))

    def async_iter_project_request_equipment(
        self, query: Query | None = None
    ) -> AsyncIterator[ProjectRequestEquipment]:
        """Yield every requested equipment line, following the cursor across pages."""
        return self._iter_collection(PROJECT_REQUEST_EQUIPMENT, CollectionArgs(query=query))

    async def async_get_project_request_equipment(
        self, project_request_equipment_id: int
    ) -> ProjectRequestEquipment | None:
        """Fetch one requested equipment line by its id."""
        return await self._call(
            PROJECT_REQUEST_EQUIPMENT_ITEM,
            ItemArgs(item_id=project_request_equipment_id),
        )

    async def async_list_project_request_equipment_of_project_request(
        self, project_request_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectRequestEquipment]:
        """Fetch one page of requested equipment of one project request."""
        return await self._call(
            PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST,
            ParentCollectionArgs(parent_id=project_request_id, query=query),
        )

    def async_iter_project_request_equipment_of_project_request(
        self, project_request_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectRequestEquipment]:
        """Yield every requested equipment line of one project request, following the cursor."""
        return self._iter_collection(
            PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST,
            ParentCollectionArgs(parent_id=project_request_id, query=query),
        )

    async def _call[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, ModelT],
        args: ArgsT,
        cursor_url: str | None = None,
    ) -> ModelT:
        """Run one endpoint against the API and parse the payload."""
        self._assert_open()
        payload = await self._request_json(endpoint, args, cursor_url)
        return endpoint.parse(payload, args)

    async def _request_json[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, ModelT],
        args: ArgsT,
        cursor_url: str | None,
    ) -> object:
        url, params = self._build_request(endpoint, args, cursor_url)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        async with self._pacer.request_slot():
            return await request_json(
                self._owned_session.session,
                method=endpoint.method,
                url=url,
                headers=headers,
                params=params,
                timeout=self._request_timeout,
            )

    def _build_request[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, ModelT],
        args: ArgsT,
        cursor_url: str | None,
    ) -> tuple[str, dict[str, str]]:
        if cursor_url is None:
            return f"{BASE_URL}{endpoint.path(args)}", endpoint.params(args)
        url, params = _split_cursor_url(cursor_url)
        _LOGGER.debug("Following collection cursor to %s", url)
        return url, params

    async def _iter_collection[ArgsT, ModelT](
        self,
        endpoint: Endpoint[ArgsT, RentmanPage[ModelT]],
        args: ArgsT,
    ) -> AsyncIterator[ModelT]:
        """Yield every item of one collection, following next_page_url."""
        cursor_url: str | None = None
        while True:
            page = await self._call(endpoint, args, cursor_url)
            for item in page.items:
                yield item
            if page.next_page_url is None:
                return
            cursor_url = page.next_page_url

    def _assert_open(self) -> None:
        if self._closed:
            msg = "The client is closed"
            raise RentmanClientClosedError(msg)

    async def async_close(self) -> None:
        """Close the session when this library created it."""
        self._closed = True
        await self._owned_session.close_if_owned()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.async_close()


def _split_cursor_url(url: str) -> tuple[str, dict[str, str]]:
    """Validate one next_page_url and split it into its URL and parameters."""
    split = urlsplit(url)
    if f"{split.scheme}://{split.netloc}" != BASE_URL:
        msg = f"The next page URL leaves {BASE_URL}"
        raise RentmanInvalidResponseError(msg)
    base = f"{split.scheme}://{split.netloc}{split.path}"
    return base, dict(parse_qsl(split.query, keep_blank_values=True))
