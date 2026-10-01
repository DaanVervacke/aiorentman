"""Immutable result models mirroring the pinned Rentman API schemas."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class RentmanLink:
    """A reference to another resource, given as its API path.

    Linked fields hold a path string such as ``/equipment/12`` unless the
    request expanded them, in which case the parser returns the full typed
    model instead of this link.
    """

    path: str

    @property
    def id(self) -> int | None:
        """The numeric id at the end of the path, or None when absent."""
        tail = self.path.rsplit("/", 1)[-1]
        try:
            return int(tail)
        except ValueError:
            return None


@dataclass(frozen=True, slots=True)
class RentmanPage[ModelT]:
    """One page of a collection: the parsed items and the paging metadata."""

    items: tuple[ModelT, ...]
    item_count: int
    limit: int
    offset: int
    next_page_url: str | None


@dataclass(frozen=True, slots=True)
class Equipment:
    """One material: a rental or sales item tracked in inventory."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    folder: RentmanLink | Folder | None
    code: str
    factor_group: RentmanLink | None
    name: str
    internal_remark: str
    external_remark: str
    unit: str
    in_shop: bool
    surface_article: bool
    shop_description_short: str
    shop_description_long: str
    shop_seo_title: str
    shop_seo_keyword: str
    shop_seo_description: str
    shop_featured: bool
    price: float | None
    subrental_costs: float | None
    critical_stock_level: int | None
    type: str
    rental_sales: str
    temporary: bool
    in_planner: bool
    in_archive: bool
    stock_management: str
    taxclass: RentmanLink | None
    list_price: float | None
    volume: float | None
    packed_per: int | None
    height: float | None
    width: float | None
    length: float | None
    weight: float | None
    empty_weight: float | None
    power: float | None
    current: float | None
    country_of_origin: str
    image: RentmanLink | None
    ledger: RentmanLink | None
    ledger_debit: RentmanLink | None
    defaultgroup: str
    is_combination: bool
    is_physical: str
    can_edit_content_during_planning: bool
    strict_container_content: str
    qrcodes: tuple[str, ...]
    qrcodes_of_serial_numbers: tuple[str, ...]
    tags: tuple[str, ...]
    current_quantity_excl_cases: int | None
    current_quantity: int | None
    quantity_in_cases: int | None
    location_in_warehouse: str
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class SerialNumber:
    """One serialized unit of a material, the unit an RFID tag links to."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    equipment: RentmanLink | Equipment
    serial: str
    purchasedate: datetime | None
    depreciation_monthly: float | None
    book_value: float | None
    residual_value: float | None
    purchase_costs: float | None
    active: bool
    remark: str
    ref: str
    asset_location: RentmanLink | StockLocation | None
    image: RentmanLink | None
    current_book_value: float | None
    next_inspection: datetime | None
    qrcodes: tuple[str, ...]
    tags: tuple[str, ...]
    last_subproject: RentmanLink | Subproject | None
    sealed: bool
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class EquipmentAssignedSerial:
    """One serial number placed inside a serialized combination."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    combination: RentmanLink | SerialNumber
    serialnumber: RentmanLink | SerialNumber
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ActualContent:
    """One equipment item physically recorded inside a combination serial."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    equipment: RentmanLink | Equipment | None
    serial: RentmanLink | SerialNumber | None
    quantity: str
    combination_serial: RentmanLink | SerialNumber | None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class EquipmentSetContent:
    """One equipment line inside an equipment set combination."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    quantity: str
    parent_equipment: RentmanLink | Equipment
    order: str
    equipment: RentmanLink | Equipment
    is_fixed: str
    is_physically_connected: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Folder:
    """One folder that groups equipment items in the inventory tree."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    parent: RentmanLink | Folder | None
    name: str
    order: str
    itemtype: str
    path: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class StockLocation:
    """One warehouse or storage location where stock is kept."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    city: str
    street: str
    house_number: str
    postal_code: str
    state_province: str
    country: str
    active: bool
    type: str
    color: str
    in_archive: bool
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class WarehouseStatus:
    """One warehouse status that equipment can be booked to."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Status:
    """One planning status that a subproject can carry."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class StockMovement:
    """One recorded change of stock for a material."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    amount: int | None
    equipment: RentmanLink | Equipment
    projectequipment: RentmanLink | ProjectEquipment | None
    description: str
    details: str
    date: datetime | None
    type: str
    stock_location: RentmanLink | StockLocation
    api_client: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Repair:
    """One repair of a material or of one of its serial numbers."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    internal_name: str
    equipment: RentmanLink | Equipment
    serialnumber: RentmanLink | SerialNumber | None
    reporter: RentmanLink | None
    assignee: RentmanLink | None
    external_repairer: RentmanLink | None
    number: str
    repairperiod_start: datetime | None
    repairperiod_end: datetime | None
    amount: int | None
    remark: str
    repair_costs: float | None
    is_usable: str
    costs_charged_to_customer: RentmanLink | None
    subproject: RentmanLink | Subproject | None
    stock_location: RentmanLink | StockLocation | None
    repair_status: str
    unrepairable_of: RentmanLink | Repair | None
    tags: tuple[str, ...]
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Project:
    """One project that plans materials, crew, and transport."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    location: RentmanLink | None
    refundabledeposit: float | None
    deposit_status: str
    customer: RentmanLink | None
    loc_contact: RentmanLink | None
    cust_contact: RentmanLink | None
    project_type: RentmanLink | None
    name: str
    reference: str
    number: str
    account_manager: RentmanLink | None
    color: str
    conditions: str
    project_total_price: float | None
    project_total_price_cancelled: float | None
    project_rental_price: float | None
    project_sale_price: float | None
    project_crew_price: float | None
    project_transport_price: float | None
    project_other_price: float | None
    project_insurance_price: float | None
    project_services_price: float | None
    estimated_cost: float | None
    planned_cost: float | None
    actual_cost: float | None
    already_invoiced: float | None
    tags: tuple[str, ...]
    usageperiod_start: datetime | None
    usageperiod_end: datetime | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    weight: float | None
    power: float | None
    current: float | None
    equipment_period_from: datetime | None
    equipment_period_to: datetime | None
    purchasecosts: float | None
    volume: float | None
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Subproject:
    """One subproject inside a project, carrying its own planning period."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    project: RentmanLink | Project
    order: str
    name: str
    status: RentmanLink | Status
    is_template: bool
    location: RentmanLink | None
    loc_contact: RentmanLink | None
    insurance_rate: float | None
    discount_rental: float | None
    discount_sale: float | None
    discount_crew: float | None
    discount_transport: float | None
    discount_additional_costs: float | None
    discount_services: float | None
    discount_subproject: float | None
    discount_fixed: bool
    discount_fixed_amount: float | None
    fixed_price: bool
    in_planning: bool
    in_financial: bool
    asset_location_from: RentmanLink | StockLocation | None
    project_total_price: float | None
    project_total_price_cancelled: float | None
    project_rental_price: float | None
    project_sale_price: float | None
    project_crew_price: float | None
    project_transport_price: float | None
    project_other_price: float | None
    project_insurance_price: float | None
    project_services_price: float | None
    estimated_cost: float | None
    planned_cost: float | None
    actual_cost: float | None
    already_invoiced: float | None
    usageperiod_start: datetime | None
    usageperiod_end: datetime | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    weight: float | None
    power: float | None
    current: float | None
    purchasecosts: float | None
    volume: float | None
    equipment_period_from: datetime | None
    equipment_period_to: datetime | None
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ProjectEquipment:
    """One planned equipment line on a project or subproject."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    equipment: RentmanLink | Equipment | None
    parent: RentmanLink | ProjectEquipment | None
    ledger: RentmanLink | None
    ledger_debit: RentmanLink | None
    quantity: str
    quantity_total: int | None
    equipment_group: RentmanLink | None
    discount: float | None
    is_option: bool
    factor: str
    order: str
    unit_price: float | None
    name: str
    external_remark: str
    internal_remark: str
    delay_notified: bool
    duration: float | None
    is_delayed: bool
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    usageperiod_start: datetime | None
    usageperiod_end: datetime | None
    has_missings: bool
    warehouse_reservations: int | None
    subrent_reservations: int | None
    serial_number_ids: str
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Accessory:
    """One material that planning adds together with its parent material."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    parent_equipment: RentmanLink | Equipment
    equipment: RentmanLink | Equipment | None
    quantity: int | None
    automatic: bool
    skip: bool
    is_free: bool
    order: str
    add_as_new_line: bool
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Alternative:
    """One material that can replace another material during planning."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    equipment: RentmanLink | Equipment
    alternative: RentmanLink | Equipment
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Supplier:
    """One purchase source of a material, priced through its contact."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    equipment: RentmanLink | Equipment
    contact: RentmanLink | None
    contactperson: RentmanLink | None
    price: float | None
    details: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Vehicle:
    """One vehicle that planning books for transport."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    folder: RentmanLink | Folder | None
    name: str
    cost_rate: RentmanLink | None
    in_planner: bool
    height: float | None
    length: float | None
    width: float | None
    seats: int | None
    inspection_date: datetime | None
    licenseplate: str
    remark: str
    payload_capacity: float | None
    surface_area: str
    multiple: str
    image: RentmanLink | None
    asset_location: RentmanLink | StockLocation | None
    tags: tuple[str, ...]
    distance_cost: float | None
    fixed_cost: float | None
    custom: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ExtraInputField:
    """One custom field definition attached to one item type."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    itemtype: str
    linkedItemType: str  # noqa: N815
    parent: RentmanLink | ExtraInputField | None
    type: str
    order: str
    hidden: bool
    classified: bool
    search_include: bool
    search_minlength: int | None
    is_customfield_mandatory: bool
    raw: dict[str, Any] | None = None
