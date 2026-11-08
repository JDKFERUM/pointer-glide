# pointer-glide

A small accessibility helper for Linux and macOS: while the guide is armed, a
left click moves the pointer to the centre of the screen and glides it straight
down at one of ten speeds.

It is for the moments when keeping the pointer steady is the hard part: nudging
a slider, selecting a column of text, drawing a straight line, keeping the
cursor on the same spot while a key is held.

The tool never clicks for you. It only moves the pointer, and only while the
left button is held.

## Behaviour

1. `F8` arms or disarms the guide.
2. While armed, pressing the left button moves the pointer to the centre of the
   primary screen.
3. Holding the button keeps `x` at the centre and moves `y` down at the chosen
   speed until the bottom edge.
4. Releasing the button stops the glide; the pointer stays where it is.
5. Every new press starts again from the centre.

Run with `--always` if you really want it on every click without arming first.

## Speeds

| Mode | Pixels per second |
| ---: | ---: |
| 1 | 600 |
| 2 | 300 |
| 3 | 200 |
| 5 | 120 |
| 7 | 85.7 |
| 10 | 60 |

Mode 1 is the fastest, mode 10 the slowest; the speed is `600 / mode`.

## Install

```bash
python -m pip install ".[runtime]"
```

`pynput` is only needed at runtime; the engine and the tests work without it.
Run from a checkout without installing anything:

```bash
python -m pointer_glide --mode 4
```

## Usage

```bash
$ python -m pointer_glide --mode 2
pointer-glide 0.1.0: mode 2, 300 px/s
guide: F8 toggles it, Ctrl+C quits
screen: 2560x1440, centre (1280, 720)
```

| Option | Meaning |
| --- | --- |
| `--mode N` | glide speed, `1` (fastest) to `10` (slowest), default `5` |
| `--screen WxH` | set the screen size manually when it cannot be detected |
| `--start-armed` | start with the guide armed |
| `--no-hotkey` | do not grab F8: the guide starts armed and runs until Ctrl+C |
| `--always` | glide on every left click, no `F8` needed |
| `--list-modes` | print the speed table and exit |
| `--version` | print the version and exit |

## Platform notes

- **Linux**: works on X11. Wayland does not let an unprivileged process read
  global button presses, so the guide cannot work there; use the X11 session.
- **macOS**: the terminal (or your launcher) needs Accessibility permission in
  *System Settings -> Privacy & Security -> Accessibility*, otherwise the
  pointer cannot be moved and no clicks are seen.
- **Tiling window managers**: F8 may already belong to the compositor. Use
  `--no-hotkey`, which skips the global hotkey listener and starts armed.
- The screen size is read through `tkinter`; on a headless machine pass
  `--screen 1920x1080`.

## Tests

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

`tests/test_engine.py` and `tests/test_e2e.py` drive the glide against a fake
pointer and a fake clock: centre, speed, the hard stop at the bottom edge, the
release/resume cycle and a clock that runs backwards. `tests/test_cli.py` covers
the mode table and `--screen` parsing. CI runs them on Linux and macOS.

## Limitations

- The pynput backend is imported lazily, so CI never exercises real pointer
  movement; the OS integration is the one part that has to be tried by hand.
- The guide takes over the left button while armed. Arm it, use it, disarm it.
- Primary screen only; multi-monitor setups glide from the primary centre.
- No click replay, no macros, no recording: the pointer is the only thing it
  touches.

## License

MIT
