"""Operating system glue: pointer via pynput, screen size via tkinter.

pynput is imported lazily so that the engine and its tests stay importable on
machines without a desktop session.
"""

from __future__ import annotations

from typing import Callable


class BackendError(RuntimeError):
    pass


def screen_size() -> tuple[int, int]:
    """Ask the window system for the primary screen size.

    tkinter ships with CPython and knows the display on X11 and macOS. On a
    headless machine it fails; the CLI then asks for ``--screen WxH``.
    """
    try:
        import tkinter
    except ImportError as error:  # pragma: no cover - depends on the interpreter build
        raise BackendError("tkinter is not available; pass --screen WxH") from error

    try:
        root = tkinter.Tk()
    except Exception as error:  # noqa: BLE001 - any Tk failure means "no display"
        raise BackendError("cannot open a display; pass --screen WxH") from error

    try:
        root.withdraw()
        return int(root.winfo_screenwidth()), int(root.winfo_screenheight())
    finally:
        root.destroy()


def _require_pynput():
    try:
        import pynput  # noqa: F401
    except ImportError as error:
        raise BackendError(
            "pynput is required at runtime: python -m pip install 'pointer-glide[runtime]'"
        ) from error


class PynputPointer:
    """Pointer backed by pynput's mouse controller and a background listener."""

    def __init__(self) -> None:
        _require_pynput()
        from pynput import mouse

        self._mouse = mouse
        self._controller = mouse.Controller()
        self._pressed = False
        self._listener = mouse.Listener(on_click=self._on_click)
        self._listener.daemon = True
        self._listener.start()

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:  # noqa: ANN001
        if button == self._mouse.Button.left:
            self._pressed = pressed

    def position(self) -> tuple[int, int]:
        x, y = self._controller.position
        return int(x), int(y)

    def move_to(self, x: int, y: int) -> None:
        self._controller.position = (x, y)

    def pressed(self) -> bool:
        return self._pressed

    def stop(self) -> None:
        self._listener.stop()


def start_toggle_hotkey(callback: Callable[[], None]):
    """Start a background F8 listener. Returns the listener so it can be stopped."""
    _require_pynput()
    from pynput import keyboard

    listener = keyboard.GlobalHotKeys({"<f8>": callback})
    listener.daemon = True
    listener.start()
    return listener
