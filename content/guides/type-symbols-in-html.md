---
title: "How to Type Symbols in HTML: Named, Decimal and Hex Entities"
h1: "How to type symbols in HTML"
description: "HTML accepts three ways to write any symbol: a named entity like &copy;, a decimal escape like &#169;, and a hex escape like &#xA9;. Here is when each one is safe to use."
slug: "type-symbols-in-html"
updated: "2026-10-13"
intent: "html entity for symbols"
---

HTML has three ways to write a symbol: a named entity such as `&copy;`, a decimal
numeric escape such as `&#169;`, and a hex numeric escape such as `&#xA9;`. Named
entities are readable but only around 2,100 of them exist and they cover a fraction of
Unicode. Decimal and hex escapes work for every code point, so they are the reliable
fallback whenever a named entity is missing. All three are parsed as text and render
as the character.

## Named entities

A named entity starts with `&`, uses a word or abbreviation from the HTML standard,
and ends with `;`.

```html
<p>&copy; 2026 AltKeyCodes</p>
<p>Temperature: 20&deg;C</p>
<p>&frac12; cup of flour</p>
```

Renders as:

> © 2026 AltKeyCodes
> Temperature: 20°C
> ½ cup of flour

The HTML5 named entity list also includes a set of five characters that must be
escaped because they have a structural meaning: `&lt;` for `<`, `&gt;` for `>`,
`&amp;` for `&`, `&quot;` for `"`, and `&apos;` for `'`. Those five are the ones you
will use most often, and getting them wrong is the usual cause of a broken page.

## Decimal escapes

A decimal escape writes the code point as a base-10 number between `&#` and `;`.

```html
<p>&#8593; &#8595; &#8592; &#8594;</p>
```

Renders as ↑ ↓ ← →

Decimal escapes work for every code point in Unicode with no exceptions and no
dependence on which named entities a browser knows.

## Hex escapes

A hex escape is the same idea in base 16, with an `x` after the `#`.

```html
<p>&#x2713; &#x2717; &#x2611;</p>
```

Renders as ✓ ✗ ☑

The hex form matches how Unicode code points are written everywhere else, so it is the
form to use when you are copying a code point out of a reference table. It is also
what you paste when you are not sure whether a named entity is safe.

## Which one to use

| Situation | Use | Why |
|---|---|---|
| `<`, `>`, `&`, `"`, `'` | Named entity | Required for correctness; the parser needs the escape |
| A common symbol with a well-known entity | Named entity | More readable in source, `&copy;` is obvious at a glance |
| A symbol you looked up in a table | Hex escape | Copy the code point directly, no name lookup |
| A symbol with no named entity | Decimal or hex | The only options |
| Inside an HTML attribute | Any of the three | All work; escape `"` if the attribute uses double quotes |

## Where entities do not work

Entities are an HTML and XML feature. They are not processed in:

- Plain text files, which show the literal characters `&copy;`
- Markdown, unless the renderer passes raw HTML through
- JSON, which has its own `\uXXXX` escape and no entity syntax
- CSS `content` values, which use backslash escapes instead

For JSON, write the character directly as UTF-8 or use the `\uXXXX` form. For CSS, see
the escape rules in the symbol pages on this site, where a trailing space is required
after a hex escape when the next character is a hex digit.

## FAQ

### Does the semicolon matter?

Yes. Writing `&copy` without the semicolon is not valid, and browsers only recover
from it in text content, not inside attributes or inside other entities. Always close
the entity.

### Can I use named entities that are not in the HTML5 list?

No. A name the standard does not define renders as the literal text you typed. If
this site's symbol table shows a dash for "Named entity", no name exists and you
should use the decimal or hex form.
