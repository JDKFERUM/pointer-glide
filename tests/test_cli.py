from __future__ import annotations

import pytest

from pointer_glide.cli import _build_parser, initial_armed, main, parse_screen
from pointer_glide.speeds import describe, speed_for


def test_mode_one_is_fastest() -> None:
    speeds = [speed_for(mode) for mode in range(1, 11)]
    assert speeds == sorted(speeds, reverse=True)
    assert speed_for(1) == 600.0
    assert speed_for(10) == 60.0


@pytest.mark.parametrize("mode", [0, 11, -3])
def test_modes_are_validated(mode: int) -> None:
    with pytest.raises(ValueError):
        speed_for(mode)


def test_describe_covers_every_mode() -> None:
    assert [mode for mode, _ in describe()] == list(range(1, 11))


def test_list_modes_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list-modes"]) == 0
    out = capsys.readouterr().out
    assert "pixels per second" in out
    assert "600.0" in out


def test_parse_screen_accepts_common_forms() -> None:
    assert parse_screen("1920x1080") == (1920, 1080)
    assert parse_screen("2560X1440") == (2560, 1440)


def test_no_hotkey_flag_is_parsed() -> None:
    args = _build_parser().parse_args(["--no-hotkey"])
    assert args.no_hotkey is True
    assert initial_armed(args) is True


def test_default_run_is_not_armed() -> None:
    args = _build_parser().parse_args([])
    assert initial_armed(args) is False


@pytest.mark.parametrize("value", ["1920", "axb", "1920x0", "-5x100"])
def test_parse_screen_rejects_garbage(value: str) -> None:
    import argparse

    with pytest.raises(argparse.ArgumentTypeError):
        parse_screen(value)
