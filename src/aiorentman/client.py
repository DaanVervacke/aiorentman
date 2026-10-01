"""The RentmanClient facade: one typed method per endpoint."""

import logging
import os
from collections.abc import AsyncIterator
from typing import Self
from urllib.parse import parse_qsl, urlsplit

import aiohttp

from ._endpoints import (
    ACTUAL_CONTENT,
    ACTUAL_CONTENT_ITEM,
    ACTUAL_CONTENT_OF_SERIAL_NUMBER,
    EQUIPMENT,
    EQUIPMENT_ASSIGNED_SERIALS,
    EQUIPMENT_ASSIGNED_SERIALS_ITEM,
    EQUIPMENT_ASSIGNED_SERIALS_OF_SERIAL_NUMBER,
    EQUIPMENT_ITEM,
    EQUIPMENT_SET_CONTENT,
    EQUIPMENT_SET_CONTENT_ITEM,
    EQUIPMENT_SET_CONTENT_OF_EQUIPMENT,
    FOLDERS,
    FOLDERS_ITEM,
    PROJECT_EQUIPMENT,
    PROJECT_EQUIPMENT_ITEM,
    PROJECT_EQUIPMENT_OF_PROJECT,
    PROJECT_EQUIPMENT_OF_SUBPROJECT,
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
    ActualContent,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
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
