"""Contract tests against the pinned Rentman OpenAPI document."""

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any, get_args

import pytest

from aiorentman._endpoints import (
    CATALOG,
    CollectionArgs,
    CreateArgs,
    DeleteArgs,
    ItemArgs,
    LinkedCreateArgs,
    ParentCollectionArgs,
    UpdateArgs,
)
from aiorentman.const import OAS_VERSION
from aiorentman.models import (
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
from aiorentman.payloads import (
    WIRE_ALIASES,
    AccessoryPayload,
    AlternativePayload,
    AppointmentCrewPayload,
    AppointmentPayload,
    ContactPayload,
    ContactPersonPayload,
    CrewAvailabilityPayload,
    EquipmentPayload,
    EquipmentSetContentPayload,
    FolderPayload,
    LeaveMutationPayload,
    LeaveRequestPayload,
    PaymentPayload,
    ProjectCostPayload,
    ProjectFunctionGroupPayload,
    ProjectFunctionPayload,
    ProjectPayload,
    ProjectRequestEquipmentPayload,
    ProjectRequestPayload,
    SerialNumberPayload,
    StockMovementPayload,
    SubprojectPayload,
    SubtaskPayload,
    SupplierPayload,
    TaskAssignmentPayload,
    TaskPayload,
    TaskStatusPayload,
    TimeRegistrationPayload,
    VehiclePayload,
)

FIXTURE = Path(__file__).parent / "fixtures" / "rentman_oas_1.16.0.json"

MODEL_SCHEMAS: dict[type, str] = {
    Accessory: "AccessoryResponse",
    ActualContent: "ActualContentResponse",
    Alternative: "AlternativeResponse",
    Appointment: "AppointmentResponse",
    AppointmentCrew: "AppointmentCrewResponse",
    Contact: "ContactResponse",
    ContactPerson: "ContactPersonResponse",
    Contract: "ContractResponse",
    Crew: "CrewResponse",
    CrewAvailability: "CrewAvailabilityResponse",
    CrewRate: "CrewRatesResponse",
    Equipment: "EquipmentResponse",
    EquipmentAssignedSerial: "EquipmentAssignedSerialsResponse",
    EquipmentSetContent: "EquipmentSetContentResponse",
    ExtraInputField: "ExtraInputFieldResponse",
    Factor: "FactorsResponse",
    FactorGroup: "FactorGroupsResponse",
    File: "FileResponse",
    FileFolder: "FileFolderResponse",
    Folder: "FolderResponse",
    Invitation: "InvitationsResponse",
    Invoice: "FactuurResponse",
    InvoiceLine: "InvoiceLineResponse",
    LeaveMutation: "LeaveMutationsResponse",
    LeaveRequest: "LeaveRequestResponse",
    LeaveType: "LeaveTypesResponse",
    LedgerCode: "LedgerResponse",
    Payment: "PaymentResponse",
    Project: "ProjectResponse",
    ProjectCost: "ProjectCostResponse",
    ProjectCrew: "ProjectCrewResponse",
    ProjectEquipment: "ProjectEquipmentResponse",
    ProjectEquipmentGroup: "ProjectEquipmentGroupResponse",
    ProjectFunction: "ProjectFunctionResponse",
    ProjectFunctionGroup: "ProjectFunctionGroupResponse",
    ProjectRequest: "ProjectRequestResponse",
    ProjectRequestEquipment: "ProjectRequestEquipmentResponse",
    ProjectStatus: "ProjectStatusResponse",
    ProjectType: "ProjectTypeResponse",
    ProjectVehicle: "ProjectVehicleResponse",
    PurchaseOrder: "PurchaseOrderResponse",
    PurchaseOrderCost: "PurchaseOrderCostResponse",
    PurchaseOrderGlobalCost: "PurchaseOrderGlobalCostResponse",
    Quote: "QuotationResponse",
    Rate: "CrewRateResponse",
    RateFactor: "CrewRateFactorResponse",
    Repair: "RepairResponse",
    SerialNumber: "SerialNumberResponse",
    Status: "StatusResponse",
    StockLocation: "StockLocationResponse",
    StockMovement: "StockMovementResponse",
    Subproject: "SubprojectResponse",
    Subrental: "SubrentalResponse",
    SubrentalEquipment: "SubrentalEquipmentResponse",
    SubrentalEquipmentGroup: "SubrentalEquipmentGroupResponse",
    Subtask: "SubtaskResponse",
    Supplier: "SupplierResponse",
    Task: "TaskResponse",
    TaskAssignment: "TaskAssignmentResponse",
    TaskStatus: "TaskStatusResponse",
    TaxClass: "TaxClassResponse",
    TimeRegistration: "TimeRegistrationResponse",
    TimeRegistrationActivity: "TimeRegistrationActivityResponse",
    Vehicle: "VehicleResponse",
    WarehouseStatus: "WarehouseStatusResponse",
}


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(FIXTURE.read_text())
    return payload


def sample_args(endpoint: Any) -> Any:
    for sample in (
        CollectionArgs(query=None),
        ItemArgs(item_id=1),
        ParentCollectionArgs(parent_id=1),
        CreateArgs(payload=TaskPayload(color="#ffffff")),
        LinkedCreateArgs(parent_id=1, payload=TaskPayload(color="#ffffff")),
        UpdateArgs(item_id=1, payload=TaskPayload(color="#ffffff")),
        DeleteArgs(item_id=1),
    ):
        try:
            endpoint.path(sample)
        except AttributeError:
            continue
        else:
            return sample
    msg = f"no sample args fit endpoint {endpoint.name}"
    raise AssertionError(msg)


def test_spec_is_the_pinned_version(spec: dict[str, Any]) -> None:
    assert spec["info"]["version"] == OAS_VERSION


def template_path(endpoint: Any) -> str:
    """Render the path template of one endpoint, with sample ids replaced back."""
    built = endpoint.path(sample_args(endpoint))
    template: str = built.replace("/1/", "/{id}/")
    if template.endswith("/1"):
        template = f"{template.removesuffix('/1')}/{{id}}"
    return template


def test_every_endpoint_exists_in_the_spec(spec: dict[str, Any]) -> None:
    paths = spec["paths"]
    for endpoint in CATALOG:
        path = template_path(endpoint)
        assert path in paths, f"{endpoint.name} path {path} is missing from the spec"
        operation = paths[path].get(endpoint.method.lower())
        assert operation is not None, f"{endpoint.name} has no {endpoint.method} on {path}"
        if endpoint.method == "DELETE":
            schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
            assert schema == {"type": "null"}, endpoint.name
            continue
        schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
        data = schema["allOf"][0]["properties"]["data"]
        referenced = data["$ref"] if "$ref" in data else data["items"]["$ref"]
        assert referenced == f"#/components/schemas/{endpoint.response_schema}", (
            f"{endpoint.name} declares schema {endpoint.response_schema}"
        )
        if endpoint.method in {"POST", "PUT"}:
            request = operation["requestBody"]["content"]["application/json"]["schema"]
            assert request["$ref"] == f"#/components/schemas/{endpoint.request_schema}", (
                f"{endpoint.name} declares body schema {endpoint.request_schema}"
            )


def test_every_write_operation_has_a_catalog_row(spec: dict[str, Any]) -> None:
    catalog = {(endpoint.method, template_path(endpoint)) for endpoint in CATALOG}
    for path, operations in spec["paths"].items():
        for method in ("post", "put", "delete"):
            if method in operations:
                assert (method.upper(), path) in catalog, (
                    f"no catalog row for {method.upper()} {path}"
                )


def test_endpoint_schemas_match_the_catalog(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for endpoint in CATALOG:
        if endpoint.response_schema is not None:
            assert endpoint.response_schema in schemas, endpoint.name
        if endpoint.request_schema is not None:
            assert endpoint.request_schema in schemas, endpoint.name


def test_model_fields_match_the_spec_properties(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for model, schema_name in MODEL_SCHEMAS.items():
        properties = set(schemas[schema_name]["properties"])
        fields = {WIRE_ALIASES.get(field.name, field.name) for field in dataclasses.fields(model)}
        assert fields - {"raw", "update_hash"} == properties, (
            f"{model.__name__} disagrees with {schema_name}"
        )


PAYLOAD_SCHEMAS: dict[type, str] = {
    AccessoryPayload: "AccessoryRequest",
    AlternativePayload: "AlternativeRequest",
    AppointmentCrewPayload: "AppointmentCrewRequest",
    AppointmentPayload: "AppointmentRequest",
    ContactPayload: "ContactRequest",
    ContactPersonPayload: "ContactPersonRequest",
    CrewAvailabilityPayload: "CrewAvailabilityRequest",
    EquipmentPayload: "EquipmentRequest",
    EquipmentSetContentPayload: "EquipmentSetContentRequest",
    FolderPayload: "FolderRequest",
    LeaveMutationPayload: "LeaveMutationsRequest",
    LeaveRequestPayload: "LeaveRequestRequest",
    PaymentPayload: "PaymentRequest",
    ProjectCostPayload: "ProjectCostRequest",
    ProjectFunctionGroupPayload: "ProjectFunctionGroupRequest",
    ProjectFunctionPayload: "ProjectFunctionRequest",
    ProjectPayload: "ProjectRequest",
    ProjectRequestEquipmentPayload: "ProjectRequestEquipmentRequest",
    ProjectRequestPayload: "ProjectRequestRequest",
    SerialNumberPayload: "SerialNumberRequest",
    StockMovementPayload: "StockMovementRequest",
    SubprojectPayload: "SubprojectRequest",
    SubtaskPayload: "SubtaskRequest",
    SupplierPayload: "SupplierRequest",
    TaskAssignmentPayload: "TaskAssignmentRequest",
    TaskPayload: "TaskRequest",
    TaskStatusPayload: "TaskStatusRequest",
    TimeRegistrationPayload: "TimeRegistrationRequest",
    VehiclePayload: "VehicleRequest",
}


def payload_base_type(field: dataclasses.Field[Any]) -> Any:
    args = get_args(field.type)
    if len(args) == 2 and type(None) in args:
        return next(arg for arg in args if arg is not type(None))
    return field.type


def spec_base_type(prop: dict[str, Any]) -> Any:
    wire_type = prop.get("type")
    if isinstance(wire_type, list):
        wire_type = next(part for part in wire_type if part != "null")
    if wire_type == "object":
        return dict[str, Any]
    if wire_type == "string":
        if prop.get("format") == "date-time":
            return datetime
        example = prop.get("example", "")
        if isinstance(example, str) and example.startswith("/"):
            return RentmanLink
        return str
    scalars: dict[str, Any] = {"integer": int, "number": float, "boolean": bool}
    assert wire_type in scalars, wire_type
    return scalars[wire_type]


def test_payload_fields_match_the_request_schemas(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for payload, schema_name in PAYLOAD_SCHEMAS.items():
        properties = schemas[schema_name]["properties"]
        fields = dataclasses.fields(payload)
        wire_names = {WIRE_ALIASES.get(field.name, field.name) for field in fields}
        assert wire_names == set(properties), f"{payload.__name__} disagrees with {schema_name}"
        for field in fields:
            prop = properties[WIRE_ALIASES.get(field.name, field.name)]
            assert payload_base_type(field) == spec_base_type(prop), (
                f"{payload.__name__}.{field.name} disagrees with {schema_name}"
            )


def test_payload_required_fields_have_no_default(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for payload, schema_name in PAYLOAD_SCHEMAS.items():
        required = set(schemas[schema_name].get("required", []))
        without_default = {
            WIRE_ALIASES.get(field.name, field.name)
            for field in dataclasses.fields(payload)
            if field.default is dataclasses.MISSING
        }
        assert without_default == required, f"{payload.__name__} disagrees with {schema_name}"


def test_spec_has_no_undocumented_in_scope_resources(spec: dict[str, Any]) -> None:
    in_scope = {
        "/accessories",
        "/actualcontent",
        "/alternatives",
        "/appointmentcrew",
        "/appointments",
        "/contacts",
        "/contactpersons",
        "/contracts",
        "/costs",
        "/crew",
        "/crewavailability",
        "/crewrates",
        "/equipment",
        "/equipmentassignedserials",
        "/equipmentsetscontent",
        "/extrainputfields",
        "/factorgroups",
        "/factors",
        "/file_folders",
        "/files",
        "/folders",
        "/invitations",
        "/invoicelines",
        "/invoices",
        "/leavemutation",
        "/leaverequest",
        "/leavetypes",
        "/ledgercodes",
        "/payments",
        "/projectcrew",
        "/projectequipment",
        "/projectequipmentgroup",
        "/projectfunctiongroups",
        "/projectfunctions",
        "/projectrequestequipment",
        "/projectrequests",
        "/projectstatuses",
        "/projecttypes",
        "/projectvehicles",
        "/projects",
        "/purchaseordercosts",
        "/purchaseorderglobalcosts",
        "/purchaseorders",
        "/quotes",
        "/ratefactors",
        "/rates",
        "/repairs",
        "/serialnumbers",
        "/statuses",
        "/stocklocations",
        "/stockmovements",
        "/subprojects",
        "/subrentalequipment",
        "/subrentalequipmentgroup",
        "/subrentals",
        "/subtasks",
        "/suppliers",
        "/taskassignments",
        "/taskstatuses",
        "/tasks",
        "/taxclasses",
        "/timeregistration",
        "/timeregistrationactivities",
        "/vehicles",
        "/warehousestatuses",
    }
    for path in in_scope:
        assert path in spec["paths"], f"expected resource root {path}"
