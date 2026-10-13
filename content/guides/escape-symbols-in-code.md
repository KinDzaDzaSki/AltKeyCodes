---
title: "How to Write Symbols in CSS, Python, JavaScript and JSON"
h1: "Escaping symbols in CSS, Python, JavaScript and JSON"
description: "Each language escapes Unicode characters differently: CSS uses a backslash with a required trailing space, JavaScript uses \u with braces above the BMP, JSON uses UTF-16 pairs, and Python has both \u and \U forms."
slug: "escape-symbols-in-code"
updated: "2026-10-13"
intent: "unicode escape css javascript python"
---

Every language has its own escape syntax for a Unicode character, and the differences
cause real bugs. CSS needs a trailing space after a hex escape when the next character
is a hex digit, JavaScript needs braces around code points above `U+FFFF`, JSON cannot
express them at all without surrogate pairs, and Python has separate `\u` and `\U`
forms. The table below maps one character, ✓ `U+2713`, across all of them.

| Context | Escape | Notes |
|---|---|---|
| CSS | `\2713 ` | Trailing space required before a hex digit |
| Python | `"\u2713"` | Four hex digits only |
| Python, above BMP | `"\U0001F600"` | Eight hex digits, capital `U` |
| JavaScript | `"\u2713"` | Four hex digits only |
| JavaScript, above BMP | `"\u{1F600}"` | Braces, ES6 and later |
| JSON | `"\u2713"` | Four hex digits only |
| JSON, above BMP | `"\ud83d\ude00"` | Surrogate pair required |
| LaTeX | `\checkmark` | Math mode; command names differ per symbol |
| HTML | `&#x2713;` | See the HTML guide |

## CSS

A CSS escape is a backslash followed by the hex code point.

```css
.badge::before {
  content: "\2713";
}
```

The trailing space rule catches people out. A hex escape is greedy: it consumes as
many hex digits as follow it. In `"\2713"` the escape ends at the closing quote, so
the space is not needed. But in the following, the escape would swallow the `a`:

```css
/* Wrong: \2713a is parsed as the escape for U+2713A */
content: "\2713abc";

/* Right: the space terminates the escape */
content: "\2713 abc";
```

The space is consumed by the parser as part of the escape terminator and does not
appear in the output. Above `U+FFFF`, use six hex digits, for example `"\01F600 "`.

## Python

```python
check = "\u2713"          # code points up to U+FFFF
grin  = "\U0001F600"      # code points above U+FFFF, capital U, 8 digits
check = chr(0x2713)       # same result, easier to read for a variable code point
```

A lowercase `\u` only accepts exactly four hex digits. Passing a longer value raises a
syntax error. Use `\U` with eight digits, or `chr()`, for anything above the Basic
Multilingual Plane.

For Python source, also confirm the file is UTF-8. Python 3 defaults to UTF-8 so
writing the character directly is usually simplest. Write `"\u2713"` when you cannot
guarantee the file encoding survives whatever pipeline it passes through.

## JavaScript

```js
const check = "\u2713";       // up to U+FFFF
const grin  = "\u{1F600}";    // above U+FFFF, ES6 and later
const same  = String.fromCodePoint(0x2713);
```

Inside a template literal the escape behaves identically, but a backslash still needs
escaping when you mean a literal one. Watch length calculations: a string containing
an emoji built from a surrogate pair reports a `length` of 2 because `length` counts
UTF-16 code units, not characters. Use `[...str].length` when you need character
counts.

## JSON

JSON has no form for a code point above `U+FFFF` other than a surrogate pair, and
`\u{...}` is invalid JSON.

```json
{
  "bmp":  "\u2713",
  "astral": "\ud83d\ude00"
}
```

The practical advice is to skip escaping entirely and write the character as UTF-8 in
the file, which is valid JSON for the whole of Unicode:

```json
{
  "check": "✓"
}
```

That only breaks if a downstream tool re-encodes the file as ASCII. When in doubt,
surrogate pairs are always safe, and `json.dumps(..., ensure_ascii=False)` in Python
produces the readable UTF-8 form.

## LaTeX

LaTeX commands are names, not code points, and most require math mode.

```latex
$\checkmark$ \quad $\degree$ \quad $\pm$ \quad $\times$
```

Wrap the command in `$...$` unless the command is a text command such as
`\textcopyright`. The symbol pages on this site mark each LaTeX command as math mode
or text mode.

## FAQ

### Why does `"\u2713"` fail in some languages?

The escape lengths differ. Python, JavaScript and JSON all read `\u` as exactly four
hex digits. A five or six digit code point needs a different form in each language,
which the table above lists.

### Do I need to escape symbols in an SQL string?

SQL strings are Unicode-aware in every current database when the connection and column
collation are correct. Write the character directly. If you must escape, use the
database's own function rather than a language-level Unicode escape.

### Is it safe to paste the character instead of escaping it?

Yes, in files saved as UTF-8. The escape forms exist for cases where the file encoding
is not under your control, for comparing invisible characters, and for source that has
to survive a pipeline that mangles non-ASCII bytes.
