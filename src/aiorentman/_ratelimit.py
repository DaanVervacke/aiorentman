"""Request pacing: a spaced send rate and a concurrency cap."""

import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


class RequestPacer:
    """Paces requests against the documented Rentman limits.

    Rentman allows 10 requests per second and at most 20 concurrent
    requests. Every request holds one concurrency slot and waits for its
    spaced send turn. Passing a None rate disables the spacing while the
    concurrency cap stays active.
    """

    def __init__(self, *, requests_per_second: float | None, max_concurrent: int) -> None:
        """Create a pacer from a rate and a concurrency cap."""
        if requests_per_second is not None and requests_per_second <= 0:
            msg = "requests_per_second must be positive or None to disable pacing"
            raise ValueError(msg)
        if max_concurrent < 1:
            msg = "max_concurrent must be at least 1"
            raise ValueError(msg)
        self._max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._interval = 0.0 if requests_per_second is None else 1.0 / requests_per_second
        self._lock = asyncio.Lock()
        self._next_slot = 0.0

    @asynccontextmanager
    async def request_slot(self) -> AsyncIterator[None]:
        """Hold one concurrency slot and wait for the next send turn."""
        async with self._semaphore:
            await self._wait_for_turn()
            yield

    async def _wait_for_turn(self) -> None:
        if self._interval == 0.0:
            return
        async with self._lock:
            now = time.monotonic()
            wait = max(0.0, self._next_slot - now)
            self._next_slot = max(now, self._next_slot) + self._interval
        if wait > 0:
            await asyncio.sleep(wait)
