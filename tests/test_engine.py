from __future__ import annotations

from typing import Iterator

import pytest

from pointer_glide.engine import Glide


class FakePointer:
    def __init__(self, x: int = 0, y: int = 0, pressed: bool = False) -> None:
        self.x = x
        self.y = y
        self.is_pressed = pressed
        self.moves: list[tuple[int, int]] = []

    def position(self) -> tuple[int, int]:
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.moves.append((x, y))

    def pressed(self) -> bool:
        return self.is_pressed


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def pointer() -> FakePointer:
    return FakePointer()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def glide(pointer: FakePointer, clock: FakeClock) -> Glide:
    return Glide(width=2560, height=1440, speed=320.0, pointer=pointer, clock=clock, armed=True)


def test_disarmed_glide_leaves_pointer_alone(glide: Glide, pointer: FakePointer) -> None:
    glide.armed = False
    pointer.is_pressed = True
    glide.tick()
    assert pointer.moves == []


def test_first_press_moves_to_the_centre(glide: Glide, pointer: FakePointer) -> None:
    pointer.is_pressed = True
    glide.tick()
    assert (pointer.x, pointer.y) == (1280, 720)


def test_held_button_glides_down_at_speed(glide: Glide, pointer: FakePointer, clock: FakeClock) -> None:
    pointer.is_pressed = True
    glide.tick()
    clock.advance(0.25)
    glide.tick()
    assert pointer.y == 720 + 80
    assert pointer.x == 1280


def test_sideways_motion_is_undone(glide: Glide, pointer: FakePointer, clock: FakeClock) -> None:
    pointer.is_pressed = True
    glide.tick()
    pointer.x = 3
    clock.advance(0.1)
    glide.tick()
    assert pointer.x == 1280


def test_bottom_edge_is_a_hard_stop(glide: Glide, pointer: FakePointer, clock: FakeClock) -> None:
    pointer.is_pressed = True
    glide.tick()
    clock.advance(60.0)
    glide.tick()
    assert pointer.y == 1439


def test_release_stops_the_glide(glide: Glide, pointer: FakePointer, clock: FakeClock) -> None:
    pointer.is_pressed = True
    glide.tick()
    clock.advance(0.1)
    glide.tick()
    frozen = pointer.y

    pointer.is_pressed = False
    clock.advance(0.5)
    glide.tick()
    assert pointer.y == frozen


def test_press_again_returns_to_the_centre(glide: Glide, pointer: FakePointer, clock: FakeClock) -> None:
    pointer.is_pressed = True
    glide.tick()
    clock.advance(1.0)
    glide.tick()
    assert pointer.y > 720

    pointer.is_pressed = False
    glide.tick()
    pointer.is_pressed = True
    clock.advance(0.2)
    glide.tick()
    assert (pointer.x, pointer.y) == (1280, 720)


def test_toggle_turns_the_guide_off(glide: Glide, pointer: FakePointer) -> None:
    assert glide.toggle() is False
    pointer.is_pressed = True
    glide.tick()
    assert pointer.moves == []


def test_time_never_runs_backwards(glide: Glide, pointer: FakePointer, clock: FakeClock) -> None:
    pointer.is_pressed = True
    glide.tick()
    clock.now -= 5
    glide.tick()
    assert pointer.y == 720
