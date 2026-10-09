"""The RentmanClient facade: one typed method per endpoint."""

from collections.abc import AsyncIterator

from ._core import ClientCore
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
    APPOINTMENT_CREW,
    APPOINTMENT_CREW_ITEM,
    APPOINTMENT_CREW_OF_APPOINTMENT,
    APPOINTMENTS,
    APPOINTMENTS_ITEM,
    APPOINTMENTS_OF_CREW,
    CONTACT_PERSONS,
    CONTACT_PERSONS_ITEM,
    CONTACT_PERSONS_OF_CONTACT,
    CONTACTS,
    CONTACTS_ITEM,
    CONTRACTS,
    CONTRACTS_ITEM,
    CONTRACTS_OF_PROJECT,
    CREATE_ACCESSORY_OF_EQUIPMENT,
    CREATE_ALTERNATIVE_OF_EQUIPMENT,
    CREATE_APPOINTMENT,
    CREATE_APPOINTMENT_CREW_OF_APPOINTMENT,
    CREATE_CONTACT,
    CREATE_CONTACT_PERSON_OF_CONTACT,
    CREATE_CREW_AVAILABILITY_OF_CREW,
    CREATE_EQUIPMENT,
    CREATE_EQUIPMENT_SET_CONTENT_OF_EQUIPMENT,
    CREATE_FOLDER,
    CREATE_LEAVE_MUTATION,
    CREATE_LEAVE_REQUEST,
    CREATE_PAYMENT_OF_INVOICE,
    CREATE_PROJECT,
    CREATE_PROJECT_COST_OF_PROJECT,
    CREATE_PROJECT_FUNCTION_GROUP_OF_PROJECT,
    CREATE_PROJECT_FUNCTION_OF_PROJECT,
    CREATE_PROJECT_REQUEST,
    CREATE_PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST,
    CREATE_SERIAL_NUMBER_OF_EQUIPMENT,
    CREATE_STOCK_MOVEMENT_OF_EQUIPMENT,
    CREATE_SUBPROJECT_OF_PROJECT,
    CREATE_SUBTASK_OF_TASK,
    CREATE_SUPPLIER_OF_EQUIPMENT,
    CREATE_TASK,
    CREATE_TASK_ASSIGNMENT_OF_TASK,
    CREATE_TASK_OF_CONTACT,
    CREATE_TASK_OF_CONTACT_PERSON,
    CREATE_TASK_OF_CONTRACT,
    CREATE_TASK_OF_CREW,
    CREATE_TASK_OF_EQUIPMENT,
    CREATE_TASK_OF_INVOICE,
    CREATE_TASK_OF_PROJECT,
    CREATE_TASK_OF_PURCHASE_ORDER,
    CREATE_TASK_OF_QUOTE,
    CREATE_TASK_OF_REPAIR,
    CREATE_TASK_OF_SERIAL_NUMBER,
    CREATE_TASK_OF_SUBRENTAL,
    CREATE_TASK_OF_SUPPLIER,
    CREATE_TASK_OF_VEHICLE,
    CREATE_TASK_STATUS,
    CREATE_TIME_REGISTRATION,
    CREATE_TIME_REGISTRATION_OF_LEAVE_REQUEST,
    CREATE_VEHICLE,
    CREATE_VEHICLE_OF_STOCK_LOCATION,
    CREW,
    CREW_AVAILABILITY,
    CREW_AVAILABILITY_ITEM,
    CREW_AVAILABILITY_OF_CREW,
    CREW_ITEM,
    CREW_RATES,
    CREW_RATES_ITEM,
    CREW_RATES_OF_CREW,
    DELETE_ACCESSORY,
    DELETE_ALTERNATIVE,
    DELETE_APPOINTMENT,
    DELETE_APPOINTMENT_CREW,
    DELETE_CONTACT,
    DELETE_CONTACT_PERSON,
    DELETE_CREW_AVAILABILITY,
    DELETE_EQUIPMENT_SET_CONTENT,
    DELETE_PROJECT_COST,
    DELETE_PROJECT_REQUEST,
    DELETE_PROJECT_REQUEST_EQUIPMENT,
    DELETE_SERIAL_NUMBER,
    DELETE_STOCK_MOVEMENT,
    DELETE_SUBTASK,
    DELETE_SUPPLIER,
    DELETE_TASK,
    DELETE_TASK_ASSIGNMENT,
    DELETE_TASK_STATUS,
    DELETE_TIME_REGISTRATION,
    DELETE_VEHICLE,
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
    FACTOR_GROUPS,
    FACTOR_GROUPS_ITEM,
    FACTORS,
    FACTORS_ITEM,
    FACTORS_OF_FACTOR_GROUP,
    FILE_FOLDERS,
    FILE_FOLDERS_ITEM,
    FILE_FOLDERS_OF_CONTACT,
    FILE_FOLDERS_OF_CONTACT_PERSON,
    FILE_FOLDERS_OF_CREW,
    FILE_FOLDERS_OF_EQUIPMENT,
    FILE_FOLDERS_OF_PROJECT,
    FILE_FOLDERS_OF_PURCHASE_ORDER,
    FILE_FOLDERS_OF_REPAIR,
    FILE_FOLDERS_OF_SERIAL_NUMBER,
    FILE_FOLDERS_OF_SUBPROJECT,
    FILE_FOLDERS_OF_SUBRENTAL,
    FILE_FOLDERS_OF_SUPPLIER,
    FILE_FOLDERS_OF_TASK,
    FILE_FOLDERS_OF_VEHICLE,
    FILES,
    FILES_ITEM,
    FILES_OF_CONTACT,
    FILES_OF_CONTACT_PERSON,
    FILES_OF_CREW,
    FILES_OF_EQUIPMENT,
    FILES_OF_INVOICE,
    FILES_OF_PROJECT,
    FILES_OF_PURCHASE_ORDER,
    FILES_OF_QUOTE,
    FILES_OF_REPAIR,
    FILES_OF_SERIAL_NUMBER,
    FILES_OF_SUBRENTAL,
    FILES_OF_SUPPLIER,
    FILES_OF_TASK,
    FILES_OF_TIME_REGISTRATION,
    FILES_OF_VEHICLE,
    FOLDERS,
    FOLDERS_ITEM,
    INVITATIONS,
    INVITATIONS_ITEM,
    INVITATIONS_OF_CREW,
    INVOICE_LINES,
    INVOICE_LINES_ITEM,
    INVOICE_LINES_OF_INVOICE,
    INVOICE_LINES_OF_PURCHASE_ORDER,
    INVOICE_LINES_OF_QUOTE,
    INVOICES,
    INVOICES_ITEM,
    LEAVE_MUTATIONS,
    LEAVE_MUTATIONS_ITEM,
    LEAVE_REQUESTS,
    LEAVE_REQUESTS_ITEM,
    LEAVE_TYPES,
    LEAVE_TYPES_ITEM,
    LEDGER_CODES,
    LEDGER_CODES_ITEM,
    PAYMENTS,
    PAYMENTS_ITEM,
    PAYMENTS_OF_INVOICE,
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
    PURCHASE_ORDER_COSTS,
    PURCHASE_ORDER_COSTS_ITEM,
    PURCHASE_ORDER_COSTS_OF_PURCHASE_ORDER,
    PURCHASE_ORDER_GLOBAL_COSTS,
    PURCHASE_ORDER_GLOBAL_COSTS_ITEM,
    PURCHASE_ORDER_GLOBAL_COSTS_OF_PURCHASE_ORDER,
    PURCHASE_ORDERS,
    PURCHASE_ORDERS_ITEM,
    QUOTES,
    QUOTES_ITEM,
    QUOTES_OF_PROJECT,
    RATE_FACTORS,
    RATE_FACTORS_ITEM,
    RATE_FACTORS_OF_RATE,
    RATES,
    RATES_ITEM,
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
    SUBRENTAL_EQUIPMENT,
    SUBRENTAL_EQUIPMENT_GROUPS,
    SUBRENTAL_EQUIPMENT_GROUPS_ITEM,
    SUBRENTAL_EQUIPMENT_GROUPS_OF_SUBRENTAL,
    SUBRENTAL_EQUIPMENT_ITEM,
    SUBRENTAL_EQUIPMENT_OF_SUBRENTAL,
    SUBRENTAL_EQUIPMENT_OF_SUBRENTAL_EQUIPMENT_GROUP,
    SUBRENTALS,
    SUBRENTALS_ITEM,
    SUBTASKS,
    SUBTASKS_ITEM,
    SUBTASKS_OF_TASK,
    SUPPLIERS,
    SUPPLIERS_ITEM,
    SUPPLIERS_OF_EQUIPMENT,
    TASK_ASSIGNMENTS,
    TASK_ASSIGNMENTS_ITEM,
    TASK_ASSIGNMENTS_OF_TASK,
    TASK_STATUSES,
    TASK_STATUSES_ITEM,
    TASKS,
    TASKS_ITEM,
    TASKS_OF_CONTACT,
    TASKS_OF_CONTACT_PERSON,
    TASKS_OF_CREW,
    TASKS_OF_EQUIPMENT,
    TASKS_OF_INVOICE,
    TASKS_OF_PROJECT,
    TASKS_OF_PURCHASE_ORDER,
    TASKS_OF_QUOTE,
    TASKS_OF_REPAIR,
    TASKS_OF_SERIAL_NUMBER,
    TASKS_OF_SUBRENTAL,
    TASKS_OF_SUPPLIER,
    TASKS_OF_VEHICLE,
    TAX_CLASSES,
    TAX_CLASSES_ITEM,
    TIME_REGISTRATION_ACTIVITIES,
    TIME_REGISTRATION_ACTIVITIES_ITEM,
    TIME_REGISTRATION_ACTIVITIES_OF_TIME_REGISTRATION,
    TIME_REGISTRATIONS,
    TIME_REGISTRATIONS_ITEM,
    TIME_REGISTRATIONS_OF_LEAVE_REQUEST,
    UPDATE_ACCESSORY,
    UPDATE_ALTERNATIVE,
    UPDATE_APPOINTMENT,
    UPDATE_APPOINTMENT_CREW,
    UPDATE_CONTACT,
    UPDATE_CONTACT_PERSON,
    UPDATE_CREW_AVAILABILITY,
    UPDATE_EQUIPMENT,
    UPDATE_EQUIPMENT_SET_CONTENT,
    UPDATE_FOLDER,
    UPDATE_LEAVE_REQUEST,
    UPDATE_PAYMENT,
    UPDATE_PROJECT_COST,
    UPDATE_PROJECT_REQUEST,
    UPDATE_PROJECT_REQUEST_EQUIPMENT,
    UPDATE_SERIAL_NUMBER,
    UPDATE_STOCK_MOVEMENT,
    UPDATE_SUBTASK,
    UPDATE_SUPPLIER,
    UPDATE_TASK,
    UPDATE_TASK_ASSIGNMENT,
    UPDATE_TASK_STATUS,
    UPDATE_TIME_REGISTRATION,
    UPDATE_VEHICLE,
    VEHICLES,
    VEHICLES_ITEM,
    VEHICLES_OF_STOCK_LOCATION,
    WAREHOUSE_STATUSES,
    WAREHOUSE_STATUSES_ITEM,
    CollectionArgs,
    CreateArgs,
    DeleteArgs,
    ItemArgs,
    LinkedCreateArgs,
    ParentCollectionArgs,
    UpdateArgs,
)
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
from .payloads import (
    AccessoryPayload,
    AlternativePayload,
    AppointmentCrewPayload,
    AppointmentPayload,
    ContactPayload,
    ContactPersonPayload,
    CrewAvailabilityPayload,
    EquipmentPayload,
    EquipmentSetContentPayload,
    FolderPayload,
    LeaveMutationPayload,
    LeaveRequestPayload,
    PaymentPayload,
    ProjectCostPayload,
    ProjectFunctionGroupPayload,
    ProjectFunctionPayload,
    ProjectPayload,
    ProjectRequestEquipmentPayload,
    ProjectRequestPayload,
    SerialNumberPayload,
    StockMovementPayload,
    SubprojectPayload,
    SubtaskPayload,
    SupplierPayload,
    TaskAssignmentPayload,
    TaskPayload,
    TaskStatusPayload,
    TimeRegistrationPayload,
    VehiclePayload,
)
from .query import Query


