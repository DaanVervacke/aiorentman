"""Immutable result models mirroring the pinned Rentman API schemas."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class RentmanLink:
    """A reference to another resource, given as its API path.

    Linked fields hold a path string such as ``/equipment/12`` unless the
    request expanded them, in which case the parser returns the full typed
    model instead of this link. An expanded object without a usable id
    parses to None.
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
    """One page of a collection: the parsed items and the paging metadata.

    The parser drops items without a usable id, and logs each one at debug
    level on the ``aiorentman.parsers`` logger. ``item_count`` is the count
    the API reported, so it can be higher than ``len(items)``.
    """

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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


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
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectStatus:
    """One status that a project can carry in the planning workflow."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectType:
    """One project type that groups projects by kind."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    color: str
    type: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectFunctionGroup:
    """One group of functions inside a subproject plan."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    project: RentmanLink | Project
    subproject: RentmanLink | Subproject
    duration: float | None
    planperiod_start_schedule_is_start: str
    usageperiod_start_schedule_is_start: str
    planperiod_end_schedule_is_start: str
    usageperiod_end_schedule_is_start: str
    usageperiod_start: datetime | None
    usageperiod_end: datetime | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    remark: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectFunction:
    """One planned crew or transport function on a subproject."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    cost_rate: RentmanLink | None
    cost_accommodation: float | None
    cost_catering: float | None
    cost_travel: float | None
    cost_other: float | None
    price_rate: RentmanLink | None
    price_accommodation: float | None
    price_catering: float | None
    price_travel: float | None
    price_other: float | None
    project: RentmanLink | Project
    subproject: RentmanLink | Subproject
    is_template: bool
    group: RentmanLink | ProjectFunctionGroup | None
    name_external: str
    name: str
    travel_time_before: float | None
    travel_time_after: float | None
    use_travel_time_from_location: bool
    use_distance_from_location: bool
    usageperiod_start: datetime | None
    planperiod_start_schedule_is_start: str
    usageperiod_start_schedule_is_start: str
    planperiod_end_schedule_is_start: str
    usageperiod_end_schedule_is_start: str
    usageperiod_end: datetime | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    type: str
    duration: float | None
    amount: int | None
    break_: float | None
    distance: float | None
    twoway: bool
    taxclass: RentmanLink | None
    ledger: RentmanLink | None
    ledger_debit: RentmanLink | None
    order: str
    remark_client: str
    remark_planner: str
    remark_crew: str
    in_financial: bool
    in_planning: bool
    is_plannable: bool
    recurrence_group: int | None
    recurrence_enddate: datetime | None
    recurrence_interval_unit: str
    recurrence_interval: int | None
    recurrence_weekdays: str | None
    price_fixed: float | None
    price_variable: float | None
    costs_fixed: float | None
    costs_variable: float | None
    price_total: float | None
    costs_total: float | None
    tags: tuple[str, ...]
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectCrew:
    """One crew member planned on a project function."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    cost_rate: RentmanLink | None
    cost_accommodation: float | None
    cost_catering: float | None
    cost_travel: float | None
    cost_other: float | None
    function: RentmanLink | ProjectFunction
    crewmember: RentmanLink
    visible: bool
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    transport: str
    remark: str
    remark_planner: str
    invoice_reference: str
    project_leader: bool
    is_visible_on_dashboard: bool
    costs: float | None
    cost_actual: float | None
    hours_registered: float | None
    hours_planned: float | None
    cost_planned: float | None
    diff_cost: float | None
    diff_hours: float | None
    activity_status: str
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectVehicle:
    """One vehicle planned on a project function."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    cost_rate: RentmanLink | None
    function: RentmanLink | ProjectFunction
    transport: str
    vehicle: RentmanLink | Vehicle
    planningperiod_start: datetime | None
    planningperiod_end: datetime | None
    remark: str
    remark_planner: str
    costs: float | None
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectEquipmentGroup:
    """One equipment group inside a subproject plan."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    project: RentmanLink | Project
    subproject: RentmanLink | Subproject
    additional_scanned: bool
    name: str
    usageperiod_start: datetime | None
    usageperiod_end: datetime | None
    duration: float | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    is_delayed: bool
    order: str
    in_price_calculation: bool
    remark: str
    weight: float | None
    power: float | None
    current: float | None
    volume: float | None
    total_new_price: float | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectCost:
    """One additional cost line on a subproject."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    remark: str
    project: RentmanLink | Project
    quantity: int | None
    discount: float | None
    order: str
    subproject: RentmanLink | Subproject
    is_template: bool
    taxclass: RentmanLink | None
    ledger: RentmanLink | None
    ledger_debit: RentmanLink | None
    sale_price: float | None
    purchase_price: float | None
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectRequest:
    """One equipment request submitted by a customer."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    linked_contact: RentmanLink | None
    contact_mailing_number: str
    contact_mailing_country: str
    contact_name: str
    contact_mailing_postalcode: str
    contact_phone: str
    contact_mailing_city: str
    contact_mailing_street: str
    linked_contact_person: RentmanLink | None
    contact_person_lastname: str
    contact_person_email: str
    contact_person_middle_name: str
    contact_person_first_name: str
    usageperiod_end: datetime | None
    usageperiod_start: datetime | None
    is_paid: bool
    language: str
    in_: datetime | None
    out_: datetime | None
    linked_location: RentmanLink | None
    location_mailing_number: str
    location_mailing_country: str
    location_name: str
    location_mailing_postalcode: str
    location_mailing_city: str
    location_mailing_street: str
    location_phone: str
    name: str
    external_reference: int | None
    remark: str
    planperiod_end: datetime | None
    planperiod_start: datetime | None
    price: float | None
    linked_project: RentmanLink | Project | None
    source: str
    status: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ProjectRequestEquipment:
    """One equipment line on a project request."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    quantity: int | None
    quantity_total: int | None
    is_comment: bool
    is_kit: bool
    discount: float | None
    linked_equipment: RentmanLink | Equipment | None
    name: str
    external_remark: str
    parent: RentmanLink | ProjectRequestEquipment | None
    unit_price: float | None
    project_request: RentmanLink | ProjectRequest
    factor: str
    order: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Quote:
    """One quotation sent to a customer for a project."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    number: str
    customer: RentmanLink | None
    contact: RentmanLink | None
    date: datetime | None
    expiration_date: datetime | None
    version: int | None
    subject: str
    show_tax: bool
    project: RentmanLink | Project
    filename: str
    project_total_price: float | None
    project_total_price_cancelled: float | None
    project_rental_price: float | None
    project_sale_price: float | None
    project_crew_price: float | None
    project_transport_price: float | None
    project_other_price: float | None
    project_insurance_price: float | None
    project_services_price: float | None
    price: float | None
    price_invat: float | None
    vat_amount: float | None
    tags: tuple[str, ...]
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Contract:
    """One contract signed with a customer for a project."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    number: str
    customer: RentmanLink | None
    contact: RentmanLink | None
    date: datetime | None
    expiration_date: datetime | None
    version: int | None
    subject: str
    show_tax: bool
    project: RentmanLink | Project
    filename: str
    project_total_price: float | None
    project_total_price_cancelled: float | None
    project_rental_price: float | None
    project_sale_price: float | None
    project_crew_price: float | None
    project_transport_price: float | None
    project_other_price: float | None
    project_insurance_price: float | None
    project_services_price: float | None
    price: float | None
    price_invat: float | None
    vat_amount: float | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Invoice:
    """One invoice issued for a project."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    customer: RentmanLink | None
    account_manager: RentmanLink | None
    contact: RentmanLink | None
    expiration: datetime | None
    date: datetime | None
    number: str
    procent: float | None
    from_project: bool
    subject: str
    finalized: bool
    integration_reference_id: str | None
    project: RentmanLink | Project | None
    filename: str
    project_total_price: float | None
    project_total_price_cancelled: float | None
    project_rental_price: float | None
    project_sale_price: float | None
    project_crew_price: float | None
    project_transport_price: float | None
    project_other_price: float | None
    project_insurance_price: float | None
    project_services_price: float | None
    sum_factuurregels: float | None
    price: float | None
    price_invat: float | None
    vat_amount: float | None
    invoicetype: str
    outstanding_balance: float | None
    total_paid: float | None
    is_paid: bool
    date_sent: datetime | None
    payment_reminder_sent: int | None
    final_payment_reminder_sent: datetime | None
    payment_date: datetime | None
    days_after_expiry: int | None
    tags: tuple[str, ...]
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class LedgerCode:
    """One ledger account that financial lines book to."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    code: str
    is_credit: bool
    is_debit: bool
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class TaxClass:
    """One tax class applied to financial lines."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    code: str
    type: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class InvoiceLine:
    """One VAT line on a quote, contract, or invoice."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    item: int | None
    base: float | None
    ledger: RentmanLink | LedgerCode
    vatrate: float | None
    vatamount: float | None
    priceincl: float | None
    ledgercode: str
    parent_api_path: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Payment:
    """One payment recorded against an invoice."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    invoice: RentmanLink | Invoice
    moment: datetime | None
    amount: float | None
    description: str
    payment_import_source: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Subrental:
    """One subrental order placed with an external supplier."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    accountmanager: RentmanLink | None
    reference: str
    supplier: RentmanLink | None
    number: str
    contactperson: RentmanLink | None
    location: RentmanLink | None
    location_contact: RentmanLink | None
    usageperiod_start: datetime | None
    usageperiod_end: datetime | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    delivery_in: datetime | None
    delivery_out: datetime | None
    equipment_cost: float | None
    price: float | None
    extra_cost: float | None
    auto_update_costs: bool
    remark: str
    type: str
    status: RentmanLink | Status
    sent: datetime | None
    asset_location_to: RentmanLink | StockLocation | None
    asset_location_from: RentmanLink | StockLocation | None
    is_internal: bool
    supplier_project: RentmanLink | Project | None
    tags: tuple[str, ...]
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class SubrentalEquipmentGroup:
    """One equipment group inside a subrental."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    subrental: RentmanLink | Subrental
    name: str
    order: str
    supplier_category: RentmanLink | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class SubrentalEquipment:
    """One equipment line inside a subrental."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    subrental_group: RentmanLink | SubrentalEquipmentGroup
    equipment: RentmanLink | Equipment | None
    parent: RentmanLink | SubrentalEquipment | None
    planperiod_start: datetime | None
    planperiod_end: datetime | None
    name: str
    quantity: int | None
    quantity_total: int | None
    unit_price: float | None
    discount: float | None
    factor: str
    order: str
    remark: str
    lineprice: float | None
    supplier_planningmateriaal: RentmanLink | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class PurchaseOrder:
    """One purchase order sent to a supplier."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    filename: str
    subject: str
    owner: RentmanLink
    date_of_issue: datetime | None
    delivery_date: datetime | None
    description: str
    number: str
    approval_status: str
    previous_status: str
    approved_amount: float | None
    supplier: RentmanLink | None
    contact_person: RentmanLink | None
    delivery_type: str
    delivery_location: RentmanLink | None
    delivery_location_person: RentmanLink | None
    delivery_warehouse: RentmanLink | StockLocation | None
    accounting_code: str
    export_status: str
    export_date: datetime | None
    export_message: str | None
    tags: tuple[str, ...]
    underlying_cost_amount: float | None
    underlying_cost_amount_tax: float | None
    underlying_cost_amount_with_tax: float | None
    approved_by: RentmanLink | None
    approved_at: datetime | None
    projects_json: str | None
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class PurchaseOrderCost:
    """One underlying cost line of a purchase order."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    purchase_order: RentmanLink | PurchaseOrder
    costitem: int | None
    costitemtype: str
    approved_amount: float | None
    project: str
    underlying_cost_amount: float | None
    underlying_cost_amount_tax: float | None
    underlying_cost_amount_with_tax: float | None
    quantity: int | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class PurchaseOrderGlobalCost:
    """One global cost line of a purchase order."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    purchase_order: RentmanLink | PurchaseOrder
    name: str
    unit_purchase_cost: float | None
    quantity: int | None
    taxclass: RentmanLink | TaxClass | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Crew:
    """One crew member registered in the account."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    folder: RentmanLink | Folder | None
    street: str
    housenumber: str
    unit_number: str
    district: str
    city: str
    postal_code: str
    addressline2: str
    extraaddressline: str
    state: str
    country: str
    birthdate: datetime | None
    passport_number: str
    emergency_contact: str
    remark: str
    driving_license: str
    contract: str
    bank: str
    contract_date: datetime | None
    company_name: str
    vat_code: str
    coc_code: str
    firstname: str
    middle_name: str
    lastname: str
    email: str
    phone: str
    active: bool
    avatar: RentmanLink | None
    vt_fullname: str
    default_warehouse: RentmanLink | StockLocation | None
    external_reference: str
    tags: tuple[str, ...]
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class CrewAvailability:
    """One availability window registered for one crew member."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    last_updater: RentmanLink | None
    last_updated: datetime | None
    start: datetime | None
    end: datetime | None
    crewmember: RentmanLink | Crew
    status: str
    remark: str
    recurrence_interval_unit: str
    recurrence_enddate: datetime | None
    recurrence_interval: int | None
    recurrent_group: int | None
    recurrence_weekdays: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class CrewRate:
    """One cost rate assigned to one crew member."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    naam: str
    cost_rate: RentmanLink | None
    medewerker: RentmanLink | Crew
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Appointment:
    """One calendar appointment in the crew planner."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    start: datetime | None
    end: datetime | None
    color: str
    location: str
    remark: str
    is_public: bool
    is_plannable: bool
    recurrence_interval_unit: str
    recurrence_enddate: datetime | None
    recurrence_interval: int | None
    recurrence_group: int | None
    recurrence_weekdays: str | None
    synchronization_id: str
    synchronisation_uri: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class AppointmentCrew:
    """One crew member attached to one appointment."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    appointment: RentmanLink | Appointment
    crew: RentmanLink | Crew
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Invitation:
    """One planning invitation sent to one crew member."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    type: str
    accepted: bool
    responded_timestamp: datetime | None
    expiration_date: datetime | None
    start: datetime | None
    end: datetime | None
    function: RentmanLink | None
    projectcrew: RentmanLink | None
    crewmember: RentmanLink | Crew
    remark: str
    emailstatus: str
    last_reminder: datetime | None
    location_details: str | None
    auto_reminder_date: datetime | None
    auto_reminder_sent: int | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class LeaveType:
    """One leave type that time registration books to."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    type: str
    name: str
    payroll_code: str
    color: str
    requires_approval: bool
    affects_availability: bool
    has_balance: bool
    balance_start_date: datetime | None
    is_labor: str
    has_calculated_duration: bool
    can_have_activities: bool
    counts_in_totals: bool
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class LeaveRequest:
    """One leave request submitted by one crew member."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    description: str
    approval_status: str
    requested_for: RentmanLink | Crew
    reviewed_on: datetime | None
    reviewer: RentmanLink | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class LeaveMutation:
    """One leave balance mutation for one crew member."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    description: str
    duration: float | None
    crewmember: RentmanLink | Crew
    leavetype: RentmanLink | LeaveType
    mutation_date: datetime | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class TimeRegistration:
    """One worked or leave time registration of one crew member."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    crewmember: RentmanLink | Crew | None
    start: datetime | None
    end: datetime | None
    distance: float | None
    is_lunch_included: bool
    leavetype: RentmanLink | LeaveType | None
    leaverequest: RentmanLink | LeaveRequest | None
    duration: float | None
    break_duration: float | None
    travel_time: float | None
    correction_duration: float | None
    remark: str
    status: str
    break_duration_with_start_end: float | None
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class TimeRegistrationActivity:
    """One activity line inside one time registration."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    time_registration: RentmanLink | TimeRegistration
    project_function: RentmanLink | ProjectFunction | None
    subproject_function: RentmanLink | ProjectFunction | None
    description: str
    duration: float | None
    is_activity: bool
    from_: datetime | None
    to: datetime | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Contact:
    """One customer or supplier contact registered in the account."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    folder: RentmanLink | Folder | None
    type: str
    ext_name_line: str
    firstname: str
    distance: float | None
    travel_time: float | None
    surfix: str
    surname: str
    longitude: float | None
    latitude: float | None
    code: str
    accounting_code: str
    vendor_accounting_code: str
    name: str
    gender: str
    mailing_city: str
    mailing_street: str
    mailing_number: str
    mailing_unit_number: str
    mailing_district: str
    mailing_extra_address_line: str
    mailing_postalcode: str
    mailing_state: str
    mailing_country: str
    visit_city: str
    visit_street: str
    visit_number: str
    visit_unit_number: str
    visit_district: str
    visit_extra_address_line: str
    visit_postalcode: str
    visit_state: str
    country: str
    invoice_city: str
    invoice_street: str
    invoice_number: str
    invoice_unit_number: str
    invoice_district: str
    invoice_extra_address_line: str
    invoice_postalcode: str
    invoice_state: str
    invoice_country: str
    phone_1: str
    phone_2: str
    email_1: str
    email_2: str
    website: str
    VAT_code: str
    fiscal_code: str
    commerce_code: str
    purchase_number: str
    bic: str
    bank_account: str
    default_person: RentmanLink | ContactPerson | None
    admin_contactperson: RentmanLink | None
    discount_crew: float | None
    discount_transport: float | None
    discount_rental: float | None
    discount_sale: float | None
    discount_total: float | None
    projectnote: str
    projectnote_title: str
    contact_warning: str
    discount_subrent: float | None
    image: RentmanLink | None
    tags: tuple[str, ...]
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class ContactPerson:
    """One person working at one contact."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    contact: RentmanLink | Contact
    firstname: str
    middle_name: str
    lastname: str
    function: str
    phone: str
    street: str
    number: str
    postalcode: str
    city: str
    state: str
    country: str
    mobilephone: str
    email: str
    tags: tuple[str, ...]
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class TaskStatus:
    """One status that a task can carry."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    color: str
    type: str
    order: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Task:
    """One task tracked against one item in the account."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    recurhoe: str
    recureind: str | None
    recurperiode: int | None
    is_template: bool
    name: str
    details: str
    color: str
    priority: str
    order: str
    deadline: datetime | None
    deadline_type: str
    deadline_relative_offset_base: str
    deadline_relative_offset_amount: int | None
    deadline_relative_offset_unit: str
    deadline_relative_offset_direction: str
    completed_at: datetime | None
    status: RentmanLink | TaskStatus
    item: int | None
    itemtype: str | None
    synchronization_id: str
    synchronization_uri: str
    public: str
    assignment_type: str
    completed_by: RentmanLink | None
    expiry_notification_date: datetime | None
    time_budget: float | None
    tags: tuple[str, ...]
    parent_api_path: str
    custom: dict[str, Any] = field(hash=False)
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Subtask:
    """One checklist line inside one task."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    task: RentmanLink | Task
    title: str
    completed: bool
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class TaskAssignment:
    """One crew member assigned to one task."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    task: RentmanLink | Task
    crew: RentmanLink | Crew
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class FileFolder:
    """One folder that groups the files of one item."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    parent: RentmanLink | FileFolder | None
    name: str
    classified: bool
    item: int | None
    itemtype: str | None
    is_template: bool
    parent_api_path: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class File:
    """One file stored against one item in the account."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    readable_name: str
    expiration: datetime | None
    size: int | None
    image: bool
    item: int | None
    itemtype: str | None
    description: str
    in_documents: bool
    in_webshop: bool
    classified: bool
    public: bool
    type: str
    preview_of: RentmanLink | None
    previewstatus: str
    file_item: int | None
    file_itemtype: str
    folder: RentmanLink | FileFolder | None
    path: str
    path_without_file_name: str
    path_with_file_folders: str
    name_without_extension: str
    friendly_name_without_extension: str
    extension: str
    url: str
    proxy_url: str
    parent_api_path: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Rate:
    """One rate definition that prices or costs book against."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    archived: bool
    type: str
    subtype: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class RateFactor:
    """One bracket inside the price or cost table of a rate."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    rate_id: RentmanLink | Rate
    from_: float | None
    to: float | None
    variable: float | None
    fixed: float | None
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class FactorGroup:
    """One group of day factors applied to rental prices."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    name: str
    raw: dict[str, Any] | None = field(default=None, hash=False)


@dataclass(frozen=True, slots=True)
class Factor:
    """One day bracket inside a factor group."""

    id: int
    created: datetime | None
    modified: datetime | None
    update_hash: str
    creator: RentmanLink | None
    displayname: str
    from_days: int | None
    to_days: int | None
    factor: str
    factor_group: RentmanLink | FactorGroup
    raw: dict[str, Any] | None = field(default=None, hash=False)
