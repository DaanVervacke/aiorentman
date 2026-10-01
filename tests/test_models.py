"""Model tests: link parsing, page shape, and immutability."""

import dataclasses

import pytest

from aiorentman.models import (
    Equipment,
    RentmanLink,
    RentmanPage,
    SerialNumber,
)


def test_link_exposes_its_numeric_id() -> None:
    assert RentmanLink("/equipment/12").id == 12
    assert RentmanLink("/serialnumbers/41").id == 41


def test_link_id_is_none_for_unusual_paths() -> None:
    assert RentmanLink("/equipment").id is None
    assert RentmanLink("/equipment/not-a-number").id is None
    assert RentmanLink("").id is None


def test_page_carries_the_envelope_metadata() -> None:
    page = RentmanPage(
        items=(RentmanLink("/equipment/1"),),
        item_count=1,
        limit=300,
        offset=0,
        next_page_url=None,
    )
    assert page.item_count == 1
    assert page.next_page_url is None


def test_models_are_frozen() -> None:
    equipment = parse_minimal_equipment()
    with pytest.raises(dataclasses.FrozenInstanceError):
        equipment.name = "changed"  # type: ignore[misc]


def test_models_are_slotted() -> None:
    equipment = parse_minimal_equipment()
    with pytest.raises(AttributeError):
        equipment.unexpected_attribute = "nope"  # type: ignore[attr-defined]


def test_serial_number_documented_for_rfid() -> None:
    """One RFID tag corresponds to exactly one serial number, per Rentman docs."""
    serial = SerialNumber(
        id=41,
        created=None,
        modified=None,
        creator=None,
        displayname="Yamaha QL5 Mixer 41",
        equipment=RentmanLink("/equipment/12"),
        serial="QL5-000041",
        purchasedate=None,
        depreciation_monthly=None,
        book_value=None,
        residual_value=None,
        purchase_costs=None,
        active=True,
        remark="",
        ref="",
        asset_location=None,
        image=None,
        current_book_value=None,
        next_inspection=None,
        qrcodes=("E28068900000000000000001",),
        tags=(),
        last_subproject=None,
        sealed=False,
        custom={},
    )
    assert serial.qrcodes == ("E28068900000000000000001",)


def parse_minimal_equipment() -> Equipment:
    return Equipment(
        id=12,
        created=None,
        modified=None,
        creator=None,
        displayname="Yamaha QL5 Mixer",
        folder=None,
        code="AUD-001",
        factor_group=None,
        name="Yamaha QL5 Mixer",
        internal_remark="",
        external_remark="",
        unit="piece",
        in_shop=False,
        surface_article=False,
        shop_description_short="",
        shop_description_long="",
        shop_seo_title="",
        shop_seo_keyword="",
        shop_seo_description="",
        shop_featured=False,
        price=None,
        subrental_costs=None,
        critical_stock_level=None,
        type="",
        rental_sales="",
        temporary=False,
        in_planner=False,
        in_archive=False,
        stock_management="",
        taxclass=None,
        list_price=None,
        volume=None,
        packed_per=None,
        height=None,
        width=None,
        length=None,
        weight=None,
        empty_weight=None,
        power=None,
        current=None,
        country_of_origin="",
        image=None,
        ledger=None,
        ledger_debit=None,
        defaultgroup="",
        is_combination=False,
        is_physical="",
        can_edit_content_during_planning=False,
        strict_container_content="",
        qrcodes=(),
        qrcodes_of_serial_numbers=(),
        tags=(),
        current_quantity_excl_cases=None,
        current_quantity=None,
        quantity_in_cases=None,
        location_in_warehouse="",
        custom={},
    )
