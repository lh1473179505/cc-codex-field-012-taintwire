"""Taint analysis engine. Not implemented in this snapshot."""

from __future__ import annotations

from typing import Any

from taintwire.astnodes import Program


def analyze_program(program: Program, config: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError("analyze_program is not implemented in this snapshot")
