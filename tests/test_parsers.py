"""Parser tests run against the committed fixtures."""

import logging
from datetime import UTC, datetime
from typing import Any

import pytest

from aiorentman.models import (
    Accessory,
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
    ExtraInputField,
    Factor,
    FactorGroup,
    File,
    FileFolder,
    Folder,
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
    ProjectEquipmentGroup,
    ProjectFunction,
    ProjectFunctionGroup,
    ProjectRequest,
    ProjectRequestEquipment,
    ProjectStatus,
    ProjectVehicle,
    PurchaseOrder,
    PurchaseOrderCost,
    PurchaseOrderGlobalCost,
    Quote,
    Rate,
    RateFactor,
    RentmanLink,
    RentmanPage,
    SerialNumber,
    Status,
    StockLocation,
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
)
from aiorentman.parsers import (
    parse_accessory,
    parse_actual_content,
    parse_alternative,
    parse_appointment,
    parse_appointment_crew,
    parse_contact,
    parse_contact_person,
    parse_contract,
    parse_crew,
    parse_crew_availability,
    parse_crew_rate,
    parse_envelope_item,
    parse_equipment,
    parse_extra_input_field,
    parse_factor,
    parse_factor_group,
    parse_file,
    parse_file_folder,
    parse_invitation,
    parse_invoice,
    parse_invoice_line,
    parse_leave_mutation,
    parse_leave_request,
    parse_leave_type,
    parse_ledger_code,
    parse_page,
    parse_payment,
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
    parse_purchase_order,
    parse_purchase_order_cost,
    parse_purchase_order_global_cost,
    parse_quote,
    parse_rate,
    parse_rate_factor,
    parse_serial_number,
    parse_subrental,
    parse_subrental_equipment,
    parse_subrental_equipment_group,
    parse_subtask,
    parse_supplier,
    parse_task,
    parse_task_assignment,
    parse_task_status,
    parse_tax_class,
    parse_time_registration,
    parse_time_registration_activity,
    parse_vehicle,
)

from .conftest import cast_response


def test_parse_rate_and_factor_keep_their_scalars() -> None:
    rate = parse_rate(
        {"id": 1, "name": "15 per hour", "type": "cost", "subtype": "flat", "archived": False}
    )
    assert isinstance(rate, Rate)
    assert rate.type == "cost"
    assert rate.subtype == "flat"
    assert rate.archived is False
    factor_group = parse_factor_group({"id": 1, "name": "Days"})
    assert isinstance(factor_group, FactorGroup)
    assert factor_group.name == "Days"


def test_parse_rate_factor_resolves_expanded_rate() -> None:
    rate_factor = parse_rate_factor(
        {"id": 1, "rate_id": {"id": 1, "name": "15 per hour"}, "from": 0, "to": 100, "variable": 15}
    )
    assert isinstance(rate_factor, RateFactor)
    assert isinstance(rate_factor.rate_id, Rate)
    assert rate_factor.rate_id.id == 1
    assert rate_factor.from_ == 0
    assert rate_factor.to == 100
    assert rate_factor.variable == 15
    assert rate_factor.fixed is None


def test_parse_rate_factor_falls_back_to_an_empty_link() -> None:
    rate_factor = parse_rate_factor(
        {
            "id": 1,
        }
    )
    assert rate_factor.rate_id == RentmanLink("")
    assert rate_factor.from_ is None


def test_parse_factor_resolves_expanded_group() -> None:
    factor = parse_factor(
        {
            "id": 1,
            "factor": 1,
            "factor_group": {"id": 1, "name": "Days"},
            "from_days": 1,
            "to_days": 1,
        }
    )
    assert isinstance(factor, Factor)
    assert factor.factor == "1"
    assert isinstance(factor.factor_group, FactorGroup)
    assert factor.factor_group.id == 1
    assert factor.from_days == 1


def test_parse_factor_falls_back_to_an_empty_link() -> None:
    factor = parse_factor(
        {
            "id": 1,
        }
    )
    assert factor.factor_group == RentmanLink("")
    assert factor.factor == ""


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
    serial = parse_serial_number(
        {
            "id": 1,
        }
    )
    assert serial.equipment == RentmanLink("")
    assert serial.equipment.id is None


def test_parse_custom_field_rejects_non_mappings() -> None:
    equipment = parse_equipment({"id": 7, "custom": "junk"})
    assert equipment.custom == {}


