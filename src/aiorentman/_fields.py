"""Field readers and envelope parsing shared by every model parser."""

import logging
from collections.abc import Callable, Mapping
from datetime import datetime
from re import compile as _compile
from typing import Any

from ._base import RentmanLink, RentmanPage

_CODE_SEPARATOR = _compile(r"[,\n]+")

_LOGGER = logging.getLogger("aiorentman.parsers")


class MissingIdError(ValueError):
    """An object payload carries no usable integer id."""


def str_field(data: Mapping[str, Any], key: str, default: str = "") -> str:
    value = data.get(key)
    return value if isinstance(value, str) else default


def str_or_none_field(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    return value if isinstance(value, str) else None


def coerced_str_field(data: Mapping[str, Any], key: str) -> str:
    """Accept text or a number where the API declares a string."""
    value = data.get(key)
    if isinstance(value, bool):
        return ""
    if isinstance(value, str | int | float):
        return str(value)
    return ""


def int_field(data: Mapping[str, Any], key: str) -> int | None:
    value = data.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def required_id(data: Mapping[str, Any]) -> int:
    """Read the id every documented object carries, or reject the object."""
    value = int_field(data, "id")
    if value is None:
        msg = "The payload carries no usable id"
        raise MissingIdError(msg)
    return value


def parse_with_id[ModelT](
    data: Mapping[str, Any],
    parse_item: Callable[[Mapping[str, Any]], ModelT],
) -> ModelT | None:
    """Parse one object, dropping it when it carries no usable id."""
    try:
        return parse_item(data)
    except MissingIdError:
        _LOGGER.debug(
            "Dropped one %s payload without a usable id",
            getattr(parse_item, "__name__", repr(parse_item)),
        )
        return None


def float_field(data: Mapping[str, Any], key: str) -> float | None:
    value = data.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def bool_field(data: Mapping[str, Any], key: str) -> bool:
    return data.get(key) is True


def datetime_field(data: Mapping[str, Any], key: str) -> datetime | None:
    value = data.get(key)
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def codes_field(data: Mapping[str, Any], key: str) -> tuple[str, ...]:
    """Split one comma or newline separated code list into a tuple."""
    value = data.get(key)
    if not isinstance(value, str):
        return ()
    return tuple(code for code in (part.strip() for part in _CODE_SEPARATOR.split(value)) if code)


def custom_field(data: Mapping[str, Any]) -> dict[str, Any]:
    value = data.get("custom")
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def link_field(data: Mapping[str, Any], key: str) -> RentmanLink | None:
    """Resolve one linked field that carries a path string."""
    value = data.get(key)
    if isinstance(value, str):
        return RentmanLink(value)
    return None


def link_or_model_field[ModelT](
    data: Mapping[str, Any],
    key: str,
    parse_model: Callable[[Mapping[str, Any]], ModelT],
) -> RentmanLink | ModelT | None:
    """Resolve one linked field: a path string or an expanded object."""
    value = data.get(key)
    if isinstance(value, str):
        return RentmanLink(value)
    if isinstance(value, Mapping):
        return parse_with_id(value, parse_model)
    return None


def parse_page[ModelT](
    data: Any,
    parse_item: Callable[[Mapping[str, Any]], ModelT],
) -> RentmanPage[ModelT]:
    """Build one page of items from a collection envelope."""
    envelope = data if isinstance(data, Mapping) else {}
    raw_items = envelope.get("data")
    items: tuple[ModelT, ...] = ()
    if isinstance(raw_items, list):
        parsed = (
            parse_with_id(item, parse_item) for item in raw_items if isinstance(item, Mapping)
        )
        items = tuple(item for item in parsed if item is not None)
    return RentmanPage(
        items=items,
        item_count=int_field(envelope, "itemCount") or len(items),
        limit=int_field(envelope, "limit") or 0,
        offset=int_field(envelope, "offset") or 0,
        next_page_url=str_or_none_field(envelope, "next_page_url"),
    )


def parse_envelope_item[ModelT](
    data: Any,
    parse_item: Callable[[Mapping[str, Any]], ModelT],
) -> ModelT | None:
    """Build one item from an item envelope or a bare object."""
    if not isinstance(data, Mapping):
        return None
    payload = data.get("data", data)
    if isinstance(payload, Mapping):
        return parse_with_id(payload, parse_item)
    return None
