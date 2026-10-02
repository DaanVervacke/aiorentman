"""Payload tests: wire rendering, aliases, and immutability."""

import dataclasses
from datetime import UTC, datetime

import pytest

from aiorentman.models import RentmanLink
from aiorentman.payloads import (
    ProjectRequestPayload,
    StockMovementPayload,
    TaskPayload,
    to_wire,
)


def test_to_wire_leaves_unset_fields_out() -> None:
    assert to_wire(TaskPayload(color="#ffffff")) == {"color": "#ffffff"}


def test_to_wire_renders_datetimes_links_and_custom() -> None:
    deadline = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
    payload = TaskPayload(
        color="#ffffff",
        name="sample",
        deadline=deadline,
        status=RentmanLink(path="/taskstatuses/3"),
        custom={"custom_1": "value"},
    )
    assert to_wire(payload) == {
        "color": "#ffffff",
        "name": "sample",
        "deadline": "2026-10-02T12:00:00+00:00",
        "status": "/taskstatuses/3",
        "custom": {"custom_1": "value"},
    }


def test_to_wire_maps_keyword_aliases_to_wire_names() -> None:
    payload = ProjectRequestPayload(
        planperiod_start=datetime(2026, 10, 2, 9, tzinfo=UTC),
        planperiod_end=datetime(2026, 10, 3, 17, tzinfo=UTC),
        in_=datetime(2026, 10, 2, 9, tzinfo=UTC),
        out_=datetime(2026, 10, 3, 17, tzinfo=UTC),
    )
    assert to_wire(payload) == {
        "planperiod_start": "2026-10-02T09:00:00+00:00",
        "planperiod_end": "2026-10-03T17:00:00+00:00",
        "in": "2026-10-02T09:00:00+00:00",
        "out": "2026-10-03T17:00:00+00:00",
    }


def test_to_wire_keeps_set_optional_fields() -> None:
    payload = StockMovementPayload(
        date=datetime(2026, 10, 2, 12, tzinfo=UTC),
        amount=3,
        stock_location=RentmanLink(path="/stocklocations/2"),
    )
    assert to_wire(payload) == {
        "date": "2026-10-02T12:00:00+00:00",
        "amount": 3,
        "stock_location": "/stocklocations/2",
    }


def test_payloads_are_frozen() -> None:
    payload = TaskPayload(color="#ffffff")
    with pytest.raises(dataclasses.FrozenInstanceError):
        payload.name = "changed"  # type: ignore[misc]


def test_payloads_are_slotted() -> None:
    payload = TaskPayload(color="#ffffff")
    with pytest.raises(AttributeError):
        payload.unexpected_attribute = "nope"  # type: ignore[attr-defined]
