# BUILD BRIEF — "AltCode" symbol reference site

You are building a **static site generator** and its templates. Read this whole file
before writing code. Obey the self-check list in section 12 at the end.

---

## 0. Context you need

`alt-codes.net` is the incumbent for "alt code" / "symbol" search traffic. It has
**96 URLs** in its sitemap, **zero JSON-LD**, injects the same 255-row table into
every page (thin duplicate content), has no search, no mobile layout, no macOS or
Unicode method, and loads third-party ad scripts. We are replacing it.

Our advantages, and therefore your job:
1. **2,052 symbols** with full multi-method data (see section 2).
2. **Instant search** that works on name, alias, glyph and code.
3. **Server-rendered HTML** — every symbol, code and answer exists in the raw HTML
   with JavaScript disabled. JS is progressive enhancement only.
4. **GEO/AI answer blocks** — every page opens with a self-contained, quotable answer.
5. **Structured data** on every page (section 8).
6. **Honest caveats** — every method states when it does *not* work.
7. **No ads, no third-party scripts, no tracking.**

---

## 1. Deliverable and file layout

Write these files. Everything is **Python 3 standard library only** — no pip installs.

```
altcodes/
  build.py                  # the generator (stdlib only)
  site.config.json          # site-level constants read by build.py
  data/symbols.json         # INPUT — already exists, do not modify
  data/groups.json          # INPUT — already exists, do not modify
  content/guides/*.md       # INPUT — already exists, consume verbatim
  templates/
    base.html               # page shell (head, nav, footer)
    home.html               # the search tool
    group.html              # category hub page
    symbol.html             # single-symbol reference page
    table.html              # the full 0-255 legacy Alt code table
    guide.html              # renders content/guides/*.md
    notfound.html
  assets/
    style.css
    app.js
  dist/                     # OUTPUT — everything build.py writes goes here
```

`build.py` runs as `python3 build.py` and must:
* Wipe and recreate `dist/`.
* Copy `assets/` into `dist/assets/`.
* Write every page plus `robots.txt`, `sitemap.xml`, `llms.txt`, `404.html`.
* Print a build report: pages written, by type, and total bytes.
* Exit non-zero on any missing input file or unknown template placeholder.

**No template engine dependencies.** Implement a small `render(template, context)`
that replaces `{{key}}` and `{{{key}}}` (raw HTML) placeholders. Keep it under
40 lines. `{{#each list}}...{{/each}}` for loops is acceptable if you also write it.

---

## 2. Data contract — `data/symbols.json`

A JSON array. Every object has exactly these keys:

| Key | Type | Notes |
|---|---|---|
| `id` | string | e.g. `"u2713"` — use as the page filename stem |
| `glyph` | string | the character itself |
| `name` | string | display name, e.g. `"Check Mark"` |
| `unicode_name` | string | official upper-case Unicode name |
| `codepoint` | int | e.g. `10003` |
| `unicode` | string | `"U+2713"` |
| `entity` | object | `{named, decimal, hex}`; `named` is `null` when HTML defines none |
| `css` | string | `"\\2713"` |
| `python` | string | `"\\u2713"` or `"\\U0001F600"` |
| `js` | string | `"\\u2713"` or `"\\u{1F600}"` |
| `utf8` | string | space-separated hex bytes, e.g. `"E2 9C 93"` |
| `block` | string | Unicode block name |
| `category` | string | Unicode general category |
| `groups` | array | group slugs this symbol belongs to (may be empty) |
| `aliases` | array | plain-language search terms — **search these** |
| `alt_legacy` | array | legacy Windows Alt codes, e.g. `["248","0176"]`; may be empty |
| `alt_decimal` | string | decimal codepoint typed after Alt (BMP only); `""` for astral |
| `alt_hex` | string | hex for the Windows `Alt`+`X` method, no `0x` |
| `oem_picture` | bool | true when `alt_legacy` comes from the OEM console picture table |
| `mac_option` | string | macOS Option shortcut, e.g. `"⌥⇧8"`; `""` if we have none |
| `mac_note` | string | what that shortcut produces on a US layout |
| `latex` | string | `""` if none |
| `latex_mode` | string | `"math"` or `"text"` |
| `weight` | int | higher = more popular; **sort hub pages by this descending** |

