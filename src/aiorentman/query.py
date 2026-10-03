"""The typed query object for collection requests."""

from dataclasses import dataclass
from enum import StrEnum

from .const import MAX_PAGE_LIMIT

type FilterValue = str | int | float | bool

_RESERVED_PARAM_NAMES = frozenset({"fields", "sort", "expand", "limit", "offset"})
_GENERATED_FIELDS = frozenset({"qrcodes", "tags", "qrcodes_of_serial_numbers"})


class FilterOperator(StrEnum):
    """The relational operators the Rentman API accepts in filter keys."""

    EQUALS = ""
    NOT_EQUALS = "neq"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUALS = "lte"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUALS = "gte"
    IS_NULL = "isnull"


def _render_value(value: FilterValue) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


@dataclass(frozen=True, slots=True)
class Filter:
    """One field filter: a field, an operator, and the value to compare with."""

    field: str
    operator: FilterOperator = FilterOperator.EQUALS
    value: FilterValue = ""

    def __post_init__(self) -> None:
        if not self.field:
            msg = "filter field must not be empty"
            raise ValueError(msg)
        if self.field in _RESERVED_PARAM_NAMES:
            msg = f"filter field {self.field} collides with a reserved query parameter"
            raise ValueError(msg)
        if self.field in _GENERATED_FIELDS:
            msg = f"filter field {self.field} is generated and cannot be filtered"
            raise ValueError(msg)

    def param(self) -> tuple[str, str]:
        """Render the filter as one query parameter key and value."""
        value = _render_value(self.value)
        if self.operator is FilterOperator.EQUALS:
            return self.field, value
        return f"{self.field}[{self.operator.value}]", value


def eq(field: str, value: FilterValue) -> Filter:
    """Filter on field equal to value."""
    return Filter(field=field, value=value)


def neq(field: str, value: FilterValue) -> Filter:
    """Filter on field not equal to value."""
    return Filter(field=field, operator=FilterOperator.NOT_EQUALS, value=value)


def lt(field: str, value: FilterValue) -> Filter:
    """Filter on field less than value."""
    return Filter(field=field, operator=FilterOperator.LESS_THAN, value=value)


def lte(field: str, value: FilterValue) -> Filter:
    """Filter on field less than or equal to value."""
    return Filter(field=field, operator=FilterOperator.LESS_THAN_OR_EQUALS, value=value)


def gt(field: str, value: FilterValue) -> Filter:
    """Filter on field greater than value."""
    return Filter(field=field, operator=FilterOperator.GREATER_THAN, value=value)


def gte(field: str, value: FilterValue) -> Filter:
    """Filter on field greater than or equal to value."""
    return Filter(field=field, operator=FilterOperator.GREATER_THAN_OR_EQUALS, value=value)


def is_null(field: str, *, value: bool = True) -> Filter:
    """Filter on field being null or, with value False, not null."""
    return Filter(field=field, operator=FilterOperator.IS_NULL, value=value)


@dataclass(frozen=True, slots=True)
class Sort:
    """One sort field with its direction."""

    field: str
    ascending: bool = True

    def __post_init__(self) -> None:
        if not self.field:
            msg = "sort field must not be empty"
            raise ValueError(msg)
        if self.field in _GENERATED_FIELDS:
            msg = f"sort field {self.field} is generated and cannot be sorted"
            raise ValueError(msg)

    def param(self) -> str:
        """Render the sort field with its direction prefix."""
        return f"+{self.field}" if self.ascending else f"-{self.field}"


@dataclass(frozen=True, slots=True)
class Query:
    """Fields, sorting, filters, expansion, and paging for one collection request.

    Field, sort, and expand names are the schema property names of the
    resource being requested, including ``custom_<number>`` names. Filters
    reject the reserved query parameter names, and filters and sorts reject
    the generated fields, which the API can neither filter nor sort on.
    """

    fields: tuple[str, ...] = ()
    sort: tuple[Sort, ...] = ()
    expand: tuple[str, ...] = ()
    filters: tuple[Filter, ...] = ()
    limit: int | None = None
    offset: int | None = None

    def __post_init__(self) -> None:
        for name in self.fields:
            if not name:
                msg = "field names must not be empty"
                raise ValueError(msg)
        for name in self.expand:
            if not name:
                msg = "expand names must not be empty"
                raise ValueError(msg)
        if self.limit is not None and not 1 <= self.limit <= MAX_PAGE_LIMIT:
            msg = f"limit must be between 1 and {MAX_PAGE_LIMIT}"
            raise ValueError(msg)
        if self.offset is not None and self.offset < 0:
            msg = "offset must not be negative"
            raise ValueError(msg)

    def params(self) -> dict[str, str]:
        """Render the query as the query parameters the API expects."""
        params: dict[str, str] = {}
        if self.fields:
            params["fields"] = ",".join(self.fields)
        if self.sort:
            params["sort"] = ",".join(item.param() for item in self.sort)
        if self.expand:
            params["expand"] = ",".join(self.expand)
        for item in self.filters:
            key, value = item.param()
            params[key] = value
        if self.limit is not None:
            params["limit"] = str(self.limit)
        if self.offset is not None:
            params["offset"] = str(self.offset)
        return params
