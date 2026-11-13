# wirelang

A tiny structured dialect. The front end already accepts this grammar:

```
program     := func+
func        := "func" ident "(" [ident ("," ident)*] ")" "{" stmt* "}"
stmt        := assign | if | return | expr ";"
assign      := ident "=" expr ";"
if          := "if" "(" expr ")" "{" stmt* "}" ["else" "{" stmt* "}"]
return      := "return" [expr] ";"
expr        := primary ("+" primary)*
primary     := ident | ident "(" [expr ("," expr)*] ")" | string | number | "true" | "false" | "(" expr ")"
```

- Comments start with `//` and run to the end of the line.
- Strings use double quotes and the escapes `\\`, `\"`, `\n`, `\t`.
- There are no arrays, maps, field access, or assignment to parameters other than by writing a new local of the same name. Parameters are ordinary locals initialized at the call site.
- `+` is the only operator. For taint purposes it is a propagating operator: if either side is tainted, the result is tainted with the union of kinds.
- There is no implicit type system. `true` / `false` and numbers are untainted literals.
- Functions are declared at the top level and may call each other, including later-declared functions. Recursion may occur; analysis must terminate.
