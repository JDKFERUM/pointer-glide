"""Full sessions against a fake pointer, driven like the CLI loop drives it."""

from __future__ import annotations

from pointer_glide.engine import Glide
from tests.test_engine import FakeClock, FakePointer

TICK = 0.05
SPEED = 240.0


def make() -> tuple[Glide, FakePointer, FakeClock]:
    pointer, clock = FakePointer(x=40, y=1200), FakeClock()
    glide = Glide(width=1920, height=1200, speed=SPEED, pointer=pointer, clock=clock, armed=True)
    return glide, pointer, clock


def run(glide: Glide, clock: FakeClock, ticks: int) -> None:
    for _ in range(ticks):
        glide.tick()
        clock.advance(TICK)


def test_session_lands_on_the_centre_column() -> None:
    glide, pointer, clock = make()
    pointer.is_pressed = True
    run(glide, clock, ticks=20)

    assert pointer.x == 960
    assert pointer.y == 600 + SPEED * TICK * 19


def test_session_stays_inside_the_screen() -> None:
    glide, pointer, clock = make()
    pointer.is_pressed = True
    run(glide, clock, ticks=120)

    ys = [y for _, y in pointer.moves] + [pointer.y]
    assert min(ys) >= 0
    assert max(ys) <= 1199


def test_three_presses_three_centres() -> None:
    glide, pointer, clock = make()

    for _ in range(3):
        pointer.is_pressed = True
        glide.tick()
        assert (pointer.x, pointer.y) == (960, 600)

        clock.advance(TICK)
        glide.tick()
        assert pointer.y == 600 + SPEED * TICK

        pointer.is_pressed = False
        glide.tick()
