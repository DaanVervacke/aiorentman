"""Generate the models, parsers, endpoint catalog, and client from the resource table.

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
from scripts.resources import ENDPOINTS, MODELS, PAYLOADS, EndpointSpec, ModelSpec

REPO = Path(__file__).resolve().parent.parent
SPEC = REPO / "tests" / "fixtures" / "rentman_oas_1.16.0.json"
PACKAGE = REPO / "src" / "aiorentman"


def load_spec() -> Mapping[str, Any]:
    """Read the pinned OpenAPI document."""
    spec: dict[str, Any] = json.loads(SPEC.read_text())
    return spec


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


ARGS = {
    "collection": "CollectionArgs",
    "item": "ItemArgs",
    "linked": "ParentCollectionArgs",
    "create": "CreateArgs",
    "linked_create": "LinkedCreateArgs",
    "update": "UpdateArgs",
    "delete": "DeleteArgs",
}
HTTP_METHODS = {
    "collection": "GET",
    "item": "GET",
    "linked": "GET",
    "create": "POST",
    "linked_create": "POST",
    "update": "PUT",
    "delete": "DELETE",
}
BODIES = {
    "create": "create_body",
    "linked_create": "linked_create_body",
    "update": "update_body",
}
ID_ATTRIBUTES = {
    "item": "item_id",
    "update": "item_id",
    "delete": "item_id",
    "linked": "parent_id",
    "linked_create": "parent_id",
}


def _operation(spec: Mapping[str, Any], endpoint: EndpointSpec) -> Mapping[str, Any]:
    operation: Mapping[str, Any] = spec["paths"][endpoint.path][HTTP_METHODS[endpoint.kind].lower()]
    return operation


def _schema_name(reference: str) -> str:
    return reference.rsplit("/", 1)[-1]


def response_schema(spec: Mapping[str, Any], endpoint: EndpointSpec) -> str | None:
    """Name the response schema of one endpoint, or None for a delete."""
    if endpoint.kind == "delete":
        return None
    content = _operation(spec, endpoint)["responses"]["200"]["content"]
    data = content["application/json"]["schema"]["allOf"][0]["properties"]["data"]
    return _schema_name(data["$ref"] if "$ref" in data else data["items"]["$ref"])


def request_schema(spec: Mapping[str, Any], endpoint: EndpointSpec) -> str | None:
    """Name the request body schema of one endpoint, or None when it sends no body."""
    if endpoint.kind not in BODIES:
        return None
    body = _operation(spec, endpoint)["requestBody"]["content"]["application/json"]["schema"]
    return _schema_name(body["$ref"])


def endpoint_model(spec: Mapping[str, Any], endpoint: EndpointSpec) -> str | None:
    """Name the result model of one endpoint, or None for a delete."""
    schema = response_schema(spec, endpoint)
    if schema is None:
        return None
    return next(model.name for model in MODELS if model.schema == schema)


def endpoint_result(spec: Mapping[str, Any], endpoint: EndpointSpec) -> str:
    """Render the parsed result type of one endpoint."""
    model = endpoint_model(spec, endpoint)
    if model is None:
        return "None"
    if endpoint.kind in {"collection", "linked"}:
        return f"RentmanPage[{model}]"
    return f"{model} | None"


def _path_lambda(endpoint: EndpointSpec) -> str:
    if "{id}" not in endpoint.path:
        return f'lambda _args: "{endpoint.path}"'
    rendered = endpoint.path.replace("{id}", "{args." + ID_ATTRIBUTES[endpoint.kind] + "}")
    return f'lambda args: f"{rendered}"'


def _endpoint_row(spec: Mapping[str, Any], endpoint: EndpointSpec) -> str:
    model = endpoint_model(spec, endpoint)
    if model is None:
        parse = "lambda _payload, _args: None"
    elif endpoint.kind in {"collection", "linked"}:
        parse = f"lambda payload, _args: parse_page(payload, parse_{snake(model)})"
    else:
        parse = f"lambda payload, _args: parse_envelope_item(payload, parse_{snake(model)})"
    params = {
        "collection": "collection_params",
        "linked": "linked_collection_params",
    }.get(endpoint.kind, "lambda _args: {}")
    schema = response_schema(spec, endpoint)
    lines = [
        f'    name="{endpoint.const.lower()}",\n',
        f'    method="{HTTP_METHODS[endpoint.kind]}",\n',
        f"    path={_path_lambda(endpoint)},\n",
    ]
    if endpoint.kind in {*BODIES, "delete"}:
        lines += [f"    parse={parse},\n", f"    params={params},\n"]
    else:
        lines += [f"    params={params},\n", f"    parse={parse},\n"]
    lines.append(f'    response_schema="{schema}",\n' if schema else "    response_schema=None,\n")
    if endpoint.kind in BODIES:
        lines += [
            f"    body={BODIES[endpoint.kind]},\n",
            f'    request_schema="{request_schema(spec, endpoint)}",\n',
        ]
    annotation = f"Endpoint[{ARGS[endpoint.kind]}, {endpoint_result(spec, endpoint)}]"
    return f"{endpoint.const}: {annotation} = Endpoint(\n" + "".join(lines) + ")\n"


def render_endpoints(spec: Mapping[str, Any]) -> str:
    """Render the source of _endpoints.py."""
    models = {"RentmanPage"}
    parsers = set()
    for endpoint in ENDPOINTS:
        model = endpoint_model(spec, endpoint)
        if model is None:
            continue
        models.add(model)
        parsers.add(f"parse_{snake(model)}")
        parsers.add(
            "parse_page" if endpoint.kind in {"collection", "linked"} else "parse_envelope_item"
        )
    helpers = sorted(
        {
            *ARGS.values(),
            "Endpoint",
            "collection_params",
            "linked_collection_params",
            *BODIES.values(),
        }
    )
    constants = [endpoint.const for endpoint in ENDPOINTS]
    head = (
        '"""The frozen endpoint catalog: one row per wire contract."""\n\n'
        "from typing import Any\n\n"
        + _import_block("._endpoint_types", helpers)
        + _import_block(".models", sorted(models))
        + _import_block(".parsers", sorted(parsers))
        + "\n"
        + _all_block([*constants, "CATALOG", *ARGS.values(), "Endpoint"])
        + "\n\n"
    )
    rows = "\n".join(_endpoint_row(spec, endpoint) for endpoint in ENDPOINTS)
    catalog = (
        "\nCATALOG: tuple[Endpoint[Any, Any], ...] = (\n"
        + "".join(f"    {const},\n" for const in constants)
        + ")\n"
    )
    return head + rows + catalog


def _import_block(module: str, names: Sequence[str]) -> str:
    return f"from {module} import (\n" + "".join(f"    {name},\n" for name in names) + ")\n"


def _client_arguments(endpoint: EndpointSpec) -> str:
    param = endpoint.param
    return {
        "collection": "CollectionArgs(query=query)",
        "linked": f"ParentCollectionArgs(parent_id={param}, query=query)",
        "item": f"ItemArgs(item_id={param})",
        "create": "CreateArgs(payload)",
        "linked_create": f"LinkedCreateArgs({param}, payload)",
        "update": f"UpdateArgs({param}, payload)",
        "delete": f"DeleteArgs({param})",
    }[endpoint.kind]


def _method(definition: str, doc: str, returned: str) -> str:
    return f'    {definition}:\n        """{doc}"""\n        return {returned}\n'


def _client_methods(spec: Mapping[str, Any], endpoint: EndpointSpec) -> list[str]:
    model = endpoint_model(spec, endpoint)
    result = endpoint_result(spec, endpoint)
    arguments = _client_arguments(endpoint)
    payload = PAYLOADS.get(request_schema(spec, endpoint) or "")
    parameters = ["self"]
    if endpoint.param is not None:
        parameters.append(f"{endpoint.param}: int")
    if payload is not None:
        parameters.append(f"payload: {payload}")
    if endpoint.kind in {"collection", "linked"}:
        parameters.append("query: Query | None = None")
        signature = ", ".join(parameters)
        list_doc, iter_doc = endpoint.docs
        return [
            _method(
                f"async def async_list_{endpoint.method}({signature}) -> {result}",
                list_doc,
                f"await self._call({endpoint.const}, {arguments})",
            ),
            _method(
                f"def async_iter_{endpoint.method}({signature}) -> AsyncIterator[{model}]",
                iter_doc,
                f"self._iter_collection({endpoint.const}, {arguments})",
            ),
        ]
    verb = {
        "item": "get",
        "create": "create",
        "linked_create": "create",
        "update": "update",
        "delete": "delete",
    }[endpoint.kind]
    (doc,) = endpoint.docs
    return [
        _method(
            f"async def async_{verb}_{endpoint.method}({', '.join(parameters)}) -> {result}",
            doc,
            f"await self._call({endpoint.const}, {arguments})",
        )
    ]


def render_client(spec: Mapping[str, Any]) -> str:
    """Render the source of client.py."""
    models = {"RentmanPage"}
    payloads = set()
    for endpoint in ENDPOINTS:
        model = endpoint_model(spec, endpoint)
        if model is not None:
            models.add(model)
        payload = PAYLOADS.get(request_schema(spec, endpoint) or "")
        if payload is not None:
            payloads.add(payload)
    endpoint_names = sorted(
        {endpoint.const for endpoint in ENDPOINTS} | {ARGS[endpoint.kind] for endpoint in ENDPOINTS}
    )
    head = (
        '"""The RentmanClient facade: one typed method per endpoint."""\n\n'
        "from collections.abc import AsyncIterator\n\n"
        "from ._core import ClientCore\n"
        + _import_block("._endpoints", endpoint_names)
        + _import_block(".models", sorted(models))
        + _import_block(".payloads", sorted(payloads))
        + "from .query import Query\n\n\n"
        "class RentmanClient(ClientCore):\n"
        '    """Asynchronous client for the Rentman API.\n\n'
        "    The client covers every documented read path, with create, update,\n"
        "    and delete methods for every documented write path. Every request is paced"
        " against the\n"
        "    documented rate limits unless pacing is disabled with\n"
        "    ``requests_per_second=None``.\n"
        '    """\n'
    )
    methods = [method for endpoint in ENDPOINTS for method in _client_methods(spec, endpoint)]
    return head + "\n" + "\n".join(methods)


def format_source(source: str, path: Path) -> str:
    """Sort the imports and apply ruff format, as the check gate expects."""
    for command in (
        ("check", "--select", "I,RUF022", "--fix-only", "--quiet"),
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
    ("models.py", lambda spec: render_models(spec["components"]["schemas"])),
    ("parsers.py", lambda spec: render_parsers(spec["components"]["schemas"])),
    ("_endpoints.py", render_endpoints),
    ("client.py", render_client),
)


def generate() -> dict[Path, str]:
    """Render every generated module, keyed by its path."""
    spec = load_spec()
    return {PACKAGE / name: format_source(render(spec), PACKAGE / name) for name, render in TARGETS}


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
