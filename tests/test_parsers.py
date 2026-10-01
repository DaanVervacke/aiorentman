"""Parser tests run against the committed fixtures."""

from datetime import UTC, datetime
from typing import Any

from aiorentman.models import (
    Accessory,
    Alternative,
    Equipment,
    ExtraInputField,
    Folder,
    Project,
    ProjectCost,
    ProjectCrew,
    ProjectEquipmentGroup,
    ProjectFunction,
    ProjectFunctionGroup,
    ProjectRequest,
    ProjectRequestEquipment,
    ProjectStatus,
    ProjectVehicle,
    RentmanLink,
    RentmanPage,
    SerialNumber,
    StockLocation,
    Subproject,
    Supplier,
    Vehicle,
)
from aiorentman.parsers import (
    parse_accessory,
    parse_actual_content,
    parse_alternative,
    parse_envelope_item,
    parse_equipment,
    parse_extra_input_field,
    parse_page,
    parse_project_cost,
    parse_project_crew,
    parse_project_equipment,
    parse_project_equipment_group,
    parse_project_function,
    parse_project_function_group,
    parse_project_request,
    parse_project_request_equipment,
    parse_project_status,
    parse_project_type,
    parse_project_vehicle,
    parse_serial_number,
    parse_supplier,
    parse_vehicle,
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
    content = parse_actual_content({"quantity": True})
    assert content.quantity == ""
    line = parse_project_equipment({"quantity": 2, "order": 15, "factor": 1.5})
    assert line.quantity == "2"
    assert line.order == "15"
    assert line.factor == "1.5"
    serial = parse_serial_number({"updateHash": "d41d8cd98f00b204"})
    assert serial.update_hash == "d41d8cd98f00b204"


def test_parse_page_counts_items_when_item_count_is_missing() -> None:
    payload = cast_response({"data": [{"id": 1}]})
    page = parse_page(payload, parse_equipment)
    assert page.item_count == 1


def test_parse_accessory_coerces_order_and_quantity() -> None:
    accessory = parse_accessory({"id": 2, "order": 2, "quantity": "3", "add_as_new_line": True})
    assert isinstance(accessory, Accessory)
    assert accessory.order == "2"
    assert accessory.quantity == 3
    assert accessory.add_as_new_line is True


def test_parse_accessory_resolves_expanded_links() -> None:
    accessory = parse_accessory(
        {
            "parent_equipment": {"id": 338, "code": "AUD-001"},
            "equipment": {"id": 340, "code": "CON-001"},
        }
    )
    assert isinstance(accessory.parent_equipment, Equipment)
    assert accessory.parent_equipment.code == "AUD-001"
    assert isinstance(accessory.equipment, Equipment)
    assert accessory.equipment.id == 340


def test_parse_alternative_resolves_expanded_links() -> None:
    alternative = parse_alternative(
        {
            "equipment": {"id": 346, "code": "AUD-002"},
            "alternative": {"id": 428, "code": "AUD-003"},
        }
    )
    assert isinstance(alternative, Alternative)
    assert isinstance(alternative.equipment, Equipment)
    assert alternative.equipment.code == "AUD-002"
    assert isinstance(alternative.alternative, Equipment)
    assert alternative.alternative.id == 428


def test_parse_required_equipment_links_fall_back_to_empty_links() -> None:
    accessory = parse_accessory({})
    alternative = parse_alternative({})
    supplier = parse_supplier({})
    assert accessory.parent_equipment == RentmanLink("")
    assert alternative.equipment == RentmanLink("")
    assert alternative.alternative == RentmanLink("")
    assert supplier.equipment == RentmanLink("")


def test_parse_supplier_keeps_contact_links() -> None:
    supplier = parse_supplier(
        {"contact": "/contacts/3610", "contactperson": "/contactpersons/5", "price": 10}
    )
    assert isinstance(supplier, Supplier)
    assert supplier.contact == RentmanLink("/contacts/3610")
    assert supplier.contactperson == RentmanLink("/contactpersons/5")
    assert supplier.price == 10.0


def test_parse_vehicle_resolves_expanded_links_and_codes() -> None:
    vehicle = parse_vehicle(
        {
            "id": 7,
            "folder": {"id": 32, "name": "Transport"},
            "cost_rate": "/rates/556",
            "asset_location": {"id": 2, "name": "Main warehouse"},
            "inspection_date": "2026-12-15T00:00:00+01:00",
            "tags": "trial, nightly",
        }
    )
    assert isinstance(vehicle, Vehicle)
    assert isinstance(vehicle.folder, Folder)
    assert vehicle.folder.name == "Transport"
    assert vehicle.cost_rate == RentmanLink("/rates/556")
    assert isinstance(vehicle.asset_location, StockLocation)
    assert vehicle.asset_location.id == 2
    assert vehicle.inspection_date is not None
    assert vehicle.tags == ("trial", "nightly")


def test_parse_vehicle_degrades_on_sparse_payloads() -> None:
    vehicle = parse_vehicle({"id": 7})
    assert vehicle.folder is None
    assert vehicle.cost_rate is None
    assert vehicle.asset_location is None
    assert vehicle.seats is None
    assert vehicle.licenseplate == ""
    assert vehicle.custom == {}
    assert vehicle.tags == ()


def test_parse_extra_input_field_keeps_its_parent_link() -> None:
    field = parse_extra_input_field({"id": 2, "parent": "/extrainputfields/1", "order": 3})
    assert isinstance(field, ExtraInputField)
    assert field.parent == RentmanLink("/extrainputfields/1")
    assert field.order == "3"
    assert field.linkedItemType == ""


def test_parse_extra_input_field_resolves_an_expanded_parent() -> None:
    field = parse_extra_input_field({"id": 2, "parent": {"id": 1, "type": "text"}})
    assert isinstance(field.parent, ExtraInputField)
    assert field.parent.id == 1


def test_parse_project_function_resolves_expanded_links() -> None:
    function = parse_project_function(
        {
            "project": {"id": 80, "name": "Festival"},
            "subproject": {"id": 81, "name": "Main stage"},
            "group": {"id": 10, "name": "Setup"},
            "cost_rate": "/rates/31",
            "break": 30,
            "order": 9,
        }
    )
    assert isinstance(function, ProjectFunction)
    assert isinstance(function.project, Project)
    assert function.project.id == 80
    assert isinstance(function.subproject, Subproject)
    assert function.subproject.id == 81
    assert isinstance(function.group, ProjectFunctionGroup)
    assert function.group.id == 10
    assert function.cost_rate == RentmanLink("/rates/31")
    assert function.break_ == 30.0
    assert function.order == "9"
    assert function.tags == ()
    assert function.custom == {}


def test_parse_project_function_group_falls_back_to_empty_links() -> None:
    group = parse_project_function_group({})
    assert group.project == RentmanLink("")
    assert group.subproject == RentmanLink("")
    assert group.remark == ""
    assert group.duration is None


def test_parse_project_crew_resolves_expanded_links() -> None:
    member = parse_project_crew(
        {
            "function": {"id": 8, "name": "Stagehand"},
            "crewmember": "/crew/228",
            "cost_rate": "/rates/546",
            "planperiod_start": "2026-09-30T14:00:00+02:00",
        }
    )
    assert isinstance(member, ProjectCrew)
    assert isinstance(member.function, ProjectFunction)
    assert member.function.id == 8
    assert member.crewmember == RentmanLink("/crew/228")
    assert member.cost_rate == RentmanLink("/rates/546")
    assert member.planperiod_start is not None


def test_parse_project_crew_falls_back_to_empty_links() -> None:
    member = parse_project_crew({})
    assert member.function == RentmanLink("")
    assert member.crewmember == RentmanLink("")
    assert member.hours_planned is None


def test_parse_project_vehicle_resolves_expanded_links() -> None:
    planned = parse_project_vehicle(
        {
            "function": {"id": 43, "name": "Transport"},
            "vehicle": {"id": 9, "name": "Truck"},
        }
    )
    assert isinstance(planned, ProjectVehicle)
    assert isinstance(planned.function, ProjectFunction)
    assert planned.function.id == 43
    assert isinstance(planned.vehicle, Vehicle)
    assert planned.vehicle.id == 9


def test_parse_project_vehicle_falls_back_to_empty_links() -> None:
    planned = parse_project_vehicle({})
    assert planned.function == RentmanLink("")
    assert planned.vehicle == RentmanLink("")
    assert planned.costs is None


def test_parse_project_equipment_group_falls_back_to_empty_links() -> None:
    group = parse_project_equipment_group({})
    assert isinstance(group, ProjectEquipmentGroup)
    assert group.project == RentmanLink("")
    assert group.subproject == RentmanLink("")
    assert group.order == ""
    assert group.total_new_price is None


def test_parse_project_cost_falls_back_to_empty_links() -> None:
    cost = parse_project_cost({})
    assert isinstance(cost, ProjectCost)
    assert cost.project == RentmanLink("")
    assert cost.subproject == RentmanLink("")
    assert cost.order == ""
    assert cost.quantity is None


def test_parse_project_request_keeps_keyword_checkins() -> None:
    request = parse_project_request(
        {
            "in": "2026-10-06T08:00:00+02:00",
            "out": "2026-10-06T18:00:00+02:00",
            "linked_project": {"id": 480, "name": "Festival"},
        }
    )
    assert isinstance(request, ProjectRequest)
    assert request.in_ is not None
    assert request.out_ is not None
    assert isinstance(request.linked_project, Project)
    assert request.linked_project.id == 480


def test_parse_project_request_degrades_on_sparse_payloads() -> None:
    request = parse_project_request({})
    assert request.in_ is None
    assert request.out_ is None
    assert request.linked_project is None
    assert request.contact_name == ""
    assert request.external_reference is None


def test_parse_project_request_equipment_resolves_links() -> None:
    line = parse_project_request_equipment(
        {
            "linked_equipment": {"id": 12, "code": "AUD-001"},
            "parent": "/projectrequestequipment/2",
            "project_request": "/projectrequests/1",
            "factor": 4.2,
            "order": 1,
        }
    )
    assert isinstance(line, ProjectRequestEquipment)
    assert isinstance(line.linked_equipment, Equipment)
    assert line.linked_equipment.id == 12
    assert line.parent == RentmanLink("/projectrequestequipment/2")
    assert line.project_request == RentmanLink("/projectrequests/1")
    assert line.factor == "4.2"
    assert line.order == "1"


def test_parse_project_request_equipment_falls_back_to_an_empty_link() -> None:
    line = parse_project_request_equipment({})
    assert line.project_request == RentmanLink("")
    assert line.parent is None


def test_parse_project_status_and_type_keep_their_scalars() -> None:
    status = parse_project_status({"id": 1, "name": "Option"})
    assert isinstance(status, ProjectStatus)
    assert status.name == "Option"
    project_type = parse_project_type({"id": 104, "color": "FF6729", "type": "regular"})
    assert project_type.color == "FF6729"
    assert project_type.type == "regular"
