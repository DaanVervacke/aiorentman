"""Convert raw Rentman payloads into result models."""

from collections.abc import Callable, Mapping
from datetime import datetime
from re import compile as _compile
from typing import Any

from .models import (
    ActualContent,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
    Folder,
    Project,
    ProjectEquipment,
    RentmanLink,
    RentmanPage,
    Repair,
    SerialNumber,
    Status,
    StockLocation,
    StockMovement,
    Subproject,
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
