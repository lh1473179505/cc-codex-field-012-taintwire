"""Recursive-descent parser for wirelang."""

from __future__ import annotations

from taintwire.astnodes import (
    Assign,
    Binary,
    Call,
    Expr,
    ExprStmt,
    Func,
    Ident,
    If,
    Literal,
    Program,
    Return,
    Span,
    Stmt,
)
from taintwire.lexer import LexerError, Token, tokenize


class ParseError(ValueError):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i]

    def at(self, *kinds: str) -> bool:
        return self.peek().kind in kinds

    def eat(self, *kinds: str) -> Token:
        tok = self.peek()
        if tok.kind not in kinds:
            raise ParseError(f"expected {'/'.join(kinds)} at {tok.span.line}:{tok.span.col}, got {tok.kind}")
        self.i += 1
        return tok

    def parse_program(self) -> Program:
        funcs: list[Func] = []
        start = self.peek().span
        while not self.at("eof"):
            funcs.append(self.parse_func())
        if not funcs:
            raise ParseError("program must contain at least one function")
        names = [f.name for f in funcs]
        if len(names) != len(set(names)):
            raise ParseError("duplicate function name")
        self.eat("eof")
        return Program(funcs=funcs, span=start)

    def parse_func(self) -> Func:
        tok = self.eat("func")
        name = self.eat("ident").value
        self.eat("(")
        params: list[str] = []
        if not self.at(")"):
            params.append(self.eat("ident").value)
            while self.at(","):
                self.eat(",")
                params.append(self.eat("ident").value)
        self.eat(")")
        self.eat("{")
        body = self.parse_block_body()
        self.eat("}")
        return Func(name=name, params=params, body=body, span=tok.span)

    def parse_block_body(self) -> list[Stmt]:
        stmts: list[Stmt] = []
        while not self.at("}", "eof"):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self) -> Stmt:
        if self.at("if"):
            return self.parse_if()
        if self.at("return"):
            tok = self.eat("return")
            expr = None if self.at(";") else self.parse_expr()
            self.eat(";")
            return Return(expr=expr, span=tok.span)
        if self.at("ident") and self._lookahead_kind() == "=":
            name = self.eat("ident")
            self.eat("=")
            expr = self.parse_expr()
            self.eat(";")
            return Assign(name=name.value, expr=expr, span=name.span)
        expr = self.parse_expr()
        self.eat(";")
        return ExprStmt(expr=expr, span=expr.span)  # type: ignore[attr-defined]

    def _lookahead_kind(self) -> str:
        if self.i + 1 < len(self.tokens):
            return self.tokens[self.i + 1].kind
        return "eof"

    def parse_if(self) -> If:
        tok = self.eat("if")
        self.eat("(")
        cond = self.parse_expr()
        self.eat(")")
        self.eat("{")
        then = self.parse_block_body()
        self.eat("}")
        orelse: list[Stmt] = []
        if self.at("else"):
            self.eat("else")
            self.eat("{")
            orelse = self.parse_block_body()
            self.eat("}")
        return If(cond=cond, then=then, orelse=orelse, span=tok.span)

    def parse_expr(self) -> Expr:
        return self.parse_plus()

    def parse_plus(self) -> Expr:
        left = self.parse_primary()
        while self.at("+"):
            op = self.eat("+")
            right = self.parse_primary()
            left = Binary(op="+", left=left, right=right, span=op.span)
        return left

    def parse_primary(self) -> Expr:
        if self.at("ident"):
            ident = self.eat("ident")
            if self.at("("):
                return self.parse_call(ident)
            return Ident(name=ident.value, span=ident.span)
        if self.at("string"):
            tok = self.eat("string")
            return Literal(value=tok.value, span=tok.span)
        if self.at("number"):
            tok = self.eat("number")
            return Literal(value=int(tok.value), span=tok.span)
        if self.at("true", "false"):
            tok = self.eat("true", "false")
            return Literal(value=tok.kind == "true", span=tok.span)
        if self.at("("):
            self.eat("(")
            expr = self.parse_expr()
            self.eat(")")
            return expr
        tok = self.peek()
        raise ParseError(f"unexpected token {tok.kind} at {tok.span.line}:{tok.span.col}")

    def parse_call(self, ident: Token) -> Call:
        self.eat("(")
        args: list[Expr] = []
        if not self.at(")"):
            args.append(self.parse_expr())
            while self.at(","):
                self.eat(",")
                args.append(self.parse_expr())
        self.eat(")")
        return Call(func=ident.value, args=args, span=ident.span)


def parse_source(src: str) -> Program:
    try:
        tokens = tokenize(src)
    except LexerError as exc:
        raise ParseError(str(exc)) from exc
    return Parser(tokens).parse_program()
