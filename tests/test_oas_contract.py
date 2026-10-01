"""Contract tests against the pinned Rentman OpenAPI document."""

import dataclasses
import json
from pathlib import Path
from typing import Any

import pytest

from aiorentman._endpoints import (
    CATALOG,
    CollectionArgs,
    ItemArgs,
    ParentCollectionArgs,
)
from aiorentman.const import OAS_VERSION
from aiorentman.models import (
    ActualContent,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
    Folder,
    Project,
    ProjectEquipment,
    Repair,
    SerialNumber,
    Status,
    StockLocation,
    StockMovement,
    Subproject,
    WarehouseStatus,
)

FIXTURE = Path(__file__).parent / "fixtures" / "rentman_oas_1.16.0.json"

MODEL_SCHEMAS: dict[type, str] = {
    ActualContent: "ActualContentResponse",
    Equipment: "EquipmentResponse",
    EquipmentAssignedSerial: "EquipmentAssignedSerialsResponse",
    EquipmentSetContent: "EquipmentSetContentResponse",
    Folder: "FolderResponse",
    Project: "ProjectResponse",
    ProjectEquipment: "ProjectEquipmentResponse",
    Repair: "RepairResponse",
    SerialNumber: "SerialNumberResponse",
    Status: "StatusResponse",
    StockLocation: "StockLocationResponse",
    StockMovement: "StockMovementResponse",
    Subproject: "SubprojectResponse",
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
        operation = paths[path].get("get")
        assert operation is not None, f"{endpoint.name} has no GET on {path}"
        schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
        data = schema["allOf"][0]["properties"]["data"]
        referenced = data["$ref"] if "$ref" in data else data["items"]["$ref"]
        assert referenced == f"#/components/schemas/{endpoint.response_schema}", (
            f"{endpoint.name} declares schema {endpoint.response_schema}"
        )


def test_endpoint_schemas_match_the_catalog(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for endpoint in CATALOG:
        assert endpoint.response_schema in schemas, endpoint.name


def test_model_fields_match_the_spec_properties(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for model, schema_name in MODEL_SCHEMAS.items():
        properties = set(schemas[schema_name]["properties"])
        fields = {field.name for field in dataclasses.fields(model)}
        assert fields - {"raw"} == properties, f"{model.__name__} disagrees with {schema_name}"


def test_spec_has_no_undocumented_in_scope_resources(spec: dict[str, Any]) -> None:
    in_scope = {
        "/actualcontent",
        "/equipment",
        "/equipmentassignedserials",
        "/equipmentsetscontent",
        "/folders",
        "/projectequipment",
        "/projects",
        "/repairs",
        "/serialnumbers",
        "/statuses",
        "/stocklocations",
        "/stockmovements",
        "/subprojects",
        "/warehousestatuses",
    }
    for path in in_scope:
        assert path in spec["paths"], f"expected resource root {path}"
