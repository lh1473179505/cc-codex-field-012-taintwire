"""CLI. parse already works; analyze is the piece to implement."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from taintwire.parser import ParseError, parse_source


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="taintwire")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("parse", help="print the AST as JSON")
    pr.add_argument("--source", required=True)

    an = sub.add_parser("analyze", help="report taint flows from sources to sinks")
    an.add_argument("--source", required=True)
    an.add_argument("--config", required=True)
    an.add_argument("--report", required=True)
    return p


def _dump(obj: Any) -> Any:
    if is_dataclass(obj):
        d = asdict(obj)
        d["kind"] = type(obj).__name__
        return d
    if isinstance(obj, list):
        return [_dump(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    return obj


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        src = Path(args.source).read_text(encoding="utf-8")
        program = parse_source(src)
    except (OSError, ParseError) as exc:
        print(f"failed to parse source: {exc}", file=sys.stderr)
        return 2

    if args.cmd == "parse":
        print(json.dumps({
            "funcs": [fn.name for fn in program.funcs],
            "ast": _dump(program),
        }, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "analyze":
        try:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"failed to load config: {exc}", file=sys.stderr)
            return 2
        from taintwire.engine import analyze_program

        try:
            report = analyze_program(program, config)
        except NotImplementedError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        # analyze is a reporter: it exits 0 when the analysis itself ran,
        # even if findings were produced. A malformed report exits 2.
        if not isinstance(report, dict) or "findings" not in report:
            print("report is missing a findings array", file=sys.stderr)
            return 2
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
