"""Endpoint catalog tests: args validation and catalog integrity."""

import pytest

from aiorentman import _endpoints as endpoints_module
from aiorentman._endpoints import (
    CATALOG,
    CollectionArgs,
    Endpoint,
    ItemArgs,
    ParentCollectionArgs,
    _collection_params,
)
from aiorentman.const import BASE_URL
from aiorentman.query import Query

SAMPLES = (
    CollectionArgs(query=None),
    ItemArgs(item_id=1),
    ParentCollectionArgs(parent_id=1),
)


def test_item_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="item_id must be a positive id"):
        ItemArgs(item_id=0)
    with pytest.raises(ValueError, match="item_id must be a positive id"):
        ItemArgs(item_id=-5)


def test_parent_collection_args_rejects_non_positive_ids() -> None:
    with pytest.raises(ValueError, match="parent_id must be a positive id"):
        ParentCollectionArgs(parent_id=0)


def test_collection_params_render_the_query() -> None:
    query = Query(fields=("name",), limit=10)
    assert _collection_params(CollectionArgs(query=query)) == {
        "fields": "name",
        "limit": "10",
    }


def test_collection_params_default_to_nothing() -> None:
    assert _collection_params(CollectionArgs(query=None)) == {}


def test_every_catalog_row_is_a_get() -> None:
    assert {endpoint.method for endpoint in CATALOG} == {"GET"}


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