`data/groups.json` is an array of:
`{slug, name, tagline, intent, count, symbols}` where `symbols` is an array of
symbol `id`s in display order, and `intent` is the search phrase the group answers
(e.g. `"check mark"`).

---

## 3. Page inventory and URL scheme

Site root: read `base_url` from `site.config.json`. All URLs are clean, lowercase,
hyphenated, **trailing slash**, no `.html` in any internal link or canonical.

| Output file | URL | Page type | Count |
|---|---|---|---|
| `dist/index.html` | `/` | home / search tool | 1 |
| `dist/symbols/<slug>/index.html` | `/symbols/<group-slug>/` | group hub | 33 |
| `dist/symbol/<id>-<name-slug>/index.html` | `/symbol/<id>-<name-slug>/` | single symbol | see below |
| `dist/legacy-alt-codes/` | `/legacy-alt-codes/` | full 0–255 table | 1 |
| `dist/how-to/<guide-slug>/` | `/how-to/<guide-slug>/` | guides | from content/ |
| `dist/symbols/index.html` | `/symbols/` | index of all groups | 1 |
| `dist/404.html` | — | not found | 1 |

**Symbol pages:** generate one for **every symbol with `weight >= 40`**, plus every
symbol that has a non-empty `mac_option`. That is the "popular" set. Name slug =
`name` lowercased, non-alphanumerics collapsed to `-`, trimmed.
Example: `/symbol/u2713-check-mark/`. `id` first guarantees uniqueness.

---

## 4. Design system — implement exactly

Light theme default, dark theme via `prefers-color-scheme` **and** a manual toggle
persisted to `localStorage` under key `altcode-theme`. `data-theme="dark"` on
`<html>` overrides.

```css
:root{
  --bg:#ffffff; --bg-subtle:#fafafa; --bg-muted:#f4f4f5; --bg-inset:#f8f8f9;
  --fg:#09090b; --fg-muted:#52525b; --fg-subtle:#a1a1aa;
  --border:#e4e4e7; --border-strong:#d4d4d8;
  --accent:#2563eb; --accent-hover:#1d4ed8; --accent-fg:#ffffff; --accent-subtle:#eff6ff;
  --ok:#15803d; --ok-subtle:#f0fdf4; --warn:#b45309; --warn-subtle:#fffbeb;
  --radius:12px; --radius-sm:8px; --radius-lg:16px;
  --shadow-sm:0 1px 2px rgb(0 0 0/.04);
  --shadow-md:0 4px 12px -2px rgb(0 0 0/.08),0 2px 4px -2px rgb(0 0 0/.04);
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace;
  --maxw:1100px; --font-size:16px;
}
[data-theme=dark]{
  --bg:#09090b; --bg-subtle:#101012; --bg-muted:#18181b; --bg-inset:#141416;
  --fg:#fafafa; --fg-muted:#a1a1aa; --fg-subtle:#71717a;
  --border:#27272a; --border-strong:#3f3f46;
  --accent:#3b82f6; --accent-hover:#60a5fa; --accent-fg:#ffffff; --accent-subtle:#172554;
  --ok:#4ade80; --ok-subtle:#052e16; --warn:#fbbf24; --warn-subtle:#451a03;
  --shadow-sm:0 1px 2px rgb(0 0 0/.4);
  --shadow-md:0 4px 12px -2px rgb(0 0 0/.5),0 2px 4px -2px rgb(0 0 0/.3);
}
```

**Fonts:** load Inter and JetBrains Mono from Google Fonts with
`rel="preconnect"` + `display=swap`. Fall back to the stacks above. Do not let a
font request block rendering.

**Type scale:** body 16px/1.6. h1 `clamp(1.9rem,1.4rem + 2vw,2.75rem)` weight 700
tracking -0.02em. h2 1.5rem/700. h3 1.05rem/600. Small text 0.85rem. Labels 0.75rem
uppercase tracking 0.06em `--fg-muted`.

**Layout:** `max-width:1100px`, `margin-inline:auto`, `padding-inline:clamp(16px,4vw,32px)`.
Section spacing `clamp(40px,6vw,72px)`.

**Component rules (non-negotiable):**
- Cards: `background:var(--bg)`, `border:1px solid var(--border)`, `border-radius:var(--radius)`.
  **No colored card backgrounds. No gradients behind text.**
