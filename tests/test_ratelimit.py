"""Rate limiter tests: send spacing, concurrency cap, and validation."""

import asyncio
import time

import pytest

from aiorentman._ratelimit import RequestPacer


async def test_pacer_spaces_sends() -> None:
    pacer = RequestPacer(requests_per_second=50.0, max_concurrent=10)

    async def one_request() -> None:
        async with pacer.request_slot():
            pass

    started = time.monotonic()
    for _ in range(3):
        await one_request()
    elapsed = time.monotonic() - started
    assert elapsed >= 0.03


async def test_pacer_runs_concurrent_requests_without_delay_when_disabled() -> None:
    pacer = RequestPacer(requests_per_second=None, max_concurrent=10)
    started = time.monotonic()

    async def one_request() -> None:
        async with pacer.request_slot():
            await asyncio.sleep(0)

    await asyncio.gather(*(one_request() for _ in range(3)))
    assert time.monotonic() - started < 1.0


async def test_pacer_caps_concurrency() -> None:
    pacer = RequestPacer(requests_per_second=None, max_concurrent=1)
    active = 0
    peak = 0

    async def one_request() -> None:
        nonlocal active, peak
        async with pacer.request_slot():
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.01)
            active -= 1

    await asyncio.gather(*(one_request() for _ in range(3)))
    assert peak == 1


async def test_disabled_rate_still_caps_concurrency() -> None:
    pacer = RequestPacer(requests_per_second=None, max_concurrent=2)
    active = 0
    peak = 0

    async def one_request() -> None:
        nonlocal active, peak
        async with pacer.request_slot():
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.01)
            active -= 1

    await asyncio.gather(*(one_request() for _ in range(4)))
    assert peak == 2


def test_pacer_rejects_bad_configuration() -> None:
    with pytest.raises(ValueError, match="requests_per_second"):
        RequestPacer(requests_per_second=0.0, max_concurrent=1)
    with pytest.raises(ValueError, match="requests_per_second"):
        RequestPacer(requests_per_second=-1.0, max_concurrent=1)
    with pytest.raises(ValueError, match="max_concurrent"):
        RequestPacer(requests_per_second=10.0, max_concurrent=0)
