"""Convert raw Rentman payloads into result models."""

from collections.abc import Callable, Mapping
from datetime import datetime
from re import compile as _compile
from typing import Any

from .models import (
    Accessory,
    ActualContent,
    Alternative,
    Contract,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
    ExtraInputField,
    Folder,
    Invoice,
    InvoiceLine,
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
    Quote,
    RentmanLink,
    RentmanPage,
    Repair,
    SerialNumber,
    Status,
    StockLocation,
    StockMovement,
    Subproject,
    Supplier,
    TaxClass,
    Vehicle,
    WarehouseStatus,
)

_CODE_SEPARATOR = _compile(r"[,\n]+")


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
    if isinstance(value, str) and value.isdigit():
        return int(value)
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
        return parse_model(value)
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
        items = tuple(parse_item(item) for item in raw_items if isinstance(item, Mapping))
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
        return parse_item(payload)
    return None


def parse_equipment(data: Mapping[str, Any]) -> Equipment:
    """Build the equipment model from one equipment payload."""
    return Equipment(
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
        id=_int_field(data, "id") or 0,
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
