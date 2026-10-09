"""The generated modules match the generator output for the pinned schema."""

import pytest
from scripts.generate import generate, main


def test_generated_modules_are_current() -> None:
    for path, source in generate().items():
        assert path.read_text() == source, (
            f"{path.name} is stale: run uv run python -m scripts.generate"
        )


def test_check_mode_reports_a_stale_module(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    generated = generate()
    first = next(iter(generated))
    stale = dict(generated)
    stale[first] = generated[first] + "\n"
    monkeypatch.setattr("scripts.generate.generate", lambda: stale)
    assert main(["--check"]) == 1
    assert f"{first.name} is stale" in capsys.readouterr().err
