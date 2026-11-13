# Analysis rules

`analyze` walks a parsed program plus the JSON config and writes a findings report. It tracks *explicit* data flow only: values flowing through assignments, `+`, arguments, and `return`. An `if` condition does not taint the branch body by itself (no implicit control-flow taint).

## Config

`fixtures/config.json` lists:

- `sources`: functions whose *return value* is tainted with a `kind` (`env`, `file`, `network`, `param`).
- `sinks`: functions that raise a finding when a listed argument index (0-based) is tainted with a kind that is still active.
- `sanitizers`: functions that take a value and return a value whose listed kinds have been cleared. Other kinds on that same value remain. A sanitizer does not mutate the argument variable in the caller unless the caller assigns the return value back.

A function name may appear in at most one of the three lists. User-defined functions in the source are neither sources nor sinks unless they also appear in the config (the public config does not include any user function names).

## Propagation

- `x = expr` gives `x` the taint set of `expr` and drops any previous taint on `x`.
- A literal is untainted.
- `a + b` unions taint sets.
- A call to a source returns that source kind, regardless of arguments.
- A call to a sanitizer: take the union of argument taint, then remove the `clears` kinds from the returned set.
- A call to a user-defined function: bind argument taint to parameters, analyze the callee (see below), and use the taint of its `return` expressions. If a callee has no `return`, or a path returns without a value, that path contributes an empty set.
- A call to any other unknown function (not source, sink, sanitizer, or defined in the file) returns an empty taint set and does not copy argument taint, except that sink argument checking still happens if it is a sink.

## Interprocedural analysis

- Build a call graph over user-defined functions. Analyze with function summaries: each function maps a tuple of argument-taint-sets to a return taint set, and also records any sink findings observed under that binding.
- Recursion and mutual recursion must terminate. It is acceptable to iterate each function/argument-taint context until the return set stops growing, or to start from empty and compute a least fixpoint. Do not loop forever.
- When the same helper is called twice with different taint, the two calls are different contexts. A helper that returns its argument must therefore be a taint propagator in `fixtures/cases/helper.wire`.

## Branches

- Analyze both arms of `if`. After the `if`, a variable's taint is the union of the end-of-then and end-of-else sets. If a variable is assigned in only one arm, the other arm contributes whatever taint it had at the start of the `if`.
- `fixtures/cases/branch.wire` therefore has one sanitized path and one unsanitized path into `sql_exec`; the unsanitized path is a finding.

## Sinks

- When a sink is called, look at each index in `tainted_args`. If that argument's taint set contains a kind that this sink cares about, record a finding.
  - `system` cares about `cmdi`. Source kinds `env`, `file`, `network`, and `param` are all capable of becoming `cmdi` when they reach `system` unless `shell_escape` has cleared `cmdi`.
  - To keep the model simple, treat every source kind as also carrying the *sink kinds it has not been sanitized for*. Concretely: a freshly sourced value carries `{source_kind, cmdi, eval, sqli, path, ssrf}`. `shell_escape` removes `cmdi` only, so the same value may still be a finding at `sql_exec` (`sqli` remains).
- `fixtures/cases/sanitized.wire` must produce no finding for the `system` call.
- `fixtures/cases/direct.wire` must produce a `cmdi` finding from `getenv` to `system`.

## Findings

Each finding names the sink call, the source that introduced the remaining kind (function name and span), the sink kind, and a short path of variable or call names that carried the value. See `docs/report-schema.md`.
