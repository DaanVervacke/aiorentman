"""Public API surface tests."""

import importlib
import importlib.metadata
import inspect

import pytest

import aiorentman
from aiorentman import __all__, client, exceptions, models, parsers, payloads, query
from aiorentman import _endpoints as endpoints


def test_all_entries_are_importable() -> None:
    for name in __all__:
        assert hasattr(aiorentman, name)


def test_all_matches_the_public_namespace() -> None:
    public = {
        name
        for name in dir(aiorentman)
        if not name.startswith("_") and not inspect.ismodule(getattr(aiorentman, name))
    }
    assert public == set(__all__) - {"__version__"}
    assert hasattr(aiorentman, "__version__")


def test_all_is_sorted() -> None:
    assert list(__all__) == sorted(__all__)


def test_reexports_are_identity_imports() -> None:
    for name in __all__:
        if name == "__version__":
            continue
        symbol = getattr(aiorentman, name)
        sources = (client, endpoints, exceptions, models, parsers, payloads, query)
        defining = [module for module in sources if symbol is getattr(module, name, None)]
        assert defining, f"{name} is not an identity re-export of a submodule symbol"


def test_version_falls_back_when_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raising(_name: object) -> str:
        msg = "aiorentman is not installed"
        raise importlib.metadata.PackageNotFoundError(msg)

    monkeypatch.setattr(importlib.metadata, "version", raising)
    reloaded = importlib.reload(aiorentman)
    assert reloaded.__version__ == "0.0.0"
    monkeypatch.undo()
    importlib.reload(aiorentman)
    assert aiorentman.__version__ != "0.0.0"


def test_user_agent_falls_back_when_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raising(_name: object) -> str:
        msg = "aiorentman is not installed"
        raise importlib.metadata.PackageNotFoundError(msg)

    monkeypatch.setattr(importlib.metadata, "version", raising)
    reloaded = importlib.reload(aiorentman.const)
    assert reloaded.USER_AGENT == "aiorentman/0.0.0"
    monkeypatch.undo()
    importlib.reload(aiorentman.const)
    assert aiorentman.const.USER_AGENT.startswith("aiorentman/")
