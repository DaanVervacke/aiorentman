"""Validate the write surface with one scripted round-trip against the live API.

Creates one scratch task with one scratch subtask, updates the task with a
partial body, deletes both, and probes one invalid body to check the 400
mapping. Records the create and update responses into captures/ for
redaction. Reads the API token the same way scripts/capture_data.py does.
This script mutates the account it runs against and never runs as part of
the check gate. Run:

    uv run python -m scripts.validate_writes
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from aiorentman import (
    RentmanClient,
    RentmanNotFoundError,
    RentmanValidationError,
    SubtaskPayload,
    TaskPayload,
)

from .capture_data import load_token

CAPTURES = Path(__file__).resolve().parent.parent / "captures"


def record(name: str, payload: dict[str, Any] | None) -> None:
    """Write one raw response body into captures/ for later redaction."""
    if payload is None:
        print(f"nothing recorded for {name}, the response body was empty")
        return
    CAPTURES.mkdir(exist_ok=True)
    (CAPTURES / f"{name}.json").write_text(json.dumps(payload, indent=2))
    print(f"recorded {name}.json")


async def main() -> None:
    """Run the round-trip and report every observed behavior."""
    client = RentmanClient(token=load_token())
    async with client:
        task = await client.async_create_task(
            TaskPayload(color="#ff0000", name="aiorentman validation", details="scratch")
        )
        assert task is not None, "creating a task returned no model"
        record("write_task_create", task.raw)
        try:
            subtask = await client.async_create_subtask_of_task(
                task.id, SubtaskPayload(title="aiorentman scratch subtask")
            )
            assert subtask is not None, "creating a subtask returned no model"
            record("write_subtask_create", subtask.raw)

            updated = await client.async_update_task(task.id, TaskPayload(color="#00ff00"))
            assert updated is not None, "updating a task returned no model"
            record("write_task_update", updated.raw)
            assert updated.name == task.name, "the partial update dropped the task name"
            assert updated.details == task.details, "the partial update dropped the task details"
            print("the partial update changed only the color")

            await client.async_delete_subtask(subtask.id)
            await client.async_delete_task(task.id)
            try:
                await client.async_get_task(task.id)
            except RentmanNotFoundError:
                print("the deleted task is gone")
            else:
                print("WARNING: the deleted task is still readable")

            try:
                probe = await client.async_create_task(
                    TaskPayload(color="#ff0000", recurhoe="not-a-unit")
                )
            except RentmanValidationError as exc:
                print(f"an invalid body was rejected: {exc}")
            else:
                print("WARNING: the invalid recurrence unit was accepted")
                if probe is not None:
                    await client.async_delete_task(probe.id)
        finally:
            try:
                await client.async_delete_task(task.id)
            except RentmanNotFoundError:
                print("the scratch task was already removed")


if __name__ == "__main__":
    asyncio.run(main())
