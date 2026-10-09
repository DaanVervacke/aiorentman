"""Convert raw Rentman payloads into result models.

A model parser raises ValueError for an object without a usable id.
parse_page, parse_envelope_item, and expanded links drop such objects.
"""

import logging
from collections.abc import Callable, Mapping
from datetime import datetime
from re import compile as _compile
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
    RentmanLink,
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

_CODE_SEPARATOR = _compile(r"[,\n]+")

_LOGGER = logging.getLogger(__name__)


class _MissingIdError(ValueError):
    """An object payload carries no usable integer id."""


def _str_field(data: Mapping[str, Any], key: str, default: str = "") -> str:
    value = data.get(key)
    return value if isinstance(value, str) else default


def _str_or_none_field(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    return value if isinstance(value, str) else None


def _coerced_str_field(data: Mapping[str, Any], key: str) -> str:
    """Accept text or a number where the API declares a string."""
    value = data.get(key)
    if isinstance(value, bool):
        return ""
    if isinstance(value, str | int | float):
        return str(value)
    return ""


def _int_field(data: Mapping[str, Any], key: str) -> int | None:
    value = data.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _required_id(data: Mapping[str, Any]) -> int:
    """Read the id every documented object carries, or reject the object."""
    value = _int_field(data, "id")
    if value is None:
        msg = "The payload carries no usable id"
        raise _MissingIdError(msg)
    return value


def _parse_with_id[ModelT](
    data: Mapping[str, Any],
    parse_item: Callable[[Mapping[str, Any]], ModelT],
) -> ModelT | None:
    """Parse one object, dropping it when it carries no usable id."""
    try:
        return parse_item(data)
    except _MissingIdError:
        _LOGGER.debug(
            "Dropped one %s payload without a usable id",
            getattr(parse_item, "__name__", repr(parse_item)),
        )
        return None


def _float_field(data: Mapping[str, Any], key: str) -> float | None:
    value = data.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _bool_field(data: Mapping[str, Any], key: str) -> bool:
    return data.get(key) is True


def _datetime_field(data: Mapping[str, Any], key: str) -> datetime | None:
    value = data.get(key)
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _codes_field(data: Mapping[str, Any], key: str) -> tuple[str, ...]:
    """Split one comma or newline separated code list into a tuple."""
    value = data.get(key)
    if not isinstance(value, str):
        return ()
    return tuple(code for code in (part.strip() for part in _CODE_SEPARATOR.split(value)) if code)


def _custom_field(data: Mapping[str, Any]) -> dict[str, Any]:
    value = data.get("custom")
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _link_field(data: Mapping[str, Any], key: str) -> RentmanLink | None:
    """Resolve one linked field that carries a path string."""
    value = data.get(key)
    if isinstance(value, str):
        return RentmanLink(value)
    return None


def _link_or_model_field[ModelT](
    data: Mapping[str, Any],
    key: str,
    parse_model: Callable[[Mapping[str, Any]], ModelT],
) -> RentmanLink | ModelT | None:
    """Resolve one linked field: a path string or an expanded object."""
    value = data.get(key)
    if isinstance(value, str):
        return RentmanLink(value)
    if isinstance(value, Mapping):
        return _parse_with_id(value, parse_model)
    return None


def parse_page[ModelT](
    data: Any,
    parse_item: Callable[[Mapping[str, Any]], ModelT],
) -> RentmanPage[ModelT]:
    """Build one page of items from a collection envelope."""
    envelope = data if isinstance(data, Mapping) else {}
    raw_items = envelope.get("data")
    items: tuple[ModelT, ...] = ()
    if isinstance(raw_items, list):
        parsed = (
            _parse_with_id(item, parse_item) for item in raw_items if isinstance(item, Mapping)
        )
        items = tuple(item for item in parsed if item is not None)
    return RentmanPage(
        items=items,
        item_count=_int_field(envelope, "itemCount") or len(items),
        limit=_int_field(envelope, "limit") or 0,
        offset=_int_field(envelope, "offset") or 0,
        next_page_url=_str_or_none_field(envelope, "next_page_url"),
    )


def parse_envelope_item[ModelT](
    data: Any,
    parse_item: Callable[[Mapping[str, Any]], ModelT],
) -> ModelT | None:
    """Build one item from an item envelope or a bare object."""
    if not isinstance(data, Mapping):
        return None
    payload = data.get("data", data)
    if isinstance(payload, Mapping):
        return _parse_with_id(payload, parse_item)
    return None


def parse_equipment(data: Mapping[str, Any]) -> Equipment:
    """Build the equipment model from one equipment payload."""
    return Equipment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        folder=_link_or_model_field(data, "folder", parse_folder),
        code=_str_field(data, "code"),
        factor_group=_link_field(data, "factor_group"),
        name=_str_field(data, "name"),
        internal_remark=_str_field(data, "internal_remark"),
        external_remark=_str_field(data, "external_remark"),
        unit=_str_field(data, "unit"),
        in_shop=_bool_field(data, "in_shop"),
        surface_article=_bool_field(data, "surface_article"),
        shop_description_short=_str_field(data, "shop_description_short"),
        shop_description_long=_str_field(data, "shop_description_long"),
        shop_seo_title=_str_field(data, "shop_seo_title"),
        shop_seo_keyword=_str_field(data, "shop_seo_keyword"),
        shop_seo_description=_str_field(data, "shop_seo_description"),
        shop_featured=_bool_field(data, "shop_featured"),
        price=_float_field(data, "price"),
        subrental_costs=_float_field(data, "subrental_costs"),
        critical_stock_level=_int_field(data, "critical_stock_level"),
        type=_str_field(data, "type"),
        rental_sales=_str_field(data, "rental_sales"),
        temporary=_bool_field(data, "temporary"),
        in_planner=_bool_field(data, "in_planner"),
        in_archive=_bool_field(data, "in_archive"),
        stock_management=_str_field(data, "stock_management"),
        taxclass=_link_field(data, "taxclass"),
        list_price=_float_field(data, "list_price"),
        volume=_float_field(data, "volume"),
        packed_per=_int_field(data, "packed_per"),
        height=_float_field(data, "height"),
        width=_float_field(data, "width"),
        length=_float_field(data, "length"),
        weight=_float_field(data, "weight"),
        empty_weight=_float_field(data, "empty_weight"),
        power=_float_field(data, "power"),
        current=_float_field(data, "current"),
        country_of_origin=_str_field(data, "country_of_origin"),
        image=_link_field(data, "image"),
        ledger=_link_field(data, "ledger"),
        ledger_debit=_link_field(data, "ledger_debit"),
        defaultgroup=_str_field(data, "defaultgroup"),
        is_combination=_bool_field(data, "is_combination"),
        is_physical=_str_field(data, "is_physical"),
        can_edit_content_during_planning=_bool_field(data, "can_edit_content_during_planning"),
        strict_container_content=_str_field(data, "strict_container_content"),
        qrcodes=_codes_field(data, "qrcodes"),
        qrcodes_of_serial_numbers=_codes_field(data, "qrcodes_of_serial_numbers"),
        tags=_codes_field(data, "tags"),
        current_quantity_excl_cases=_int_field(data, "current_quantity_excl_cases"),
        current_quantity=_int_field(data, "current_quantity"),
        quantity_in_cases=_int_field(data, "quantity_in_cases"),
        location_in_warehouse=_str_field(data, "location_in_warehouse"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_serial_number(data: Mapping[str, Any]) -> SerialNumber:
    """Build the serial number model from one serial number payload."""
    return SerialNumber(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment)
        or RentmanLink(_str_field(data, "equipment")),
        serial=_str_field(data, "serial"),
        purchasedate=_datetime_field(data, "purchasedate"),
        depreciation_monthly=_float_field(data, "depreciation_monthly"),
        book_value=_float_field(data, "book_value"),
        residual_value=_float_field(data, "residual_value"),
        purchase_costs=_float_field(data, "purchase_costs"),
        active=_bool_field(data, "active"),
        remark=_str_field(data, "remark"),
        ref=_str_field(data, "ref"),
        asset_location=_link_or_model_field(data, "asset_location", parse_stock_location),
        image=_link_field(data, "image"),
        current_book_value=_float_field(data, "current_book_value"),
        next_inspection=_datetime_field(data, "next_inspection"),
        qrcodes=_codes_field(data, "qrcodes"),
        tags=_codes_field(data, "tags"),
        last_subproject=_link_or_model_field(data, "last_subproject", parse_subproject),
        sealed=_bool_field(data, "sealed"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_equipment_assigned_serial(data: Mapping[str, Any]) -> EquipmentAssignedSerial:
    """Build the assigned serial model from one assignment payload."""
    return EquipmentAssignedSerial(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        combination=_link_or_model_field(data, "combination", parse_serial_number)
        or RentmanLink(_str_field(data, "combination")),
        serialnumber=_link_or_model_field(data, "serialnumber", parse_serial_number)
        or RentmanLink(_str_field(data, "serialnumber")),
        raw=dict(data),
    )


def parse_actual_content(data: Mapping[str, Any]) -> ActualContent:
    """Build the actual content model from one content payload."""
    return ActualContent(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment),
        serial=_link_or_model_field(data, "serial", parse_serial_number),
        quantity=_coerced_str_field(data, "quantity"),
        combination_serial=_link_or_model_field(data, "combination_serial", parse_serial_number),
        raw=dict(data),
    )


def parse_equipment_set_content(data: Mapping[str, Any]) -> EquipmentSetContent:
    """Build the set content model from one set content payload."""
    return EquipmentSetContent(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        quantity=_coerced_str_field(data, "quantity"),
        parent_equipment=_link_or_model_field(data, "parent_equipment", parse_equipment)
        or RentmanLink(_str_field(data, "parent_equipment")),
        order=_coerced_str_field(data, "order"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment)
        or RentmanLink(_str_field(data, "equipment")),
        is_fixed=_str_field(data, "is_fixed"),
        is_physically_connected=_str_field(data, "is_physically_connected"),
        raw=dict(data),
    )


def parse_folder(data: Mapping[str, Any]) -> Folder:
    """Build the folder model from one folder payload."""
    return Folder(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        parent=_link_or_model_field(data, "parent", parse_folder),
        name=_str_field(data, "name"),
        order=_coerced_str_field(data, "order"),
        itemtype=_str_field(data, "itemtype"),
        path=_str_field(data, "path"),
        raw=dict(data),
    )


def parse_stock_location(data: Mapping[str, Any]) -> StockLocation:
    """Build the stock location model from one stock location payload."""
    return StockLocation(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        city=_str_field(data, "city"),
        street=_str_field(data, "street"),
        house_number=_str_field(data, "house_number"),
        postal_code=_str_field(data, "postal_code"),
        state_province=_str_field(data, "state_province"),
        country=_str_field(data, "country"),
        active=_bool_field(data, "active"),
        type=_str_field(data, "type"),
        color=_str_field(data, "color"),
        in_archive=_bool_field(data, "in_archive"),
        raw=dict(data),
    )


def parse_warehouse_status(data: Mapping[str, Any]) -> WarehouseStatus:
    """Build the warehouse status model from one warehouse status payload."""
    return WarehouseStatus(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        raw=dict(data),
    )


def parse_status(data: Mapping[str, Any]) -> Status:
    """Build the status model from one status payload."""
    return Status(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        raw=dict(data),
    )


def parse_stock_movement(data: Mapping[str, Any]) -> StockMovement:
    """Build the stock movement model from one stock movement payload."""
    return StockMovement(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        amount=_int_field(data, "amount"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment)
        or RentmanLink(_str_field(data, "equipment")),
        projectequipment=_link_or_model_field(data, "projectequipment", parse_project_equipment),
        description=_str_field(data, "description"),
        details=_str_field(data, "details"),
        date=_datetime_field(data, "date"),
        type=_str_field(data, "type"),
        stock_location=_link_or_model_field(data, "stock_location", parse_stock_location)
        or RentmanLink(_str_field(data, "stock_location")),
        api_client=_str_field(data, "api_client"),
        raw=dict(data),
    )


def parse_repair(data: Mapping[str, Any]) -> Repair:
    """Build the repair model from one repair payload."""
    return Repair(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        internal_name=_str_field(data, "internal_name"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment)
        or RentmanLink(_str_field(data, "equipment")),
        serialnumber=_link_or_model_field(data, "serialnumber", parse_serial_number),
        reporter=_link_field(data, "reporter"),
        assignee=_link_field(data, "assignee"),
        external_repairer=_link_field(data, "external_repairer"),
        number=_str_field(data, "number"),
        repairperiod_start=_datetime_field(data, "repairperiod_start"),
        repairperiod_end=_datetime_field(data, "repairperiod_end"),
        amount=_int_field(data, "amount"),
        remark=_str_field(data, "remark"),
        repair_costs=_float_field(data, "repair_costs"),
        is_usable=_str_field(data, "is_usable"),
        costs_charged_to_customer=_link_field(data, "costs_charged_to_customer"),
        subproject=_link_or_model_field(data, "subproject", parse_subproject),
        stock_location=_link_or_model_field(data, "stock_location", parse_stock_location),
        repair_status=_str_field(data, "repair_status"),
        unrepairable_of=_link_or_model_field(data, "unrepairable_of", parse_repair),
        tags=_codes_field(data, "tags"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_project(data: Mapping[str, Any]) -> Project:
    """Build the project model from one project payload."""
    return Project(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        location=_link_field(data, "location"),
        refundabledeposit=_float_field(data, "refundabledeposit"),
        deposit_status=_str_field(data, "deposit_status"),
        customer=_link_field(data, "customer"),
        loc_contact=_link_field(data, "loc_contact"),
        cust_contact=_link_field(data, "cust_contact"),
        project_type=_link_field(data, "project_type"),
        name=_str_field(data, "name"),
        reference=_str_field(data, "reference"),
        number=_str_field(data, "number"),
        account_manager=_link_field(data, "account_manager"),
        color=_str_field(data, "color"),
        conditions=_str_field(data, "conditions"),
        project_total_price=_float_field(data, "project_total_price"),
        project_total_price_cancelled=_float_field(data, "project_total_price_cancelled"),
        project_rental_price=_float_field(data, "project_rental_price"),
        project_sale_price=_float_field(data, "project_sale_price"),
        project_crew_price=_float_field(data, "project_crew_price"),
        project_transport_price=_float_field(data, "project_transport_price"),
        project_other_price=_float_field(data, "project_other_price"),
        project_insurance_price=_float_field(data, "project_insurance_price"),
        project_services_price=_float_field(data, "project_services_price"),
        estimated_cost=_float_field(data, "estimated_cost"),
        planned_cost=_float_field(data, "planned_cost"),
        actual_cost=_float_field(data, "actual_cost"),
        already_invoiced=_float_field(data, "already_invoiced"),
        tags=_codes_field(data, "tags"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        weight=_float_field(data, "weight"),
        power=_float_field(data, "power"),
        current=_float_field(data, "current"),
        equipment_period_from=_datetime_field(data, "equipment_period_from"),
        equipment_period_to=_datetime_field(data, "equipment_period_to"),
        purchasecosts=_float_field(data, "purchasecosts"),
        volume=_float_field(data, "volume"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_subproject(data: Mapping[str, Any]) -> Subproject:
    """Build the subproject model from one subproject payload."""
    return Subproject(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        order=_coerced_str_field(data, "order"),
        name=_str_field(data, "name"),
        status=_link_or_model_field(data, "status", parse_status)
        or RentmanLink(_str_field(data, "status")),
        is_template=_bool_field(data, "is_template"),
        location=_link_field(data, "location"),
        loc_contact=_link_field(data, "loc_contact"),
        insurance_rate=_float_field(data, "insurance_rate"),
        discount_rental=_float_field(data, "discount_rental"),
        discount_sale=_float_field(data, "discount_sale"),
        discount_crew=_float_field(data, "discount_crew"),
        discount_transport=_float_field(data, "discount_transport"),
        discount_additional_costs=_float_field(data, "discount_additional_costs"),
        discount_services=_float_field(data, "discount_services"),
        discount_subproject=_float_field(data, "discount_subproject"),
        discount_fixed=_bool_field(data, "discount_fixed"),
        discount_fixed_amount=_float_field(data, "discount_fixed_amount"),
        fixed_price=_bool_field(data, "fixed_price"),
        in_planning=_bool_field(data, "in_planning"),
        in_financial=_bool_field(data, "in_financial"),
        asset_location_from=_link_or_model_field(data, "asset_location_from", parse_stock_location),
        project_total_price=_float_field(data, "project_total_price"),
        project_total_price_cancelled=_float_field(data, "project_total_price_cancelled"),
        project_rental_price=_float_field(data, "project_rental_price"),
        project_sale_price=_float_field(data, "project_sale_price"),
        project_crew_price=_float_field(data, "project_crew_price"),
        project_transport_price=_float_field(data, "project_transport_price"),
        project_other_price=_float_field(data, "project_other_price"),
        project_insurance_price=_float_field(data, "project_insurance_price"),
        project_services_price=_float_field(data, "project_services_price"),
        estimated_cost=_float_field(data, "estimated_cost"),
        planned_cost=_float_field(data, "planned_cost"),
        actual_cost=_float_field(data, "actual_cost"),
        already_invoiced=_float_field(data, "already_invoiced"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        weight=_float_field(data, "weight"),
        power=_float_field(data, "power"),
        current=_float_field(data, "current"),
        purchasecosts=_float_field(data, "purchasecosts"),
        volume=_float_field(data, "volume"),
        equipment_period_from=_datetime_field(data, "equipment_period_from"),
        equipment_period_to=_datetime_field(data, "equipment_period_to"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_project_equipment(data: Mapping[str, Any]) -> ProjectEquipment:
    """Build the project equipment model from one planned equipment payload."""
    return ProjectEquipment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment),
        parent=_link_or_model_field(data, "parent", parse_project_equipment),
        ledger=_link_field(data, "ledger"),
        ledger_debit=_link_field(data, "ledger_debit"),
        quantity=_coerced_str_field(data, "quantity"),
        quantity_total=_int_field(data, "quantity_total"),
        equipment_group=_link_field(data, "equipment_group"),
        discount=_float_field(data, "discount"),
        is_option=_bool_field(data, "is_option"),
        factor=_coerced_str_field(data, "factor"),
        order=_coerced_str_field(data, "order"),
        unit_price=_float_field(data, "unit_price"),
        name=_str_field(data, "name"),
        external_remark=_str_field(data, "external_remark"),
        internal_remark=_str_field(data, "internal_remark"),
        delay_notified=_bool_field(data, "delay_notified"),
        duration=_float_field(data, "duration"),
        is_delayed=_bool_field(data, "is_delayed"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        has_missings=_bool_field(data, "has_missings"),
        warehouse_reservations=_int_field(data, "warehouse_reservations"),
        subrent_reservations=_int_field(data, "subrent_reservations"),
        serial_number_ids=_str_field(data, "serial_number_ids"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_accessory(data: Mapping[str, Any]) -> Accessory:
    """Build the accessory model from one accessory payload."""
    return Accessory(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        parent_equipment=_link_or_model_field(data, "parent_equipment", parse_equipment)
        or RentmanLink(_str_field(data, "parent_equipment")),
        equipment=_link_or_model_field(data, "equipment", parse_equipment),
        quantity=_int_field(data, "quantity"),
        automatic=_bool_field(data, "automatic"),
        skip=_bool_field(data, "skip"),
        is_free=_bool_field(data, "is_free"),
        order=_coerced_str_field(data, "order"),
        add_as_new_line=_bool_field(data, "add_as_new_line"),
        raw=dict(data),
    )


def parse_alternative(data: Mapping[str, Any]) -> Alternative:
    """Build the alternative model from one alternative payload."""
    return Alternative(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment)
        or RentmanLink(_str_field(data, "equipment")),
        alternative=_link_or_model_field(data, "alternative", parse_equipment)
        or RentmanLink(_str_field(data, "alternative")),
        raw=dict(data),
    )


def parse_supplier(data: Mapping[str, Any]) -> Supplier:
    """Build the supplier model from one supplier payload."""
    return Supplier(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        equipment=_link_or_model_field(data, "equipment", parse_equipment)
        or RentmanLink(_str_field(data, "equipment")),
        contact=_link_field(data, "contact"),
        contactperson=_link_field(data, "contactperson"),
        price=_float_field(data, "price"),
        details=_str_field(data, "details"),
        raw=dict(data),
    )


def parse_vehicle(data: Mapping[str, Any]) -> Vehicle:
    """Build the vehicle model from one vehicle payload."""
    return Vehicle(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        folder=_link_or_model_field(data, "folder", parse_folder),
        name=_str_field(data, "name"),
        cost_rate=_link_field(data, "cost_rate"),
        in_planner=_bool_field(data, "in_planner"),
        height=_float_field(data, "height"),
        length=_float_field(data, "length"),
        width=_float_field(data, "width"),
        seats=_int_field(data, "seats"),
        inspection_date=_datetime_field(data, "inspection_date"),
        licenseplate=_str_field(data, "licenseplate"),
        remark=_str_field(data, "remark"),
        payload_capacity=_float_field(data, "payload_capacity"),
        surface_area=_str_field(data, "surface_area"),
        multiple=_str_field(data, "multiple"),
        image=_link_field(data, "image"),
        asset_location=_link_or_model_field(data, "asset_location", parse_stock_location),
        tags=_codes_field(data, "tags"),
        distance_cost=_float_field(data, "distance_cost"),
        fixed_cost=_float_field(data, "fixed_cost"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_extra_input_field(data: Mapping[str, Any]) -> ExtraInputField:
    """Build the extra input field model from one field definition payload."""
    return ExtraInputField(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        itemtype=_str_field(data, "itemtype"),
        linkedItemType=_str_field(data, "linkedItemType"),
        parent=_link_or_model_field(data, "parent", parse_extra_input_field),
        type=_str_field(data, "type"),
        order=_coerced_str_field(data, "order"),
        hidden=_bool_field(data, "hidden"),
        classified=_bool_field(data, "classified"),
        search_include=_bool_field(data, "search_include"),
        search_minlength=_int_field(data, "search_minlength"),
        is_customfield_mandatory=_bool_field(data, "is_customfield_mandatory"),
        raw=dict(data),
    )


def parse_project_status(data: Mapping[str, Any]) -> ProjectStatus:
    """Build the project status model from one status payload."""
    return ProjectStatus(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        raw=dict(data),
    )


def parse_project_type(data: Mapping[str, Any]) -> ProjectType:
    """Build the project type model from one type payload."""
    return ProjectType(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        color=_str_field(data, "color"),
        type=_str_field(data, "type"),
        raw=dict(data),
    )


def parse_project_function_group(data: Mapping[str, Any]) -> ProjectFunctionGroup:
    """Build the function group model from one group payload."""
    return ProjectFunctionGroup(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        subproject=_link_or_model_field(data, "subproject", parse_subproject)
        or RentmanLink(_str_field(data, "subproject")),
        duration=_float_field(data, "duration"),
        planperiod_start_schedule_is_start=_str_field(data, "planperiod_start_schedule_is_start"),
        usageperiod_start_schedule_is_start=_str_field(data, "usageperiod_start_schedule_is_start"),
        planperiod_end_schedule_is_start=_str_field(data, "planperiod_end_schedule_is_start"),
        usageperiod_end_schedule_is_start=_str_field(data, "usageperiod_end_schedule_is_start"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        remark=_str_field(data, "remark"),
        raw=dict(data),
    )


def parse_project_function(data: Mapping[str, Any]) -> ProjectFunction:
    """Build the function model from one planned function payload."""
    return ProjectFunction(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        cost_rate=_link_field(data, "cost_rate"),
        cost_accommodation=_float_field(data, "cost_accommodation"),
        cost_catering=_float_field(data, "cost_catering"),
        cost_travel=_float_field(data, "cost_travel"),
        cost_other=_float_field(data, "cost_other"),
        price_rate=_link_field(data, "price_rate"),
        price_accommodation=_float_field(data, "price_accommodation"),
        price_catering=_float_field(data, "price_catering"),
        price_travel=_float_field(data, "price_travel"),
        price_other=_float_field(data, "price_other"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        subproject=_link_or_model_field(data, "subproject", parse_subproject)
        or RentmanLink(_str_field(data, "subproject")),
        is_template=_bool_field(data, "is_template"),
        group=_link_or_model_field(data, "group", parse_project_function_group),
        name_external=_str_field(data, "name_external"),
        name=_str_field(data, "name"),
        travel_time_before=_float_field(data, "travel_time_before"),
        travel_time_after=_float_field(data, "travel_time_after"),
        use_travel_time_from_location=_bool_field(data, "use_travel_time_from_location"),
        use_distance_from_location=_bool_field(data, "use_distance_from_location"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        planperiod_start_schedule_is_start=_str_field(data, "planperiod_start_schedule_is_start"),
        usageperiod_start_schedule_is_start=_str_field(data, "usageperiod_start_schedule_is_start"),
        planperiod_end_schedule_is_start=_str_field(data, "planperiod_end_schedule_is_start"),
        usageperiod_end_schedule_is_start=_str_field(data, "usageperiod_end_schedule_is_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        type=_str_field(data, "type"),
        duration=_float_field(data, "duration"),
        amount=_int_field(data, "amount"),
        break_=_float_field(data, "break"),
        distance=_float_field(data, "distance"),
        twoway=_bool_field(data, "twoway"),
        taxclass=_link_field(data, "taxclass"),
        ledger=_link_field(data, "ledger"),
        ledger_debit=_link_field(data, "ledger_debit"),
        order=_coerced_str_field(data, "order"),
        remark_client=_str_field(data, "remark_client"),
        remark_planner=_str_field(data, "remark_planner"),
        remark_crew=_str_field(data, "remark_crew"),
        in_financial=_bool_field(data, "in_financial"),
        in_planning=_bool_field(data, "in_planning"),
        is_plannable=_bool_field(data, "is_plannable"),
        recurrence_group=_int_field(data, "recurrence_group"),
        recurrence_enddate=_datetime_field(data, "recurrence_enddate"),
        recurrence_interval_unit=_str_field(data, "recurrence_interval_unit"),
        recurrence_interval=_int_field(data, "recurrence_interval"),
        recurrence_weekdays=_str_or_none_field(data, "recurrence_weekdays"),
        price_fixed=_float_field(data, "price_fixed"),
        price_variable=_float_field(data, "price_variable"),
        costs_fixed=_float_field(data, "costs_fixed"),
        costs_variable=_float_field(data, "costs_variable"),
        price_total=_float_field(data, "price_total"),
        costs_total=_float_field(data, "costs_total"),
        tags=_codes_field(data, "tags"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_project_crew(data: Mapping[str, Any]) -> ProjectCrew:
    """Build the project crew model from one crew planning payload."""
    return ProjectCrew(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        cost_rate=_link_field(data, "cost_rate"),
        cost_accommodation=_float_field(data, "cost_accommodation"),
        cost_catering=_float_field(data, "cost_catering"),
        cost_travel=_float_field(data, "cost_travel"),
        cost_other=_float_field(data, "cost_other"),
        function=_link_or_model_field(data, "function", parse_project_function)
        or RentmanLink(_str_field(data, "function")),
        crewmember=_link_field(data, "crewmember") or RentmanLink(_str_field(data, "crewmember")),
        visible=_bool_field(data, "visible"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        transport=_str_field(data, "transport"),
        remark=_str_field(data, "remark"),
        remark_planner=_str_field(data, "remark_planner"),
        invoice_reference=_str_field(data, "invoice_reference"),
        project_leader=_bool_field(data, "project_leader"),
        is_visible_on_dashboard=_bool_field(data, "is_visible_on_dashboard"),
        costs=_float_field(data, "costs"),
        cost_actual=_float_field(data, "cost_actual"),
        hours_registered=_float_field(data, "hours_registered"),
        hours_planned=_float_field(data, "hours_planned"),
        cost_planned=_float_field(data, "cost_planned"),
        diff_cost=_float_field(data, "diff_cost"),
        diff_hours=_float_field(data, "diff_hours"),
        activity_status=_str_field(data, "activity_status"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_project_vehicle(data: Mapping[str, Any]) -> ProjectVehicle:
    """Build the project vehicle model from one transport planning payload."""
    return ProjectVehicle(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        cost_rate=_link_field(data, "cost_rate"),
        function=_link_or_model_field(data, "function", parse_project_function)
        or RentmanLink(_str_field(data, "function")),
        transport=_str_field(data, "transport"),
        vehicle=_link_or_model_field(data, "vehicle", parse_vehicle)
        or RentmanLink(_str_field(data, "vehicle")),
        planningperiod_start=_datetime_field(data, "planningperiod_start"),
        planningperiod_end=_datetime_field(data, "planningperiod_end"),
        remark=_str_field(data, "remark"),
        remark_planner=_str_field(data, "remark_planner"),
        costs=_float_field(data, "costs"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_project_equipment_group(data: Mapping[str, Any]) -> ProjectEquipmentGroup:
    """Build the equipment group model from one group payload."""
    return ProjectEquipmentGroup(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        subproject=_link_or_model_field(data, "subproject", parse_subproject)
        or RentmanLink(_str_field(data, "subproject")),
        additional_scanned=_bool_field(data, "additional_scanned"),
        name=_str_field(data, "name"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        duration=_float_field(data, "duration"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        is_delayed=_bool_field(data, "is_delayed"),
        order=_coerced_str_field(data, "order"),
        in_price_calculation=_bool_field(data, "in_price_calculation"),
        remark=_str_field(data, "remark"),
        weight=_float_field(data, "weight"),
        power=_float_field(data, "power"),
        current=_float_field(data, "current"),
        volume=_float_field(data, "volume"),
        total_new_price=_float_field(data, "total_new_price"),
        raw=dict(data),
    )


def parse_project_cost(data: Mapping[str, Any]) -> ProjectCost:
    """Build the project cost model from one cost line payload."""
    return ProjectCost(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        remark=_str_field(data, "remark"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        quantity=_int_field(data, "quantity"),
        discount=_float_field(data, "discount"),
        order=_coerced_str_field(data, "order"),
        subproject=_link_or_model_field(data, "subproject", parse_subproject)
        or RentmanLink(_str_field(data, "subproject")),
        is_template=_bool_field(data, "is_template"),
        taxclass=_link_field(data, "taxclass"),
        ledger=_link_field(data, "ledger"),
        ledger_debit=_link_field(data, "ledger_debit"),
        sale_price=_float_field(data, "sale_price"),
        purchase_price=_float_field(data, "purchase_price"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_project_request(data: Mapping[str, Any]) -> ProjectRequest:
    """Build the project request model from one request payload."""
    return ProjectRequest(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        linked_contact=_link_field(data, "linked_contact"),
        contact_mailing_number=_str_field(data, "contact_mailing_number"),
        contact_mailing_country=_str_field(data, "contact_mailing_country"),
        contact_name=_str_field(data, "contact_name"),
        contact_mailing_postalcode=_str_field(data, "contact_mailing_postalcode"),
        contact_phone=_str_field(data, "contact_phone"),
        contact_mailing_city=_str_field(data, "contact_mailing_city"),
        contact_mailing_street=_str_field(data, "contact_mailing_street"),
        linked_contact_person=_link_field(data, "linked_contact_person"),
        contact_person_lastname=_str_field(data, "contact_person_lastname"),
        contact_person_email=_str_field(data, "contact_person_email"),
        contact_person_middle_name=_str_field(data, "contact_person_middle_name"),
        contact_person_first_name=_str_field(data, "contact_person_first_name"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        is_paid=_bool_field(data, "is_paid"),
        language=_str_field(data, "language"),
        in_=_datetime_field(data, "in"),
        out_=_datetime_field(data, "out"),
        linked_location=_link_field(data, "linked_location"),
        location_mailing_number=_str_field(data, "location_mailing_number"),
        location_mailing_country=_str_field(data, "location_mailing_country"),
        location_name=_str_field(data, "location_name"),
        location_mailing_postalcode=_str_field(data, "location_mailing_postalcode"),
        location_mailing_city=_str_field(data, "location_mailing_city"),
        location_mailing_street=_str_field(data, "location_mailing_street"),
        location_phone=_str_field(data, "location_phone"),
        name=_str_field(data, "name"),
        external_reference=_int_field(data, "external_reference"),
        remark=_str_field(data, "remark"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        price=_float_field(data, "price"),
        linked_project=_link_or_model_field(data, "linked_project", parse_project),
        source=_str_field(data, "source"),
        status=_str_field(data, "status"),
        raw=dict(data),
    )


def parse_project_request_equipment(data: Mapping[str, Any]) -> ProjectRequestEquipment:
    """Build the request equipment model from one requested line payload."""
    return ProjectRequestEquipment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        quantity=_int_field(data, "quantity"),
        quantity_total=_int_field(data, "quantity_total"),
        is_comment=_bool_field(data, "is_comment"),
        is_kit=_bool_field(data, "is_kit"),
        discount=_float_field(data, "discount"),
        linked_equipment=_link_or_model_field(data, "linked_equipment", parse_equipment),
        name=_str_field(data, "name"),
        external_remark=_str_field(data, "external_remark"),
        parent=_link_or_model_field(data, "parent", parse_project_request_equipment),
        unit_price=_float_field(data, "unit_price"),
        project_request=_link_or_model_field(data, "project_request", parse_project_request)
        or RentmanLink(_str_field(data, "project_request")),
        factor=_coerced_str_field(data, "factor"),
        order=_coerced_str_field(data, "order"),
        raw=dict(data),
    )


def parse_quote(data: Mapping[str, Any]) -> Quote:
    """Build the quote model from one quotation payload."""
    return Quote(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        number=_str_field(data, "number"),
        customer=_link_field(data, "customer"),
        contact=_link_field(data, "contact"),
        date=_datetime_field(data, "date"),
        expiration_date=_datetime_field(data, "expiration_date"),
        version=_int_field(data, "version"),
        subject=_str_field(data, "subject"),
        show_tax=_bool_field(data, "show_tax"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        filename=_str_field(data, "filename"),
        project_total_price=_float_field(data, "project_total_price"),
        project_total_price_cancelled=_float_field(data, "project_total_price_cancelled"),
        project_rental_price=_float_field(data, "project_rental_price"),
        project_sale_price=_float_field(data, "project_sale_price"),
        project_crew_price=_float_field(data, "project_crew_price"),
        project_transport_price=_float_field(data, "project_transport_price"),
        project_other_price=_float_field(data, "project_other_price"),
        project_insurance_price=_float_field(data, "project_insurance_price"),
        project_services_price=_float_field(data, "project_services_price"),
        price=_float_field(data, "price"),
        price_invat=_float_field(data, "price_invat"),
        vat_amount=_float_field(data, "vat_amount"),
        tags=_codes_field(data, "tags"),
        raw=dict(data),
    )


def parse_contract(data: Mapping[str, Any]) -> Contract:
    """Build the contract model from one contract payload."""
    return Contract(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        number=_str_field(data, "number"),
        customer=_link_field(data, "customer"),
        contact=_link_field(data, "contact"),
        date=_datetime_field(data, "date"),
        expiration_date=_datetime_field(data, "expiration_date"),
        version=_int_field(data, "version"),
        subject=_str_field(data, "subject"),
        show_tax=_bool_field(data, "show_tax"),
        project=_link_or_model_field(data, "project", parse_project)
        or RentmanLink(_str_field(data, "project")),
        filename=_str_field(data, "filename"),
        project_total_price=_float_field(data, "project_total_price"),
        project_total_price_cancelled=_float_field(data, "project_total_price_cancelled"),
        project_rental_price=_float_field(data, "project_rental_price"),
        project_sale_price=_float_field(data, "project_sale_price"),
        project_crew_price=_float_field(data, "project_crew_price"),
        project_transport_price=_float_field(data, "project_transport_price"),
        project_other_price=_float_field(data, "project_other_price"),
        project_insurance_price=_float_field(data, "project_insurance_price"),
        project_services_price=_float_field(data, "project_services_price"),
        price=_float_field(data, "price"),
        price_invat=_float_field(data, "price_invat"),
        vat_amount=_float_field(data, "vat_amount"),
        raw=dict(data),
    )


def parse_invoice(data: Mapping[str, Any]) -> Invoice:
    """Build the invoice model from one invoice payload."""
    return Invoice(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        customer=_link_field(data, "customer"),
        account_manager=_link_field(data, "account_manager"),
        contact=_link_field(data, "contact"),
        expiration=_datetime_field(data, "expiration"),
        date=_datetime_field(data, "date"),
        number=_str_field(data, "number"),
        procent=_float_field(data, "procent"),
        from_project=_bool_field(data, "from_project"),
        subject=_str_field(data, "subject"),
        finalized=_bool_field(data, "finalized"),
        integration_reference_id=_str_or_none_field(data, "integration_reference_id"),
        project=_link_or_model_field(data, "project", parse_project),
        filename=_str_field(data, "filename"),
        project_total_price=_float_field(data, "project_total_price"),
        project_total_price_cancelled=_float_field(data, "project_total_price_cancelled"),
        project_rental_price=_float_field(data, "project_rental_price"),
        project_sale_price=_float_field(data, "project_sale_price"),
        project_crew_price=_float_field(data, "project_crew_price"),
        project_transport_price=_float_field(data, "project_transport_price"),
        project_other_price=_float_field(data, "project_other_price"),
        project_insurance_price=_float_field(data, "project_insurance_price"),
        project_services_price=_float_field(data, "project_services_price"),
        sum_factuurregels=_float_field(data, "sum_factuurregels"),
        price=_float_field(data, "price"),
        price_invat=_float_field(data, "price_invat"),
        vat_amount=_float_field(data, "vat_amount"),
        invoicetype=_str_field(data, "invoicetype"),
        outstanding_balance=_float_field(data, "outstanding_balance"),
        total_paid=_float_field(data, "total_paid"),
        is_paid=_bool_field(data, "is_paid"),
        date_sent=_datetime_field(data, "date_sent"),
        payment_reminder_sent=_int_field(data, "payment_reminder_sent"),
        final_payment_reminder_sent=_datetime_field(data, "final_payment_reminder_sent"),
        payment_date=_datetime_field(data, "payment_date"),
        days_after_expiry=_int_field(data, "days_after_expiry"),
        tags=_codes_field(data, "tags"),
        raw=dict(data),
    )


def parse_ledger_code(data: Mapping[str, Any]) -> LedgerCode:
    """Build the ledger code model from one ledger account payload."""
    return LedgerCode(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        code=_str_field(data, "code"),
        is_credit=_bool_field(data, "is_credit"),
        is_debit=_bool_field(data, "is_debit"),
        raw=dict(data),
    )


def parse_tax_class(data: Mapping[str, Any]) -> TaxClass:
    """Build the tax class model from one tax class payload."""
    return TaxClass(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        code=_str_field(data, "code"),
        type=_str_field(data, "type"),
        raw=dict(data),
    )


def parse_invoice_line(data: Mapping[str, Any]) -> InvoiceLine:
    """Build the invoice line model from one VAT line payload."""
    return InvoiceLine(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        item=_int_field(data, "item"),
        base=_float_field(data, "base"),
        ledger=_link_or_model_field(data, "ledger", parse_ledger_code)
        or RentmanLink(_str_field(data, "ledger")),
        vatrate=_float_field(data, "vatrate"),
        vatamount=_float_field(data, "vatamount"),
        priceincl=_float_field(data, "priceincl"),
        ledgercode=_str_field(data, "ledgercode"),
        parent_api_path=_str_field(data, "parent_api_path"),
        raw=dict(data),
    )


def parse_payment(data: Mapping[str, Any]) -> Payment:
    """Build the payment model from one payment payload."""
    return Payment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        invoice=_link_or_model_field(data, "invoice", parse_invoice)
        or RentmanLink(_str_field(data, "invoice")),
        moment=_datetime_field(data, "moment"),
        amount=_float_field(data, "amount"),
        description=_str_field(data, "description"),
        payment_import_source=_str_field(data, "payment_import_source"),
        raw=dict(data),
    )


def parse_subrental(data: Mapping[str, Any]) -> Subrental:
    """Build the subrental model from one subrental payload."""
    return Subrental(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        accountmanager=_link_field(data, "accountmanager"),
        reference=_str_field(data, "reference"),
        supplier=_link_field(data, "supplier"),
        number=_coerced_str_field(data, "number"),
        contactperson=_link_field(data, "contactperson"),
        location=_link_field(data, "location"),
        location_contact=_link_field(data, "location_contact"),
        usageperiod_start=_datetime_field(data, "usageperiod_start"),
        usageperiod_end=_datetime_field(data, "usageperiod_end"),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        delivery_in=_datetime_field(data, "delivery_in"),
        delivery_out=_datetime_field(data, "delivery_out"),
        equipment_cost=_float_field(data, "equipment_cost"),
        price=_float_field(data, "price"),
        extra_cost=_float_field(data, "extra_cost"),
        auto_update_costs=_bool_field(data, "auto_update_costs"),
        remark=_str_field(data, "remark"),
        type=_str_field(data, "type"),
        status=_link_or_model_field(data, "status", parse_status)
        or RentmanLink(_str_field(data, "status")),
        sent=_datetime_field(data, "sent"),
        asset_location_to=_link_or_model_field(data, "asset_location_to", parse_stock_location),
        asset_location_from=_link_or_model_field(data, "asset_location_from", parse_stock_location),
        is_internal=_bool_field(data, "is_internal"),
        supplier_project=_link_or_model_field(data, "supplier_project", parse_project),
        tags=_codes_field(data, "tags"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_subrental_equipment_group(data: Mapping[str, Any]) -> SubrentalEquipmentGroup:
    """Build the subrental group model from one group payload."""
    return SubrentalEquipmentGroup(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        subrental=_link_or_model_field(data, "subrental", parse_subrental)
        or RentmanLink(_str_field(data, "subrental")),
        name=_str_field(data, "name"),
        order=_coerced_str_field(data, "order"),
        supplier_category=_link_field(data, "supplier_category"),
        raw=dict(data),
    )


def parse_subrental_equipment(data: Mapping[str, Any]) -> SubrentalEquipment:
    """Build the subrental equipment model from one subrental line payload."""
    return SubrentalEquipment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        subrental_group=_link_or_model_field(
            data, "subrental_group", parse_subrental_equipment_group
        )
        or RentmanLink(_str_field(data, "subrental_group")),
        equipment=_link_or_model_field(data, "equipment", parse_equipment),
        parent=_link_or_model_field(data, "parent", parse_subrental_equipment),
        planperiod_start=_datetime_field(data, "planperiod_start"),
        planperiod_end=_datetime_field(data, "planperiod_end"),
        name=_str_field(data, "name"),
        quantity=_int_field(data, "quantity"),
        quantity_total=_int_field(data, "quantity_total"),
        unit_price=_float_field(data, "unit_price"),
        discount=_float_field(data, "discount"),
        factor=_coerced_str_field(data, "factor"),
        order=_coerced_str_field(data, "order"),
        remark=_str_field(data, "remark"),
        lineprice=_float_field(data, "lineprice"),
        supplier_planningmateriaal=_link_field(data, "supplier_planningmateriaal"),
        raw=dict(data),
    )


def parse_purchase_order(data: Mapping[str, Any]) -> PurchaseOrder:
    """Build the purchase order model from one purchase order payload."""
    return PurchaseOrder(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        filename=_str_field(data, "filename"),
        subject=_str_field(data, "subject"),
        owner=_link_field(data, "owner") or RentmanLink(_str_field(data, "owner")),
        date_of_issue=_datetime_field(data, "date_of_issue"),
        delivery_date=_datetime_field(data, "delivery_date"),
        description=_str_field(data, "description"),
        number=_str_field(data, "number"),
        approval_status=_str_field(data, "approval_status"),
        previous_status=_str_field(data, "previous_status"),
        approved_amount=_float_field(data, "approved_amount"),
        supplier=_link_field(data, "supplier"),
        contact_person=_link_field(data, "contact_person"),
        delivery_type=_str_field(data, "delivery_type"),
        delivery_location=_link_field(data, "delivery_location"),
        delivery_location_person=_link_field(data, "delivery_location_person"),
        delivery_warehouse=_link_or_model_field(data, "delivery_warehouse", parse_stock_location),
        accounting_code=_str_field(data, "accounting_code"),
        export_status=_str_field(data, "export_status"),
        export_date=_datetime_field(data, "export_date"),
        export_message=_str_or_none_field(data, "export_message"),
        tags=_codes_field(data, "tags"),
        underlying_cost_amount=_float_field(data, "underlying_cost_amount"),
        underlying_cost_amount_tax=_float_field(data, "underlying_cost_amount_tax"),
        underlying_cost_amount_with_tax=_float_field(data, "underlying_cost_amount_with_tax"),
        approved_by=_link_field(data, "approved_by"),
        approved_at=_datetime_field(data, "approved_at"),
        projects_json=_str_or_none_field(data, "projects_json"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_purchase_order_cost(data: Mapping[str, Any]) -> PurchaseOrderCost:
    """Build the purchase order cost model from one cost line payload."""
    return PurchaseOrderCost(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        purchase_order=_link_or_model_field(data, "purchase_order", parse_purchase_order)
        or RentmanLink(_str_field(data, "purchase_order")),
        costitem=_int_field(data, "costitem"),
        costitemtype=_str_field(data, "costitemtype"),
        approved_amount=_float_field(data, "approved_amount"),
        project=_str_field(data, "project"),
        underlying_cost_amount=_float_field(data, "underlying_cost_amount"),
        underlying_cost_amount_tax=_float_field(data, "underlying_cost_amount_tax"),
        underlying_cost_amount_with_tax=_float_field(data, "underlying_cost_amount_with_tax"),
        quantity=_int_field(data, "quantity"),
        raw=dict(data),
    )


def parse_purchase_order_global_cost(data: Mapping[str, Any]) -> PurchaseOrderGlobalCost:
    """Build the global cost model from one global cost line payload."""
    return PurchaseOrderGlobalCost(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        purchase_order=_link_or_model_field(data, "purchase_order", parse_purchase_order)
        or RentmanLink(_str_field(data, "purchase_order")),
        name=_str_field(data, "name"),
        unit_purchase_cost=_float_field(data, "unit_purchase_cost"),
        quantity=_int_field(data, "quantity"),
        taxclass=_link_or_model_field(data, "taxclass", parse_tax_class),
        raw=dict(data),
    )


def parse_crew(data: Mapping[str, Any]) -> Crew:
    """Build the crew model from one crew member payload."""
    return Crew(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        folder=_link_or_model_field(data, "folder", parse_folder),
        street=_str_field(data, "street"),
        housenumber=_str_field(data, "housenumber"),
        unit_number=_str_field(data, "unit_number"),
        district=_str_field(data, "district"),
        city=_str_field(data, "city"),
        postal_code=_str_field(data, "postal_code"),
        addressline2=_str_field(data, "addressline2"),
        extraaddressline=_str_field(data, "extraaddressline"),
        state=_str_field(data, "state"),
        country=_str_field(data, "country"),
        birthdate=_datetime_field(data, "birthdate"),
        passport_number=_str_field(data, "passport_number"),
        emergency_contact=_str_field(data, "emergency_contact"),
        remark=_str_field(data, "remark"),
        driving_license=_str_field(data, "driving_license"),
        contract=_coerced_str_field(data, "contract"),
        bank=_str_field(data, "bank"),
        contract_date=_datetime_field(data, "contract_date"),
        company_name=_str_field(data, "company_name"),
        vat_code=_str_field(data, "vat_code"),
        coc_code=_str_field(data, "coc_code"),
        firstname=_str_field(data, "firstname"),
        middle_name=_str_field(data, "middle_name"),
        lastname=_str_field(data, "lastname"),
        email=_str_field(data, "email"),
        phone=_str_field(data, "phone"),
        active=_bool_field(data, "active"),
        avatar=_link_field(data, "avatar"),
        vt_fullname=_str_field(data, "vt_fullname"),
        default_warehouse=_link_or_model_field(data, "default_warehouse", parse_stock_location),
        external_reference=_str_field(data, "external_reference"),
        tags=_codes_field(data, "tags"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_crew_availability(data: Mapping[str, Any]) -> CrewAvailability:
    """Build the availability model from one availability window payload."""
    return CrewAvailability(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        last_updater=_link_field(data, "last_updater"),
        last_updated=_datetime_field(data, "last_updated"),
        start=_datetime_field(data, "start"),
        end=_datetime_field(data, "end"),
        crewmember=_link_or_model_field(data, "crewmember", parse_crew)
        or RentmanLink(_str_field(data, "crewmember")),
        status=_str_field(data, "status"),
        remark=_str_field(data, "remark"),
        recurrence_interval_unit=_str_field(data, "recurrence_interval_unit"),
        recurrence_enddate=_datetime_field(data, "recurrence_enddate"),
        recurrence_interval=_int_field(data, "recurrence_interval"),
        recurrent_group=_int_field(data, "recurrent_group"),
        recurrence_weekdays=_str_field(data, "recurrence_weekdays"),
        raw=dict(data),
    )


def parse_crew_rate(data: Mapping[str, Any]) -> CrewRate:
    """Build the crew rate model from one crew rate payload."""
    return CrewRate(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        naam=_str_field(data, "naam"),
        cost_rate=_link_field(data, "cost_rate"),
        medewerker=_link_or_model_field(data, "medewerker", parse_crew)
        or RentmanLink(_str_field(data, "medewerker")),
        raw=dict(data),
    )


def parse_appointment(data: Mapping[str, Any]) -> Appointment:
    """Build the appointment model from one appointment payload."""
    return Appointment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        start=_datetime_field(data, "start"),
        end=_datetime_field(data, "end"),
        color=_str_field(data, "color"),
        location=_str_field(data, "location"),
        remark=_str_field(data, "remark"),
        is_public=_bool_field(data, "is_public"),
        is_plannable=_bool_field(data, "is_plannable"),
        recurrence_interval_unit=_str_field(data, "recurrence_interval_unit"),
        recurrence_enddate=_datetime_field(data, "recurrence_enddate"),
        recurrence_interval=_int_field(data, "recurrence_interval"),
        recurrence_group=_int_field(data, "recurrence_group"),
        recurrence_weekdays=_str_or_none_field(data, "recurrence_weekdays"),
        synchronization_id=_str_field(data, "synchronization_id"),
        synchronisation_uri=_str_field(data, "synchronisation_uri"),
        raw=dict(data),
    )


def parse_appointment_crew(data: Mapping[str, Any]) -> AppointmentCrew:
    """Build the appointment crew model from one attachment payload."""
    return AppointmentCrew(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        appointment=_link_or_model_field(data, "appointment", parse_appointment)
        or RentmanLink(_str_field(data, "appointment")),
        crew=_link_or_model_field(data, "crew", parse_crew)
        or RentmanLink(_str_field(data, "crew")),
        raw=dict(data),
    )


def parse_invitation(data: Mapping[str, Any]) -> Invitation:
    """Build the invitation model from one planning invitation payload."""
    return Invitation(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        type=_str_field(data, "type"),
        accepted=_bool_field(data, "accepted"),
        responded_timestamp=_datetime_field(data, "responded_timestamp"),
        expiration_date=_datetime_field(data, "expiration_date"),
        start=_datetime_field(data, "start"),
        end=_datetime_field(data, "end"),
        function=_link_field(data, "function"),
        projectcrew=_link_field(data, "projectcrew"),
        crewmember=_link_or_model_field(data, "crewmember", parse_crew)
        or RentmanLink(_str_field(data, "crewmember")),
        remark=_str_field(data, "remark"),
        emailstatus=_str_field(data, "emailstatus"),
        last_reminder=_datetime_field(data, "last_reminder"),
        location_details=_str_or_none_field(data, "location_details"),
        auto_reminder_date=_datetime_field(data, "auto_reminder_date"),
        auto_reminder_sent=_int_field(data, "auto_reminder_sent"),
        raw=dict(data),
    )


def parse_leave_type(data: Mapping[str, Any]) -> LeaveType:
    """Build the leave type model from one leave type payload."""
    return LeaveType(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        type=_str_field(data, "type"),
        name=_str_field(data, "name"),
        payroll_code=_str_field(data, "payroll_code"),
        color=_str_field(data, "color"),
        requires_approval=_bool_field(data, "requires_approval"),
        affects_availability=_bool_field(data, "affects_availability"),
        has_balance=_bool_field(data, "has_balance"),
        balance_start_date=_datetime_field(data, "balance_start_date"),
        is_labor=_str_field(data, "is_labor"),
        has_calculated_duration=_bool_field(data, "has_calculated_duration"),
        can_have_activities=_bool_field(data, "can_have_activities"),
        counts_in_totals=_bool_field(data, "counts_in_totals"),
        raw=dict(data),
    )


def parse_leave_request(data: Mapping[str, Any]) -> LeaveRequest:
    """Build the leave request model from one leave request payload."""
    return LeaveRequest(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        description=_str_field(data, "description"),
        approval_status=_str_field(data, "approval_status"),
        requested_for=_link_or_model_field(data, "requested_for", parse_crew)
        or RentmanLink(_str_field(data, "requested_for")),
        reviewed_on=_datetime_field(data, "reviewed_on"),
        reviewer=_link_field(data, "reviewer"),
        raw=dict(data),
    )


def parse_leave_mutation(data: Mapping[str, Any]) -> LeaveMutation:
    """Build the leave mutation model from one balance mutation payload."""
    return LeaveMutation(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        description=_str_field(data, "description"),
        duration=_float_field(data, "duration"),
        crewmember=_link_or_model_field(data, "crewmember", parse_crew)
        or RentmanLink(_str_field(data, "crewmember")),
        leavetype=_link_or_model_field(data, "leavetype", parse_leave_type)
        or RentmanLink(_str_field(data, "leavetype")),
        mutation_date=_datetime_field(data, "mutation_date"),
        raw=dict(data),
    )


def parse_time_registration(data: Mapping[str, Any]) -> TimeRegistration:
    """Build the time registration model from one registration payload."""
    return TimeRegistration(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        crewmember=_link_or_model_field(data, "crewmember", parse_crew),
        start=_datetime_field(data, "start"),
        end=_datetime_field(data, "end"),
        distance=_float_field(data, "distance"),
        is_lunch_included=_bool_field(data, "is_lunch_included"),
        leavetype=_link_or_model_field(data, "leavetype", parse_leave_type),
        leaverequest=_link_or_model_field(data, "leaverequest", parse_leave_request),
        duration=_float_field(data, "duration"),
        break_duration=_float_field(data, "break_duration"),
        travel_time=_float_field(data, "travel_time"),
        correction_duration=_float_field(data, "correction_duration"),
        remark=_str_field(data, "remark"),
        status=_str_field(data, "status"),
        break_duration_with_start_end=_float_field(data, "break_duration_with_start_end"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_time_registration_activity(data: Mapping[str, Any]) -> TimeRegistrationActivity:
    """Build the activity model from one activity line payload."""
    return TimeRegistrationActivity(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        time_registration=_link_or_model_field(data, "time_registration", parse_time_registration)
        or RentmanLink(_str_field(data, "time_registration")),
        project_function=_link_or_model_field(data, "project_function", parse_project_function),
        subproject_function=_link_or_model_field(
            data, "subproject_function", parse_project_function
        ),
        description=_str_field(data, "description"),
        duration=_float_field(data, "duration"),
        is_activity=_bool_field(data, "is_activity"),
        from_=_datetime_field(data, "from"),
        to=_datetime_field(data, "to"),
        raw=dict(data),
    )


def parse_contact(data: Mapping[str, Any]) -> Contact:
    """Build the contact model from one contact payload."""
    return Contact(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        folder=_link_or_model_field(data, "folder", parse_folder),
        type=_str_field(data, "type"),
        ext_name_line=_str_field(data, "ext_name_line"),
        firstname=_str_field(data, "firstname"),
        distance=_float_field(data, "distance"),
        travel_time=_float_field(data, "travel_time"),
        surfix=_str_field(data, "surfix"),
        surname=_str_field(data, "surname"),
        longitude=_float_field(data, "longitude"),
        latitude=_float_field(data, "latitude"),
        code=_str_field(data, "code"),
        accounting_code=_str_field(data, "accounting_code"),
        vendor_accounting_code=_str_field(data, "vendor_accounting_code"),
        name=_str_field(data, "name"),
        gender=_str_field(data, "gender"),
        mailing_city=_str_field(data, "mailing_city"),
        mailing_street=_str_field(data, "mailing_street"),
        mailing_number=_str_field(data, "mailing_number"),
        mailing_unit_number=_str_field(data, "mailing_unit_number"),
        mailing_district=_str_field(data, "mailing_district"),
        mailing_extra_address_line=_str_field(data, "mailing_extra_address_line"),
        mailing_postalcode=_str_field(data, "mailing_postalcode"),
        mailing_state=_str_field(data, "mailing_state"),
        mailing_country=_str_field(data, "mailing_country"),
        visit_city=_str_field(data, "visit_city"),
        visit_street=_str_field(data, "visit_street"),
        visit_number=_str_field(data, "visit_number"),
        visit_unit_number=_str_field(data, "visit_unit_number"),
        visit_district=_str_field(data, "visit_district"),
        visit_extra_address_line=_str_field(data, "visit_extra_address_line"),
        visit_postalcode=_str_field(data, "visit_postalcode"),
        visit_state=_str_field(data, "visit_state"),
        country=_str_field(data, "country"),
        invoice_city=_str_field(data, "invoice_city"),
        invoice_street=_str_field(data, "invoice_street"),
        invoice_number=_str_field(data, "invoice_number"),
        invoice_unit_number=_str_field(data, "invoice_unit_number"),
        invoice_district=_str_field(data, "invoice_district"),
        invoice_extra_address_line=_str_field(data, "invoice_extra_address_line"),
        invoice_postalcode=_str_field(data, "invoice_postalcode"),
        invoice_state=_str_field(data, "invoice_state"),
        invoice_country=_str_field(data, "invoice_country"),
        phone_1=_str_field(data, "phone_1"),
        phone_2=_str_field(data, "phone_2"),
        email_1=_str_field(data, "email_1"),
        email_2=_str_field(data, "email_2"),
        website=_str_field(data, "website"),
        VAT_code=_str_field(data, "VAT_code"),
        fiscal_code=_str_field(data, "fiscal_code"),
        commerce_code=_str_field(data, "commerce_code"),
        purchase_number=_str_field(data, "purchase_number"),
        bic=_str_field(data, "bic"),
        bank_account=_str_field(data, "bank_account"),
        default_person=_link_or_model_field(data, "default_person", parse_contact_person),
        admin_contactperson=_link_field(data, "admin_contactperson"),
        discount_crew=_float_field(data, "discount_crew"),
        discount_transport=_float_field(data, "discount_transport"),
        discount_rental=_float_field(data, "discount_rental"),
        discount_sale=_float_field(data, "discount_sale"),
        discount_total=_float_field(data, "discount_total"),
        projectnote=_str_field(data, "projectnote"),
        projectnote_title=_str_field(data, "projectnote_title"),
        contact_warning=_str_field(data, "contact_warning"),
        discount_subrent=_float_field(data, "discount_subrent"),
        image=_link_field(data, "image"),
        tags=_codes_field(data, "tags"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_contact_person(data: Mapping[str, Any]) -> ContactPerson:
    """Build the contact person model from one contact person payload."""
    return ContactPerson(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        contact=_link_or_model_field(data, "contact", parse_contact)
        or RentmanLink(_str_field(data, "contact")),
        firstname=_str_field(data, "firstname"),
        middle_name=_str_field(data, "middle_name"),
        lastname=_str_field(data, "lastname"),
        function=_str_field(data, "function"),
        phone=_str_field(data, "phone"),
        street=_str_field(data, "street"),
        number=_str_field(data, "number"),
        postalcode=_str_field(data, "postalcode"),
        city=_str_field(data, "city"),
        state=_str_field(data, "state"),
        country=_str_field(data, "country"),
        mobilephone=_str_field(data, "mobilephone"),
        email=_str_field(data, "email"),
        tags=_codes_field(data, "tags"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_task_status(data: Mapping[str, Any]) -> TaskStatus:
    """Build the task status model from one status payload."""
    return TaskStatus(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        color=_str_field(data, "color"),
        type=_str_field(data, "type"),
        order=_coerced_str_field(data, "order"),
        raw=dict(data),
    )


def parse_task(data: Mapping[str, Any]) -> Task:
    """Build the task model from one task payload."""
    return Task(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        recurhoe=_str_field(data, "recurhoe"),
        recureind=_str_or_none_field(data, "recureind"),
        recurperiode=_int_field(data, "recurperiode"),
        is_template=_bool_field(data, "is_template"),
        name=_str_field(data, "name"),
        details=_str_field(data, "details"),
        color=_str_field(data, "color"),
        priority=_str_field(data, "priority"),
        order=_coerced_str_field(data, "order"),
        deadline=_datetime_field(data, "deadline"),
        deadline_type=_str_field(data, "deadline_type"),
        deadline_relative_offset_base=_str_field(data, "deadline_relative_offset_base"),
        deadline_relative_offset_amount=_int_field(data, "deadline_relative_offset_amount"),
        deadline_relative_offset_unit=_str_field(data, "deadline_relative_offset_unit"),
        deadline_relative_offset_direction=_str_field(data, "deadline_relative_offset_direction"),
        completed_at=_datetime_field(data, "completed_at"),
        status=_link_or_model_field(data, "status", parse_task_status)
        or RentmanLink(_str_field(data, "status")),
        item=_int_field(data, "item"),
        itemtype=_str_or_none_field(data, "itemtype"),
        synchronization_id=_str_field(data, "synchronization_id"),
        synchronization_uri=_str_field(data, "synchronization_uri"),
        public=_coerced_str_field(data, "public"),
        assignment_type=_str_field(data, "assignment_type"),
        completed_by=_link_field(data, "completed_by"),
        expiry_notification_date=_datetime_field(data, "expiry_notification_date"),
        time_budget=_float_field(data, "time_budget"),
        tags=_codes_field(data, "tags"),
        parent_api_path=_str_field(data, "parent_api_path"),
        custom=_custom_field(data),
        raw=dict(data),
    )


def parse_subtask(data: Mapping[str, Any]) -> Subtask:
    """Build the subtask model from one checklist line payload."""
    return Subtask(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        task=_link_or_model_field(data, "task", parse_task)
        or RentmanLink(_str_field(data, "task")),
        title=_str_field(data, "title"),
        completed=_bool_field(data, "completed"),
        raw=dict(data),
    )


def parse_task_assignment(data: Mapping[str, Any]) -> TaskAssignment:
    """Build the task assignment model from one assignment payload."""
    return TaskAssignment(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        task=_link_or_model_field(data, "task", parse_task)
        or RentmanLink(_str_field(data, "task")),
        crew=_link_or_model_field(data, "crew", parse_crew)
        or RentmanLink(_str_field(data, "crew")),
        raw=dict(data),
    )


def parse_file_folder(data: Mapping[str, Any]) -> FileFolder:
    """Build the file folder model from one folder payload."""
    return FileFolder(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        parent=_link_or_model_field(data, "parent", parse_file_folder),
        name=_str_field(data, "name"),
        classified=_bool_field(data, "classified"),
        item=_int_field(data, "item"),
        itemtype=_str_or_none_field(data, "itemtype"),
        is_template=_bool_field(data, "is_template"),
        parent_api_path=_str_field(data, "parent_api_path"),
        raw=dict(data),
    )


def parse_file(data: Mapping[str, Any]) -> File:
    """Build the file model from one stored file payload."""
    return File(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        readable_name=_str_field(data, "readable_name"),
        expiration=_datetime_field(data, "expiration"),
        size=_int_field(data, "size"),
        image=_bool_field(data, "image"),
        item=_int_field(data, "item"),
        itemtype=_str_or_none_field(data, "itemtype"),
        description=_str_field(data, "description"),
        in_documents=_bool_field(data, "in_documents"),
        in_webshop=_bool_field(data, "in_webshop"),
        classified=_bool_field(data, "classified"),
        public=_bool_field(data, "public"),
        type=_str_field(data, "type"),
        preview_of=_link_field(data, "preview_of"),
        previewstatus=_str_field(data, "previewstatus"),
        file_item=_int_field(data, "file_item"),
        file_itemtype=_str_field(data, "file_itemtype"),
        folder=_link_or_model_field(data, "folder", parse_file_folder),
        path=_str_field(data, "path"),
        path_without_file_name=_str_field(data, "path_without_file_name"),
        path_with_file_folders=_str_field(data, "path_with_file_folders"),
        name_without_extension=_str_field(data, "name_without_extension"),
        friendly_name_without_extension=_str_field(data, "friendly_name_without_extension"),
        extension=_str_field(data, "extension"),
        url=_str_field(data, "url"),
        proxy_url=_str_field(data, "proxy_url"),
        parent_api_path=_str_field(data, "parent_api_path"),
        raw=dict(data),
    )


def parse_rate(data: Mapping[str, Any]) -> Rate:
    """Build the rate model from one rate definition payload."""
    return Rate(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        archived=_bool_field(data, "archived"),
        type=_str_field(data, "type"),
        subtype=_str_field(data, "subtype"),
        raw=dict(data),
    )


def parse_rate_factor(data: Mapping[str, Any]) -> RateFactor:
    """Build the rate factor model from one rate bracket payload."""
    return RateFactor(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        rate_id=_link_or_model_field(data, "rate_id", parse_rate)
        or RentmanLink(_str_field(data, "rate_id")),
        from_=_float_field(data, "from"),
        to=_float_field(data, "to"),
        variable=_float_field(data, "variable"),
        fixed=_float_field(data, "fixed"),
        raw=dict(data),
    )


def parse_factor_group(data: Mapping[str, Any]) -> FactorGroup:
    """Build the factor group model from one group payload."""
    return FactorGroup(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        name=_str_field(data, "name"),
        raw=dict(data),
    )


def parse_factor(data: Mapping[str, Any]) -> Factor:
    """Build the factor model from one day bracket payload."""
    return Factor(
        id=_required_id(data),
        created=_datetime_field(data, "created"),
        modified=_datetime_field(data, "modified"),
        update_hash=_str_field(data, "updateHash"),
        creator=_link_field(data, "creator"),
        displayname=_str_field(data, "displayname"),
        from_days=_int_field(data, "from_days"),
        to_days=_int_field(data, "to_days"),
        factor=_coerced_str_field(data, "factor"),
        factor_group=_link_or_model_field(data, "factor_group", parse_factor_group)
        or RentmanLink(_str_field(data, "factor_group")),
        raw=dict(data),
    )
