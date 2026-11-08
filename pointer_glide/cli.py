"""Command line loop for pointer-glide."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Sequence

from . import __version__
from .backends import BackendError
from .engine import Glide
from .speeds import MODES, describe, speed_for

TICK_SECONDS = 0.008


def parse_screen(text: str) -> tuple[int, int]:
    """Parse '1920x1080' into a pair of positive integers."""
    normalized = text.lower().replace("×", "x").strip()
    parts = normalized.split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"expected WxH, got {text!r}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected WxH, got {text!r}")
    if width < 2 or height < 2:
        raise argparse.ArgumentTypeError("screen size must be at least 2x2")
    return width, height


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pointer-glide",
        description="Glide the pointer straight down while the left button is held (Linux and macOS).",
    )
    parser.add_argument(
        "--mode",
        type=int,
        default=5,
        choices=list(MODES),
        help="1 is the fastest glide, 10 the slowest (default: 5)",
    )
    parser.add_argument(
        "--screen",
        type=parse_screen,
        metavar="WxH",
        help="screen size, for sessions where it cannot be detected (e.g. 1920x1080)",
    )
    parser.add_argument(
        "--always",
        action="store_true",
        help="glide on every left click without arming the guide with F8 first",
    )
    parser.add_argument("--start-armed", action="store_true", help="start with the guide already armed")
    parser.add_argument(
        "--no-hotkey",
        action="store_true",
        help="do not grab F8; the guide starts armed and Ctrl+C stops the tool",
    )
    parser.add_argument("--list-modes", action="store_true", help="print the speed table and exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _print_modes() -> None:
    print("mode  pixels per second")
    for mode, speed in describe():
        print(f"{mode:>4}  {speed:>17.1f}")


def initial_armed(args: argparse.Namespace) -> bool:
    """The guide starts active when there is no way to arm it later."""
    return bool(args.always or args.start_armed or args.no_hotkey)


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_modes:
        _print_modes()
        return 0

    if not sys.platform.startswith(("linux", "darwin")):
        print("pointer-glide: this build targets Linux and macOS", file=sys.stderr)
        return 2

    try:
        from .backends import PynputPointer, screen_size, start_toggle_hotkey

        width, height = args.screen or screen_size()
        pointer = PynputPointer()
        glide = Glide(
            width=width,
            height=height,
            speed=speed_for(args.mode),
            pointer=pointer,
            clock=time.perf_counter,
            armed=initial_armed(args),
        )
        hotkey = (
            None
            if (args.always or args.no_hotkey)
            else start_toggle_hotkey(lambda: print("guide:", "on" if glide.toggle() else "off"))
        )
    except BackendError as error:
        print(f"pointer-glide: {error}", file=sys.stderr)
        return 2

    print(f"pointer-glide {__version__}: mode {args.mode}, {glide.speed:.0f} px/s")
    if args.no_hotkey:
        print("guide: always on, no hotkey listener")
    elif hotkey:
        print("guide: F8 toggles it, Ctrl+C quits")
    else:
        print("guide: always on")
    print(f"screen: {width}x{height}, centre {glide.center}")

    try:
        while True:
            glide.tick()
            time.sleep(TICK_SECONDS)
    except KeyboardInterrupt:
        print("\npointer-glide: stopped")
    finally:
        if hotkey is not None:
            hotkey.stop()
        pointer.stop()
    return 0


def entry() -> None:  # pragma: no cover
    raise SystemExit(main())
