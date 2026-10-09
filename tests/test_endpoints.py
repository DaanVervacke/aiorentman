"""Endpoint catalog tests: args validation and catalog integrity."""

import pytest

from aiorentman import _endpoints as endpoints_module
from aiorentman._endpoint_types import query_params
from aiorentman._endpoints import (
    CATALOG,
    CollectionArgs,
    CreateArgs,
    DeleteArgs,
    Endpoint,
    ItemArgs,
    LinkedCreateArgs,
    ParentCollectionArgs,
    UpdateArgs,
)
from aiorentman.const import BASE_URL
from aiorentman.payloads import TaskPayload
from aiorentman.query import Query

SAMPLES = (
    CollectionArgs(query=None),
    ItemArgs(item_id=1),
    ParentCollectionArgs(parent_id=1),
    CreateArgs(payload=TaskPayload(color="#ffffff")),
    LinkedCreateArgs(parent_id=1, payload=TaskPayload(color="#ffffff")),
    UpdateArgs(item_id=1, payload=TaskPayload(color="#ffffff")),
    DeleteArgs(item_id=1),
)


def test_item_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="item_id must be a positive id"):
        ItemArgs(item_id=0)
    with pytest.raises(ValueError, match="item_id must be a positive id"):
        ItemArgs(item_id=-5)


def test_parent_collection_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="parent_id must be a positive id"):
        ParentCollectionArgs(parent_id=0)


def test_linked_create_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="parent_id must be a positive id"):
        LinkedCreateArgs(parent_id=0, payload=TaskPayload(color="#ffffff"))


def test_update_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="item_id must be a positive id"):
        UpdateArgs(item_id=0, payload=TaskPayload(color="#ffffff"))


def test_delete_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="item_id must be a positive id"):
        DeleteArgs(item_id=0)


def test_query_params_render_the_query() -> None:
    query = Query(fields=("name",), limit=10)
    assert query_params(CollectionArgs(query=query)) == {
        "fields": "name",
        "limit": "10",
    }


def test_query_params_default_to_nothing() -> None:
    assert query_params(CollectionArgs(query=None)) == {}


def test_every_catalog_row_uses_a_documented_method() -> None:
    assert {endpoint.method for endpoint in CATALOG} <= {"GET", "POST", "PUT", "DELETE"}


def test_write_rows_carry_a_request_schema_and_reads_do_not() -> None:
    for endpoint in CATALOG:
        if endpoint.method == "GET":
            assert endpoint.request_schema is None, endpoint.name
            assert endpoint.response_schema is not None, endpoint.name
        elif endpoint.method == "DELETE":
            assert endpoint.request_schema is None, endpoint.name
            assert endpoint.response_schema is None, endpoint.name
        else:
            assert endpoint.request_schema is not None, endpoint.name
            assert endpoint.response_schema is not None, endpoint.name


def test_write_rows_render_a_body_and_reads_do_not() -> None:
    payload = TaskPayload(color="#ffffff")
    for endpoint in CATALOG:
        if endpoint.method in {"GET", "DELETE"}:
            assert endpoint.body(None) is None, endpoint.name
        elif endpoint.name.startswith("create_") and "_of_" in endpoint.name:
            linked = LinkedCreateArgs(parent_id=1, payload=payload)
            assert endpoint.body(linked) == {"color": "#ffffff"}, endpoint.name
        elif endpoint.name.startswith("create_"):
            assert endpoint.body(CreateArgs(payload=payload)) == {"color": "#ffffff"}, endpoint.name
        else:
            update = UpdateArgs(item_id=1, payload=payload)
            assert endpoint.body(update) == {"color": "#ffffff"}, endpoint.name


def test_catalog_names_are_unique() -> None:
    names = [endpoint.name for endpoint in CATALOG]
    assert len(names) == len(set(names))


def test_catalog_covers_every_endpoint_module_constant() -> None:
    catalog_names = {endpoint.name for endpoint in CATALOG}
    declared = {
        value.name for value in vars(endpoints_module).values() if isinstance(value, Endpoint)
    }
    assert catalog_names == declared


def test_catalog_paths_build_without_placeholders() -> None:
    for endpoint in CATALOG:
        path = sample_path(endpoint)
        assert path.startswith("/")
        assert "{" not in path
        assert " " not in path


def test_base_url_is_the_rentman_api() -> None:
    assert BASE_URL == "https://api.rentman.net"


def sample_path(endpoint: Endpoint[object, object]) -> str:
    """Build one path with whichever sample args the endpoint accepts."""
    for sample in SAMPLES:
        try:
            path = endpoint.path(sample)
        except AttributeError:
            continue
        else:
            return path
    msg = f"no sample args build a path for {endpoint.name}"
    raise AssertionError(msg)