def test_parse_codes_field_handles_newline_separation() -> None:
    serial = parse_serial_number({"id": 1, "qrcodes": "E2801\nE2802\n"})
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
    content = parse_actual_content({"id": 1, "quantity": True})
    assert content.quantity == ""
    line = parse_project_equipment({"id": 1, "quantity": 2, "order": 15, "factor": 1.5})
    assert line.quantity == "2"
    assert line.order == "15"
    assert line.factor == "1.5"
    serial = parse_serial_number({"id": 1, "updateHash": "d41d8cd98f00b204"})
    assert serial.update_hash == "d41d8cd98f00b204"


def test_parse_int_field_degrades_on_unconvertible_strings() -> None:
    equipment = parse_equipment({"id": 1, "critical_stock_level": "²"})
    assert equipment.critical_stock_level is None
    equipment = parse_equipment({"id": 1, "critical_stock_level": "7" * 5000})
    assert equipment.critical_stock_level is None


@pytest.mark.parametrize(
    "payload", [{}, {"id": None}, {"id": True}, {"id": "²"}, {"id": "7" * 5000}]
)
def test_parsers_reject_objects_without_a_usable_id(payload: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="no usable id"):
        parse_equipment(payload)


def test_parse_page_drops_items_without_a_usable_id(caplog: pytest.LogCaptureFixture) -> None:
    payload = {"data": [{"id": 1}, {}, {"id": True}, {"id": "²"}], "itemCount": 4}
    with caplog.at_level(logging.DEBUG, logger="aiorentman.parsers"):
        page = parse_page(payload, parse_equipment)
    assert [item.id for item in page.items] == [1]
    assert page.item_count == 4
    assert caplog.messages.count("Dropped one parse_equipment payload without a usable id") == 3


def test_parse_envelope_item_drops_an_object_without_an_id() -> None:
    assert parse_envelope_item({"data": {"code": "AUD-001"}}, parse_equipment) is None


def test_parse_expanded_link_without_an_id_is_none() -> None:
    vehicle = parse_vehicle({"id": 1, "folder": {"name": "Transport"}})
    assert vehicle.folder is None


def test_parse_int_field_converts_negative_strings() -> None:
    equipment = parse_equipment({"id": "-5"})
    assert equipment.id == -5


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
            "id": 1,
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
            "id": 1,
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
    accessory = parse_accessory(
        {
            "id": 1,
        }
    )
    alternative = parse_alternative(
        {
            "id": 1,
        }
    )
    supplier = parse_supplier(
        {
            "id": 1,
        }
    )
    assert accessory.parent_equipment == RentmanLink("")
    assert alternative.equipment == RentmanLink("")
    assert alternative.alternative == RentmanLink("")
    assert supplier.equipment == RentmanLink("")


