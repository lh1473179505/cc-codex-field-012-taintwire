# taintwire

A static taint checker for a small internal script dialect called wirelang. The lexer, parser, and `parse` command already work. `analyze` is still a stub in this snapshot.

Reviewers want a report of data flows from configured sources (`getenv`, `recv`, `read_file`, `param`) to configured sinks (`system`, `sql_exec`, `eval`, `write_file`, `http_post`), taking sanitizers and simple helper functions into account.

## Requirements

- Python 3.11+, standard library only
- No containers, no external analysis frameworks

## Already working

```bash
python -m taintwire parse --source fixtures/cases/direct.wire
python -m taintwire parse --source fixtures/cases/helper.wire
python -m taintwire parse --source fixtures/cases/branch.wire
```

The language is described in `docs/language.md`. Analysis rules are in `docs/analysis.md`. The report object is in `docs/report-schema.md`. The source/sink/sanitizer map is `fixtures/config.json`.

## Intended CLI

```bash
python -m taintwire analyze \
  --source fixtures/cases/direct.wire \
  --config fixtures/config.json \
  --report /tmp/taintwire-report.json
```

Parameter names are fixed in `taintwire/__main__.py`. Keep them. Reuse the existing parser; `analyze` should exit 0 when the analysis itself ran, including when it produced findings. Syntax errors still exit 2.

## Layout

- `taintwire/lexer.py`, `taintwire/parser.py`, `taintwire/astnodes.py` — language front end
- `taintwire/engine.py` — `analyze_program` (not implemented yet)
- `fixtures/cases/` — direct taint, a sanitized flow, an interprocedural helper, and a branch
