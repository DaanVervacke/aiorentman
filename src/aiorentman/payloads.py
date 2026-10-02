"""Write payloads: one frozen dataclass per request schema of the pinned document."""

from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, cast

from .models import RentmanLink

WIRE_ALIASES: dict[str, str] = {
    "break_": "break",
    "from_": "from",
    "in_": "in",
    "out_": "out",
}


def to_wire(payload: object) -> dict[str, Any]:
    """Render one payload as its request body, leaving every unset field out."""
    body: dict[str, Any] = {}
    for payload_field in fields(cast("Any", payload)):
        value = getattr(payload, payload_field.name)
        if value is None:
            continue
        key = WIRE_ALIASES.get(payload_field.name, payload_field.name)
        body[key] = _wire_value(value)
    return body


def _wire_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, RentmanLink):
        return value.path
    return value


@dataclass(frozen=True, slots=True)
class AccessoryPayload:
    """The write payload for one accessory of a material."""

    equipment: RentmanLink | None = None
    quantity: int | None = None
    automatic: bool | None = None
    skip: bool | None = None
    is_free: bool | None = None
    order: str | None = None
    add_as_new_line: bool | None = None


@dataclass(frozen=True, slots=True)
class AlternativePayload:
    """The write payload for one alternative of a material."""

    alternative: RentmanLink


@dataclass(frozen=True, slots=True)
class AppointmentCrewPayload:
    """The write payload for one crew member on an appointment."""

    crew: RentmanLink


@dataclass(frozen=True, slots=True)
class AppointmentPayload:
    """The write payload for one appointment."""

    start: datetime
    end: datetime
    name: str | None = None
    color: str | None = None
    location: str | None = None
    remark: str | None = None
    is_public: bool | None = None
    is_plannable: bool | None = None


@dataclass(frozen=True, slots=True)
class ContactPayload:
    """The write payload for one contact."""

    folder: RentmanLink | None = None
    type: str | None = None
    ext_name_line: str | None = None
    firstname: str | None = None
    distance: float | None = None
    travel_time: float | None = None
    surfix: str | None = None
    surname: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    code: str | None = None
    accounting_code: str | None = None
    vendor_accounting_code: str | None = None
    name: str | None = None
    gender: str | None = None
    mailing_city: str | None = None
    mailing_street: str | None = None
    mailing_number: str | None = None
    mailing_unit_number: str | None = None
    mailing_district: str | None = None
    mailing_extra_address_line: str | None = None
    mailing_postalcode: str | None = None
    mailing_state: str | None = None
    mailing_country: str | None = None
    visit_city: str | None = None
    visit_street: str | None = None
    visit_number: str | None = None
    visit_unit_number: str | None = None
    visit_district: str | None = None
    visit_extra_address_line: str | None = None
    visit_postalcode: str | None = None
    visit_state: str | None = None
    country: str | None = None
    invoice_city: str | None = None
    invoice_street: str | None = None
    invoice_number: str | None = None
    invoice_unit_number: str | None = None
    invoice_district: str | None = None
    invoice_extra_address_line: str | None = None
    invoice_postalcode: str | None = None
    invoice_state: str | None = None
    invoice_country: str | None = None
    phone_1: str | None = None
    phone_2: str | None = None
    email_1: str | None = None
    email_2: str | None = None
    website: str | None = None
    VAT_code: str | None = None
    fiscal_code: str | None = None
    commerce_code: str | None = None
    purchase_number: str | None = None
    bic: str | None = None
    bank_account: str | None = None
    default_person: RentmanLink | None = None
    admin_contactperson: RentmanLink | None = None
    discount_crew: float | None = None
    discount_transport: float | None = None
    discount_rental: float | None = None
    discount_sale: float | None = None
    discount_total: float | None = None
    projectnote: str | None = None
    projectnote_title: str | None = None
    contact_warning: str | None = None
    discount_subrent: float | None = None
    image: RentmanLink | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ContactPersonPayload:
    """The write payload for one contact person."""

    firstname: str | None = None
    middle_name: str | None = None
    lastname: str | None = None
    function: str | None = None
    phone: str | None = None
    street: str | None = None
    number: str | None = None
    postalcode: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    mobilephone: str | None = None
    email: str | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class CrewAvailabilityPayload:
    """The write payload for one availability window of a crew member."""

    start: datetime
    end: datetime
    last_updater: RentmanLink | None = None
    last_updated: datetime | None = None
    status: str | None = None
    remark: str | None = None
    recurrence_interval_unit: str | None = None
    recurrence_enddate: str | None = None
    recurrence_interval: int | None = None
    recurrent_group: int | None = None
    recurrence_weekdays: str | None = None


