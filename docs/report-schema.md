# Report schema

```json
{
  "findings": [
    {
      "kind": "cmdi",
      "sink": "system",
      "sink_span": {"line": 3, "col": 3},
      "source": "getenv",
      "source_span": {"line": 2, "col": 9},
      "path": ["getenv", "cmd", "system"]
    }
  ]
}
```

- `findings` is always present (an empty array when there is no unsanitized flow).
- `kind` is a sink kind (`cmdi`, `sqli`, `eval`, `path`, `ssrf`).
- `sink` / `source` are function names.
- Spans use the start of the corresponding call expression from the AST (`line` / `col`, 1-based, as produced by the lexer).
- `path` is a list of source, intermediate variable names, helper names, and the sink name, in flow order. It is acceptable to include only the names that appeared as assignments or calls on that flow.
- The same sink call with two distinct sources may produce two findings. Do not collapse the unsanitized arm of a branch into the sanitized arm.
