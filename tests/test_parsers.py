"""Parser tests run against the committed fixtures."""

from datetime import UTC, datetime
from typing import Any

from aiorentman.models import (
    Equipment,
    RentmanLink,
    RentmanPage,
    SerialNumber,
    StockLocation,
)
from aiorentman.parsers import (
    parse_envelope_item,
    parse_equipment,
    parse_page,
    parse_serial_number,
)

from .conftest import cast_response


def test_parse_equipment_page(load_fixture: Any) -> None:
    page = parse_page(load_fixture("equipment_page.json"), parse_equipment)
    assert isinstance(page, RentmanPage)
    assert page.item_count == 2
    assert page.limit == 300
    assert page.offset == 0
    assert page.next_page_url is None
    mixer = page.items[0]
    assert mixer.id == 12
    assert mixer.name == "Yamaha QL5 Mixer"
    assert mixer.code == "AUD-001"
    assert mixer.price == 150.0
    assert mixer.is_combination is False
    assert mixer.qrcodes == ("AUD-001",)
    assert mixer.qrcodes_of_serial_numbers == (
        "E28068900000000000000001",
        "E28068900000000000000002",
    )
    assert mixer.tags == ("audio", "mixer")
    assert isinstance(mixer.folder, RentmanLink)
    assert mixer.folder.path == "/folders/3"
    assert mixer.folder.id == 3
    assert mixer.created == datetime(2025, 3, 4, 10, 15, tzinfo=UTC)
    rack = page.items[1]
    assert rack.is_combination is True
    assert rack.custom == {}


def test_parse_equipment_item(load_fixture: Any) -> None:
    equipment = parse_envelope_item(load_fixture("equipment_item.json"), parse_equipment)
    assert isinstance(equipment, Equipment)
    assert equipment.id == 12
    assert equipment.custom == {"custom_1": "insured"}
    assert equipment.raw is not None
    assert equipment.raw["code"] == "AUD-001"


def test_parse_serial_number_page(load_fixture: Any) -> None:
    page = parse_page(load_fixture("serialnumber_page.json"), parse_serial_number)
    assert page.next_page_url is not None
    assert "cursor=" in page.next_page_url
    first = page.items[0]
    assert first.id == 41
    assert first.serial == "QL5-000041"
    equipment = first.equipment
    assert isinstance(equipment, RentmanLink)
    assert equipment.path == "/equipment/12"
    assert first.qrcodes == ("E28068900000000000000001",)
    second = page.items[1]
    assert second.qrcodes == ("E28068900000000000000002", "E28068900000000000000099")
    assert second.active is True
    assert second.last_subproject is None
    assert isinstance(first.last_subproject, RentmanLink)
    assert first.last_subproject.path == "/subprojects/501"


def test_parse_serial_number_with_expanded_links(load_fixture: Any) -> None:
    page = parse_page(load_fixture("serialnumber_page_expanded.json"), parse_serial_number)
    serial = page.items[0]
    assert isinstance(serial.equipment, Equipment)
    assert serial.equipment.code == "AUD-001"
    assert isinstance(serial.asset_location, StockLocation)
    assert serial.asset_location.name == "Main warehouse"


def test_parse_serial_number_item(load_fixture: Any) -> None:
    serial = parse_envelope_item(load_fixture("serialnumber_item.json"), parse_serial_number)
    assert isinstance(serial, SerialNumber)
    assert serial.ref == "SR-041"


def test_parse_page_degrades_on_unusable_payloads() -> None:
    page = parse_page(None, parse_equipment)
    assert page.items == ()
    assert page.item_count == 0
    page = parse_page({"itemCount": 5}, parse_equipment)
    assert page.items == ()
    assert page.item_count == 5


def test_parse_page_skips_non_mapping_entries() -> None:
    payload = {"data": [{"id": 1}, "junk", 3], "itemCount": 3, "limit": 300, "offset": 0}
    page = parse_page(payload, parse_equipment)
    assert len(page.items) == 1
    assert page.items[0].id == 1
    assert page.item_count == 3


def test_parse_envelope_item_accepts_a_bare_object() -> None:
    equipment = parse_envelope_item({"id": 12, "code": "AUD-001"}, parse_equipment)
    assert isinstance(equipment, Equipment)
    assert equipment.code == "AUD-001"


def test_parse_envelope_item_returns_none_for_unusable_payloads() -> None:
    assert parse_envelope_item(None, parse_equipment) is None
    assert parse_envelope_item("junk", parse_equipment) is None
    assert parse_envelope_item({"data": None}, parse_equipment) is None


def test_parse_lenient_fields_from_sparse_payloads() -> None:
    equipment = parse_equipment({"id": 7})
    assert equipment.id == 7
    assert equipment.name == ""
    assert equipment.price is None
    assert equipment.in_shop is False
    assert equipment.qrcodes == ()
    assert equipment.custom == {}
    assert equipment.created is None
    assert equipment.creator is None
    assert equipment.folder is None


def test_parse_crew_link_stays_a_link_after_expansion_attempts() -> None:
    equipment = parse_equipment({"id": 7, "creator": "/crew/237"})
    assert equipment.creator == RentmanLink("/crew/237")


def test_parse_required_link_falls_back_to_an_empty_link() -> None:
    serial = parse_serial_number({})
    assert serial.equipment == RentmanLink("")
    assert serial.equipment.id is None


def test_parse_custom_field_rejects_non_mappings() -> None:
    equipment = parse_equipment({"id": 7, "custom": "junk"})
    assert equipment.custom == {}


def test_parse_codes_field_handles_newline_separation() -> None:
    serial = parse_serial_number({"qrcodes": "E2801\nE2802\n"})
    assert serial.qrcodes == ("E2801", "E2802")


def test_parse_coerces_lenient_scalars() -> None:
    equipment = parse_equipment(
        {
            "id": "7",
            "packed_per": "3",
            "price": "not-a-number",
            "critical_stock_level": True,
            "list_price": False,
            "created": "not-a-date",
            "name": 12,
            "is_physical": "1",
        }
    )
    assert equipment.id == 7
    assert equipment.packed_per == 3
    assert equipment.price is None
    assert equipment.created is None
    assert equipment.name == ""
    assert equipment.is_physical == "1"


def test_parse_page_counts_items_when_item_count_is_missing() -> None:
    payload = cast_response({"data": [{"id": 1}]})
    page = parse_page(payload, parse_equipment)
    assert page.item_count == 1
