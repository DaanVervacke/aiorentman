"""Generate the model and parser modules from the pinned schema and the resource table.

Run ``uv run python -m scripts.generate`` to rewrite the generated modules, or
add ``--check`` to fail when a committed module differs from the generator
output.
"""

import json
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from aiorentman.payloads import WIRE_ALIASES
from scripts.resources import MODELS, ModelSpec

REPO = Path(__file__).resolve().parent.parent
SPEC = REPO / "tests" / "fixtures" / "rentman_oas_1.16.0.json"
PACKAGE = REPO / "src" / "aiorentman"


def load_schemas() -> Mapping[str, Any]:
    """Read the component schemas of the pinned OpenAPI document."""
    spec: dict[str, Any] = json.loads(SPEC.read_text())
    schemas: Mapping[str, Any] = spec["components"]["schemas"]
    return schemas


def snake(name: str) -> str:
    """Turn a CamelCase model name into its snake_case form."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


ATTRIBUTES = {wire: name for name, wire in WIRE_ALIASES.items()}


def attribute(wire: str) -> str:
    """Name the model attribute of one wire key, renaming the reserved ones."""
    return ATTRIBUTES.get(wire, wire)


def _base_type(prop: Mapping[str, Any]) -> tuple[str, bool]:
    wire_type = prop.get("type")
    if isinstance(wire_type, list):
        return next(part for part in wire_type if part != "null"), "null" in wire_type
    return str(wire_type), False


def _is_link(prop: Mapping[str, Any]) -> bool:
    example = prop.get("example")
    return isinstance(example, str) and example.startswith("/")


def field_rule(model: ModelSpec, wire: str, prop: Mapping[str, Any]) -> tuple[str, str]:
    """Pick the annotation and the parser expression of one model field."""
    name = attribute(wire)
    base, nullable = _base_type(prop)
    nullable = nullable or name in model.nullable
    key = f'"{wire}"'
    override = _override_rule(model, name, prop, key)
    if override is not None:
        return override
    if base == "string" and _is_link(prop):
        return _link_rule(model, name, key, nullable=nullable)
    return _scalar_rule(base, key, nullable=nullable)


def _override_rule(
    model: ModelSpec, name: str, prop: Mapping[str, Any], key: str
) -> tuple[str, str] | None:
    if name == "id":
        return "int", "required_id(data)"
    if name == "custom":
        return "dict[str, Any] = field(hash=False)", "custom_field(data)"
    if name in model.codes:
        return "tuple[str, ...]", f"codes_field(data, {key})"
    if name in model.datetimes or prop.get("format") == "date-time":
        return "datetime | None", f"datetime_field(data, {key})"
    if name in model.coerced:
        return "str", f"coerced_str_field(data, {key})"
    return None


def _scalar_rule(base: str, key: str, *, nullable: bool) -> tuple[str, str]:
    if base == "string" and nullable:
        return "str | None", f"str_or_none_field(data, {key})"
    scalars = {
        "string": ("str", "str_field"),
        "integer": ("int | None", "int_field"),
        "number": ("float | None", "float_field"),
        "boolean": ("bool", "bool_field"),
    }
    annotation, reader = scalars[base]
    return annotation, f"{reader}(data, {key})"


def _link_rule(model: ModelSpec, name: str, key: str, *, nullable: bool) -> tuple[str, str]:
    target = model.expand.get(name)
    if target is None:
        annotation, call = "RentmanLink", f"link_field(data, {key})"
    else:
        annotation = f"RentmanLink | {target}"
        call = f"link_or_model_field(data, {key}, parse_{snake(target)})"
    if nullable:
        return f"{annotation} | None", call
    return annotation, f"{call} or RentmanLink(str_field(data, {key}))"


def model_fields(model: ModelSpec, schemas: Mapping[str, Any]) -> list[tuple[str, str, str]]:
    """List the attribute, annotation, and parser expression of every model field."""
    properties: Mapping[str, Any] = schemas[model.schema]["properties"]
    rows: list[tuple[str, str, str]] = []
    custom: tuple[str, str, str] | None = None
    for wire, prop in properties.items():
        annotation, expression = field_rule(model, wire, prop)
        row = (attribute(wire), annotation, expression)
        if wire == "custom":
            custom = row
            continue
        rows.append(row)
        if wire == "modified":
            rows.append(("update_hash", "str", 'str_field(data, "updateHash")'))
    if custom is not None:
        rows.append(custom)
    rows.append(("raw", "dict[str, Any] | None = field(default=None, hash=False)", "dict(data)"))
    return rows


def _naming_pragma(name: str) -> str:
    mixed_case = name[0].islower() and name != name.lower()
    return "  # noqa: N815" if mixed_case else ""


def _all_block(names: Sequence[str]) -> str:
    return "__all__ = [\n" + "".join(f'    "{name}",\n' for name in sorted(names)) + "]\n"


def render_models(schemas: Mapping[str, Any]) -> str:
    """Render the source of models.py."""
    parts = [
        (
            '"""Immutable result models mirroring the pinned Rentman API schemas."""\n\n'
            "from dataclasses import dataclass, field\n"
            "from datetime import datetime\n"
            "from typing import Any\n\n"
            "from ._base import RentmanLink, RentmanPage\n\n"
        ),
        _all_block([*(model.name for model in MODELS), "RentmanLink", "RentmanPage"]),
    ]
    for model in MODELS:
        body = "".join(
            f"    {name}: {annotation}{_naming_pragma(name)}\n"
            for name, annotation, _ in model_fields(model, schemas)
        )
        parts.append(
            "\n\n@dataclass(frozen=True, slots=True)\n"
            f"class {model.name}:\n"
            f'    """{model.doc}"""\n\n'
            f"{body}"
        )
    return "".join(parts)


def render_parsers(schemas: Mapping[str, Any]) -> str:
    """Render the source of parsers.py."""
    functions: list[str] = []
    readers: set[str] = {"parse_envelope_item", "parse_page"}
    for model in MODELS:
        rows = model_fields(model, schemas)
        for _, _, expression in rows:
            readers.update(re.findall(r"\b([a-z_]+_field|required_id)\(", expression))
        arguments = "".join(f"        {name}={expression},\n" for name, _, expression in rows)
        model_noun, payload_noun = model.nouns
        functions.append(
            f"\n\ndef parse_{snake(model.name)}(data: Mapping[str, Any]) -> {model.name}:\n"
            f'    """Build the {model_noun} model from one {payload_noun} payload."""\n'
            f"    return {model.name}(\n{arguments}    )\n"
        )
    model_imports = sorted([*(model.name for model in MODELS), "RentmanLink"])
    parser_names = [f"parse_{snake(model.name)}" for model in MODELS]
    head = (
        '"""Convert raw Rentman payloads into result models.\n\n'
        "A model parser raises ValueError for an object without a usable id.\n"
        "parse_page, parse_envelope_item, and expanded links drop such objects.\n"
        '"""\n\n'
        "from collections.abc import Mapping\n"
        "from typing import Any\n\n"
        "from ._fields import (\n" + "".join(f"    {name},\n" for name in sorted(readers)) + ")\n"
        "from .models import (\n"
        + "".join(f"    {name},\n" for name in model_imports)
        + ")\n\n"
        + _all_block([*parser_names, "parse_envelope_item", "parse_page"])
    )
    return head + "".join(functions)


def format_source(source: str, path: Path) -> str:
    """Sort the imports and apply ruff format, as the check gate expects."""
    for command in (
        ("check", "--select", "I", "--fix-only", "--quiet"),
        ("format", "--quiet"),
    ):
        completed = subprocess.run(
            [sys.executable, "-m", "ruff", *command, "--stdin-filename", str(path), "-"],
            input=source,
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO,
        )
        source = completed.stdout
    return source


TARGETS: tuple[tuple[str, Callable[[Mapping[str, Any]], str]], ...] = (
    ("models.py", render_models),
    ("parsers.py", render_parsers),
)


def generate() -> dict[Path, str]:
    """Render every generated module, keyed by its path."""
    schemas = load_schemas()
    return {
        PACKAGE / name: format_source(render(schemas), PACKAGE / name) for name, render in TARGETS
    }


def main(argv: Sequence[str]) -> int:
    """Write the generated modules, or with --check report the stale ones."""
    check = "--check" in argv
    stale = []
    for path, source in generate().items():
        if path.read_text() == source:
            continue
        stale.append(path)
        if not check:
            path.write_text(source)
    for path in stale:
        verb = "is stale" if check else "regenerated"
        print(f"{path.relative_to(REPO)} {verb}", file=sys.stderr)
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
