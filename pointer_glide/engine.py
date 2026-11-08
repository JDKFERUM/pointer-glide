"""Platform independent glide logic.

The engine never imports pynput: it talks to a :class:`Pointer` and a clock.
That keeps the interesting part testable on any machine, including headless CI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol


class Pointer(Protocol):
    def position(self) -> tuple[int, int]: ...

    def move_to(self, x: int, y: int) -> None: ...

    def pressed(self) -> bool: ...


@dataclass
class Glide:
    """Pins the pointer to the screen centre and moves it straight down.

    The guide is inactive until :attr:`armed` is true. While armed and the
    primary button is held, the pointer is moved to the centre and then down at
    ``speed`` pixels per second.
    """

    width: int
    height: int
    speed: float
    pointer: Pointer
    clock: Callable[[], float]
    armed: bool = False

    _gliding: bool = False
    _last: Optional[float] = None

    @property
    def center(self) -> tuple[int, int]:
        return self.width // 2, self.height // 2

    def toggle(self) -> bool:
        self.armed = not self.armed
        self._gliding = False
        self._last = None
        return self.armed

    def tick(self) -> None:
        now = self.clock()
        if not (self.armed and self.pointer.pressed()):
            self._gliding = False
            self._last = None
            return

        if not self._gliding:
            self._gliding = True
            self._last = now
            self.pointer.move_to(*self.center)
            return

        assert self._last is not None
        elapsed = max(now - self._last, 0.0)
        self._last = now

        center_x, _ = self.center
        x, y = self.pointer.position()
        next_y = min(y + self.speed * elapsed, self.height - 1)
        if (center_x, int(next_y)) != (x, y):
            self.pointer.move_to(center_x, int(next_y))
