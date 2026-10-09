"""The generated modules match the generator output for the pinned schema."""

from pathlib import Path

import pytest
from scripts.generate import generate, main


@pytest.fixture(scope="module")
def generated() -> dict[Path, str]:
    return generate()


def test_generated_modules_are_current(generated: dict[Path, str]) -> None:
    for path, source in generated.items():
        assert path.read_text() == source, (
            f"{path.name} is stale: run uv run python -m scripts.generate"
        )


def test_check_mode_reports_a_stale_module(
    generated: dict[Path, str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    first = next(iter(generated))
    stale = {**generated, first: generated[first] + "\n"}
    monkeypatch.setattr("scripts.generate.generate", lambda: stale)
    assert main(["--check"]) == 1
    assert f"{first.name} is stale" in capsys.readouterr().err
