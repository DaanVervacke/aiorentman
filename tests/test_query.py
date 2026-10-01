"""Query DSL tests: rendering, operators, and validation."""

import pytest

from aiorentman import Query, Sort, eq, gt, gte, is_null, lt, lte, neq
from aiorentman.query import Filter, FilterOperator


def test_empty_query_renders_no_params() -> None:
    assert Query().params() == {}


def test_full_query_renders_every_param() -> None:
    query = Query(
        fields=("name", "code"),
        sort=(Sort("name"), Sort("code", ascending=False)),
        expand=("equipment", "equipment.folder"),
        filters=(eq("code", "AUD-001"), lt("price", 200), is_null("image", value=False)),
        limit=10,
        offset=20,
    )
    assert query.params() == {
        "fields": "name,code",
        "sort": "+name,-code",
        "expand": "equipment,equipment.folder",
        "code": "AUD-001",
        "price[lt]": "200",
        "image[isnull]": "false",
        "limit": "10",
        "offset": "20",
    }


def test_operators_render_their_keys() -> None:
    filters = (
        neq("type", "0"),
        lte("price", 10),
        gt("price", 5),
        gte("price", 7),
        is_null("folder"),
    )
    rendered = dict(item.param() for item in filters)
    assert rendered == {
        "type[neq]": "0",
        "price[lte]": "10",
        "price[gt]": "5",
        "price[gte]": "7",
        "folder[isnull]": "true",
    }


def test_filter_values_render_as_strings() -> None:
    assert eq("active", True).param() == ("active", "true")
    assert eq("active", False).param() == ("active", "false")
    assert eq("amount", 3).param() == ("amount", "3")
    assert eq("price", 12.5).param() == ("price", "12.5")


def test_limit_bounds_are_enforced() -> None:
    with pytest.raises(ValueError, match="limit must be between"):
        Query(limit=0)
    with pytest.raises(ValueError, match="limit must be between"):
        Query(limit=1501)


def test_offset_must_not_be_negative() -> None:
    with pytest.raises(ValueError, match="offset must not be negative"):
        Query(offset=-1)


def test_names_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="field names"):
        Query(fields=("",))
    with pytest.raises(ValueError, match="expand names"):
        Query(expand=("",))
    with pytest.raises(ValueError, match="sort field"):
        Query(sort=(Sort(""),))
    with pytest.raises(ValueError, match="filter field"):
        Filter(field="")
    with pytest.raises(ValueError, match="filter field"):
        eq("", "value")


def test_operator_enum_values_match_the_api() -> None:
    assert FilterOperator.NOT_EQUALS.value == "neq"
    assert FilterOperator.LESS_THAN.value == "lt"
    assert FilterOperator.LESS_THAN_OR_EQUALS.value == "lte"
    assert FilterOperator.GREATER_THAN.value == "gt"
    assert FilterOperator.GREATER_THAN_OR_EQUALS.value == "gte"
    assert FilterOperator.IS_NULL.value == "isnull"