class RentmanClient(ClientCore):
    """Asynchronous client for the Rentman API.

    The client covers every documented read path, with create, update,
    and delete methods for every documented write path. Every request is paced against the
    documented rate limits unless pacing is disabled with
    ``requests_per_second=None``.
    """

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
            SERIAL_NUMBERS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_serial_numbers_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[SerialNumber]:
        """Yield every serial number of one material, following the cursor."""
        return self._iter_collection(
            SERIAL_NUMBERS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    async def async_list_stock_movements_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[StockMovement]:
        """Fetch one page of stock movements of one material."""
        return await self._call(
            STOCK_MOVEMENTS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_stock_movements_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[StockMovement]:
        """Yield every stock movement of one material, following the cursor."""
        return self._iter_collection(
            STOCK_MOVEMENTS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    async def async_list_repairs_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[Repair]:
        """Fetch one page of repairs of one material."""
        return await self._call(
            REPAIRS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_repairs_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Repair]:
        """Yield every repair of one material, following the cursor."""
        return self._iter_collection(
            REPAIRS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
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
            SUBPROJECTS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_subprojects_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[Subproject]:
        """Yield every subproject of one project, following the cursor."""
        return self._iter_collection(
            SUBPROJECTS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
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
            PROJECT_EQUIPMENT_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_project_equipment_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectEquipment]:
        """Yield every planned equipment line of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_EQUIPMENT_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
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
            ACCESSORIES_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_accessories_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Accessory]:
        """Yield every accessory of one material, following the cursor."""
        return self._iter_collection(
            ACCESSORIES_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
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
            ALTERNATIVES_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_alternatives_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Alternative]:
        """Yield every alternative of one material, following the cursor."""
        return self._iter_collection(
            ALTERNATIVES_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
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
            SUPPLIERS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_suppliers_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Supplier]:
        """Yield every supplier of one material, following the cursor."""
        return self._iter_collection(
            SUPPLIERS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
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
        return await self._call(EXTRA_INPUT_FIELDS_ITEM, ItemArgs(item_id=extra_input_field_id))

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
            PROJECT_FUNCTIONS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_project_functions_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectFunction]:
        """Yield every function of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_FUNCTIONS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
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
            PROJECT_CREW_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_project_crew_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCrew]:
        """Yield every planned crew member of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_CREW_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    async def async_list_project_crew_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[ProjectCrew]:
        """Fetch one page of planned crew of one subproject."""
        return await self._call(
            PROJECT_CREW_OF_SUBPROJECT, ParentCollectionArgs(parent_id=subproject_id, query=query)
        )

    def async_iter_project_crew_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCrew]:
        """Yield every planned crew member of one subproject, following the cursor."""
        return self._iter_collection(
            PROJECT_CREW_OF_SUBPROJECT, ParentCollectionArgs(parent_id=subproject_id, query=query)
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
            PROJECT_VEHICLES_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_project_vehicles_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectVehicle]:
        """Yield every planned vehicle of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_VEHICLES_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
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
            PROJECT_COSTS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_project_costs_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[ProjectCost]:
        """Yield every cost line of one project, following the cursor."""
        return self._iter_collection(
            PROJECT_COSTS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
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
            PROJECT_REQUEST_EQUIPMENT_ITEM, ItemArgs(item_id=project_request_equipment_id)
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

    async def async_list_quotes(self, query: Query | None = None) -> RentmanPage[Quote]:
        """Fetch one page of quotes."""
        return await self._call(QUOTES, CollectionArgs(query=query))

    def async_iter_quotes(self, query: Query | None = None) -> AsyncIterator[Quote]:
        """Yield every quote, following the cursor across pages."""
        return self._iter_collection(QUOTES, CollectionArgs(query=query))

    async def async_get_quote(self, quote_id: int) -> Quote | None:
        """Fetch one quote by its id."""
        return await self._call(QUOTES_ITEM, ItemArgs(item_id=quote_id))

    async def async_list_quotes_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[Quote]:
        """Fetch one page of quotes of one project."""
        return await self._call(
            QUOTES_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_quotes_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[Quote]:
        """Yield every quote of one project, following the cursor."""
        return self._iter_collection(
            QUOTES_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    async def async_list_invoice_lines_of_quote(
        self, quote_id: int, query: Query | None = None
    ) -> RentmanPage[InvoiceLine]:
        """Fetch one page of invoice lines of one quote."""
        return await self._call(
            INVOICE_LINES_OF_QUOTE, ParentCollectionArgs(parent_id=quote_id, query=query)
        )

    def async_iter_invoice_lines_of_quote(
        self, quote_id: int, query: Query | None = None
    ) -> AsyncIterator[InvoiceLine]:
        """Yield every invoice line of one quote, following the cursor."""
        return self._iter_collection(
            INVOICE_LINES_OF_QUOTE, ParentCollectionArgs(parent_id=quote_id, query=query)
        )

    async def async_list_contracts(self, query: Query | None = None) -> RentmanPage[Contract]:
        """Fetch one page of contracts."""
        return await self._call(CONTRACTS, CollectionArgs(query=query))

    def async_iter_contracts(self, query: Query | None = None) -> AsyncIterator[Contract]:
        """Yield every contract, following the cursor across pages."""
        return self._iter_collection(CONTRACTS, CollectionArgs(query=query))

    async def async_get_contract(self, contract_id: int) -> Contract | None:
        """Fetch one contract by its id."""
        return await self._call(CONTRACTS_ITEM, ItemArgs(item_id=contract_id))

    async def async_list_contracts_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[Contract]:
        """Fetch one page of contracts of one project."""
        return await self._call(
            CONTRACTS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_contracts_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[Contract]:
        """Yield every contract of one project, following the cursor."""
        return self._iter_collection(
            CONTRACTS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    async def async_list_invoices(self, query: Query | None = None) -> RentmanPage[Invoice]:
        """Fetch one page of invoices."""
        return await self._call(INVOICES, CollectionArgs(query=query))

    def async_iter_invoices(self, query: Query | None = None) -> AsyncIterator[Invoice]:
        """Yield every invoice, following the cursor across pages."""
        return self._iter_collection(INVOICES, CollectionArgs(query=query))

    async def async_get_invoice(self, invoice_id: int) -> Invoice | None:
        """Fetch one invoice by its id."""
        return await self._call(INVOICES_ITEM, ItemArgs(item_id=invoice_id))

    async def async_list_invoice_lines_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> RentmanPage[InvoiceLine]:
        """Fetch one page of invoice lines of one invoice."""
        return await self._call(
            INVOICE_LINES_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    def async_iter_invoice_lines_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> AsyncIterator[InvoiceLine]:
        """Yield every invoice line of one invoice, following the cursor."""
        return self._iter_collection(
            INVOICE_LINES_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    async def async_list_payments_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> RentmanPage[Payment]:
        """Fetch one page of payments of one invoice."""
        return await self._call(
            PAYMENTS_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    def async_iter_payments_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> AsyncIterator[Payment]:
        """Yield every payment of one invoice, following the cursor."""
        return self._iter_collection(
            PAYMENTS_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    async def async_list_invoice_lines(
        self, query: Query | None = None
    ) -> RentmanPage[InvoiceLine]:
        """Fetch one page of invoice lines."""
        return await self._call(INVOICE_LINES, CollectionArgs(query=query))

    def async_iter_invoice_lines(self, query: Query | None = None) -> AsyncIterator[InvoiceLine]:
        """Yield every invoice line, following the cursor across pages."""
        return self._iter_collection(INVOICE_LINES, CollectionArgs(query=query))

    async def async_get_invoice_line(self, invoice_line_id: int) -> InvoiceLine | None:
        """Fetch one invoice line by its id."""
        return await self._call(INVOICE_LINES_ITEM, ItemArgs(item_id=invoice_line_id))

    async def async_list_payments(self, query: Query | None = None) -> RentmanPage[Payment]:
        """Fetch one page of payments."""
        return await self._call(PAYMENTS, CollectionArgs(query=query))

    def async_iter_payments(self, query: Query | None = None) -> AsyncIterator[Payment]:
        """Yield every payment, following the cursor across pages."""
        return self._iter_collection(PAYMENTS, CollectionArgs(query=query))

    async def async_get_payment(self, payment_id: int) -> Payment | None:
        """Fetch one payment by its id."""
        return await self._call(PAYMENTS_ITEM, ItemArgs(item_id=payment_id))

    async def async_list_ledger_codes(self, query: Query | None = None) -> RentmanPage[LedgerCode]:
        """Fetch one page of ledger codes."""
        return await self._call(LEDGER_CODES, CollectionArgs(query=query))

    def async_iter_ledger_codes(self, query: Query | None = None) -> AsyncIterator[LedgerCode]:
        """Yield every ledger code, following the cursor across pages."""
        return self._iter_collection(LEDGER_CODES, CollectionArgs(query=query))

    async def async_get_ledger_code(self, ledger_code_id: int) -> LedgerCode | None:
        """Fetch one ledger code by its id."""
        return await self._call(LEDGER_CODES_ITEM, ItemArgs(item_id=ledger_code_id))

    async def async_list_tax_classes(self, query: Query | None = None) -> RentmanPage[TaxClass]:
        """Fetch one page of tax classes."""
        return await self._call(TAX_CLASSES, CollectionArgs(query=query))

    def async_iter_tax_classes(self, query: Query | None = None) -> AsyncIterator[TaxClass]:
        """Yield every tax class, following the cursor across pages."""
        return self._iter_collection(TAX_CLASSES, CollectionArgs(query=query))

    async def async_get_tax_class(self, tax_class_id: int) -> TaxClass | None:
        """Fetch one tax class by its id."""
        return await self._call(TAX_CLASSES_ITEM, ItemArgs(item_id=tax_class_id))

    async def async_list_subrentals(self, query: Query | None = None) -> RentmanPage[Subrental]:
        """Fetch one page of subrentals."""
        return await self._call(SUBRENTALS, CollectionArgs(query=query))

    def async_iter_subrentals(self, query: Query | None = None) -> AsyncIterator[Subrental]:
        """Yield every subrental, following the cursor across pages."""
        return self._iter_collection(SUBRENTALS, CollectionArgs(query=query))

    async def async_get_subrental(self, subrental_id: int) -> Subrental | None:
        """Fetch one subrental by its id."""
        return await self._call(SUBRENTALS_ITEM, ItemArgs(item_id=subrental_id))

    async def async_list_subrental_equipment_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> RentmanPage[SubrentalEquipment]:
        """Fetch one page of equipment of one subrental."""
        return await self._call(
            SUBRENTAL_EQUIPMENT_OF_SUBRENTAL,
            ParentCollectionArgs(parent_id=subrental_id, query=query),
        )

    def async_iter_subrental_equipment_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> AsyncIterator[SubrentalEquipment]:
        """Yield every equipment line of one subrental, following the cursor."""
        return self._iter_collection(
            SUBRENTAL_EQUIPMENT_OF_SUBRENTAL,
            ParentCollectionArgs(parent_id=subrental_id, query=query),
        )

    async def async_list_subrental_equipment_groups_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> RentmanPage[SubrentalEquipmentGroup]:
        """Fetch one page of equipment groups of one subrental."""
        return await self._call(
            SUBRENTAL_EQUIPMENT_GROUPS_OF_SUBRENTAL,
            ParentCollectionArgs(parent_id=subrental_id, query=query),
        )

    def async_iter_subrental_equipment_groups_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> AsyncIterator[SubrentalEquipmentGroup]:
        """Yield every equipment group of one subrental, following the cursor."""
        return self._iter_collection(
            SUBRENTAL_EQUIPMENT_GROUPS_OF_SUBRENTAL,
            ParentCollectionArgs(parent_id=subrental_id, query=query),
        )

    async def async_list_subrental_equipment(
        self, query: Query | None = None
    ) -> RentmanPage[SubrentalEquipment]:
        """Fetch one page of subrental equipment lines."""
        return await self._call(SUBRENTAL_EQUIPMENT, CollectionArgs(query=query))

    def async_iter_subrental_equipment(
        self, query: Query | None = None
    ) -> AsyncIterator[SubrentalEquipment]:
        """Yield every subrental equipment line, following the cursor across pages."""
        return self._iter_collection(SUBRENTAL_EQUIPMENT, CollectionArgs(query=query))

    async def async_get_subrental_equipment(
        self, subrental_equipment_id: int
    ) -> SubrentalEquipment | None:
        """Fetch one subrental equipment line by its id."""
        return await self._call(SUBRENTAL_EQUIPMENT_ITEM, ItemArgs(item_id=subrental_equipment_id))

    async def async_list_subrental_equipment_of_subrental_equipment_group(
        self, group_id: int, query: Query | None = None
    ) -> RentmanPage[SubrentalEquipment]:
        """Fetch one page of equipment of one subrental equipment group."""
        return await self._call(
            SUBRENTAL_EQUIPMENT_OF_SUBRENTAL_EQUIPMENT_GROUP,
            ParentCollectionArgs(parent_id=group_id, query=query),
        )

    def async_iter_subrental_equipment_of_subrental_equipment_group(
        self, group_id: int, query: Query | None = None
    ) -> AsyncIterator[SubrentalEquipment]:
        """Yield every equipment line of one subrental group, following the cursor."""
        return self._iter_collection(
            SUBRENTAL_EQUIPMENT_OF_SUBRENTAL_EQUIPMENT_GROUP,
            ParentCollectionArgs(parent_id=group_id, query=query),
        )

    async def async_list_subrental_equipment_groups(
        self, query: Query | None = None
    ) -> RentmanPage[SubrentalEquipmentGroup]:
        """Fetch one page of subrental equipment groups."""
        return await self._call(SUBRENTAL_EQUIPMENT_GROUPS, CollectionArgs(query=query))

    def async_iter_subrental_equipment_groups(
        self, query: Query | None = None
    ) -> AsyncIterator[SubrentalEquipmentGroup]:
        """Yield every subrental equipment group, following the cursor across pages."""
        return self._iter_collection(SUBRENTAL_EQUIPMENT_GROUPS, CollectionArgs(query=query))

    async def async_get_subrental_equipment_group(
        self, group_id: int
    ) -> SubrentalEquipmentGroup | None:
        """Fetch one subrental equipment group by its id."""
        return await self._call(SUBRENTAL_EQUIPMENT_GROUPS_ITEM, ItemArgs(item_id=group_id))

    async def async_list_purchase_orders(
        self, query: Query | None = None
    ) -> RentmanPage[PurchaseOrder]:
        """Fetch one page of purchase orders."""
        return await self._call(PURCHASE_ORDERS, CollectionArgs(query=query))

    def async_iter_purchase_orders(
        self, query: Query | None = None
    ) -> AsyncIterator[PurchaseOrder]:
        """Yield every purchase order, following the cursor across pages."""
        return self._iter_collection(PURCHASE_ORDERS, CollectionArgs(query=query))

    async def async_get_purchase_order(self, purchase_order_id: int) -> PurchaseOrder | None:
        """Fetch one purchase order by its id."""
        return await self._call(PURCHASE_ORDERS_ITEM, ItemArgs(item_id=purchase_order_id))

    async def async_list_invoice_lines_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> RentmanPage[InvoiceLine]:
        """Fetch one page of invoice lines of one purchase order."""
        return await self._call(
            INVOICE_LINES_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    def async_iter_invoice_lines_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> AsyncIterator[InvoiceLine]:
        """Yield every invoice line of one purchase order, following the cursor."""
        return self._iter_collection(
            INVOICE_LINES_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    async def async_list_purchase_order_costs_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> RentmanPage[PurchaseOrderCost]:
        """Fetch one page of cost lines of one purchase order."""
        return await self._call(
            PURCHASE_ORDER_COSTS_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    def async_iter_purchase_order_costs_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> AsyncIterator[PurchaseOrderCost]:
        """Yield every cost line of one purchase order, following the cursor."""
        return self._iter_collection(
            PURCHASE_ORDER_COSTS_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    async def async_list_purchase_order_global_costs_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> RentmanPage[PurchaseOrderGlobalCost]:
        """Fetch one page of global cost lines of one purchase order."""
        return await self._call(
            PURCHASE_ORDER_GLOBAL_COSTS_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    def async_iter_purchase_order_global_costs_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> AsyncIterator[PurchaseOrderGlobalCost]:
        """Yield every global cost line of one purchase order, following the cursor."""
        return self._iter_collection(
            PURCHASE_ORDER_GLOBAL_COSTS_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    async def async_list_purchase_order_costs(
        self, query: Query | None = None
    ) -> RentmanPage[PurchaseOrderCost]:
        """Fetch one page of purchase order cost lines."""
        return await self._call(PURCHASE_ORDER_COSTS, CollectionArgs(query=query))

    def async_iter_purchase_order_costs(
        self, query: Query | None = None
    ) -> AsyncIterator[PurchaseOrderCost]:
        """Yield every purchase order cost line, following the cursor across pages."""
        return self._iter_collection(PURCHASE_ORDER_COSTS, CollectionArgs(query=query))

    async def async_get_purchase_order_cost(
        self, purchase_order_cost_id: int
    ) -> PurchaseOrderCost | None:
        """Fetch one purchase order cost line by its id."""
        return await self._call(PURCHASE_ORDER_COSTS_ITEM, ItemArgs(item_id=purchase_order_cost_id))

    async def async_list_purchase_order_global_costs(
        self, query: Query | None = None
    ) -> RentmanPage[PurchaseOrderGlobalCost]:
        """Fetch one page of purchase order global cost lines."""
        return await self._call(PURCHASE_ORDER_GLOBAL_COSTS, CollectionArgs(query=query))

    def async_iter_purchase_order_global_costs(
        self, query: Query | None = None
    ) -> AsyncIterator[PurchaseOrderGlobalCost]:
        """Yield every purchase order global cost line, following the cursor across pages."""
        return self._iter_collection(PURCHASE_ORDER_GLOBAL_COSTS, CollectionArgs(query=query))

    async def async_get_purchase_order_global_cost(
        self, purchase_order_global_cost_id: int
    ) -> PurchaseOrderGlobalCost | None:
        """Fetch one purchase order global cost line by its id."""
        return await self._call(
            PURCHASE_ORDER_GLOBAL_COSTS_ITEM, ItemArgs(item_id=purchase_order_global_cost_id)
        )

    async def async_list_crew(self, query: Query | None = None) -> RentmanPage[Crew]:
        """Fetch one page of crew members."""
        return await self._call(CREW, CollectionArgs(query=query))

    def async_iter_crew(self, query: Query | None = None) -> AsyncIterator[Crew]:
        """Yield every crew member, following the cursor across pages."""
        return self._iter_collection(CREW, CollectionArgs(query=query))

    async def async_get_crew(self, crew_id: int) -> Crew | None:
        """Fetch one crew member by their id."""
        return await self._call(CREW_ITEM, ItemArgs(item_id=crew_id))

    async def async_list_appointments_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[Appointment]:
        """Fetch one page of appointments of one crew member."""
        return await self._call(
            APPOINTMENTS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    def async_iter_appointments_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[Appointment]:
        """Yield every appointment of one crew member, following the cursor."""
        return self._iter_collection(
            APPOINTMENTS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_crew_availability_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[CrewAvailability]:
        """Fetch one page of availability windows of one crew member."""
        return await self._call(
            CREW_AVAILABILITY_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    def async_iter_crew_availability_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[CrewAvailability]:
        """Yield every availability window of one crew member, following the cursor."""
        return self._iter_collection(
            CREW_AVAILABILITY_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_crew_rates_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[CrewRate]:
        """Fetch one page of rates of one crew member."""
        return await self._call(
            CREW_RATES_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    def async_iter_crew_rates_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[CrewRate]:
        """Yield every rate of one crew member, following the cursor."""
        return self._iter_collection(
            CREW_RATES_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_invitations_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[Invitation]:
        """Fetch one page of invitations of one crew member."""
        return await self._call(
            INVITATIONS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    def async_iter_invitations_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[Invitation]:
        """Yield every invitation of one crew member, following the cursor."""
        return self._iter_collection(
            INVITATIONS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_crew_availability(
        self, query: Query | None = None
    ) -> RentmanPage[CrewAvailability]:
        """Fetch one page of availability windows."""
        return await self._call(CREW_AVAILABILITY, CollectionArgs(query=query))

    def async_iter_crew_availability(
        self, query: Query | None = None
    ) -> AsyncIterator[CrewAvailability]:
        """Yield every availability window, following the cursor across pages."""
        return self._iter_collection(CREW_AVAILABILITY, CollectionArgs(query=query))

    async def async_get_crew_availability(self, availability_id: int) -> CrewAvailability | None:
        """Fetch one availability window by its id."""
        return await self._call(CREW_AVAILABILITY_ITEM, ItemArgs(item_id=availability_id))

    async def async_list_crew_rates(self, query: Query | None = None) -> RentmanPage[CrewRate]:
        """Fetch one page of crew rates."""
        return await self._call(CREW_RATES, CollectionArgs(query=query))

    def async_iter_crew_rates(self, query: Query | None = None) -> AsyncIterator[CrewRate]:
        """Yield every crew rate, following the cursor across pages."""
        return self._iter_collection(CREW_RATES, CollectionArgs(query=query))

    async def async_get_crew_rate(self, crew_rate_id: int) -> CrewRate | None:
        """Fetch one crew rate by its id."""
        return await self._call(CREW_RATES_ITEM, ItemArgs(item_id=crew_rate_id))

    async def async_list_invitations(self, query: Query | None = None) -> RentmanPage[Invitation]:
        """Fetch one page of planning invitations."""
        return await self._call(INVITATIONS, CollectionArgs(query=query))

    def async_iter_invitations(self, query: Query | None = None) -> AsyncIterator[Invitation]:
        """Yield every planning invitation, following the cursor across pages."""
        return self._iter_collection(INVITATIONS, CollectionArgs(query=query))

    async def async_get_invitation(self, invitation_id: int) -> Invitation | None:
        """Fetch one planning invitation by its id."""
        return await self._call(INVITATIONS_ITEM, ItemArgs(item_id=invitation_id))

    async def async_list_appointments(self, query: Query | None = None) -> RentmanPage[Appointment]:
        """Fetch one page of appointments."""
        return await self._call(APPOINTMENTS, CollectionArgs(query=query))

    def async_iter_appointments(self, query: Query | None = None) -> AsyncIterator[Appointment]:
        """Yield every appointment, following the cursor across pages."""
        return self._iter_collection(APPOINTMENTS, CollectionArgs(query=query))

    async def async_get_appointment(self, appointment_id: int) -> Appointment | None:
        """Fetch one appointment by its id."""
        return await self._call(APPOINTMENTS_ITEM, ItemArgs(item_id=appointment_id))

    async def async_list_appointment_crew_of_appointment(
        self, appointment_id: int, query: Query | None = None
    ) -> RentmanPage[AppointmentCrew]:
        """Fetch one page of crew attached to one appointment."""
        return await self._call(
            APPOINTMENT_CREW_OF_APPOINTMENT,
            ParentCollectionArgs(parent_id=appointment_id, query=query),
        )

    def async_iter_appointment_crew_of_appointment(
        self, appointment_id: int, query: Query | None = None
    ) -> AsyncIterator[AppointmentCrew]:
        """Yield every crew member attached to one appointment, following the cursor."""
        return self._iter_collection(
            APPOINTMENT_CREW_OF_APPOINTMENT,
            ParentCollectionArgs(parent_id=appointment_id, query=query),
        )

    async def async_list_appointment_crew(
        self, query: Query | None = None
    ) -> RentmanPage[AppointmentCrew]:
        """Fetch one page of appointment crew attachments."""
        return await self._call(APPOINTMENT_CREW, CollectionArgs(query=query))

    def async_iter_appointment_crew(
        self, query: Query | None = None
    ) -> AsyncIterator[AppointmentCrew]:
        """Yield every appointment crew attachment, following the cursor across pages."""
        return self._iter_collection(APPOINTMENT_CREW, CollectionArgs(query=query))

    async def async_get_appointment_crew(self, appointment_crew_id: int) -> AppointmentCrew | None:
        """Fetch one appointment crew attachment by its id."""
        return await self._call(APPOINTMENT_CREW_ITEM, ItemArgs(item_id=appointment_crew_id))

    async def async_list_time_registrations(
        self, query: Query | None = None
    ) -> RentmanPage[TimeRegistration]:
        """Fetch one page of time registrations."""
        return await self._call(TIME_REGISTRATIONS, CollectionArgs(query=query))

    def async_iter_time_registrations(
        self, query: Query | None = None
    ) -> AsyncIterator[TimeRegistration]:
        """Yield every time registration, following the cursor across pages."""
        return self._iter_collection(TIME_REGISTRATIONS, CollectionArgs(query=query))

    async def async_get_time_registration(
        self, time_registration_id: int
    ) -> TimeRegistration | None:
        """Fetch one time registration by its id."""
        return await self._call(TIME_REGISTRATIONS_ITEM, ItemArgs(item_id=time_registration_id))

    async def async_list_time_registration_activities_of_time_registration(
        self, time_registration_id: int, query: Query | None = None
    ) -> RentmanPage[TimeRegistrationActivity]:
        """Fetch one page of activities of one time registration."""
        return await self._call(
            TIME_REGISTRATION_ACTIVITIES_OF_TIME_REGISTRATION,
            ParentCollectionArgs(parent_id=time_registration_id, query=query),
        )

    def async_iter_time_registration_activities_of_time_registration(
        self, time_registration_id: int, query: Query | None = None
    ) -> AsyncIterator[TimeRegistrationActivity]:
        """Yield every activity of one time registration, following the cursor."""
        return self._iter_collection(
            TIME_REGISTRATION_ACTIVITIES_OF_TIME_REGISTRATION,
            ParentCollectionArgs(parent_id=time_registration_id, query=query),
        )

    async def async_list_time_registration_activities(
        self, query: Query | None = None
    ) -> RentmanPage[TimeRegistrationActivity]:
        """Fetch one page of time registration activities."""
        return await self._call(TIME_REGISTRATION_ACTIVITIES, CollectionArgs(query=query))

    def async_iter_time_registration_activities(
        self, query: Query | None = None
    ) -> AsyncIterator[TimeRegistrationActivity]:
        """Yield every time registration activity, following the cursor across pages."""
        return self._iter_collection(TIME_REGISTRATION_ACTIVITIES, CollectionArgs(query=query))

    async def async_get_time_registration_activity(
        self, activity_id: int
    ) -> TimeRegistrationActivity | None:
        """Fetch one time registration activity by its id."""
        return await self._call(TIME_REGISTRATION_ACTIVITIES_ITEM, ItemArgs(item_id=activity_id))

    async def async_list_leave_requests(
        self, query: Query | None = None
    ) -> RentmanPage[LeaveRequest]:
        """Fetch one page of leave requests."""
        return await self._call(LEAVE_REQUESTS, CollectionArgs(query=query))

    def async_iter_leave_requests(self, query: Query | None = None) -> AsyncIterator[LeaveRequest]:
        """Yield every leave request, following the cursor across pages."""
        return self._iter_collection(LEAVE_REQUESTS, CollectionArgs(query=query))

    async def async_get_leave_request(self, leave_request_id: int) -> LeaveRequest | None:
        """Fetch one leave request by its id."""
        return await self._call(LEAVE_REQUESTS_ITEM, ItemArgs(item_id=leave_request_id))

    async def async_list_time_registrations_of_leave_request(
        self, leave_request_id: int, query: Query | None = None
    ) -> RentmanPage[TimeRegistration]:
        """Fetch one page of time registrations of one leave request."""
        return await self._call(
            TIME_REGISTRATIONS_OF_LEAVE_REQUEST,
            ParentCollectionArgs(parent_id=leave_request_id, query=query),
        )

    def async_iter_time_registrations_of_leave_request(
        self, leave_request_id: int, query: Query | None = None
    ) -> AsyncIterator[TimeRegistration]:
        """Yield every time registration of one leave request, following the cursor."""
        return self._iter_collection(
            TIME_REGISTRATIONS_OF_LEAVE_REQUEST,
            ParentCollectionArgs(parent_id=leave_request_id, query=query),
        )

    async def async_list_leave_mutations(
        self, query: Query | None = None
    ) -> RentmanPage[LeaveMutation]:
        """Fetch one page of leave balance mutations."""
        return await self._call(LEAVE_MUTATIONS, CollectionArgs(query=query))

    def async_iter_leave_mutations(
        self, query: Query | None = None
    ) -> AsyncIterator[LeaveMutation]:
        """Yield every leave balance mutation, following the cursor across pages."""
        return self._iter_collection(LEAVE_MUTATIONS, CollectionArgs(query=query))

    async def async_get_leave_mutation(self, leave_mutation_id: int) -> LeaveMutation | None:
        """Fetch one leave balance mutation by its id."""
        return await self._call(LEAVE_MUTATIONS_ITEM, ItemArgs(item_id=leave_mutation_id))

    async def async_list_leave_types(self, query: Query | None = None) -> RentmanPage[LeaveType]:
        """Fetch one page of leave types."""
        return await self._call(LEAVE_TYPES, CollectionArgs(query=query))

    def async_iter_leave_types(self, query: Query | None = None) -> AsyncIterator[LeaveType]:
        """Yield every leave type, following the cursor across pages."""
        return self._iter_collection(LEAVE_TYPES, CollectionArgs(query=query))

    async def async_get_leave_type(self, leave_type_id: int) -> LeaveType | None:
        """Fetch one leave type by its id."""
        return await self._call(LEAVE_TYPES_ITEM, ItemArgs(item_id=leave_type_id))

    async def async_list_contacts(self, query: Query | None = None) -> RentmanPage[Contact]:
        """Fetch one page of contacts."""
        return await self._call(CONTACTS, CollectionArgs(query=query))

    def async_iter_contacts(self, query: Query | None = None) -> AsyncIterator[Contact]:
        """Yield every contact, following the cursor across pages."""
        return self._iter_collection(CONTACTS, CollectionArgs(query=query))

    async def async_get_contact(self, contact_id: int) -> Contact | None:
        """Fetch one contact by its id."""
        return await self._call(CONTACTS_ITEM, ItemArgs(item_id=contact_id))

    async def async_list_contact_persons_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> RentmanPage[ContactPerson]:
        """Fetch one page of contact persons of one contact."""
        return await self._call(
            CONTACT_PERSONS_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    def async_iter_contact_persons_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> AsyncIterator[ContactPerson]:
        """Yield every contact person of one contact, following the cursor."""
        return self._iter_collection(
            CONTACT_PERSONS_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    async def async_list_contact_persons(
        self, query: Query | None = None
    ) -> RentmanPage[ContactPerson]:
        """Fetch one page of contact persons."""
        return await self._call(CONTACT_PERSONS, CollectionArgs(query=query))

    def async_iter_contact_persons(
        self, query: Query | None = None
    ) -> AsyncIterator[ContactPerson]:
        """Yield every contact person, following the cursor across pages."""
        return self._iter_collection(CONTACT_PERSONS, CollectionArgs(query=query))

    async def async_get_contact_person(self, contact_person_id: int) -> ContactPerson | None:
        """Fetch one contact person by their id."""
        return await self._call(CONTACT_PERSONS_ITEM, ItemArgs(item_id=contact_person_id))

    async def async_list_tasks(self, query: Query | None = None) -> RentmanPage[Task]:
        """Fetch one page of tasks."""
        return await self._call(TASKS, CollectionArgs(query=query))

    def async_iter_tasks(self, query: Query | None = None) -> AsyncIterator[Task]:
        """Yield every task, following the cursor across pages."""
        return self._iter_collection(TASKS, CollectionArgs(query=query))

    async def async_get_task(self, task_id: int) -> Task | None:
        """Fetch one task by its id."""
        return await self._call(TASKS_ITEM, ItemArgs(item_id=task_id))

    async def async_list_subtasks(self, query: Query | None = None) -> RentmanPage[Subtask]:
        """Fetch one page of subtasks."""
        return await self._call(SUBTASKS, CollectionArgs(query=query))

    def async_iter_subtasks(self, query: Query | None = None) -> AsyncIterator[Subtask]:
        """Yield every subtask, following the cursor across pages."""
        return self._iter_collection(SUBTASKS, CollectionArgs(query=query))

    async def async_get_subtask(self, subtask_id: int) -> Subtask | None:
        """Fetch one subtask by its id."""
        return await self._call(SUBTASKS_ITEM, ItemArgs(item_id=subtask_id))

    async def async_list_task_assignments(
        self, query: Query | None = None
    ) -> RentmanPage[TaskAssignment]:
        """Fetch one page of task assignments."""
        return await self._call(TASK_ASSIGNMENTS, CollectionArgs(query=query))

    def async_iter_task_assignments(
        self, query: Query | None = None
    ) -> AsyncIterator[TaskAssignment]:
        """Yield every task_assignment, following the cursor across pages."""
        return self._iter_collection(TASK_ASSIGNMENTS, CollectionArgs(query=query))

    async def async_get_task_assignment(self, task_assignment_id: int) -> TaskAssignment | None:
        """Fetch one task assignment by its id."""
        return await self._call(TASK_ASSIGNMENTS_ITEM, ItemArgs(item_id=task_assignment_id))

    async def async_list_task_statuses(self, query: Query | None = None) -> RentmanPage[TaskStatus]:
        """Fetch one page of task statuses."""
        return await self._call(TASK_STATUSES, CollectionArgs(query=query))

    def async_iter_task_statuses(self, query: Query | None = None) -> AsyncIterator[TaskStatus]:
        """Yield every task_status, following the cursor across pages."""
        return self._iter_collection(TASK_STATUSES, CollectionArgs(query=query))

    async def async_get_task_status(self, task_status_id: int) -> TaskStatus | None:
        """Fetch one task status by its id."""
        return await self._call(TASK_STATUSES_ITEM, ItemArgs(item_id=task_status_id))

    async def async_list_files(self, query: Query | None = None) -> RentmanPage[File]:
        """Fetch one page of files."""
        return await self._call(FILES, CollectionArgs(query=query))

    def async_iter_files(self, query: Query | None = None) -> AsyncIterator[File]:
        """Yield every file, following the cursor across pages."""
        return self._iter_collection(FILES, CollectionArgs(query=query))

    async def async_get_file(self, file_id: int) -> File | None:
        """Fetch one file by its id."""
        return await self._call(FILES_ITEM, ItemArgs(item_id=file_id))

    async def async_list_file_folders(self, query: Query | None = None) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders."""
        return await self._call(FILE_FOLDERS, CollectionArgs(query=query))

    def async_iter_file_folders(self, query: Query | None = None) -> AsyncIterator[FileFolder]:
        """Yield every file_folder, following the cursor across pages."""
        return self._iter_collection(FILE_FOLDERS, CollectionArgs(query=query))

    async def async_get_file_folder(self, file_folder_id: int) -> FileFolder | None:
        """Fetch one file folder by its id."""
        return await self._call(FILE_FOLDERS_ITEM, ItemArgs(item_id=file_folder_id))

    async def async_list_subtasks_of_task(
        self, task_id: int, query: Query | None = None
    ) -> RentmanPage[Subtask]:
        """Fetch one page of subtasks of one task."""
        return await self._call(
            SUBTASKS_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    def async_iter_subtasks_of_task(
        self, task_id: int, query: Query | None = None
    ) -> AsyncIterator[Subtask]:
        """Yield every subtask of one task, following the cursor."""
        return self._iter_collection(
            SUBTASKS_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    async def async_list_task_assignments_of_task(
        self, task_id: int, query: Query | None = None
    ) -> RentmanPage[TaskAssignment]:
        """Fetch one page of task assignments of one task."""
        return await self._call(
            TASK_ASSIGNMENTS_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    def async_iter_task_assignments_of_task(
        self, task_id: int, query: Query | None = None
    ) -> AsyncIterator[TaskAssignment]:
        """Yield every task assignment of one task, following the cursor."""
        return self._iter_collection(
            TASK_ASSIGNMENTS_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    async def async_list_files_of_task(
        self, task_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one task."""
        return await self._call(FILES_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query))

    def async_iter_files_of_task(
        self, task_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one task, following the cursor."""
        return self._iter_collection(
            FILES_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    async def async_list_file_folders_of_task(
        self, task_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one task."""
        return await self._call(
            FILE_FOLDERS_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    def async_iter_file_folders_of_task(
        self, task_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one task, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_TASK, ParentCollectionArgs(parent_id=task_id, query=query)
        )

    async def async_list_tasks_of_contact_person(
        self, contact_person_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one contact person."""
        return await self._call(
            TASKS_OF_CONTACT_PERSON, ParentCollectionArgs(parent_id=contact_person_id, query=query)
        )

    def async_iter_tasks_of_contact_person(
        self, contact_person_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one contact person, following the cursor."""
        return self._iter_collection(
            TASKS_OF_CONTACT_PERSON, ParentCollectionArgs(parent_id=contact_person_id, query=query)
        )

    async def async_list_tasks_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one contact."""
        return await self._call(
            TASKS_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    def async_iter_tasks_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one contact, following the cursor."""
        return self._iter_collection(
            TASKS_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    async def async_list_tasks_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one crew member."""
        return await self._call(TASKS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query))

    def async_iter_tasks_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one crew member, following the cursor."""
        return self._iter_collection(
            TASKS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_tasks_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one material."""
        return await self._call(
            TASKS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_tasks_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one material, following the cursor."""
        return self._iter_collection(
            TASKS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    async def async_list_tasks_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one invoice."""
        return await self._call(
            TASKS_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    def async_iter_tasks_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one invoice, following the cursor."""
        return self._iter_collection(
            TASKS_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    async def async_list_tasks_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one project."""
        return await self._call(
            TASKS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_tasks_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one project, following the cursor."""
        return self._iter_collection(
            TASKS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    async def async_list_tasks_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one purchase order."""
        return await self._call(
            TASKS_OF_PURCHASE_ORDER, ParentCollectionArgs(parent_id=purchase_order_id, query=query)
        )

    def async_iter_tasks_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one purchase order, following the cursor."""
        return self._iter_collection(
            TASKS_OF_PURCHASE_ORDER, ParentCollectionArgs(parent_id=purchase_order_id, query=query)
        )

    async def async_list_tasks_of_quote(
        self, quote_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one quote."""
        return await self._call(
            TASKS_OF_QUOTE, ParentCollectionArgs(parent_id=quote_id, query=query)
        )

    def async_iter_tasks_of_quote(
        self, quote_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one quote, following the cursor."""
        return self._iter_collection(
            TASKS_OF_QUOTE, ParentCollectionArgs(parent_id=quote_id, query=query)
        )

    async def async_list_tasks_of_repair(
        self, repair_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one repair."""
        return await self._call(
            TASKS_OF_REPAIR, ParentCollectionArgs(parent_id=repair_id, query=query)
        )

    def async_iter_tasks_of_repair(
        self, repair_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one repair, following the cursor."""
        return self._iter_collection(
            TASKS_OF_REPAIR, ParentCollectionArgs(parent_id=repair_id, query=query)
        )

    async def async_list_tasks_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one serial number."""
        return await self._call(
            TASKS_OF_SERIAL_NUMBER, ParentCollectionArgs(parent_id=serial_number_id, query=query)
        )

    def async_iter_tasks_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one serial number, following the cursor."""
        return self._iter_collection(
            TASKS_OF_SERIAL_NUMBER, ParentCollectionArgs(parent_id=serial_number_id, query=query)
        )

    async def async_list_tasks_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one subrental."""
        return await self._call(
            TASKS_OF_SUBRENTAL, ParentCollectionArgs(parent_id=subrental_id, query=query)
        )

    def async_iter_tasks_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one subrental, following the cursor."""
        return self._iter_collection(
            TASKS_OF_SUBRENTAL, ParentCollectionArgs(parent_id=subrental_id, query=query)
        )

    async def async_list_tasks_of_vehicle(
        self, vehicle_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one vehicle."""
        return await self._call(
            TASKS_OF_VEHICLE, ParentCollectionArgs(parent_id=vehicle_id, query=query)
        )

    def async_iter_tasks_of_vehicle(
        self, vehicle_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one vehicle, following the cursor."""
        return self._iter_collection(
            TASKS_OF_VEHICLE, ParentCollectionArgs(parent_id=vehicle_id, query=query)
        )

    async def async_list_tasks_of_supplier(
        self, supplier_id: int, query: Query | None = None
    ) -> RentmanPage[Task]:
        """Fetch one page of tasks of one supplier."""
        return await self._call(
            TASKS_OF_SUPPLIER, ParentCollectionArgs(parent_id=supplier_id, query=query)
        )

    def async_iter_tasks_of_supplier(
        self, supplier_id: int, query: Query | None = None
    ) -> AsyncIterator[Task]:
        """Yield every task of one supplier, following the cursor."""
        return self._iter_collection(
            TASKS_OF_SUPPLIER, ParentCollectionArgs(parent_id=supplier_id, query=query)
        )

    async def async_list_files_of_contact_person(
        self, contact_person_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one contact person."""
        return await self._call(
            FILES_OF_CONTACT_PERSON, ParentCollectionArgs(parent_id=contact_person_id, query=query)
        )

    def async_iter_files_of_contact_person(
        self, contact_person_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one contact person, following the cursor."""
        return self._iter_collection(
            FILES_OF_CONTACT_PERSON, ParentCollectionArgs(parent_id=contact_person_id, query=query)
        )

    async def async_list_files_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one contact."""
        return await self._call(
            FILES_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    def async_iter_files_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one contact, following the cursor."""
        return self._iter_collection(
            FILES_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    async def async_list_files_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one crew member."""
        return await self._call(FILES_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query))

    def async_iter_files_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one crew member, following the cursor."""
        return self._iter_collection(
            FILES_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_files_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one material."""
        return await self._call(
            FILES_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_files_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one material, following the cursor."""
        return self._iter_collection(
            FILES_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    async def async_list_files_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one invoice."""
        return await self._call(
            FILES_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    def async_iter_files_of_invoice(
        self, invoice_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one invoice, following the cursor."""
        return self._iter_collection(
            FILES_OF_INVOICE, ParentCollectionArgs(parent_id=invoice_id, query=query)
        )

    async def async_list_files_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one project."""
        return await self._call(
            FILES_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_files_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one project, following the cursor."""
        return self._iter_collection(
            FILES_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    async def async_list_files_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one purchase order."""
        return await self._call(
            FILES_OF_PURCHASE_ORDER, ParentCollectionArgs(parent_id=purchase_order_id, query=query)
        )

    def async_iter_files_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one purchase order, following the cursor."""
        return self._iter_collection(
            FILES_OF_PURCHASE_ORDER, ParentCollectionArgs(parent_id=purchase_order_id, query=query)
        )

    async def async_list_files_of_quote(
        self, quote_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one quote."""
        return await self._call(
            FILES_OF_QUOTE, ParentCollectionArgs(parent_id=quote_id, query=query)
        )

    def async_iter_files_of_quote(
        self, quote_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one quote, following the cursor."""
        return self._iter_collection(
            FILES_OF_QUOTE, ParentCollectionArgs(parent_id=quote_id, query=query)
        )

    async def async_list_files_of_repair(
        self, repair_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one repair."""
        return await self._call(
            FILES_OF_REPAIR, ParentCollectionArgs(parent_id=repair_id, query=query)
        )

    def async_iter_files_of_repair(
        self, repair_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one repair, following the cursor."""
        return self._iter_collection(
            FILES_OF_REPAIR, ParentCollectionArgs(parent_id=repair_id, query=query)
        )

    async def async_list_files_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one serial number."""
        return await self._call(
            FILES_OF_SERIAL_NUMBER, ParentCollectionArgs(parent_id=serial_number_id, query=query)
        )

    def async_iter_files_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one serial number, following the cursor."""
        return self._iter_collection(
            FILES_OF_SERIAL_NUMBER, ParentCollectionArgs(parent_id=serial_number_id, query=query)
        )

    async def async_list_files_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one subrental."""
        return await self._call(
            FILES_OF_SUBRENTAL, ParentCollectionArgs(parent_id=subrental_id, query=query)
        )

    def async_iter_files_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one subrental, following the cursor."""
        return self._iter_collection(
            FILES_OF_SUBRENTAL, ParentCollectionArgs(parent_id=subrental_id, query=query)
        )

    async def async_list_files_of_time_registration(
        self, time_registration_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one time registration."""
        return await self._call(
            FILES_OF_TIME_REGISTRATION,
            ParentCollectionArgs(parent_id=time_registration_id, query=query),
        )

    def async_iter_files_of_time_registration(
        self, time_registration_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one time registration, following the cursor."""
        return self._iter_collection(
            FILES_OF_TIME_REGISTRATION,
            ParentCollectionArgs(parent_id=time_registration_id, query=query),
        )

    async def async_list_files_of_vehicle(
        self, vehicle_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one vehicle."""
        return await self._call(
            FILES_OF_VEHICLE, ParentCollectionArgs(parent_id=vehicle_id, query=query)
        )

    def async_iter_files_of_vehicle(
        self, vehicle_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one vehicle, following the cursor."""
        return self._iter_collection(
            FILES_OF_VEHICLE, ParentCollectionArgs(parent_id=vehicle_id, query=query)
        )

    async def async_list_files_of_supplier(
        self, supplier_id: int, query: Query | None = None
    ) -> RentmanPage[File]:
        """Fetch one page of files of one supplier."""
        return await self._call(
            FILES_OF_SUPPLIER, ParentCollectionArgs(parent_id=supplier_id, query=query)
        )

    def async_iter_files_of_supplier(
        self, supplier_id: int, query: Query | None = None
    ) -> AsyncIterator[File]:
        """Yield every file of one supplier, following the cursor."""
        return self._iter_collection(
            FILES_OF_SUPPLIER, ParentCollectionArgs(parent_id=supplier_id, query=query)
        )

    async def async_list_file_folders_of_contact_person(
        self, contact_person_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one contact person."""
        return await self._call(
            FILE_FOLDERS_OF_CONTACT_PERSON,
            ParentCollectionArgs(parent_id=contact_person_id, query=query),
        )

    def async_iter_file_folders_of_contact_person(
        self, contact_person_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one contact person, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_CONTACT_PERSON,
            ParentCollectionArgs(parent_id=contact_person_id, query=query),
        )

    async def async_list_file_folders_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one contact."""
        return await self._call(
            FILE_FOLDERS_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    def async_iter_file_folders_of_contact(
        self, contact_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one contact, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_CONTACT, ParentCollectionArgs(parent_id=contact_id, query=query)
        )

    async def async_list_file_folders_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one crew member."""
        return await self._call(
            FILE_FOLDERS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    def async_iter_file_folders_of_crew(
        self, crew_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one crew member, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_CREW, ParentCollectionArgs(parent_id=crew_id, query=query)
        )

    async def async_list_file_folders_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one material."""
        return await self._call(
            FILE_FOLDERS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    def async_iter_file_folders_of_equipment(
        self, equipment_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one material, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_EQUIPMENT, ParentCollectionArgs(parent_id=equipment_id, query=query)
        )

    async def async_list_file_folders_of_project(
        self, project_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one project."""
        return await self._call(
            FILE_FOLDERS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    def async_iter_file_folders_of_project(
        self, project_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one project, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_PROJECT, ParentCollectionArgs(parent_id=project_id, query=query)
        )

    async def async_list_file_folders_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one purchase order."""
        return await self._call(
            FILE_FOLDERS_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    def async_iter_file_folders_of_purchase_order(
        self, purchase_order_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one purchase order, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_PURCHASE_ORDER,
            ParentCollectionArgs(parent_id=purchase_order_id, query=query),
        )

    async def async_list_file_folders_of_repair(
        self, repair_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one repair."""
        return await self._call(
            FILE_FOLDERS_OF_REPAIR, ParentCollectionArgs(parent_id=repair_id, query=query)
        )

    def async_iter_file_folders_of_repair(
        self, repair_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one repair, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_REPAIR, ParentCollectionArgs(parent_id=repair_id, query=query)
        )

    async def async_list_file_folders_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one serial number."""
        return await self._call(
            FILE_FOLDERS_OF_SERIAL_NUMBER,
            ParentCollectionArgs(parent_id=serial_number_id, query=query),
        )

    def async_iter_file_folders_of_serial_number(
        self, serial_number_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one serial number, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_SERIAL_NUMBER,
            ParentCollectionArgs(parent_id=serial_number_id, query=query),
        )

    async def async_list_file_folders_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one subproject."""
        return await self._call(
            FILE_FOLDERS_OF_SUBPROJECT, ParentCollectionArgs(parent_id=subproject_id, query=query)
        )

    def async_iter_file_folders_of_subproject(
        self, subproject_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one subproject, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_SUBPROJECT, ParentCollectionArgs(parent_id=subproject_id, query=query)
        )

    async def async_list_file_folders_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one subrental."""
        return await self._call(
            FILE_FOLDERS_OF_SUBRENTAL, ParentCollectionArgs(parent_id=subrental_id, query=query)
        )

    def async_iter_file_folders_of_subrental(
        self, subrental_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one subrental, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_SUBRENTAL, ParentCollectionArgs(parent_id=subrental_id, query=query)
        )

    async def async_list_file_folders_of_supplier(
        self, supplier_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one supplier."""
        return await self._call(
            FILE_FOLDERS_OF_SUPPLIER, ParentCollectionArgs(parent_id=supplier_id, query=query)
        )

    def async_iter_file_folders_of_supplier(
        self, supplier_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one supplier, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_SUPPLIER, ParentCollectionArgs(parent_id=supplier_id, query=query)
        )

    async def async_list_file_folders_of_vehicle(
        self, vehicle_id: int, query: Query | None = None
    ) -> RentmanPage[FileFolder]:
        """Fetch one page of file folders of one vehicle."""
        return await self._call(
            FILE_FOLDERS_OF_VEHICLE, ParentCollectionArgs(parent_id=vehicle_id, query=query)
        )

    def async_iter_file_folders_of_vehicle(
        self, vehicle_id: int, query: Query | None = None
    ) -> AsyncIterator[FileFolder]:
        """Yield every file folder of one vehicle, following the cursor."""
        return self._iter_collection(
            FILE_FOLDERS_OF_VEHICLE, ParentCollectionArgs(parent_id=vehicle_id, query=query)
        )

    async def async_list_rates(self, query: Query | None = None) -> RentmanPage[Rate]:
        """Fetch one page of rates."""
        return await self._call(RATES, CollectionArgs(query=query))

    def async_iter_rates(self, query: Query | None = None) -> AsyncIterator[Rate]:
        """Yield every rate, following the cursor across pages."""
        return self._iter_collection(RATES, CollectionArgs(query=query))

    async def async_get_rate(self, rate_id: int) -> Rate | None:
        """Fetch one rate by its id."""
        return await self._call(RATES_ITEM, ItemArgs(item_id=rate_id))

    async def async_list_rate_factors(self, query: Query | None = None) -> RentmanPage[RateFactor]:
        """Fetch one page of rate factors."""
        return await self._call(RATE_FACTORS, CollectionArgs(query=query))

    def async_iter_rate_factors(self, query: Query | None = None) -> AsyncIterator[RateFactor]:
        """Yield every rate factor, following the cursor across pages."""
        return self._iter_collection(RATE_FACTORS, CollectionArgs(query=query))

    async def async_get_rate_factor(self, rate_factor_id: int) -> RateFactor | None:
        """Fetch one rate factor by its id."""
        return await self._call(RATE_FACTORS_ITEM, ItemArgs(item_id=rate_factor_id))

    async def async_list_rate_factors_of_rate(
        self, rate_id: int, query: Query | None = None
    ) -> RentmanPage[RateFactor]:
        """Fetch one page of rate factors of one rate."""
        return await self._call(
            RATE_FACTORS_OF_RATE, ParentCollectionArgs(parent_id=rate_id, query=query)
        )

    def async_iter_rate_factors_of_rate(
        self, rate_id: int, query: Query | None = None
    ) -> AsyncIterator[RateFactor]:
        """Yield every rate factor of one rate, following the cursor."""
        return self._iter_collection(
            RATE_FACTORS_OF_RATE, ParentCollectionArgs(parent_id=rate_id, query=query)
        )

    async def async_list_factors(self, query: Query | None = None) -> RentmanPage[Factor]:
        """Fetch one page of factors."""
        return await self._call(FACTORS, CollectionArgs(query=query))

    def async_iter_factors(self, query: Query | None = None) -> AsyncIterator[Factor]:
        """Yield every factor, following the cursor across pages."""
        return self._iter_collection(FACTORS, CollectionArgs(query=query))

    async def async_get_factor(self, factor_id: int) -> Factor | None:
        """Fetch one factor by its id."""
        return await self._call(FACTORS_ITEM, ItemArgs(item_id=factor_id))

    async def async_list_factors_of_factor_group(
        self, factor_group_id: int, query: Query | None = None
    ) -> RentmanPage[Factor]:
        """Fetch one page of factors of one factor group."""
        return await self._call(
            FACTORS_OF_FACTOR_GROUP, ParentCollectionArgs(parent_id=factor_group_id, query=query)
        )

    def async_iter_factors_of_factor_group(
        self, factor_group_id: int, query: Query | None = None
    ) -> AsyncIterator[Factor]:
        """Yield every factor of one factor group, following the cursor."""
        return self._iter_collection(
            FACTORS_OF_FACTOR_GROUP, ParentCollectionArgs(parent_id=factor_group_id, query=query)
        )

    async def async_list_factor_groups(
        self, query: Query | None = None
    ) -> RentmanPage[FactorGroup]:
        """Fetch one page of factor groups."""
        return await self._call(FACTOR_GROUPS, CollectionArgs(query=query))

    def async_iter_factor_groups(self, query: Query | None = None) -> AsyncIterator[FactorGroup]:
        """Yield every factor group, following the cursor across pages."""
        return self._iter_collection(FACTOR_GROUPS, CollectionArgs(query=query))

    async def async_get_factor_group(self, factor_group_id: int) -> FactorGroup | None:
        """Fetch one factor group by its id."""
        return await self._call(FACTOR_GROUPS_ITEM, ItemArgs(item_id=factor_group_id))

    async def async_create_appointment(self, payload: AppointmentPayload) -> Appointment | None:
        """Create one appointment."""
        return await self._call(CREATE_APPOINTMENT, CreateArgs(payload))

    async def async_create_contact(self, payload: ContactPayload) -> Contact | None:
        """Create one contact."""
        return await self._call(CREATE_CONTACT, CreateArgs(payload))

    async def async_create_equipment(self, payload: EquipmentPayload) -> Equipment | None:
        """Create one material."""
        return await self._call(CREATE_EQUIPMENT, CreateArgs(payload))

    async def async_create_folder(self, payload: FolderPayload) -> Folder | None:
        """Create one folder."""
        return await self._call(CREATE_FOLDER, CreateArgs(payload))

    async def async_create_leave_request(self, payload: LeaveRequestPayload) -> LeaveRequest | None:
        """Create one leave request."""
        return await self._call(CREATE_LEAVE_REQUEST, CreateArgs(payload))

    async def async_create_leave_mutation(
        self, payload: LeaveMutationPayload
    ) -> LeaveMutation | None:
        """Create one leave mutation."""
        return await self._call(CREATE_LEAVE_MUTATION, CreateArgs(payload))

    async def async_create_project_request(
        self, payload: ProjectRequestPayload
    ) -> ProjectRequest | None:
        """Create one project request."""
        return await self._call(CREATE_PROJECT_REQUEST, CreateArgs(payload))

    async def async_create_project(self, payload: ProjectPayload) -> Project | None:
        """Create one project."""
        return await self._call(CREATE_PROJECT, CreateArgs(payload))

    async def async_create_task(self, payload: TaskPayload) -> Task | None:
        """Create one task."""
        return await self._call(CREATE_TASK, CreateArgs(payload))

    async def async_create_task_status(self, payload: TaskStatusPayload) -> TaskStatus | None:
        """Create one task status."""
        return await self._call(CREATE_TASK_STATUS, CreateArgs(payload))

    async def async_create_time_registration(
        self, payload: TimeRegistrationPayload
    ) -> TimeRegistration | None:
        """Create one time registration."""
        return await self._call(CREATE_TIME_REGISTRATION, CreateArgs(payload))

    async def async_create_vehicle(self, payload: VehiclePayload) -> Vehicle | None:
        """Create one vehicle."""
        return await self._call(CREATE_VEHICLE, CreateArgs(payload))

    async def async_create_appointment_crew_of_appointment(
        self, appointment_id: int, payload: AppointmentCrewPayload
    ) -> AppointmentCrew | None:
        """Create one appointment crew on one appointment."""
        return await self._call(
            CREATE_APPOINTMENT_CREW_OF_APPOINTMENT, LinkedCreateArgs(appointment_id, payload)
        )

    async def async_create_contact_person_of_contact(
        self, contact_id: int, payload: ContactPersonPayload
    ) -> ContactPerson | None:
        """Create one contact person on one contact."""
        return await self._call(
            CREATE_CONTACT_PERSON_OF_CONTACT, LinkedCreateArgs(contact_id, payload)
        )

    async def async_create_crew_availability_of_crew(
        self, crew_id: int, payload: CrewAvailabilityPayload
    ) -> CrewAvailability | None:
        """Create one crew availability on one crew member."""
        return await self._call(
            CREATE_CREW_AVAILABILITY_OF_CREW, LinkedCreateArgs(crew_id, payload)
        )

    async def async_create_accessory_of_equipment(
        self, equipment_id: int, payload: AccessoryPayload
    ) -> Accessory | None:
        """Create one accessory on one material."""
        return await self._call(
            CREATE_ACCESSORY_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload)
        )

    async def async_create_alternative_of_equipment(
        self, equipment_id: int, payload: AlternativePayload
    ) -> Alternative | None:
        """Create one alternative on one material."""
        return await self._call(
            CREATE_ALTERNATIVE_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload)
        )

    async def async_create_equipment_set_content_of_equipment(
        self, equipment_id: int, payload: EquipmentSetContentPayload
    ) -> EquipmentSetContent | None:
        """Create one equipment set content on one material."""
        return await self._call(
            CREATE_EQUIPMENT_SET_CONTENT_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload)
        )

    async def async_create_serial_number_of_equipment(
        self, equipment_id: int, payload: SerialNumberPayload
    ) -> SerialNumber | None:
        """Create one serial number on one material."""
        return await self._call(
            CREATE_SERIAL_NUMBER_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload)
        )

    async def async_create_stock_movement_of_equipment(
        self, equipment_id: int, payload: StockMovementPayload
    ) -> StockMovement | None:
        """Create one stock movement on one material."""
        return await self._call(
            CREATE_STOCK_MOVEMENT_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload)
        )

    async def async_create_supplier_of_equipment(
        self, equipment_id: int, payload: SupplierPayload
    ) -> Supplier | None:
        """Create one supplier on one material."""
        return await self._call(
            CREATE_SUPPLIER_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload)
        )

    async def async_create_payment_of_invoice(
        self, invoice_id: int, payload: PaymentPayload
    ) -> Payment | None:
        """Create one payment on one invoice."""
        return await self._call(CREATE_PAYMENT_OF_INVOICE, LinkedCreateArgs(invoice_id, payload))

    async def async_create_time_registration_of_leave_request(
        self, leave_request_id: int, payload: TimeRegistrationPayload
    ) -> TimeRegistration | None:
        """Create one time registration on one leave request."""
        return await self._call(
            CREATE_TIME_REGISTRATION_OF_LEAVE_REQUEST, LinkedCreateArgs(leave_request_id, payload)
        )

    async def async_create_project_request_equipment_of_project_request(
        self, project_request_id: int, payload: ProjectRequestEquipmentPayload
    ) -> ProjectRequestEquipment | None:
        """Create one project request equipment on one project request."""
        return await self._call(
            CREATE_PROJECT_REQUEST_EQUIPMENT_OF_PROJECT_REQUEST,
            LinkedCreateArgs(project_request_id, payload),
        )

    async def async_create_project_cost_of_project(
        self, project_id: int, payload: ProjectCostPayload
    ) -> ProjectCost | None:
        """Create one project cost on one project."""
        return await self._call(
            CREATE_PROJECT_COST_OF_PROJECT, LinkedCreateArgs(project_id, payload)
        )

    async def async_create_project_function_group_of_project(
        self, project_id: int, payload: ProjectFunctionGroupPayload
    ) -> ProjectFunctionGroup | None:
        """Create one project function group on one project."""
        return await self._call(
            CREATE_PROJECT_FUNCTION_GROUP_OF_PROJECT, LinkedCreateArgs(project_id, payload)
        )

    async def async_create_project_function_of_project(
        self, project_id: int, payload: ProjectFunctionPayload
    ) -> ProjectFunction | None:
        """Create one project function on one project."""
        return await self._call(
            CREATE_PROJECT_FUNCTION_OF_PROJECT, LinkedCreateArgs(project_id, payload)
        )

    async def async_create_subproject_of_project(
        self, project_id: int, payload: SubprojectPayload
    ) -> Subproject | None:
        """Create one subproject on one project."""
        return await self._call(CREATE_SUBPROJECT_OF_PROJECT, LinkedCreateArgs(project_id, payload))

    async def async_create_task_of_purchase_order(
        self, purchase_order_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one purchase order."""
        return await self._call(
            CREATE_TASK_OF_PURCHASE_ORDER, LinkedCreateArgs(purchase_order_id, payload)
        )

    async def async_create_task_of_quote(self, quote_id: int, payload: TaskPayload) -> Task | None:
        """Create one task on one quote."""
        return await self._call(CREATE_TASK_OF_QUOTE, LinkedCreateArgs(quote_id, payload))

    async def async_create_task_of_repair(
        self, repair_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one repair."""
        return await self._call(CREATE_TASK_OF_REPAIR, LinkedCreateArgs(repair_id, payload))

    async def async_create_task_of_serial_number(
        self, serial_number_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one serial number."""
        return await self._call(
            CREATE_TASK_OF_SERIAL_NUMBER, LinkedCreateArgs(serial_number_id, payload)
        )

    async def async_create_vehicle_of_stock_location(
        self, stock_location_id: int, payload: VehiclePayload
    ) -> Vehicle | None:
        """Create one vehicle on one stock location."""
        return await self._call(
            CREATE_VEHICLE_OF_STOCK_LOCATION, LinkedCreateArgs(stock_location_id, payload)
        )

    async def async_create_task_of_subrental(
        self, subrental_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one subrental."""
        return await self._call(CREATE_TASK_OF_SUBRENTAL, LinkedCreateArgs(subrental_id, payload))

    async def async_create_subtask_of_task(
        self, task_id: int, payload: SubtaskPayload
    ) -> Subtask | None:
        """Create one subtask on one task."""
        return await self._call(CREATE_SUBTASK_OF_TASK, LinkedCreateArgs(task_id, payload))

    async def async_create_task_assignment_of_task(
        self, task_id: int, payload: TaskAssignmentPayload
    ) -> TaskAssignment | None:
        """Create one task assignment on one task."""
        return await self._call(CREATE_TASK_ASSIGNMENT_OF_TASK, LinkedCreateArgs(task_id, payload))

    async def async_create_task_of_contact_person(
        self, contact_person_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one contact person."""
        return await self._call(
            CREATE_TASK_OF_CONTACT_PERSON, LinkedCreateArgs(contact_person_id, payload)
        )

    async def async_create_task_of_contact(
        self, contact_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one contact."""
        return await self._call(CREATE_TASK_OF_CONTACT, LinkedCreateArgs(contact_id, payload))

    async def async_create_task_of_contract(
        self, contract_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one contract."""
        return await self._call(CREATE_TASK_OF_CONTRACT, LinkedCreateArgs(contract_id, payload))

    async def async_create_task_of_crew(self, crew_id: int, payload: TaskPayload) -> Task | None:
        """Create one task on one crew member."""
        return await self._call(CREATE_TASK_OF_CREW, LinkedCreateArgs(crew_id, payload))

    async def async_create_task_of_equipment(
        self, equipment_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one material."""
        return await self._call(CREATE_TASK_OF_EQUIPMENT, LinkedCreateArgs(equipment_id, payload))

    async def async_create_task_of_invoice(
        self, invoice_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one invoice."""
        return await self._call(CREATE_TASK_OF_INVOICE, LinkedCreateArgs(invoice_id, payload))

    async def async_create_task_of_project(
        self, project_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one project."""
        return await self._call(CREATE_TASK_OF_PROJECT, LinkedCreateArgs(project_id, payload))

    async def async_create_task_of_supplier(
        self, supplier_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one supplier."""
        return await self._call(CREATE_TASK_OF_SUPPLIER, LinkedCreateArgs(supplier_id, payload))

    async def async_create_task_of_vehicle(
        self, vehicle_id: int, payload: TaskPayload
    ) -> Task | None:
        """Create one task on one vehicle."""
        return await self._call(CREATE_TASK_OF_VEHICLE, LinkedCreateArgs(vehicle_id, payload))

    async def async_update_accessory(
        self, accessory_id: int, payload: AccessoryPayload
    ) -> Accessory | None:
        """Update one accessory by its id."""
        return await self._call(UPDATE_ACCESSORY, UpdateArgs(accessory_id, payload))

    async def async_update_alternative(
        self, alternative_id: int, payload: AlternativePayload
    ) -> Alternative | None:
        """Update one alternative by its id."""
        return await self._call(UPDATE_ALTERNATIVE, UpdateArgs(alternative_id, payload))

    async def async_update_appointment_crew(
        self, appointment_crew_id: int, payload: AppointmentCrewPayload
    ) -> AppointmentCrew | None:
        """Update one appointment crew by its id."""
        return await self._call(UPDATE_APPOINTMENT_CREW, UpdateArgs(appointment_crew_id, payload))

    async def async_update_appointment(
        self, appointment_id: int, payload: AppointmentPayload
    ) -> Appointment | None:
        """Update one appointment by its id."""
        return await self._call(UPDATE_APPOINTMENT, UpdateArgs(appointment_id, payload))

    async def async_update_contact_person(
        self, contact_person_id: int, payload: ContactPersonPayload
    ) -> ContactPerson | None:
        """Update one contact person by its id."""
        return await self._call(UPDATE_CONTACT_PERSON, UpdateArgs(contact_person_id, payload))

    async def async_update_contact(
        self, contact_id: int, payload: ContactPayload
    ) -> Contact | None:
        """Update one contact by its id."""
        return await self._call(UPDATE_CONTACT, UpdateArgs(contact_id, payload))

    async def async_update_project_cost(
        self, project_cost_id: int, payload: ProjectCostPayload
    ) -> ProjectCost | None:
        """Update one project cost by its id."""
        return await self._call(UPDATE_PROJECT_COST, UpdateArgs(project_cost_id, payload))

    async def async_update_crew_availability(
        self, crew_availability_id: int, payload: CrewAvailabilityPayload
    ) -> CrewAvailability | None:
        """Update one crew availability by its id."""
        return await self._call(UPDATE_CREW_AVAILABILITY, UpdateArgs(crew_availability_id, payload))

    async def async_update_equipment(
        self, equipment_id: int, payload: EquipmentPayload
    ) -> Equipment | None:
        """Update one equipment by its id."""
        return await self._call(UPDATE_EQUIPMENT, UpdateArgs(equipment_id, payload))

    async def async_update_equipment_set_content(
        self, equipment_set_content_id: int, payload: EquipmentSetContentPayload
    ) -> EquipmentSetContent | None:
        """Update one equipment set content by its id."""
        return await self._call(
            UPDATE_EQUIPMENT_SET_CONTENT, UpdateArgs(equipment_set_content_id, payload)
        )

    async def async_update_folder(self, folder_id: int, payload: FolderPayload) -> Folder | None:
        """Update one folder by its id."""
        return await self._call(UPDATE_FOLDER, UpdateArgs(folder_id, payload))

    async def async_update_leave_request(
        self, leave_request_id: int, payload: LeaveRequestPayload
    ) -> LeaveRequest | None:
        """Update one leave request by its id."""
        return await self._call(UPDATE_LEAVE_REQUEST, UpdateArgs(leave_request_id, payload))

    async def async_update_payment(
        self, payment_id: int, payload: PaymentPayload
    ) -> Payment | None:
        """Update one payment by its id."""
        return await self._call(UPDATE_PAYMENT, UpdateArgs(payment_id, payload))

    async def async_update_project_request_equipment(
        self, project_request_equipment_id: int, payload: ProjectRequestEquipmentPayload
    ) -> ProjectRequestEquipment | None:
        """Update one project request equipment by its id."""
        return await self._call(
            UPDATE_PROJECT_REQUEST_EQUIPMENT, UpdateArgs(project_request_equipment_id, payload)
        )

    async def async_update_project_request(
        self, project_request_id: int, payload: ProjectRequestPayload
    ) -> ProjectRequest | None:
        """Update one project request by its id."""
        return await self._call(UPDATE_PROJECT_REQUEST, UpdateArgs(project_request_id, payload))

    async def async_update_serial_number(
        self, serial_number_id: int, payload: SerialNumberPayload
    ) -> SerialNumber | None:
        """Update one serial number by its id."""
        return await self._call(UPDATE_SERIAL_NUMBER, UpdateArgs(serial_number_id, payload))

    async def async_update_stock_movement(
        self, stock_movement_id: int, payload: StockMovementPayload
    ) -> StockMovement | None:
        """Update one stock movement by its id."""
        return await self._call(UPDATE_STOCK_MOVEMENT, UpdateArgs(stock_movement_id, payload))

    async def async_update_subtask(
        self, subtask_id: int, payload: SubtaskPayload
    ) -> Subtask | None:
        """Update one subtask by its id."""
        return await self._call(UPDATE_SUBTASK, UpdateArgs(subtask_id, payload))

    async def async_update_supplier(
        self, supplier_id: int, payload: SupplierPayload
    ) -> Supplier | None:
        """Update one supplier by its id."""
        return await self._call(UPDATE_SUPPLIER, UpdateArgs(supplier_id, payload))

    async def async_update_task_assignment(
        self, task_assignment_id: int, payload: TaskAssignmentPayload
    ) -> TaskAssignment | None:
        """Update one task assignment by its id."""
        return await self._call(UPDATE_TASK_ASSIGNMENT, UpdateArgs(task_assignment_id, payload))

    async def async_update_task(self, task_id: int, payload: TaskPayload) -> Task | None:
        """Update one task by its id."""
        return await self._call(UPDATE_TASK, UpdateArgs(task_id, payload))

    async def async_update_task_status(
        self, task_status_id: int, payload: TaskStatusPayload
    ) -> TaskStatus | None:
        """Update one task status by its id."""
        return await self._call(UPDATE_TASK_STATUS, UpdateArgs(task_status_id, payload))

    async def async_update_time_registration(
        self, time_registration_id: int, payload: TimeRegistrationPayload
    ) -> TimeRegistration | None:
        """Update one time registration by its id."""
        return await self._call(UPDATE_TIME_REGISTRATION, UpdateArgs(time_registration_id, payload))

    async def async_update_vehicle(
        self, vehicle_id: int, payload: VehiclePayload
    ) -> Vehicle | None:
        """Update one vehicle by its id."""
        return await self._call(UPDATE_VEHICLE, UpdateArgs(vehicle_id, payload))

    async def async_delete_accessory(self, accessory_id: int) -> None:
        """Delete one accessory by its id."""
        return await self._call(DELETE_ACCESSORY, DeleteArgs(accessory_id))

    async def async_delete_alternative(self, alternative_id: int) -> None:
        """Delete one alternative by its id."""
        return await self._call(DELETE_ALTERNATIVE, DeleteArgs(alternative_id))

    async def async_delete_appointment_crew(self, appointment_crew_id: int) -> None:
        """Delete one appointment crew by its id."""
        return await self._call(DELETE_APPOINTMENT_CREW, DeleteArgs(appointment_crew_id))

    async def async_delete_appointment(self, appointment_id: int) -> None:
        """Delete one appointment by its id."""
        return await self._call(DELETE_APPOINTMENT, DeleteArgs(appointment_id))

    async def async_delete_contact_person(self, contact_person_id: int) -> None:
        """Delete one contact person by its id."""
        return await self._call(DELETE_CONTACT_PERSON, DeleteArgs(contact_person_id))

    async def async_delete_contact(self, contact_id: int) -> None:
        """Delete one contact by its id."""
        return await self._call(DELETE_CONTACT, DeleteArgs(contact_id))

    async def async_delete_project_cost(self, project_cost_id: int) -> None:
        """Delete one project cost by its id."""
        return await self._call(DELETE_PROJECT_COST, DeleteArgs(project_cost_id))

    async def async_delete_crew_availability(self, crew_availability_id: int) -> None:
        """Delete one crew availability by its id."""
        return await self._call(DELETE_CREW_AVAILABILITY, DeleteArgs(crew_availability_id))

    async def async_delete_equipment_set_content(self, equipment_set_content_id: int) -> None:
        """Delete one equipment set content by its id."""
        return await self._call(DELETE_EQUIPMENT_SET_CONTENT, DeleteArgs(equipment_set_content_id))

    async def async_delete_project_request_equipment(
        self, project_request_equipment_id: int
    ) -> None:
        """Delete one project request equipment by its id."""
        return await self._call(
            DELETE_PROJECT_REQUEST_EQUIPMENT, DeleteArgs(project_request_equipment_id)
        )

    async def async_delete_project_request(self, project_request_id: int) -> None:
        """Delete one project request by its id."""
        return await self._call(DELETE_PROJECT_REQUEST, DeleteArgs(project_request_id))

    async def async_delete_serial_number(self, serial_number_id: int) -> None:
        """Delete one serial number by its id."""
        return await self._call(DELETE_SERIAL_NUMBER, DeleteArgs(serial_number_id))

    async def async_delete_stock_movement(self, stock_movement_id: int) -> None:
        """Delete one stock movement by its id."""
        return await self._call(DELETE_STOCK_MOVEMENT, DeleteArgs(stock_movement_id))

    async def async_delete_subtask(self, subtask_id: int) -> None:
        """Delete one subtask by its id."""
        return await self._call(DELETE_SUBTASK, DeleteArgs(subtask_id))

    async def async_delete_supplier(self, supplier_id: int) -> None:
        """Delete one supplier by its id."""
        return await self._call(DELETE_SUPPLIER, DeleteArgs(supplier_id))

    async def async_delete_task_assignment(self, task_assignment_id: int) -> None:
        """Delete one task assignment by its id."""
        return await self._call(DELETE_TASK_ASSIGNMENT, DeleteArgs(task_assignment_id))

    async def async_delete_task(self, task_id: int) -> None:
        """Delete one task by its id."""
        return await self._call(DELETE_TASK, DeleteArgs(task_id))

    async def async_delete_task_status(self, task_status_id: int) -> None:
        """Delete one task status by its id."""
        return await self._call(DELETE_TASK_STATUS, DeleteArgs(task_status_id))

    async def async_delete_time_registration(self, time_registration_id: int) -> None:
        """Delete one time registration by its id."""
        return await self._call(DELETE_TIME_REGISTRATION, DeleteArgs(time_registration_id))

    async def async_delete_vehicle(self, vehicle_id: int) -> None:
        """Delete one vehicle by its id."""
        return await self._call(DELETE_VEHICLE, DeleteArgs(vehicle_id))
