"""Argument shapes and the endpoint row type shared by the endpoint catalog."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .payloads import to_wire
from .query import Query


@dataclass(frozen=True, slots=True)
class CollectionArgs:
    """One top-level collection page with its query."""

    query: Query | None = None


@dataclass(frozen=True, slots=True)
class ItemArgs:
    """One item, addressed by its numeric id."""

    item_id: int

    def __post_init__(self) -> None:
        if self.item_id < 1:
            msg = "item_id must be a positive id"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ParentCollectionArgs:
    """One linked collection page: the parent id and its query."""

    parent_id: int
    query: Query | None = None

    def __post_init__(self) -> None:
        if self.parent_id < 1:
            msg = "parent_id must be a positive id"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class CreateArgs:
    """One create body for a standalone collection."""

    payload: object


@dataclass(frozen=True, slots=True)
class LinkedCreateArgs:
    """One create body attached to one parent id."""

    parent_id: int
    payload: object

    def __post_init__(self) -> None:
        if self.parent_id < 1:
            msg = "parent_id must be a positive id"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class UpdateArgs:
    """One update body for one item id."""

    item_id: int
    payload: object

    def __post_init__(self) -> None:
        if self.item_id < 1:
            msg = "item_id must be a positive id"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class DeleteArgs:
    """One item to delete, addressed by its numeric id."""

    item_id: int

    def __post_init__(self) -> None:
        if self.item_id < 1:
            msg = "item_id must be a positive id"
            raise ValueError(msg)


def no_body(_args: Any) -> dict[str, Any] | None:
    return None


def create_body(args: CreateArgs) -> dict[str, Any] | None:
    return to_wire(args.payload)


def linked_create_body(args: LinkedCreateArgs) -> dict[str, Any] | None:
    return to_wire(args.payload)


def update_body(args: UpdateArgs) -> dict[str, Any] | None:
    return to_wire(args.payload)


@dataclass(frozen=True, slots=True)
class Endpoint[ArgsT, ModelT]:
    """One wire contract: method, path, params, body, the parse step, and schemas."""

    name: str
    method: str
    path: Callable[[ArgsT], str]
    parse: Callable[[Any, ArgsT], ModelT]
    params: Callable[[ArgsT], dict[str, str]]
    response_schema: str | None
    body: Callable[[ArgsT], dict[str, Any] | None] = no_body
    request_schema: str | None = None


def collection_params(args: CollectionArgs) -> dict[str, str]:
    return {} if args.query is None else args.query.params()


def linked_collection_params(args: ParentCollectionArgs) -> dict[str, str]:
    return {} if args.query is None else args.query.params()