- Buttons: 3 variants only — primary (accent fill), secondary (border + `--bg`),
  ghost (text only). Height 36px, radius `--radius-sm`, `font-size:.875rem`, `font-weight:500`.
  Transitions `120ms` on `background,border-color,color`. No scale/shadow tricks.
- **Every glyph tile is a copy button.** Glyph rendered at ~2rem in `--mono`.
  Hover: border becomes `--border-strong`, background `--bg-muted`.
- Code chips: `--mono`, 0.8rem, `background:var(--bg-inset)`, 1px border, radius 6px,
  padding 2px 8px, click-to-copy.
- Focus: `outline:2px solid var(--accent); outline-offset:2px`. **Never remove.**
- Tables: `border-collapse:collapse`, 1px `--border` rules, sticky `<thead>`,
  zebra rows using `--bg-subtle`.
- Motion: 120–160ms, `ease`. Wrap all animation in
  `@media (prefers-reduced-motion:no-preference)`.
- **No external images. No icon fonts.** Use inline SVG (24×24, `stroke:currentColor`,
  `stroke-width:1.75`, `fill:none`, round caps) for the handful of UI icons needed,
  or the project's own glyphs.

---

## 5. Home page (`dist/index.html`) — the search tool

This is the product. Build in this order:

1. **Header** — wordmark "AltCode", inline search input (id `q`), theme toggle button.
2. **Hero** — h1 `"Alt codes, Unicode and symbol reference"`. One-line sub: every
   symbol you can type on Windows, macOS, HTML, CSS and Python, in one searchable
   table. Then the **answer block** (section 7).
3. **Search panel** — sticky under the header.
   - `<input type="search" id="q" autofocus placeholder="Search 2,052 symbols — try “check mark”, “degree”, “euro”, “♥” or 2713">`
   - Filter row: group `<select>`, "has Alt code" checkbox, "has Option shortcut" checkbox.
   - Live result count in an `aria-live="polite"` region.
4. **Result grid** — `<div id="results">`. Each result is a `<button class="sym">`
   containing: the glyph, the name, and the best available primary code chip.
5. **No-JS fallback** — `<noscript>` tells the user search needs JavaScript and points
   them at `/symbols/` and `/legacy-alt-codes/`. **Before JS runs, `#results` must
   already contain the first 240 symbols as plain HTML** so crawlers and no-JS users
   see content. JS then takes over.
6. **Group directory** — a grid of all 33 groups, each linking to its hub with its count.
7. **"How to" cards** — links to every guide.
8. **Method comparison table** — one row per method (Windows legacy Alt, Windows Alt
   decimal, Windows Alt+X hex, macOS Option, macOS Character Viewer, HTML entity,
   CSS escape, Python/JS escape), with columns: Method, Works on, Numpad needed?,
   Works for all Unicode? Read the caveats in section 7 and stay accurate.
9. **Footer** — about line, links to `/symbols/`, all guides, `sitemap.xml`, `llms.txt`.
   State plainly: no ads, no tracking, no cookies.

---

## 6. Symbol page (`dist/symbol/<id>-<slug>/index.html`)

Template order — this exact order, because ~44% of AI citations come from the first
30% of a page:

1. Breadcrumb nav: Home › Symbols › `<group name>` › `<symbol name>`.
2. **h1**: `"<Name> Alt Code and Symbol"` — but omit "Alt Code" if `alt_legacy` is
   empty; use `"<Name> Symbol"` instead.
3. **Glyph display**: huge (5–7rem), centred, in a bordered panel, itself a copy button.
4. **Answer block** — 130–170 words, self-contained, first 60 words answer the
   question directly. Pattern in section 7.
5. **Codes table** — one row per field that exists: Legacy Alt code(s) / Alt +
   decimal / Alt + hex → `Alt`+`X` / Option / HTML named / HTML decimal / HTML hex /
   CSS / Python / JavaScript / UTF-8 bytes / Unicode codepoint / Unicode block /
   Unicode category. Each value cell contains a click-to-copy chip. **Omit rows whose
   value is empty — never print a dash for a method that does not apply**, except in
   a single "Not available for this symbol" note listing what is genuinely missing.
