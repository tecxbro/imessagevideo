"""Editable attention transfer from a foreground screen to a physical clue."""


def unit(frame, start, duration):
    return min(1.0, max(0.0, (frame - start) / duration))


def smooth(t):
    return t * t * (3 - 2 * t)


def move_to_clue(frame, cut, lead=12, settle=15):
    """Return phone exit and background sharpening before a cut, push after it."""
    exit_phase = unit(frame, cut - lead, lead)
    reveal_phase = smooth(exit_phase)
    push = 1 - (1 - unit(frame, cut - 3, settle + 3)) ** 2
    return exit_phase ** 1.7, reveal_phase, push