@dataclass(frozen=True, slots=True)
class EquipmentPayload:
    """The write payload for one material."""

    folder: RentmanLink | None = None
    code: str | None = None
    factor_group: RentmanLink | None = None
    name: str | None = None
    internal_remark: str | None = None
    external_remark: str | None = None
    unit: str | None = None
    in_shop: bool | None = None
    surface_article: bool | None = None
    shop_description_short: str | None = None
    shop_description_long: str | None = None
    shop_seo_title: str | None = None
    shop_seo_keyword: str | None = None
    shop_seo_description: str | None = None
    shop_featured: bool | None = None
    price: float | None = None
    subrental_costs: float | None = None
    critical_stock_level: int | None = None
    type: str | None = None
    rental_sales: str | None = None
    temporary: bool | None = None
    in_planner: bool | None = None
    in_archive: bool | None = None
    stock_management: str | None = None
    taxclass: RentmanLink | None = None
    list_price: float | None = None
    volume: float | None = None
    packed_per: int | None = None
    height: float | None = None
    width: float | None = None
    length: float | None = None
    weight: float | None = None
    empty_weight: float | None = None
    power: float | None = None
    current: float | None = None
    country_of_origin: str | None = None
    image: RentmanLink | None = None
    ledger: RentmanLink | None = None
    ledger_debit: RentmanLink | None = None
    defaultgroup: str | None = None
    is_combination: bool | None = None
    is_physical: str | None = None
    can_edit_content_during_planning: bool | None = None
    strict_container_content: str | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class EquipmentSetContentPayload:
    """The write payload for one line of set content."""

    equipment: RentmanLink
    quantity: str | None = None
    order: str | None = None
    is_fixed: str | None = None
    is_physically_connected: str | None = None


@dataclass(frozen=True, slots=True)
class FolderPayload:
    """The write payload for one folder."""

    parent: RentmanLink | None = None
    name: str | None = None
    order: str | None = None
    itemtype: str | None = None


@dataclass(frozen=True, slots=True)
class LeaveMutationPayload:
    """The write payload for one leave mutation."""

    crewmember: RentmanLink
    leavetype: RentmanLink
    description: str | None = None
    duration: float | None = None
    mutation_date: str | None = None


@dataclass(frozen=True, slots=True)
class LeaveRequestPayload:
    """The write payload for one leave request."""

    requested_for: RentmanLink
    description: str | None = None
    approval_status: str | None = None
    reviewed_on: datetime | None = None
    reviewer: RentmanLink | None = None


@dataclass(frozen=True, slots=True)
class PaymentPayload:
    """The write payload for one payment."""

    moment: datetime
    amount: float | None = None
    description: str | None = None
    payment_import_source: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectCostPayload:
    """The write payload for one project cost."""

    subproject: RentmanLink
    name: str | None = None
    remark: str | None = None
    quantity: int | None = None
    discount: float | None = None
    is_template: bool | None = None
    taxclass: RentmanLink | None = None
    ledger: RentmanLink | None = None
    ledger_debit: RentmanLink | None = None
    sale_price: float | None = None
    purchase_price: float | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ProjectFunctionGroupPayload:
    """The write payload for one project function group."""

    subproject: RentmanLink
    name: str | None = None
    usageperiod_start: datetime | None = None
    usageperiod_end: datetime | None = None
    planperiod_start: datetime | None = None
    planperiod_end: datetime | None = None
    remark: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectFunctionPayload:
    """The write payload for one project function."""

    cost_rate: RentmanLink
    price_rate: RentmanLink
    subproject: RentmanLink
    cost_accommodation: float | None = None
    cost_catering: float | None = None
    cost_travel: float | None = None
    cost_other: float | None = None
    price_accommodation: float | None = None
    price_catering: float | None = None
    price_travel: float | None = None
    price_other: float | None = None
    group: RentmanLink | None = None
    name_external: str | None = None
    name: str | None = None
    usageperiod_start: datetime | None = None
    usageperiod_end: datetime | None = None
    planperiod_start: datetime | None = None
    planperiod_end: datetime | None = None
    type: str | None = None
    amount: int | None = None
    is_plannable: bool | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ProjectPayload:
    """The write payload for one project."""

    name: str | None = None
    reference: str | None = None
    number: str | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ProjectRequestEquipmentPayload:
    """The write payload for one equipment line of a project request."""

    quantity: int | None = None
    quantity_total: int | None = None
    is_comment: bool | None = None
    is_kit: bool | None = None
    discount: float | None = None
    linked_equipment: RentmanLink | None = None
    name: str | None = None
    external_remark: str | None = None
    parent: RentmanLink | None = None
    unit_price: float | None = None
    factor: str | None = None
    order: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectRequestPayload:
    """The write payload for one project request."""

    planperiod_end: datetime
    planperiod_start: datetime
    linked_contact: RentmanLink | None = None
    contact_mailing_number: str | None = None
    contact_mailing_country: str | None = None
    contact_name: str | None = None
    contact_mailing_postalcode: str | None = None
    contact_phone: str | None = None
    contact_mailing_city: str | None = None
    contact_mailing_street: str | None = None
    contact_person_lastname: str | None = None
    contact_person_email: str | None = None
    contact_person_middle_name: str | None = None
    contact_person_first_name: str | None = None
    usageperiod_end: datetime | None = None
    usageperiod_start: datetime | None = None
    is_paid: bool | None = None
    language: str | None = None
    in_: datetime | None = None
    out_: datetime | None = None
    location_mailing_number: str | None = None
    location_mailing_country: str | None = None
    location_name: str | None = None
    location_mailing_postalcode: str | None = None
    location_mailing_city: str | None = None
    location_mailing_street: str | None = None
    location_phone: str | None = None
    name: str | None = None
    external_reference: int | None = None
    remark: str | None = None
    price: float | None = None