6. **Step-by-step: how to type it on Windows** — `<ol>` with real key-by-key steps,
   including the numpad caveat and the "no numpad?" link.
7. **How to type it on macOS** — include the Option shortcut when present (state it
   assumes a US layout), otherwise the Character Viewer method (⌃⌘Space, search the
   `unicode_name`).
8. **How to use it in code** — HTML, CSS, Python, JavaScript, JSON, LaTeX when present.
9. **Related symbols** — 12–20 other symbols from the same group(s), as glyph tiles.
10. **FAQ** — 3–5 `<h3>` questions with real answers, phrased the way people search
    (`"What is the Alt code for a check mark?"`, `"Is there an Alt code for ✓?"`,
    `"How do I type ✓ without a numpad?"`, `"Why does Alt+10003 not work?"`).
11. Prev/next links within the group, and a back-to-group link.

---

## 7. Copy rules — this is the part that decides whether the site ranks

**Answer-block pattern** (use for every page; write the real numbers in from the data,
never invent them):

> The Alt code for `<name>` is **`<n>`**. Hold <kbd>Alt</kbd>, type `<n>` on the
> numeric keypad, then release <kbd>Alt</kbd>. `<name>` also has the Unicode
> codepoint `<U+XXXX>`, so you can type it with `Alt`+`<decimal>` on Windows, `⌥<hex>`
> in macOS's Character Viewer, `&<entity>;` in HTML, or `<css>` in CSS. If your
> keyboard has no numeric keypad, use the Character Viewer, the HTML entity, or copy
> the character directly — the Alt key method requires a physical numpad.

Then 2–3 more sentences of genuinely useful, specific detail. Total 130–170 words.
**Vary the wording between pages** — do not emit one string with the nouns swapped.
Read the symbol's own data and say what is actually true about *this* symbol.

**Accuracy requirements — get these right or the page is wrong:**
- 3-digit Alt codes (1–255) are the **OEM code page 437** characters. 4-digit
  `0`-prefixed codes (0128–0255) are the **ANSI / Windows-1252** characters. Both
  tables exist and they disagree above 127, which is why some symbols have two codes.
- Alt codes **1–31 and 127** have no printable Unicode character of their own. They
  produce a picture only because the OEM console font draws one in that cell — say
  this explicitly on those pages (`oem_picture: true`), and note that in a modern
  app using a TrueType font the same keystroke may insert nothing visible or a
  control character.
- **Alt + decimal codepoint** (e.g. `Alt`+`10003`) works only for code points at or
  below `U+FFFF`, and only in applications that accept the numeric-keypad input path.
  Say "BMP only" and name that limit.
- **Alt + hex then `X`** (e.g. `2713` then `Alt`+`X`) is a Word / WordPad /
  Outlook rich-text behaviour, not a system-wide feature. It needs the extra
  `EnableHexNumpad` registry value if you use the numpad form instead.
- macOS: `mac_option` shortcuts assume a **US keyboard layout**. Shortcuts for
  accented letters differ on other layouts. When we have no shortcut, the honest
  answer is the **Character Viewer** (`⌃⌘Space`) or the Emoji & Symbols pane.
- HTML: `entity.named` is `null` for most symbols. When it is null, say the symbol has
  no named HTML entity and give the numeric `&#NNNN;` / `&#xHHHH;` forms. Do not
  invent entity names.
- CSS: a hex escape must be followed by a space when the next character is a hex
  digit, e.g. `content:"\2713 "`. Say so.
- **Never claim a symbol "works everywhere"**, never claim a specific Windows version
  added or removed a code, and never state an adoption statistic unless it is in this
  brief.

**Banned constructions** (write none of these anywhere in the site):
- Em dashes in headings. Lazy absolutes ("every", "all", "any", "always" as filler).
- Binary contrasts ("not just X, it's Y").
- Adverbs "simply", "just", "really", "fully", "freely".
- "-ing" clauses appended to a claim ("ensuring", "allowing you to", "fostering").
- Marketing filler: "seamless", "powerful", "comprehensive", "ultimate", "effortless",
  "revolutionary", "game-changing", "delve", "unlock", "elevate", "in today's world".
- Second sentences in a card description that add nothing.

