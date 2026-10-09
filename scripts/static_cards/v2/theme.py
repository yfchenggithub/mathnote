"""Shared V2 design tokens. Values are in 1080×1440 card pixels."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    paper: str = "#FAFBFD"
    ink: str = "#18283D"
    muted: str = "#64748B"
    blue: str = "#2563EB"
    teal: str = "#0F9D91"
    amber: str = "#C76A16"
    pale_blue: str = "#EFF6FF"
    pale_teal: str = "#EDFAF7"
    line: str = "#DCE5EF"
    axis: str = "#A8B6C8"


@dataclass(frozen=True)
class TypeScale:
    eyebrow: int = 24
    title: int = 45
    formula_hero: int = 70
    body: int = 28
    diagram: int = 25
    step: int = 29
    note: int = 28


@dataclass(frozen=True)
class Space:
    safe: int = 76
    content: int = 928
    footer_y: int = 1358
    block: int = 36
    inner: int = 30


@dataclass(frozen=True)
class Strokes:
    curve: float = 5
    construction: float = 5
    auxiliary: float = 2
    axis: float = 2
    emphasis: float = 6


P = Palette()
T = TypeScale()
S = Space()
L = Strokes()