def test_parse_supplier_keeps_contact_links() -> None:
    supplier = parse_supplier(
        {"id": 1, "contact": "/contacts/3610", "contactperson": "/contactpersons/5", "price": 10}
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
            "id": 1,
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
    group = parse_project_function_group(
        {
            "id": 1,
        }
    )
    assert group.project == RentmanLink("")
    assert group.subproject == RentmanLink("")
    assert group.remark == ""
    assert group.duration is None


def test_parse_project_crew_resolves_expanded_links() -> None:
    member = parse_project_crew(
        {
            "id": 1,
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
    member = parse_project_crew(
        {
            "id": 1,
        }
    )
    assert member.function == RentmanLink("")
    assert member.crewmember == RentmanLink("")
    assert member.hours_planned is None


def test_parse_project_vehicle_resolves_expanded_links() -> None:
    planned = parse_project_vehicle(
        {
            "id": 1,
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
    planned = parse_project_vehicle(
        {
            "id": 1,
        }
    )
    assert planned.function == RentmanLink("")
    assert planned.vehicle == RentmanLink("")
    assert planned.costs is None


def test_parse_project_equipment_group_falls_back_to_empty_links() -> None:
    group = parse_project_equipment_group(
        {
            "id": 1,
        }
    )
    assert isinstance(group, ProjectEquipmentGroup)
    assert group.project == RentmanLink("")
    assert group.subproject == RentmanLink("")
    assert group.order == ""
    assert group.total_new_price is None


def test_parse_project_cost_falls_back_to_empty_links() -> None:
    cost = parse_project_cost(
        {
            "id": 1,
        }
    )
    assert isinstance(cost, ProjectCost)
    assert cost.project == RentmanLink("")
    assert cost.subproject == RentmanLink("")
    assert cost.order == ""
    assert cost.quantity is None


def test_parse_project_request_keeps_keyword_checkins() -> None:
    request = parse_project_request(
        {
            "id": 1,
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
    request = parse_project_request(
        {
            "id": 1,
        }
    )
    assert request.in_ is None
    assert request.out_ is None
    assert request.linked_project is None
    assert request.contact_name == ""
    assert request.external_reference is None


def test_parse_project_request_equipment_resolves_links() -> None:
    line = parse_project_request_equipment(
        {
            "id": 1,
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
    line = parse_project_request_equipment(
        {
            "id": 1,
        }
    )
    assert line.project_request == RentmanLink("")
    assert line.parent is None


def test_parse_project_status_and_type_keep_their_scalars() -> None:
    status = parse_project_status({"id": 1, "name": "Option"})
    assert isinstance(status, ProjectStatus)
    assert status.name == "Option"
    project_type = parse_project_type({"id": 104, "color": "FF6729", "type": "regular"})
    assert project_type.color == "FF6729"
    assert project_type.type == "regular"


def test_parse_quote_resolves_expanded_links() -> None:
    quote = parse_quote(
        {
            "id": 1,
            "project": {"id": 128, "name": "Festival"},
            "customer": "/contacts/3623",
            "date": "2027-11-28T00:00:00+01:00",
            "tags": "trial, priority",
        }
    )
    assert isinstance(quote, Quote)
    assert isinstance(quote.project, Project)
    assert quote.project.id == 128
    assert quote.customer == RentmanLink("/contacts/3623")
    assert quote.date is not None
    assert quote.tags == ("trial", "priority")


def test_parse_quote_and_contract_fall_back_to_empty_links() -> None:
    quote = parse_quote(
        {
            "id": 1,
        }
    )
    contract = parse_contract(
        {
            "id": 1,
        }
    )
    assert isinstance(contract, Contract)
    assert quote.project == RentmanLink("")
    assert contract.project == RentmanLink("")
    assert quote.project_total_price is None
    assert contract.vat_amount is None
    assert quote.version is None


def test_parse_invoice_resolves_expanded_links() -> None:
    invoice = parse_invoice(
        {
            "id": 1,
            "project": {"id": 113, "name": "Dry hire"},
            "invoicetype": "F",
            "is_paid": True,
            "date_sent": "2026-09-20T00:00:00+02:00",
        }
    )
    assert isinstance(invoice, Invoice)
    assert isinstance(invoice.project, Project)
    assert invoice.project.id == 113
    assert invoice.invoicetype == "F"
    assert invoice.is_paid is True
    assert invoice.date_sent is not None


def test_parse_invoice_degrades_on_sparse_payloads() -> None:
    invoice = parse_invoice(
        {
            "id": 1,
        }
    )
    assert invoice.project is None
    assert invoice.integration_reference_id is None
    assert invoice.days_after_expiry is None
    assert invoice.tags == ()


def test_parse_invoice_line_resolves_expanded_ledger() -> None:
    line = parse_invoice_line(
        {
            "id": 1,
            "item": 1,
            "base": 1350,
            "ledger": {"id": 1, "code": "Rental"},
            "vatrate": 0.21,
            "ledgercode": "Rental",
        }
    )
    assert isinstance(line, InvoiceLine)
    assert isinstance(line.ledger, LedgerCode)
    assert line.ledger.id == 1
    assert line.ledgercode == "Rental"
    assert line.vatrate == 0.21
    assert line.parent_api_path == ""


def test_parse_invoice_line_falls_back_to_an_empty_link() -> None:
    line = parse_invoice_line(
        {
            "id": 1,
        }
    )
    assert line.ledger == RentmanLink("")
    assert line.item is None
    assert line.priceincl is None


def test_parse_payment_resolves_expanded_invoice() -> None:
    payment = parse_payment(
        {
            "id": 1,
            "invoice": {"id": 4, "number": "4"},
            "moment": "2026-09-25T10:00:00+02:00",
            "amount": 120.5,
            "payment_import_source": "publicapi",
        }
    )
    assert isinstance(payment, Payment)
    assert isinstance(payment.invoice, Invoice)
    assert payment.invoice.id == 4
    assert payment.moment is not None
    assert payment.amount == 120.5
    assert payment.payment_import_source == "publicapi"


def test_parse_payment_falls_back_to_an_empty_link() -> None:
    payment = parse_payment(
        {
            "id": 1,
        }
    )
    assert payment.invoice == RentmanLink("")
    assert payment.moment is None
    assert payment.description == ""


def test_parse_ledger_code_and_tax_class_keep_their_scalars() -> None:
    ledger = parse_ledger_code({"id": 1, "code": "Rental", "is_credit": True})
    assert isinstance(ledger, LedgerCode)
    assert ledger.code == "Rental"
    assert ledger.is_credit is True
    assert ledger.is_debit is False
    tax_class = parse_tax_class({"id": 2, "name": "Laag tarief", "type": "vat"})
    assert isinstance(tax_class, TaxClass)
    assert tax_class.type == "vat"


def test_parse_subrental_coerces_number_and_resolves_links() -> None:
    subrental = parse_subrental(
        {
            "id": 1,
            "number": 1,
            "status": {"id": 3, "name": "Optie"},
            "asset_location_to": {"id": 1, "name": "Main warehouse"},
            "supplier_project": "/projects/130",
            "tags": "trial",
        }
    )
    assert isinstance(subrental, Subrental)
    assert subrental.number == "1"
    assert isinstance(subrental.status, Status)
    assert subrental.status.id == 3
    assert isinstance(subrental.asset_location_to, StockLocation)
    assert subrental.asset_location_to.id == 1
    assert subrental.supplier_project == RentmanLink("/projects/130")


def test_parse_subrental_falls_back_to_empty_links() -> None:
    subrental = parse_subrental(
        {
            "id": 1,
        }
    )
    assert subrental.status == RentmanLink("")
    assert subrental.number == ""
    assert subrental.supplier_project is None
    assert subrental.tags == ()


def test_parse_subrental_group_and_equipment_keep_their_scalars() -> None:
    group = parse_subrental_equipment_group({"id": 1, "subrental": "/subrentals/17", "order": 0})
    assert isinstance(group, SubrentalEquipmentGroup)
    assert group.subrental == RentmanLink("/subrentals/17")
    assert group.order == "0"
    line = parse_subrental_equipment(
        {
            "id": 1,
            "subrental_group": {"id": 2, "name": "Inhuur"},
            "equipment": {"id": 358, "code": "AUD-001"},
            "factor": 1,
            "order": 0,
        }
    )
    assert isinstance(line, SubrentalEquipment)
    assert isinstance(line.subrental_group, SubrentalEquipmentGroup)
    assert line.subrental_group.id == 2
    assert isinstance(line.equipment, Equipment)
    assert line.equipment.id == 358
    assert line.factor == "1"
    assert line.order == "0"


def test_parse_subrental_equipment_resolves_self_reference() -> None:
    line = parse_subrental_equipment({"id": 1, "parent": {"id": 3, "name": "Truck"}})
    assert isinstance(line.parent, SubrentalEquipment)
    assert line.parent.id == 3


def test_parse_subrental_equipment_falls_back_to_an_empty_link() -> None:
    line = parse_subrental_equipment(
        {
            "id": 1,
        }
    )
    assert line.subrental_group == RentmanLink("")
    assert line.parent is None
    assert line.lineprice is None


def test_parse_purchase_order_keeps_its_scalars() -> None:
    order = parse_purchase_order(
        {
            "id": 1,
            "owner": "/crew/33",
            "delivery_warehouse": {"id": 1, "name": "Main warehouse"},
            "projects_json": '[{"id": 118}]',
            "export_message": None,
            "previous_status": "draft",
        }
    )
    assert isinstance(order, PurchaseOrder)
    assert order.owner == RentmanLink("/crew/33")
    assert isinstance(order.delivery_warehouse, StockLocation)
    assert order.delivery_warehouse.id == 1
    assert order.projects_json == '[{"id": 118}]'
    assert order.export_message is None
    assert order.previous_status == "draft"


def test_parse_purchase_order_degrades_on_sparse_payloads() -> None:
    order = parse_purchase_order(
        {
            "id": 1,
        }
    )
    assert order.owner == RentmanLink("")
    assert order.previous_status == ""
    assert order.delivery_warehouse is None
    assert order.tags == ()


def test_parse_purchase_order_cost_keeps_its_project_text() -> None:
    cost = parse_purchase_order_cost(
        {
            "id": 1,
            "purchase_order": {"id": 1, "number": "01"},
            "project": "116 Festival Demo Dance",
            "costitem": 52,
            "costitemtype": "Planningpersoneel",
        }
    )
    assert isinstance(cost, PurchaseOrderCost)
    assert isinstance(cost.purchase_order, PurchaseOrder)
    assert cost.purchase_order.id == 1
    assert cost.project == "116 Festival Demo Dance"
    assert cost.costitem == 52


def test_parse_purchase_order_cost_falls_back_to_an_empty_link() -> None:
    cost = parse_purchase_order_cost(
        {
            "id": 1,
        }
    )
    assert cost.purchase_order == RentmanLink("")
    assert cost.project == ""
    assert cost.quantity is None


def test_parse_purchase_order_global_cost_resolves_expanded_links() -> None:
    global_cost = parse_purchase_order_global_cost(
        {
            "id": 1,
            "purchase_order": {"id": 1, "number": "01"},
            "taxclass": {"id": 3, "name": "Hoog tarief"},
            "unit_purchase_cost": 10.5,
        }
    )
    assert isinstance(global_cost, PurchaseOrderGlobalCost)
    assert isinstance(global_cost.purchase_order, PurchaseOrder)
    assert global_cost.purchase_order.id == 1
    assert isinstance(global_cost.taxclass, TaxClass)
    assert global_cost.taxclass.id == 3
    assert global_cost.unit_purchase_cost == 10.5


def test_parse_purchase_order_global_cost_falls_back_to_an_empty_link() -> None:
    global_cost = parse_purchase_order_global_cost(
        {
            "id": 1,
        }
    )
    assert global_cost.purchase_order == RentmanLink("")
    assert global_cost.taxclass is None


def test_parse_crew_coerces_contract_and_resolves_links() -> None:
    member = parse_crew(
        {
            "id": 1,
            "contract": 40,
            "folder": {"id": 40, "name": "Crew"},
            "default_warehouse": {"id": 1, "name": "Main warehouse"},
            "tags": "trial",
        }
    )
    assert isinstance(member, Crew)
    assert member.contract == "40"
    assert isinstance(member.folder, Folder)
    assert member.folder.id == 40
    assert isinstance(member.default_warehouse, StockLocation)
    assert member.default_warehouse.id == 1
    assert member.email == ""
    assert member.custom == {}


def test_parse_crew_models_keep_required_crew_links() -> None:
    availability = parse_crew_availability(
        {"id": 1, "crewmember": {"id": 230, "firstname": "Stage"}, "status": "N"}
    )
    assert isinstance(availability, CrewAvailability)
    assert isinstance(availability.crewmember, Crew)
    assert availability.crewmember.id == 230
    assert availability.status == "N"
    rate = parse_crew_rate({"id": 1, "cost_rate": "/rates/541", "medewerker": "/crew/33"})
    assert isinstance(rate, CrewRate)
    assert rate.cost_rate == RentmanLink("/rates/541")
    assert rate.medewerker == RentmanLink("/crew/33")


def test_parse_crew_models_fall_back_to_empty_links() -> None:
    availability = parse_crew_availability(
        {
            "id": 1,
        }
    )
    rate = parse_crew_rate(
        {
            "id": 1,
        }
    )
    invitation = parse_invitation(
        {
            "id": 1,
        }
    )
    assert availability.crewmember == RentmanLink("")
    assert rate.medewerker == RentmanLink("")
    assert invitation.crewmember == RentmanLink("")
    assert invitation.function is None
    assert invitation.projectcrew is None


def test_parse_appointment_and_crew_resolves_expanded_links() -> None:
    attachment = parse_appointment_crew(
        {
            "id": 1,
            "appointment": {"id": 28, "name": "Dentist"},
            "crew": {"id": 223, "firstname": "Brian"},
        }
    )
    assert isinstance(attachment, AppointmentCrew)
    assert isinstance(attachment.appointment, Appointment)
    assert attachment.appointment.id == 28
    assert isinstance(attachment.crew, Crew)
    assert attachment.crew.id == 223


def test_parse_appointment_and_crew_fall_back_to_empty_links() -> None:
    attachment = parse_appointment_crew(
        {
            "id": 1,
        }
    )
    assert attachment.appointment == RentmanLink("")
    assert attachment.crew == RentmanLink("")
    appointment = parse_appointment({"id": 1, "start": "2026-10-05T10:00:00+02:00"})
    assert isinstance(appointment, Appointment)
    assert appointment.start is not None
    assert appointment.recurrence_weekdays is None


def test_parse_leave_models_keep_their_links() -> None:
    request = parse_leave_request(
        {"id": 1, "requested_for": {"id": 228, "firstname": "Crew"}, "reviewer": "/crew/33"}
    )
    assert isinstance(request, LeaveRequest)
    assert isinstance(request.requested_for, Crew)
    assert request.requested_for.id == 228
    assert request.reviewer == RentmanLink("/crew/33")
    mutation = parse_leave_mutation(
        {"id": 1, "leavetype": {"id": 2, "name": "Vakantie"}, "crewmember": "/crew/228"}
    )
    assert isinstance(mutation, LeaveMutation)
    assert isinstance(mutation.leavetype, LeaveType)
    assert mutation.leavetype.id == 2
    assert mutation.crewmember == RentmanLink("/crew/228")


def test_parse_leave_models_fall_back_to_empty_links() -> None:
    request = parse_leave_request(
        {
            "id": 1,
        }
    )
    mutation = parse_leave_mutation(
        {
            "id": 1,
        }
    )
    assert request.requested_for == RentmanLink("")
    assert mutation.leavetype == RentmanLink("")
    assert mutation.crewmember == RentmanLink("")
    leave_type = parse_leave_type({"id": 1, "type": "G", "is_labor": "worked"})
    assert isinstance(leave_type, LeaveType)
    assert leave_type.type == "G"
    assert leave_type.is_labor == "worked"


def test_parse_time_registration_resolves_expanded_links() -> None:
    registration = parse_time_registration(
        {
            "id": 1,
            "crewmember": {"id": 226, "firstname": "Stage"},
            "leavetype": {"id": 1, "name": "Gewerkt"},
            "leaverequest": "/leaverequest/1",
            "status": "approved",
        }
    )
    assert isinstance(registration, TimeRegistration)
    assert isinstance(registration.crewmember, Crew)
    assert registration.crewmember.id == 226
    assert isinstance(registration.leavetype, LeaveType)
    assert registration.leavetype.id == 1
    assert registration.leaverequest == RentmanLink("/leaverequest/1")


def test_parse_time_registration_activity_keeps_keyword_times() -> None:
    activity = parse_time_registration_activity(
        {
            "id": 1,
            "time_registration": {"id": 20, "status": "approved"},
            "project_function": "/projectfunctions/490",
            "from": "2026-09-19T14:00:00+02:00",
            "to": "2026-09-19T16:00:00+02:00",
        }
    )
    assert isinstance(activity, TimeRegistrationActivity)
    assert isinstance(activity.time_registration, TimeRegistration)
    assert activity.time_registration.id == 20
    assert activity.project_function == RentmanLink("/projectfunctions/490")
    assert activity.from_ is not None
    assert activity.to is not None


def test_parse_time_registration_activity_falls_back_to_an_empty_link() -> None:
    activity = parse_time_registration_activity(
        {
            "id": 1,
        }
    )
    assert activity.time_registration == RentmanLink("")
    assert activity.from_ is None
    assert activity.subproject_function is None


def test_parse_contact_resolves_expanded_links() -> None:
    contact = parse_contact(
        {
            "id": 1,
            "folder": {"id": 32, "name": "Customers"},
            "default_person": {"id": 8, "firstname": "Luke"},
            "VAT_code": "NL1234567890",
            "type": "company",
        }
    )
    assert isinstance(contact, Contact)
    assert isinstance(contact.folder, Folder)
    assert contact.folder.id == 32
    assert isinstance(contact.default_person, ContactPerson)
    assert contact.default_person.id == 8
    assert contact.VAT_code == "NL1234567890"
    assert contact.type == "company"


def test_parse_contact_person_resolves_expanded_contact() -> None:
    person = parse_contact_person(
        {"id": 1, "contact": {"id": 3609, "name": "Wow Music"}, "firstname": "Luke"}
    )
    assert isinstance(person, ContactPerson)
    assert isinstance(person.contact, Contact)
    assert person.contact.id == 3609
    assert person.function == ""


def test_parse_contact_models_fall_back_to_empty_links() -> None:
    contact = parse_contact(
        {
            "id": 1,
        }
    )
    person = parse_contact_person(
        {
            "id": 1,
        }
    )
    assert contact.default_person is None
    assert contact.VAT_code == ""
    assert person.contact == RentmanLink("")
    assert person.email == ""


def test_parse_task_coerces_scalars_and_resolves_links() -> None:
    task = parse_task(
        {
            "id": 1,
            "status": {"id": 1, "name": "To do"},
            "order": 576,
            "public": 1,
            "deadline": "2026-09-30T00:00:00+02:00",
            "tags": "preparation, trial",
            "itemtype": "Project",
        }
    )
    assert isinstance(task, Task)
    assert isinstance(task.status, TaskStatus)
    assert task.status.id == 1
    assert task.order == "576"
    assert task.public == "1"
    assert task.deadline is not None
    assert task.tags == ("preparation", "trial")
    assert task.itemtype == "Project"


def test_parse_task_falls_back_to_an_empty_link() -> None:
    task = parse_task(
        {
            "id": 1,
        }
    )
    assert task.status == RentmanLink("")
    assert task.recurhoe == ""
    assert task.recurperiode is None
    assert task.parent_api_path == ""
    assert task.custom == {}


def test_parse_subtask_and_assignment_resolve_expanded_links() -> None:
    subtask = parse_subtask({"id": 1, "task": {"id": 95, "name": "Check"}, "completed": True})
    assert isinstance(subtask, Subtask)
    assert isinstance(subtask.task, Task)
    assert subtask.task.id == 95
    assert subtask.completed is True
    assignment = parse_task_assignment(
        {"id": 1, "task": {"id": 95, "name": "Check"}, "crew": {"id": 33, "firstname": "Daan"}}
    )
    assert isinstance(assignment, TaskAssignment)
    assert isinstance(assignment.task, Task)
    assert isinstance(assignment.crew, Crew)
    assert assignment.crew.id == 33


def test_parse_subtask_and_assignment_fall_back_to_empty_links() -> None:
    subtask = parse_subtask(
        {
            "id": 1,
        }
    )
    assignment = parse_task_assignment(
        {
            "id": 1,
        }
    )
    assert subtask.task == RentmanLink("")
    assert assignment.task == RentmanLink("")
    assert assignment.crew == RentmanLink("")


def test_parse_task_status_keeps_its_scalars() -> None:
    status = parse_task_status(
        {"id": 1, "name": "To do", "color": "00FF00", "type": "todo", "order": 1}
    )
    assert isinstance(status, TaskStatus)
    assert status.type == "todo"
    assert status.color == "00FF00"
    assert status.order == "1"


def test_parse_file_resolves_expanded_folder() -> None:
    file = parse_file(
        {
            "id": 1,
            "readable_name": "Quotation 10.pdf",
            "size": 23455,
            "folder": {"id": 1, "name": "Quotations"},
            "preview_of": "/files/27",
            "file_itemtype": "Offerte",
        }
    )
    assert isinstance(file, File)
    assert file.readable_name == "Quotation 10.pdf"
    assert file.size == 23455
    assert isinstance(file.folder, FileFolder)
    assert file.folder.id == 1
    assert file.preview_of == RentmanLink("/files/27")
    assert file.file_itemtype == "Offerte"


def test_parse_file_degrades_on_sparse_payloads() -> None:
    file = parse_file(
        {
            "id": 1,
        }
    )
    assert file.folder is None
    assert file.preview_of is None
    assert file.url == ""
    assert file.parent_api_path == ""


def test_parse_file_folder_resolves_self_reference() -> None:
    folder = parse_file_folder({"id": 1, "parent": {"id": 2, "name": "Root"}, "is_template": False})
    assert isinstance(folder, FileFolder)
    assert isinstance(folder.parent, FileFolder)
    assert folder.parent.id == 2
    assert folder.is_template is False


def test_parse_file_folder_degrades_on_sparse_payloads() -> None:
    folder = parse_file_folder(
        {
            "id": 1,
        }
    )
    assert folder.parent is None
    assert folder.name == ""
    assert folder.parent_api_path == ""
