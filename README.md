# AltKeyCodes

A searchable reference for **2,052 symbols** — legacy Windows Alt codes, Unicode code
points, macOS Option keys, HTML entities, CSS escapes and Python/JavaScript escape
sequences.

Live at **[altkeycodes.com](https://altkeycodes.com)**.

## Why this exists

The incumbent reference (`alt-codes.net`) has 96 pages, zero structured data, injects the
same 255-row table into every page, has no search, and only documents the Windows legacy
Alt codes. This project is a static, ad-free replacement:

| | alt-codes.net | AltKeyCodes |
|---|---|---|
| Pages | 96 | 253 |
| JSON-LD nodes | 0 | 6,800+ across 18 types |
| Symbols in raw HTML | 255-row table repeated on every page | 240 tiles server-rendered on the home page |
| Input methods | Windows legacy Alt only | 9, each with its real limits documented |
| JavaScript required for content | — | No. JS is progressive enhancement only |
| Third-party scripts | Ad network | None |

## Quick start

```bash
python3 build_symbols.py   # regenerate data/symbols.json + data/groups.json
python3 build.py           # generate dist/
```

Then serve the result:

```bash
python3 -m http.server 8899 --directory dist
```

No dependencies. Python 3 standard library only.

## Project layout

```
build_symbols.py        dataset generator (stdlib + unicodedata + codecs)
build.py                static site generator (stdlib only)
site.config.json        site name, domain, author
data/symbols.json       generated: 2,052 symbols with every code form
data/groups.json        generated: 33 symbol groups
content/guides/*.md     hand-written guide copy, consumed verbatim
templates/*.html        page shells, {{key}} placeholder renderer
assets/style.css        design tokens, light + dark theme
assets/app.js           instant search, copy-to-clipboard, theme toggle
dist/                   generated output — deploy this
```

## Data provenance

Nothing in the symbol data is guessed at runtime.

- **Legacy Alt codes** are derived from Python's own `cp437` and `cp1252` codecs. Three-digit
  codes (1–255) are OEM code page 437; `0`-prefixed four-digit codes (0128–0255) are
  Windows-1252. All 345 printable codes were cross-checked against the codecs with zero
  mismatches.
- **Unicode names, categories and blocks** come from the standard library's `unicodedata`
  (Unicode 16.0.0).
- **HTML named entities** come from the standard library's `html.entities.codepoint2name`.
  Where no named entity exists, the field is `null` rather than invented.
- **Aliases, LaTeX commands and macOS Option shortcuts** are curated tables inside
  `build_symbols.py`. The Option shortcuts assume a **US keyboard layout**, which the site
  states on every page that uses them.

### Documented behaviour, not marketing

The build encodes the awkward truths rather than hiding them:

- Alt codes 1–31 and 127 have no printable character of their own. They draw a picture only
  because the OEM console font puts a glyph in that cell. The `oem_picture` flag marks them.
- `Alt` + a decimal code point works only at or below `U+FFFF`.
- `Alt`+`X` hex conversion is a Word / WordPad / Outlook behaviour, not a system feature.
- A hex escape in CSS needs a trailing space when the next character is a hex digit.

## SEO and AI-search setup

- Every page: one canonical (trailing slash), a unique title under 60 characters, a unique
  description of 120–160 characters, exactly one `h1`, and a parseable JSON-LD `@graph`.
- Structured data covers `WebSite` + `SearchAction`, `DefinedTerm`, `DefinedTermSet`,
  `FAQPage` (1,044 Q&As), `HowTo` (794 steps), `Article`, `ItemList`, `BreadcrumbList`.
- `robots.txt` names 19 AI crawlers explicitly, separating search citability
  (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`) from training access (`GPTBot`,
  `ClaudeBot`, `CCBot`, `Applebot-Extended`).
- `llms.txt` is included for non-Google systems. It carries no ranking weight in Google
  Search and is not claimed to.
- Content is server-rendered, so crawlers that do not execute JavaScript still see it.

## Verification

`build.py` self-checks its own output (including an orphan-page reachability walk) and
reports the result. An independent verifier is used to re-check the artifact on disk rather
than trusting the build's own summary.

## Licence

Symbol data derives from the Unicode Character Database. Guide copy and site code are
original to this project.
