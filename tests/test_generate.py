"""Generator tests: resource table validation, field rules, formatting, and the CLI."""

import copy
import dataclasses
from pathlib import Path
from typing import Any

import pytest
from scripts import generate
from scripts.generate import ResourceTableError, field_rule, format_source, validate
from scripts.resources import ENDPOINTS, MODELS, PAYLOADS


@pytest.fixture(scope="module")
def pinned() -> dict[str, Any]:
    spec: dict[str, Any] = copy.deepcopy(dict(generate.load_spec()))
    return spec


def model(name: str) -> Any:
    return next(spec for spec in MODELS if spec.name == name)


def endpoint(const: str) -> Any:
    return next(spec for spec in ENDPOINTS if spec.const == const)


def problems_for(spec: dict[str, Any]) -> str:
    with pytest.raises(ResourceTableError) as info:
        validate(spec)
    return str(info.value)


def replace_model(monkeypatch: pytest.MonkeyPatch, name: str, **changes: Any) -> None:
    replaced = tuple(
        dataclasses.replace(spec, **changes) if spec.name == name else spec for spec in MODELS
    )
    monkeypatch.setattr(generate, "MODELS", replaced)


def replace_endpoint(monkeypatch: pytest.MonkeyPatch, const: str, **changes: Any) -> None:
    replaced = tuple(
        dataclasses.replace(spec, **changes) if spec.const == const else spec for spec in ENDPOINTS
    )
    monkeypatch.setattr(generate, "ENDPOINTS", replaced)


def test_the_committed_table_is_valid(pinned: dict[str, Any]) -> None:
    validate(pinned)


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"datetimes": ("purchasedat",)}, "datetimes: 'purchasedat' is not a field"),
        ({"coerced": ("nope",)}, "coerced: 'nope' is not a field"),
        ({"codes": ("nope",)}, "codes: 'nope' is not a field"),
        ({"nullable": ("nope",)}, "nullable: 'nope' is not a field"),
        ({"nullable": ("in_shop",)}, "nullable: 'in_shop' is not a string or link field"),
        ({"expand": {"name": "Folder"}}, "expand: 'name' is not a link field"),
        ({"expand": {"folder": "Fldr"}}, "expand: 'folder' targets unknown model 'Fldr'"),
        ({"schema": "MissingResponse"}, "schema MissingResponse is not in the pinned document"),
    ],
)
def test_model_overrides_must_match_the_schema(
    monkeypatch: pytest.MonkeyPatch,
    pinned: dict[str, Any],
    changes: dict[str, Any],
    expected: str,
) -> None:
    replace_model(monkeypatch, "Equipment", **changes)
    assert "ModelSpec Equipment" in (found := problems_for(pinned))
    assert expected in found


@pytest.mark.parametrize(
    ("prop", "expected"),
    [
        ({"type": "array"}, "type 'array' has no rule"),
        ({"type": "object"}, "type 'object' has no rule"),
        ({"description": "untyped"}, "type None has no rule"),
        ({"type": ["boolean", "null"]}, "nullable boolean has no rule"),
    ],
)
def test_schema_types_without_a_rule_are_reported(
    pinned: dict[str, Any], prop: dict[str, Any], expected: str
) -> None:
    spec = copy.deepcopy(pinned)
    spec["components"]["schemas"]["FolderResponse"]["properties"]["extra"] = prop
    assert f"ModelSpec Folder.extra: {expected}" in problems_for(spec)


def test_keyword_wire_keys_need_an_alias(pinned: dict[str, Any]) -> None:
    spec = copy.deepcopy(pinned)
    spec["components"]["schemas"]["FolderResponse"]["properties"]["class"] = {"type": "string"}
    assert "wire key 'class' is a Python keyword, add it to WIRE_ALIASES" in problems_for(spec)