**Guides (`content/guides/*.md`)** — consume them **verbatim**, do not rewrite,
shorten or summarise. They have YAML-ish frontmatter between `---` fences with keys
`title`, `h1`, `description`, `slug`, `updated`, `intent`. Body is Markdown.
Support these Markdown constructs only: `##`/`###` headings, paragraphs, `-`/`1.`
lists, `|` tables, `> ` blockquotes, `**bold**`, `` `code` ``, ``` fenced code
blocks, and `[text](url)` links. Convert to HTML. `<kbd>` written literally in the
source must pass through unchanged.

---

## 8. SEO and GEO requirements

**Every page's `<head>` must contain:**
- `<title>` — unique, ≤ 60 characters. Patterns: home → `AltCode: Alt Codes, Unicode & Symbol Reference`; group → `Check Mark Symbols: Alt Codes & Unicode`; symbol → `Check Mark ✓ Alt Code (Alt+10003) & Unicode U+2713`.
- `<meta name="description">` — unique, 120–160 characters, includes the actual code.
- `<link rel="canonical">` — absolute, trailing slash.
- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- `<meta property="og:type|og:title|og:description|og:url|og:site_name">` and
  `<meta name="twitter:card" content="summary">`.
- `<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">`
- **Visible** `<time datetime="YYYY-MM-DD">` for published and last-updated on every
  guide and symbol page, and a byline reading `By <author>` where `author` comes from
  `site.config.json`.

**JSON-LD on every page** — one `<script type="application/ld+json">` block containing
an `@graph` array. Build the nodes per page type:

| Page | Required nodes |
|---|---|
| all | `WebSite` (with `potentialAction` → `SearchAction` targeting `/?q={search_term_string}`), `Organization`, `BreadcrumbList` |
| home | `WebPage`, `CollectionPage` with `hasPart` listing the 33 groups |
| group | `CollectionPage`, `ItemList` (`itemListElement` = the symbols, `position` set) |
| symbol | `WebPage`, `DefinedTerm` (name, the glyph as `termCode`, `inDefinedTermSet`), `FAQPage` built from the on-page FAQ, `HowTo` only on pages that have a numbered "how to type" list (set `step`, `totalTime: "PT1M"`) |
| guide | `Article` (headline, `datePublished`, `dateModified`, `author` as `Person`, `publisher` as `Organization`), `FAQPage` if the guide has FAQs |
| legacy table | `WebPage`, `ItemList` |

Rules: absolute URLs only. `@id` on every node so the graph links up. **JSON-LD must
describe only content that is actually visible on the page** — never mark up an FAQ
that a reader cannot see.

**`dist/robots.txt`** — allow everything, and name each AI crawler explicitly so the
intent is unambiguous:
`GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `ClaudeBot`, `Claude-SearchBot`,
`Claude-User`, `PerplexityBot`, `Perplexity-User`, `Googlebot`,
`Google-Extended`, `Applebot`, `Applebot-Extended`, `Bingbot`, `CCBot`,
`cohere-ai`, `Bytespider`, `Amazonbot`, `meta-externalagent`, `DuckAssistBot`.
Then `User-agent: *` / `Allow: /`, and a `Sitemap:` line pointing at the absolute
sitemap URL.

**`dist/sitemap.xml`** — every page, absolute URLs, `<lastmod>` = the build date.
Split into `sitemap.xml` (index) + `sitemap-pages.xml` + `sitemap-symbols.xml` +
`sitemap-groups.xml` if the total exceeds 5,000 URLs; otherwise one file is fine.
Reference any child sitemaps correctly from the index and from `robots.txt`.

**`dist/llms.txt`** — follow the community format: `# AltCode`, a one-line `>`
summary, then `## Sections` with links to the home page, `/symbols/`,
`/legacy-alt-codes/` and every guide, each with a one-line description. Add a
`## Notes` section stating that all content is server-rendered static HTML and that
the dataset contains 2,052 symbols. Keep it under 60 lines.

**Internal linking:** every symbol page links to its group, its group's siblings, and
at least two guides. Every group page links to all its symbols. The home page links
to every group and every guide. No orphan pages — `build.py` must assert that every
generated page is reachable from `/` by following links in the generated HTML, and
print the result of that check.

---

## 9. Accessibility — required, not optional

