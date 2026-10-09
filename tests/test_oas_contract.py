"""Contract tests against the pinned Rentman OpenAPI document."""

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from types import UnionType
from typing import Any, get_args, get_origin, get_type_hints

import pytest
from scripts.resources import MODELS, PAYLOADS

from aiorentman import models, payloads
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
from aiorentman.models import RentmanLink
from aiorentman.payloads import WIRE_ALIASES, TaskPayload

FIXTURE = Path(__file__).parent / "fixtures" / "rentman_oas_1.16.0.json"

MODEL_SCHEMAS: dict[type, str] = {getattr(models, spec.name): spec.schema for spec in MODELS}


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


def test_every_operation_has_a_catalog_row(spec: dict[str, Any]) -> None:
    catalog = {(endpoint.method, template_path(endpoint)) for endpoint in CATALOG}
    for path, operations in spec["paths"].items():
        for method in ("get", "post", "put", "delete"):
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


def test_envelope_keys_match_the_api_response_schema(spec: dict[str, Any]) -> None:
    envelope = spec["components"]["schemas"]["ApiResponse"]["properties"]
    assert set(envelope) == {"itemCount", "limit", "offset", "next_page_url"}


def _annotation_members(annotation: Any) -> list[Any]:
    origin = get_origin(annotation)
    if origin is UnionType:
        return [arg for arg in get_args(annotation) if arg is not type(None)]
    return [annotation]


def test_nullable_spec_fields_are_optional_on_models(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for model, schema_name in MODEL_SCHEMAS.items():
        properties = schemas[schema_name]["properties"]
        hints = get_type_hints(model)
        for field in dataclasses.fields(model):
            if field.name in {"raw", "update_hash"}:
                continue
            prop = properties[WIRE_ALIASES.get(field.name, field.name)]
            wire_type = prop.get("type")
            nullable = isinstance(wire_type, list) and "null" in wire_type
            annotation = hints[field.name]
            assert not nullable or type(None) in get_args(annotation), (
                f"{model.__name__}.{field.name} is nullable in {schema_name}"
            )


def test_model_field_types_match_the_spec_categories(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    for model, schema_name in MODEL_SCHEMAS.items():
        properties = schemas[schema_name]["properties"]
        hints = get_type_hints(model)
        for field in dataclasses.fields(model):
            if field.name in {"raw", "update_hash"}:
                continue
            prop = properties[WIRE_ALIASES.get(field.name, field.name)]
            annotation = hints[field.name]
            if get_origin(annotation) is tuple:
                continue
            members = _annotation_members(annotation)
            wire_type = prop.get("type")
            if isinstance(wire_type, list):
                wire_type = next((part for part in wire_type if part != "null"), None)
            if wire_type is None or wire_type == "array":
                continue
            spec_type = spec_base_type(prop)
            if spec_type is RentmanLink and RentmanLink in members:
                continue
            if members == [datetime] and spec_type is str:
                continue
            assert members == [spec_type], (
                f"{model.__name__}.{field.name} disagrees with {schema_name}"
            )


PAYLOAD_SCHEMAS: dict[type, str] = {
    getattr(payloads, name): schema for schema, name in PAYLOADS.items()
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