@pytest.mark.parametrize(
    ("const", "changes", "expected"),
    [
        ("VEHICLES", {"path": "/nope"}, "GET /nope is not in the pinned document"),
        ("VEHICLES_ITEM", {"path": "/vehicles"}, "item paths must hold {id}"),
        ("VEHICLES", {"path": "/vehicles/{id}"}, "collection paths must not hold {id}"),
        ("VEHICLES_ITEM", {"param": None}, "item rows must set param"),
        ("VEHICLES", {"param": "vehicle_id"}, "collection rows must not set param"),
        ("VEHICLES", {"docs": ("Only one.",)}, "collection rows need 2 docstrings"),
        ("VEHICLES_ITEM", {"docs": ("One.", "Two.")}, "item rows need 1 docstrings"),
    ],
)
def test_endpoint_rows_must_match_the_schema(
    monkeypatch: pytest.MonkeyPatch,
    pinned: dict[str, Any],
    const: str,
    changes: dict[str, Any],
    expected: str,
) -> None:
    replace_endpoint(monkeypatch, const, **changes)
    assert f"EndpointSpec {const}: {expected}" in problems_for(pinned)


def test_response_schemas_need_a_model(
    monkeypatch: pytest.MonkeyPatch, pinned: dict[str, Any]
) -> None:
    monkeypatch.setattr(generate, "MODELS", tuple(m for m in MODELS if m.name != "Vehicle"))
    assert "EndpointSpec VEHICLES: response schema VehicleResponse has no ModelSpec" in (
        problems_for(pinned)
    )


def test_request_schemas_need_a_payload(
    monkeypatch: pytest.MonkeyPatch, pinned: dict[str, Any]
) -> None:
    payloads = {schema: name for schema, name in PAYLOADS.items() if schema != "VehicleRequest"}
    monkeypatch.setattr(generate, "PAYLOADS", payloads)
    assert "EndpointSpec CREATE_VEHICLE: request schema VehicleRequest has no PAYLOADS entry" in (
        problems_for(pinned)
    )


def test_payload_classes_must_exist(
    monkeypatch: pytest.MonkeyPatch, pinned: dict[str, Any]
) -> None:
    monkeypatch.setattr(generate, "PAYLOADS", {**PAYLOADS, "VehicleRequest": "VehiclePayloud"})
    assert "PAYLOADS VehicleRequest: VehiclePayloud is not in aiorentman.payloads" in (
        problems_for(pinned)
    )


def test_names_must_be_unique(monkeypatch: pytest.MonkeyPatch, pinned: dict[str, Any]) -> None:
    monkeypatch.setattr(generate, "ENDPOINTS", (*ENDPOINTS, endpoint("VEHICLES")))
    monkeypatch.setattr(generate, "MODELS", (*MODELS, model("Vehicle")))
    found = problems_for(pinned)
    assert "EndpointSpec VEHICLES: VEHICLES repeats VEHICLES" in found
    assert "EndpointSpec VEHICLES: async_list_vehicles repeats VEHICLES" in found
    assert "ModelSpec Vehicle: name repeats" in found


def test_every_problem_is_reported_at_once(
    monkeypatch: pytest.MonkeyPatch, pinned: dict[str, Any]
) -> None:
    replace_model(monkeypatch, "Equipment", codes=("one",), coerced=("two",))
    with pytest.raises(ResourceTableError) as info:
        validate(pinned)
    assert len(info.value.problems) == 2


def test_field_rule_applies_nullable_overrides_to_links() -> None:
    serial = model("SerialNumber")
    rule = field_rule(serial, "asset_location", {"type": "string", "example": "/stocklocations/0"})
    assert rule == (
        "RentmanLink | StockLocation | None",
        'link_or_model_field(data, "asset_location", parse_stock_location)',
    )


def test_field_rule_reads_nullable_strings_as_optional() -> None:
    rule = field_rule(model("Folder"), "note", {"type": ["string", "null"]})
    assert rule == ("str | None", 'str_or_none_field(data, "note")')


def test_format_source_reports_the_ruff_error() -> None:
    with pytest.raises(RuntimeError, match=r"ruff format failed on generated broken\.py:\n.*parse"):
        format_source("def (:\n", Path("src/aiorentman/broken.py"))


def test_main_rejects_unknown_flags() -> None:
    with pytest.raises(SystemExit) as info:
        generate.main(["--chek"])
    assert info.value.code == 2


def test_main_writes_stale_modules(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stale = tmp_path / "models.py"
    stale.write_text("old\n")
    current = tmp_path / "parsers.py"
    current.write_text("same\n")
    monkeypatch.setattr(generate, "REPO", tmp_path)
    monkeypatch.setattr(generate, "generate", lambda: {stale: "new\n", current: "same\n"})
    assert generate.main([]) == 0
    assert stale.read_text() == "new\n"
    assert capsys.readouterr().err == "models.py regenerated\n"
