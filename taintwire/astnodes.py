"""AST nodes for the wirelang dialect."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass
class Span:
    line: int
    col: int


@dataclass
class Ident:
    name: str
    span: Span


@dataclass
class Literal:
    value: str | int | bool
    span: Span


@dataclass
class Binary:
    op: str  # + only, string/int concat-or-add
    left: "Expr"
    right: "Expr"
    span: Span


@dataclass
class Call:
    func: str
    args: list["Expr"]
    span: Span


Expr = Ident | Literal | Binary | Call


@dataclass
class Assign:
    name: str
    expr: Expr
    span: Span


@dataclass
class Return:
    expr: Expr | None
    span: Span


@dataclass
class ExprStmt:
    expr: Expr
    span: Span


@dataclass
class If:
    cond: Expr
    then: list["Stmt"]
    orelse: list["Stmt"]
    span: Span


Stmt = Assign | Return | ExprStmt | If


@dataclass
class Func:
    name: str
    params: list[str]
    body: list[Stmt]
    span: Span


@dataclass
class Program:
    funcs: list[Func]
    span: Span