- Skip link as the first focusable element on every page.
- One `<h1>` per page. Heading levels never skip.
- Every copy button is a real `<button>`, has an `aria-label` naming what it copies
  (e.g. `Copy the check mark character`, `Copy Alt code 10003`), and is reachable by
  Tab. Do not use `<div onclick>` anywhere.
- Copy feedback must be announced: `role="status" aria-live="polite"` region.
- Search results region `aria-live="polite"`, and the count phrased as
  `"204 results"`.
- Tables use `<caption>`, `<th scope="col">` and `<th scope="row">`.
- Colour contrast ≥ 4.5:1 for body text and ≥ 3:1 for large text and borders, in
  **both** themes.
- Glyph tiles get `aria-hidden` on the decorative glyph and the real name as text.
- Mobile: search input font-size ≥ 16px so iOS does not zoom on focus.
- Every page and the whole search must work with keyboard only.

## 10. JavaScript — `assets/app.js`

Vanilla, no dependencies, no build step, no third-party requests. Roughly:

- `fetch('/assets/symbols.json')` (build.py must also emit `dist/assets/symbols.json`)
  and power instant client-side search over it.
- **Scoring:** exact glyph match > exact alias match > alias prefix > name prefix >
  name substring > alias substring > codepoint/alt-code exact match. Tie-break by
  `weight` descending, then codepoint ascending. Sort results by score.
- Debounce input at ~90ms. Render at most 200 results, then a "showing 200 of N" line.
- Keyboard: `/` or `⌘K`/`Ctrl+K` focuses search; `↓`/`↑` move between results;
  `Enter` copies the focused result's glyph; `Esc` clears.
- Copy via `navigator.clipboard.writeText`, with a `document.execCommand('copy')`
  fallback for non-secure contexts. Never throw on failure — show a status message.
- Persist theme, plus a "recently copied" list (last 12, under key `altcode-recent`)
  rendered on the home page.
- Progressive enhancement only: with JS off, the home page still shows the first 240
  symbols and all guides and group links work.

## 11. Performance budget

- One CSS file, one JS file. Total CSS ≤ 22 KB uncompressed, JS ≤ 18 KB.
- No frameworks, no polyfills, no analytics, no external requests other than the two
  Google Fonts hosts.
- Every `<img>` (there should be none, or only the SVG favicon as a data URI) has
  width/height set. Reserve space for the sticky search panel so nothing shifts.
- `loading="lazy"` is not needed because there are no images. Do not add scripts that
  run before first paint.

---

## 12. Self-check — run every item, fix failures, then report honestly

Run these and report the actual numbers you get. Do not claim a check passed unless
you ran it.

1. `python3 build.py` exits 0 and prints the page counts.
2. Count `dist/**/*.html` — report the total, and the breakdown by page type.
3. Every HTML file: exactly one `<h1>`, and no heading level is skipped.
4. Every HTML file contains exactly one `<link rel="canonical">` with a trailing slash.
5. Every HTML file contains a parseable `application/ld+json` block (validate with
   `json.loads` in a small script). Report the node types present per page type.
6. Grep every generated HTML file for `http://` — report any occurrence.
7. Grep for banned phrases: `simply`, `effortless`, `seamless`, `comprehensive`,
   `powerful`, `ultimate`, `in today's`, `delve`, `unlock`, `elevate`, `game-chang`.
   Report zero hits.
8. Confirm with JavaScript disabled that `/` contains at least 240 glyph characters in
   the raw HTML: `grep -o 'class="sym"' dist/index.html | wc -l`.
9. Search sanity: load `dist/assets/symbols.json` in Python and confirm that the query
   `"tick"` can reach `u2713`, `"heart"` reaches `u2665`, `"euro"` reaches `u20AC`,
   and `"degree"` reaches `u00B0` through name-or-alias matching.
10. Confirm every file in `content/guides/` produced a page, and that each page's body
    contains the guide's first paragraph **verbatim**.
11. Link check: every internal `href="/..."` resolves to a file that exists in `dist/`.
    Report any broken internal links.
12. Orphan check (section 8): every generated page reachable from `/`.
13. Report the on-disk byte size of `style.css` and `app.js`.
14. Report the total `dist/` size and file count.

Write `BUILD_REPORT.md` into the project root with the real output of every check
above. If a check failed and you could not fix it, say so plainly in that file.
