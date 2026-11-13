"""Lexer for wirelang."""

from __future__ import annotations

from dataclasses import dataclass

from taintwire.astnodes import Span

KEYWORDS = {"func", "if", "else", "return", "true", "false"}


@dataclass
class Token:
    kind: str
    value: str
    span: Span


class LexerError(ValueError):
    pass


def tokenize(src: str) -> list[Token]:
    i = 0
    n = len(src)
    line = 1
    col = 1
    out: list[Token] = []

    def span_at(l: int, c: int) -> Span:
        return Span(l, c)

    def advance(k: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(k):
            if i < n and src[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        ch = src[i]
        if ch in " \t\r":
            advance()
            continue
        if ch == "\n":
            advance()
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                advance()
            continue
        sl, sc = line, col
        if ch.isalpha() or ch == "_":
            start = i
            while i < n and (src[i].isalnum() or src[i] == "_"):
                advance()
            text = src[start:i]
            kind = text if text in KEYWORDS else "ident"
            out.append(Token(kind, text, span_at(sl, sc)))
            continue
        if ch.isdigit():
            start = i
            while i < n and src[i].isdigit():
                advance()
            out.append(Token("number", src[start:i], span_at(sl, sc)))
            continue
        if ch == '"':
            advance()
            start = i
            buf = []
            while i < n and src[i] != '"':
                if src[i] == "\\" and i + 1 < n:
                    nxt = src[i + 1]
                    mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                    buf.append(mapping.get(nxt, nxt))
                    advance(2)
                    continue
                if src[i] == "\n":
                    raise LexerError(f"unterminated string at {sl}:{sc}")
                buf.append(src[i])
                advance()
            if i >= n or src[i] != '"':
                raise LexerError(f"unterminated string at {sl}:{sc}")
            advance()
            out.append(Token("string", "".join(buf), span_at(sl, sc)))
            continue
        two = src[i : i + 2]
        if two in {"==", "!="}:
            out.append(Token(two, two, span_at(sl, sc)))
            advance(2)
            continue
        if ch in "(){},=+;-":
            out.append(Token(ch, ch, span_at(sl, sc)))
            advance()
            continue
        raise LexerError(f"unexpected character {ch!r} at {line}:{col}")
    out.append(Token("eof", "", span_at(line, col)))
    return out