@dataclass(frozen=True, slots=True)
class SerialNumberPayload:
    """The write payload for one serial number."""

    serial: str | None = None
    purchasedate: str | None = None
    depreciation_monthly: float | None = None
    book_value: float | None = None
    residual_value: float | None = None
    purchase_costs: float | None = None
    active: bool | None = None
    remark: str | None = None
    ref: str | None = None
    asset_location: RentmanLink | None = None
    image: RentmanLink | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class StockMovementPayload:
    """The write payload for one stock movement."""

    date: datetime
    amount: int | None = None
    projectequipment: RentmanLink | None = None
    description: str | None = None
    details: str | None = None
    stock_location: RentmanLink | None = None
    api_client: str | None = None


@dataclass(frozen=True, slots=True)
class SubprojectPayload:
    """The write payload for one subproject."""

    name: str | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class SubtaskPayload:
    """The write payload for one subtask."""

    title: str | None = None
    completed: bool | None = None


@dataclass(frozen=True, slots=True)
class SupplierPayload:
    """The write payload for one supplier of a material."""

    contact: RentmanLink
    contactperson: RentmanLink | None = None
    price: float | None = None
    details: str | None = None


@dataclass(frozen=True, slots=True)
class TaskAssignmentPayload:
    """The write payload for one task assignment."""

    crew: RentmanLink


@dataclass(frozen=True, slots=True)
class TaskPayload:
    """The write payload for one task."""

    color: str
    recurhoe: str | None = None
    recureind: str | None = None
    recurperiode: int | None = None
    is_template: bool | None = None
    name: str | None = None
    details: str | None = None
    priority: str | None = None
    order: str | None = None
    deadline: datetime | None = None
    deadline_type: str | None = None
    deadline_relative_offset_base: str | None = None
    deadline_relative_offset_amount: int | None = None
    deadline_relative_offset_unit: str | None = None
    deadline_relative_offset_direction: str | None = None
    completed_at: datetime | None = None
    status: RentmanLink | None = None
    item: int | None = None
    itemtype: str | None = None
    synchronization_id: str | None = None
    synchronization_uri: str | None = None
    public: str | None = None
    assignment_type: str | None = None
    completed_by: RentmanLink | None = None
    expiry_notification_date: datetime | None = None
    time_budget: float | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class TaskStatusPayload:
    """The write payload for one task status."""

    color: str
    name: str | None = None
    type: str | None = None
    order: str | None = None


@dataclass(frozen=True, slots=True)
class TimeRegistrationPayload:
    """The write payload for one time registration."""

    crewmember: RentmanLink | None = None
    start: datetime | None = None
    end: datetime | None = None
    distance: float | None = None
    is_lunch_included: bool | None = None
    leavetype: RentmanLink | None = None
    duration: float | None = None
    break_duration: float | None = None
    travel_time: float | None = None
    correction_duration: float | None = None
    remark: str | None = None
    custom: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class VehiclePayload:
    """The write payload for one vehicle."""

    folder: RentmanLink | None = None
    name: str | None = None
    cost_rate: RentmanLink | None = None
    in_planner: bool | None = None
    height: float | None = None
    length: float | None = None
    width: float | None = None
    seats: int | None = None
    inspection_date: str | None = None
    licenseplate: str | None = None
    remark: str | None = None
    payload_capacity: float | None = None
    surface_area: str | None = None
    multiple: str | None = None
    image: RentmanLink | None = None
    asset_location: RentmanLink | None = None
    custom: dict[str, Any] | None = None
