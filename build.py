#!/usr/bin/env python3
"""Static site generator for AltKeyCodes. Python 3 standard library only."""
import json
import os
import re
import shutil
import sys
from datetime import date, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
CONTENT = ROOT / "content" / "guides"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def html_esc(s):
    return escape(str(s), quote=True)


def slugify(name):
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", name.lower()))


# ---------------------------------------------------------------------------
# Tiny template renderer
# ---------------------------------------------------------------------------


def render(template, context):
    """Replace {{key}} (escaped), {{{key}}} (raw), and {{#each list}}...{{/each}}."""
    ctx = {k: ("" if v is None else v) for k, v in context.items()}

    def each_repl(m):
        key = m.group(1).strip()
        body = m.group(2)
        items = ctx.get(key)
        if not items:
            return ""
        out = []
        for item in items:
            out.append(render(body, item if isinstance(item, dict) else {"this": item}))
        return "".join(out)

    tmpl = re.sub(r"\{\{#each\s+(\w+)\s*\}\}(.*?)\{\{/each\}\}", each_repl, template, flags=re.S)

    def raw_repl(m):
        key = m.group(1).strip()
        if key not in ctx:
            raise KeyError(f"Unknown template placeholder: {key}")
        return str(ctx[key])

    def esc_repl(m):
        key = m.group(1).strip()
        if key not in ctx:
            raise KeyError(f"Unknown template placeholder: {key}")
        return html_esc(ctx[key])

    tmpl = re.sub(r"\{\{\{\s*(\w+)\s*\}\}\}", raw_repl, tmpl)
    tmpl = re.sub(r"\{\{\s*(\w+)\s*\}\}", esc_repl, tmpl)
    return tmpl


# ---------------------------------------------------------------------------
# Markdown subset converter
# ---------------------------------------------------------------------------


def parse_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = {}
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm, parts[2].strip()
    return {}, text.strip()


def md_to_html(md):
    lines = md.splitlines()
    out = []
    i = 0
    in_code = False
    code_lang = ""
    code_lines = []
    in_table = False
    table_rows = []

    def flush_code():
        nonlocal in_code, code_lines, code_lang
        if in_code:
            out.append(f'<pre><code class="language-{code_lang}">')
            out.append(escape("\n".join(code_lines)))
            out.append("</code></pre>")
            in_code = False
            code_lang = ""
            code_lines = []

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table or len(table_rows) < 2:
            return
        out.append('<div class="table-wrap"><table>')
        header = table_rows[0]
        out.append("<thead><tr>")
        for cell in header:
            out.append(f"<th scope=\"col\">{inline_md(cell)}</th>")
        out.append("</tr></thead><tbody>")
        for row in table_rows[2:]:
            out.append("<tr>")
            first = True
            for cell in row:
                tag = 'th scope="row"' if first else "td"
                first = False
                out.append(f"<{tag}>{inline_md(cell)}</{tag.split()[0]}>")
            out.append("</tr>")
        out.append("</tbody></table></div>")
        in_table = False
        table_rows = []

    def inline_md(text):
        # Text must be HTML-escaped BEFORE inline markup is applied, otherwise a
        # literal `&copy;` inside a code span renders as (c) instead of showing
        # the code. Code spans, links and literal <kbd> tags are stashed so the
        # escaping pass can run over the rest of the string safely.
        stash = []

        def keep(fragment):
            stash.append(fragment)
            return f"\x00{len(stash) - 1}\x00"

        text = text.replace("<kbd>", "\x00KO\x00").replace("</kbd>", "\x00KC\x00")
        text = re.sub(r"`([^`]+)`", lambda m: keep("<code>" + html_esc(m.group(1)) + "</code>"), text)
        text = html_esc(text)
        # bold
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # links
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        # restore stashed code spans and the literal <kbd> tags
        text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
        text = text.replace("\x00KO\x00", "<kbd>").replace("\x00KC\x00", "</kbd>")
        return text

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                flush_code()
            else:
                in_code = True
                code_lang = line[3:].strip()
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if line.startswith("|"):
            in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells and not all(re.match(r"^-+$", c) for c in cells):
                table_rows.append(cells)
            i += 1
            continue
        else:
            flush_table()

        if line.startswith("### "):
            out.append(f"<h3>{inline_md(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline_md(line[3:])}</h2>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline_md(line[2:])}")
            j = i + 1
            while j < len(lines) and lines[j].startswith("> "):
                out.append(" " + inline_md(lines[j][2:]))
                j += 1
            out.append("</blockquote>")
            i = j
            continue
        elif re.match(r"^\d+\.\s", line):
            out.append("<ol>")
            j = i
            while j < len(lines) and re.match(r"^\d+\.\s", lines[j]):
                out.append(f"<li>{inline_md(re.sub(r'^\d+\.\\s*', '', lines[j]))}</li>")
                j += 1
            out.append("</ol>")
            i = j
            continue
        elif line.startswith("- "):
            out.append("<ul>")
            j = i
            while j < len(lines) and lines[j].startswith("- "):
                out.append(f"<li>{inline_md(lines[j][2:])}</li>")
                j += 1
            out.append("</ul>")
            i = j
            continue
        elif line.strip() == "":
            pass
        else:
            out.append(f"<p>{inline_md(line)}</p>")
        i += 1
    flush_table()
    flush_code()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Data loading and helpers
# ---------------------------------------------------------------------------


def load_data():
    config = load_json(ROOT / "site.config.json")
    symbols = load_json(DATA / "symbols.json")
    groups = load_json(DATA / "groups.json")
    guides = []
    for p in sorted(CONTENT.glob("*.md")):
        raw = load_text(p)
        fm, body = parse_frontmatter(raw)
        fm["body"] = body
        fm["html"] = md_to_html(body)
        guides.append(fm)
    sym_by_id = {s["id"]: s for s in symbols}
    return config, symbols, groups, guides, sym_by_id


def symbol_url(s):
    return f"/symbol/{s['id']}-{slugify(s['name'])}/"


def group_url(g):
    return f"/symbols/{g['slug']}/"


def guide_url(g):
    return f"/how-to/{g['slug']}/"


def abs_url(config, path):
    base = config["base_url"].rstrip("/")
    return base + path


def primary_code(s):
    if s.get("alt_legacy"):
        return "Alt+" + s["alt_legacy"][0]
    if s.get("alt_decimal"):
        return "Alt+" + s["alt_decimal"]
    if s.get("mac_option"):
        return s["mac_option"]
    return s["unicode"]


def symbol_tile(s):
    return (
        f'<button class="sym" data-copy="{html_esc(s["glyph"])}" '
        f'data-href="{symbol_url(s)}" aria-label="Copy {html_esc(s["name"])}">'
        f'<span class="g" aria-hidden="true">{html_esc(s["glyph"])}</span>'
        f'<span class="n">{html_esc(s["name"])}</span>'
        f'<span class="c">{html_esc(primary_code(s))}</span></button>'
    )


def symbol_link_tile(s):
    return (
        f'<a class="sym" href="{symbol_url(s)}" aria-label="{html_esc(s["name"])} symbol page">'
        f'<span class="g" aria-hidden="true">{html_esc(s["glyph"])}</span>'
        f'<span class="n">{html_esc(s["name"])}</span>'
        f'<span class="c">{html_esc(primary_code(s))}</span></a>'
    )


def chip(value, label):
    if not value:
        return ""
    return (
        f'<button type="button" class="chip" data-copy="{html_esc(value)}" '
        f'aria-label="Copy {html_esc(label)}">{html_esc(value)}</button>'
    )


def jsonld(data):
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


def is_popular(s):
    return s.get("weight", 0) >= 40 or bool(s.get("mac_option"))


# ---------------------------------------------------------------------------
# Legacy code page helpers
# ---------------------------------------------------------------------------

CP437_PICTURES = {
    1: "\u263a", 2: "\u263b", 3: "\u2665", 4: "\u2666", 5: "\u2663",
    6: "\u2660", 7: "\u2022", 8: "\u25d8", 9: "\u25cb", 10: "\u25d9",
    11: "\u2642", 12: "\u2640", 13: "\u266a", 14: "\u266b", 15: "\u263c",
    16: "\u25ba", 17: "\u25c4", 18: "\u2195", 19: "\u203c", 20: "\u00b6",
    21: "\u00a7", 22: "\u25ac", 23: "\u21a8", 24: "\u2191", 25: "\u2193",
    26: "\u2192", 27: "\u2190", 28: "\u221f", 29: "\u2194", 30: "\u25b2",
    31: "\u25bc", 127: "\u2302",
}


def cp437_char(n):
    if n in CP437_PICTURES:
        return CP437_PICTURES[n]
    return bytes([n]).decode("cp437")


def win1252_char(n):
    return bytes([n]).decode("cp1252", errors="replace")


def char_unicode(ch):
    return f"U+{ord(ch):04X}"


# ---------------------------------------------------------------------------
# Page context builders
# ---------------------------------------------------------------------------


def base_context(config, title, meta_desc, canonical_path, og_type="website", head_extra="", body_class=""):
    base = config["base_url"].rstrip("/")
    canonical = base + canonical_path
    return {
        "lang": config.get("language", "en"),
        "title": title,
        "meta_desc": meta_desc,
        "canonical": canonical,
        "og_type": og_type,
        "og_title": title,
        "og_desc": meta_desc,
        "og_url": canonical,
        "og_site_name": config["name"],
        "og_image": config.get("og_image", ""),
        "head_extra": head_extra,
        "body_class": body_class,
        "skip_target": "content",
        "footer_about": f"{config['name']} — {config['tagline']}",
    }


def build_answer_block(s, config):
    name = s["name"]
    glyph = s["glyph"]
    uni = s["unicode"]
    dec = s.get("alt_decimal") or ""
    legacy = s.get("alt_legacy") or []
    entity_dec = s["entity"]["decimal"]
    entity_named = s["entity"].get("named")
    css = s["css"]
    mac_opt = s.get("mac_option") or ""
    oem = s.get("oem_picture", False)
    codepoint = s["codepoint"]
    is_bmp = codepoint <= 0xFFFF

    sentences = []
    if legacy:
        primary = legacy[0]
        sentences.append(
            f"The Alt code for {name} is {primary}. Hold <kbd>Alt</kbd>, type {primary} on the numeric keypad, then release <kbd>Alt</kbd>. "
            f"{name} also has the Unicode codepoint {uni}, so you can type it with <kbd>Alt</kbd>+<kbd>{dec}</kbd> on Windows, "
            f"search for {uni} in macOS's Character Viewer, use {entity_dec} in HTML, or {css} in CSS. "
            f"If your keyboard has no numeric keypad, use the Character Viewer, the HTML entity, or copy the character directly — the Alt key method requires a physical numpad."
        )
    else:
        sentences.append(
            f"There is no legacy Windows Alt code for {name} because it is not in either the OEM code page 437 or Windows-1252 tables. "
            f"The Unicode codepoint is {uni}, which you can use as {entity_dec} in HTML, {css} in CSS, "
        )
        if is_bmp and dec:
            sentences[-1] += f"or type with <kbd>Alt</kbd>+<kbd>{dec}</kbd> on Windows (BMP only). "
        else:
            sentences[-1] += f"but the <kbd>Alt</kbd>+decimal method does not work because the codepoint is above the Basic Multilingual Plane. "
        sentences[-1] += "If your keyboard has no numeric keypad, use the Character Viewer, the HTML entity, or copy the character directly."

    if oem:
        sentences.append(
            f" The code comes from the OEM console picture table, so the {glyph} picture appears only when an OEM raster font is active; "
            f"in a modern application using a TrueType font the same keystroke may insert nothing visible or a control character."
        )
    elif not legacy and is_bmp:
        sentences.append(
            f" {name} is outside both legacy code pages, which is why {uni} is the identifier that works across Word, HTML, CSS, Python and JavaScript."
        )
    elif mac_opt:
        sentences.append(
            f" On a US Mac keyboard, press <kbd>{mac_opt}</kbd> for {name}; shortcuts can differ on other layouts."
        )
    else:
        sentences.append(
            f" Copy the {name} character from this page when you need it in a form, chat message or document that does not accept Alt codes."
        )

    if entity_named:
        sentences.append(f" HTML also defines the named entity {entity_named} for {name}, but the numeric form {entity_dec} is safer when compatibility is uncertain.")
    else:
        sentences.append(f" {name} has no named HTML entity, so use the numeric escape {entity_dec} or the hex escape {s['entity']['hex']}.")

    if css and re.match(r"^[0-9a-fA-F]+", css):
        sentences.append(f' In CSS, write <code>content:"{css} "</code>; the trailing space terminates the escape when the next character is a hex digit.')

    text = "".join(sentences)
    return text


def build_codes_rows(s):
    rows = []
    if s.get("alt_legacy"):
        rows.append(("Legacy Alt code", ", ".join(s["alt_legacy"])))
    if s.get("alt_decimal"):
        rows.append(("Alt + decimal", s["alt_decimal"]))
    if s.get("alt_hex"):
        rows.append(("Alt + X hex", s["alt_hex"]))
    if s.get("mac_option"):
        rows.append(("macOS Option", s["mac_option"]))
    if s["entity"].get("named"):
        rows.append(("HTML named entity", s["entity"]["named"]))
    rows.append(("HTML decimal", s["entity"]["decimal"]))
    rows.append(("HTML hex", s["entity"]["hex"]))
    rows.append(("CSS escape", s["css"]))
    rows.append(("Python escape", s["python"]))
    rows.append(("JavaScript escape", s["js"]))
    rows.append(("UTF-8 bytes", s["utf8"]))
    rows.append(("Unicode codepoint", s["unicode"]))
    rows.append(("Unicode block", s["block"]))
    rows.append(("Unicode category", s["category"]))

    html = ""
    for label, value in rows:
        html += f'<tr><th scope="row">{html_esc(label)}</th><td>{chip(value, label)}</td></tr>\n'
    return html


def build_missing_note(s):
    missing = []
    if not s.get("alt_legacy"):
        missing.append("legacy Windows Alt code")
    if not s.get("alt_decimal"):
        missing.append("Alt + decimal (BMP limit)")
    if not s.get("mac_option"):
        missing.append("macOS Option shortcut")
    if not s["entity"].get("named"):
        missing.append("named HTML entity")
    if missing:
        return f'<p class="missing-note">Not available for this symbol: {", ".join(missing)}.</p>'
    return ""


def build_windows_steps(s):
    steps = []
    legacy = s.get("alt_legacy") or []
    dec = s.get("alt_decimal") or ""
    if legacy:
        code = legacy[0]
        steps.append(f"Turn <kbd>Num Lock</kbd> on so the numeric keypad is active.")
        steps.append(f"Hold the left <kbd>Alt</kbd> key.")
        steps.append(f"Type <kbd>{'</kbd> <kbd>'.join(code)}</kbd> on the numeric keypad.")
        steps.append(f"Release <kbd>Alt</kbd>. The {s['name']} character ({s['glyph']}) appears.")
    elif dec:
        steps.append(f"Turn <kbd>Num Lock</kbd> on so the numeric keypad is active.")
        steps.append(f"Hold the left <kbd>Alt</kbd> key.")
        steps.append(f"Type <kbd>{'</kbd> <kbd>'.join(dec)}</kbd> on the numeric keypad for the decimal codepoint {dec}.")
        steps.append(f"Release <kbd>Alt</kbd>. The {s['name']} character ({s['glyph']}) appears.")
    else:
        steps.append(f"{s['name']} cannot be typed with a legacy Alt code or Alt + decimal because its codepoint is above U+FFFF.")
        steps.append(f"Use the Character Viewer, an HTML entity, or copy the character directly.")
    return "\n".join(f"<li>{st}</li>" for st in steps)


def build_mac_content(s):
    name = s["name"]
    if s.get("mac_option"):
        return (
            f'<p>On a US keyboard layout, press <kbd>{html_esc(s["mac_option"])}</kbd> to insert {html_esc(name)}. '
            f'This shortcut assumes a US layout; other layouts may remap it.</p>'
            f'<p>If the shortcut does not work on your layout, open the Character Viewer with <kbd>⌃⌘Space</kbd>, search for "{html_esc(s["unicode_name"].title())}" and click the character.</p>'
        )
    return (
        f'<p>There is no direct Option shortcut for {html_esc(name)}. Open the Character Viewer with <kbd>⌃⌘Space</kbd>, '
        f'search for "{html_esc(s["unicode_name"].title())}" and click the character to insert it.</p>'
    )


def build_code_content(s):
    name = s["name"]
    html = "<ul>"
    html += f'<li><strong>HTML:</strong> {chip(s["entity"]["decimal"], "HTML decimal")} or {chip(s["entity"]["hex"], "HTML hex")}'
    if s["entity"].get("named"):
        html += f', also {chip(s["entity"]["named"], "HTML named entity")}'
    html += "</li>"
    css_ex = s["css"]
    if css_ex and re.match(r"^[0-9a-fA-F]+", css_ex):
        css_ex += " "
    html += f'<li><strong>CSS:</strong> <code>content:\"{html_esc(css_ex)}\";</code> ({chip(s["css"], "CSS escape")})</li>'
    html += f'<li><strong>Python:</strong> <code>{html_esc(s["python"])}</code> or <code>chr(0x{html_esc(s["alt_hex"] or "0")})</code></li>'
    html += f'<li><strong>JavaScript:</strong> <code>{html_esc(s["js"])}</code> or <code>String.fromCodePoint(0x{html_esc(s["alt_hex"] or "0")})</code></li>'
    cp = s["codepoint"]
    if cp <= 0xFFFF:
        html += f'<li><strong>JSON:</strong> <code>"\\u{cp:04X}"</code></li>'
    else:
        high, low = divmod(cp - 0x10000, 0x400)
        html += f'<li><strong>JSON:</strong> <code>"\\u{0xD800+high:04X}\\u{0xDC00+low:04X}"</code> (surrogate pair)</li>'
    if s.get("latex"):
        mode = s.get("latex_mode", "math")
        html += f'<li><strong>LaTeX:</strong> <code>${html_esc(s["latex"])}$</code> ({mode} mode)</li>'
    html += "</ul>"
    return html


def build_faq(s):
    name = s["name"]
    glyph = s["glyph"]
    dec = s.get("alt_decimal") or ""
    legacy = s.get("alt_legacy") or []
    uni = s["unicode"]
    faqs = []
    if legacy:
        faqs.append((
            f"What is the Alt code for {name}?",
            f"The legacy Alt code for {name} is <strong>{legacy[0]}</strong>. Hold <kbd>Alt</kbd>, type <kbd>{'</kbd> <kbd>'.join(legacy[0])}</kbd> on the numeric keypad, then release <kbd>Alt</kbd>."
        ))
    else:
        faqs.append((
            f"Is there an Alt code for {glyph}?",
            f"No legacy Alt code exists for {name} because it is not in code page 437 or Windows-1252. Use the Unicode codepoint {uni} in HTML, CSS or the Character Viewer instead."
        ))
    faqs.append((
        f"How do I type {glyph} without a numpad?",
        f"Use the Windows Character Viewer (<kbd>Win</kbd>+<kbd>.</kbd>), the macOS Character Viewer (<kbd>⌃⌘Space</kbd>), an HTML entity such as {s['entity']['decimal']}, or copy the character directly from this page."
    ))
    if dec:
        faqs.append((
            f"Why does Alt+{dec} not work?",
            f"<kbd>Alt</kbd>+{dec} only works on a keyboard with a physical numeric keypad. It also requires the application to accept the numeric-keypad input path. Laptops without a numpad need an alternative method."
        ))
    faqs.append((
        f"What is the Unicode for {name}?",
        f"The Unicode codepoint for {name} is {uni}. You can use this value in HTML as {s['entity']['hex']}, in CSS as {s['css']}, and in Word with <kbd>Alt</kbd>+<kbd>X</kbd>."
    ))
    if s.get("mac_option"):
        faqs.append((
            f"How do I type {glyph} on a Mac?",
            f"On a US Mac keyboard, press <kbd>{html_esc(s['mac_option'])}</kbd>. If that does not work on your layout, open <kbd>⌃⌘Space</kbd> and search for {uni}."
        ))
    else:
        faqs.append((
            f"How do I type {glyph} on a Mac?",
            f"Open the Character Viewer with <kbd>⌃⌘Space</kbd> and search for the character name or {uni}, then click it."
        ))
    html = ""
    for q, a in faqs:
        html += f'<h3>{html_esc(q)}</h3>\n<p>{a}</p>\n'
    return html


def build_related_symbols(s, sym_by_id):
    seen = {s["id"]}
    related = []
    for gslug in s.get("groups", []):
        for rel_id in group_symbols.get(gslug, []):
            if rel_id in seen:
                continue
            seen.add(rel_id)
            rel = sym_by_id.get(rel_id)
            if rel and is_popular(rel):
                related.append(rel)
    related.sort(key=lambda x: (-x.get("weight", 0), x["codepoint"]))
    return related[:18]


# Global populated later
group_symbols = {}


def build_symbol_page(s, sym_by_id, groups, config, build_date):
    related = build_related_symbols(s, sym_by_id)
    group = None
    group_name = "Symbols"
    group_url_path = "/symbols/"
    if s.get("groups"):
        gslug = s["groups"][0]
        for g in groups:
            if g["slug"] == gslug:
                group = g
                group_name = g["name"]
                group_url_path = group_url(g)
                break

    h1 = f"{s['name']} Symbol" if not s.get("alt_legacy") else f"{s['name']} Alt Code and Symbol"
    title_base = f"{s['name']} {s['glyph']}"
    if s.get("alt_legacy"):
        title = f"{title_base} Alt Code (Alt+{s['alt_legacy'][0]}) and Unicode {s['unicode']}"
    elif s.get("alt_decimal"):
        title = f"{title_base} Alt Code (Alt+{s['alt_decimal']}) and Unicode {s['unicode']}"
    else:
        title = f"{title_base} Symbol and Unicode {s['unicode']}"
    title = title[:60].rstrip()

    desc = f"Alt code, Unicode codepoint {s['unicode']}, HTML entity and macOS Option shortcut for {s['name']} {s['glyph']}. Includes copy values for Windows, macOS, HTML, CSS, Python and JavaScript."
    if len(desc) > 160:
        desc = desc[:157].rstrip() + "..."

    base = config["base_url"].rstrip("/")
    url = base + symbol_url(s)
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "Symbols", "item": base + "/symbols/"},
                {"@type": "ListItem", "position": 3, "name": group_name, "item": base + group_url_path},
                {"@type": "ListItem", "position": 4, "name": s["name"], "item": url},
            ],
        },
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": s["name"],
            "description": desc,
            "inLanguage": config.get("language", "en"),
        },
        {
            "@type": "DefinedTerm",
            "@id": url + "#term",
            "name": s["name"],
            "termCode": s["glyph"],
            "inDefinedTermSet": {"@type": "DefinedTermSet", "@id": base + "/symbols/", "name": group_name},
        },
    ]

    faq_html = build_faq(s)
    faq_items = []
    for m in re.finditer(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", faq_html, re.S):
        q = re.sub(r"<[^>]+>", "", m.group(1))
        a = re.sub(r"<[^>]+>", "", m.group(2))
        faq_items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    if faq_items:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": faq_items})

    steps = []
    for idx, line in enumerate(re.findall(r"<li>(.*?)</li>", build_windows_steps(s), re.S), start=1):
        text = re.sub(r"<[^>]+>", "", line)
        steps.append({"@type": "HowToStep", "position": idx, "text": text})
    if steps:
        graph.append({
            "@type": "HowTo",
            "@id": url + "#howto",
            "name": f"How to type {s['name']} on Windows",
            "totalTime": "PT1M",
            "step": steps,
        })

    ctx = base_context(config, title, desc, symbol_url(s), og_type="article", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="symbol-page")
    ctx.update({
        "h1": h1,
        "symbol_name": s["name"],
        "symbol_name_lc": s["name"].lower(),
        "glyph": s["glyph"],
        "group_name": group_name,
        "group_url": group_url_path,
        "answer_block": build_answer_block(s, config),
        "codes_rows": build_codes_rows(s),
        "missing_note": build_missing_note(s),
        "windows_steps": build_windows_steps(s),
        "mac_content": build_mac_content(s),
        "code_content": build_code_content(s),
        "related_symbols": "\n".join(symbol_tile(r) for r in related),
        "faq": faq_html,
        "prev_next": build_prev_next(s, group, sym_by_id),
        "author": config["author"],
        "published": build_date,
        "updated": build_date,
    })
    ctx["content"] = render(load_text(TEMPLATES / "symbol.html"), ctx)
    return ctx


def build_prev_next(s, group, sym_by_id):
    if not group:
        return ""
    ids = group["symbols"]
    try:
        idx = ids.index(s["id"])
    except ValueError:
        return ""
    links = []
    # walk backwards/forwards to nearest popular symbol in group order
    for j in range(idx - 1, -1, -1):
        prev = sym_by_id.get(ids[j])
        if prev and is_popular(prev):
            links.append(f'<a href="{symbol_url(prev)}" class="btn secondary">← {html_esc(prev["name"])}</a>')
            break
    for j in range(idx + 1, len(ids)):
        nxt = sym_by_id.get(ids[j])
        if nxt and is_popular(nxt):
            links.append(f'<a href="{symbol_url(nxt)}" class="btn secondary" style="margin-left:auto;">{html_esc(nxt["name"])} →</a>')
            break
    return "\n".join(links)


def build_group_page(g, sym_by_id, config, build_date):
    members = [sym_by_id[sid] for sid in g["symbols"] if sid in sym_by_id]
    members.sort(key=lambda x: (-x.get("weight", 0), x["codepoint"]))
    tiles = "\n".join(symbol_link_tile(s) if is_popular(s) else symbol_tile(s) for s in members)
    title = f"{g['name']}: Alt Codes & Unicode"
    if len(title) > 60:
        title = f"{g['name']}: Alt Codes"[:60].rstrip()
    desc = f"{g['tagline']}. Browse {g['count']} symbols with Alt codes, Unicode codepoints, HTML entities and macOS shortcuts. Copy any value in one click."
    if len(desc) > 160:
        desc = desc[:157].rstrip() + "..."
    base = config["base_url"].rstrip("/")
    url = base + group_url(g)
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "Symbols", "item": base + "/symbols/"},
                {"@type": "ListItem", "position": 3, "name": g["name"], "item": url},
            ],
        },
        {
            "@type": "CollectionPage",
            "@id": url + "#collection",
            "url": url,
            "name": g["name"],
            "description": desc,
        },
        {
            "@type": "ItemList",
            "@id": url + "#items",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": s["name"], "item": base + symbol_url(s)}
                for i, s in enumerate(members)
            ],
        },
    ]
    ctx = base_context(config, title, desc, group_url(g), og_type="website", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="group-page")
    ctx.update({
        "h1": g["name"],
        "tagline": g["tagline"],
        "group_name": g["name"],
        "symbols_count": len(members),
        "answer_block": f"Use the {g['name'].lower()} reference below to copy any symbol, its Alt code, Unicode codepoint, HTML entity and macOS shortcut.",
        "symbols": tiles,
        "sibling_groups": build_sibling_groups(g, config),
    })
    ctx["content"] = render(load_text(TEMPLATES / "group.html"), ctx)
    return ctx


def build_sibling_groups(current, config):
    return "\n".join(
        f'<a class="group-card" href="{group_url(g)}"><h3>{html_esc(g["name"])}</h3><p>{html_esc(g["tagline"])}</p><span class="count">{g["count"]} symbols</span></a>'
        for g in groups_global if g["slug"] != current["slug"]
    )


def build_symbols_index_page(config, symbols, build_date):
    title = "All Symbol Groups: Alt Codes & Unicode"
    desc = "Browse every symbol group on AltKeyCodes: arrows, math, currency, hearts, check marks, accents and more. Each group lists Alt codes, Unicode and shortcuts."
    grid = "\n".join(
        f'<a class="group-card" href="{group_url(g)}"><h3>{html_esc(g["name"])}</h3><p>{html_esc(g["tagline"])}</p><span class="count">{g["count"]} symbols</span></a>'
        for g in groups_global
    )
    popular = sorted([s for s in symbols if is_popular(s)], key=lambda x: (-x.get("weight", 0), x["codepoint"]))
    popular_tiles = "\n".join(symbol_link_tile(s) for s in popular)
    base = config["base_url"].rstrip("/")
    url = base + "/symbols/"
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "Symbols", "item": url},
            ],
        },
        {
            "@type": "CollectionPage",
            "@id": url + "#collection",
            "url": url,
            "name": "All Symbol Groups",
            "description": desc,
        },
        {
            "@type": "ItemList",
            "@id": url + "#items",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": g["name"], "item": base + group_url(g)}
                for i, g in enumerate(groups_global)
            ],
        },
    ]
    ctx = base_context(config, title, desc, "/symbols/", og_type="website", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="symbols-index-page")
    ctx.update({
        "h1": "All symbol groups",
        "tagline": "Browse 33 symbol groups covering every Alt code, Unicode character and shortcut on this site.",
        "answer_block": "Find the group that matches what you are looking for. Each group lists every symbol with its Alt code, Unicode codepoint, HTML entity and macOS Option shortcut.",
        "group_grid": grid,
        "popular_symbols": popular_tiles,
    })
    ctx["content"] = render(load_text(TEMPLATES / "symbols-index.html"), ctx)
    return ctx


# Guide display order for the /how-to/ index. Falls back to any guide not listed,
# so adding a content/guides/*.md file can never drop it off the index.
GUIDE_ORDER = [
    "what-is-an-alt-code",
    "how-to-type-alt-codes-on-windows",
    "type-symbols-without-a-numpad",
    "unicode-alt-x-hex-codes-windows",
    "type-symbols-on-mac",
    "type-symbols-in-html",
    "escape-symbols-in-code",
]


def ordered_guides():
    by_slug = {g["slug"]: g for g in guides_global}
    out = [by_slug[s] for s in GUIDE_ORDER if s in by_slug]
    out += [g for g in guides_global if g["slug"] not in GUIDE_ORDER]
    return out


def build_guides_index_page(config, build_date):
    """Category page for /how-to/. The guide breadcrumb points here, mirroring the
    way the symbol breadcrumb points at /symbols/."""
    title = "How to Type Symbols: Every Alt Code Guide"
    desc = ("Every AltKeyCodes guide in one place: Windows Alt codes, typing symbols "
            "without a numpad, macOS Option keys, HTML entities and CSS escapes.")
    assert 120 <= len(desc) <= 160, f"description is {len(desc)} chars"
    assert len(title) <= 60, f"title is {len(title)} chars"
    base = config["base_url"].rstrip("/")
    url = base + "/how-to/"
    glist = ordered_guides()
    cards = "\n".join(
        f'<a class="guide-card" href="{guide_url(g)}"><h3>{html_esc(g["title"])}</h3>'
        f'<p>{html_esc(g["description"])}</p></a>'
        for g in glist
    )
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "How to", "item": url},
            ],
        },
        {
            "@type": "CollectionPage",
            "@id": url + "#collection",
            "url": url,
            "name": "How to type symbols",
            "description": desc,
        },
        {
            "@type": "ItemList",
            "@id": url + "#items",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": g["title"], "item": base + guide_url(g)}
                for i, g in enumerate(glist)
            ],
        },
    ]
    ctx = base_context(config, title, desc, "/how-to/", og_type="website",
                       head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}),
                       body_class="guides-index-page")
    ctx.update({
        "h1": "How to type symbols",
        "tagline": f"{len(glist)} guides covering every method for typing a symbol on Windows, macOS and the web.",
        "answer_block": (
            "Start with the guide that matches your keyboard and your target. With a Windows "
            "keyboard that has a numeric keypad, the Alt code guide is the fastest route. On a "
            "laptop without a numpad, or on a Mac, or when you are writing HTML or code, one of "
            "the other guides covers that path."
        ),
        "guide_cards": cards,
        "guides_count": len(glist),
    })
    ctx["content"] = render(load_text(TEMPLATES / "guides-index.html"), ctx)
    return ctx


def build_home_page(config, symbols, build_date):
    title = "AltKeyCodes: Alt Codes, Unicode & Symbol Reference"
    desc = "Search 2,052 symbols. Find legacy Windows Alt codes, Unicode codepoints, macOS Option keys, HTML entities, CSS escapes and Python/JS escapes. No ads."
    preview = sorted(symbols, key=lambda s: (-s.get("weight", 0), s["codepoint"]))[:config.get("home_symbol_preview", 240)]
    results = "\n".join(symbol_tile(s) for s in preview)
    group_opts = [{"value": g["slug"], "label": g["name"]} for g in groups_global]
    group_grid = "\n".join(
        f'<a class="group-card" href="{group_url(g)}"><h3>{html_esc(g["name"])}</h3><p>{html_esc(g["tagline"])}</p><span class="count">{g["count"]} symbols</span></a>'
        for g in groups_global
    )
    guide_cards = "\n".join(
        f'<a class="guide-card" href="{guide_url(g)}"><h3>{html_esc(g["title"])}</h3><p>{html_esc(g["description"])}</p></a>'
        for g in guides_global
    )
    method_table = (
        '<div class="table-wrap"><table><caption>Comparison of methods for typing symbols on Windows, macOS and the web.</caption>'
        '<thead><tr><th scope="col">Method</th><th scope="col">Works on</th><th scope="col">Numpad needed?</th><th scope="col">Works for all Unicode?</th></tr></thead><tbody>'
        '<tr><th scope="row">Windows legacy Alt</th><td>Windows</td><td>Yes</td><td>No — stops at 255, two code pages</td></tr>'
        '<tr><th scope="row">Windows Alt + decimal</th><td>Windows</td><td>Yes</td><td>No — BMP only (U+0000 to U+FFFF)</td></tr>'
        '<tr><th scope="row">Windows Alt + X hex</th><td>Word, WordPad, Outlook</td><td>No</td><td>Yes</td></tr>'
        '<tr><th scope="row">macOS Option shortcut</th><td>macOS</td><td>No</td><td>No — limited mapped set</td></tr>'
        '<tr><th scope="row">macOS Character Viewer</th><td>macOS</td><td>No</td><td>Yes</td></tr>'
        '<tr><th scope="row">HTML entity</th><td>HTML / XML</td><td>No</td><td>Yes</td></tr>'
        '<tr><th scope="row">CSS escape</th><td>CSS</td><td>No</td><td>Yes</td></tr>'
        '<tr><th scope="row">Python / JS escape</th><td>Python, JavaScript, JSON</td><td>No</td><td>Yes, with surrogate pairs in JSON</td></tr>'
        '</tbody></table></div>'
    )
    base = config["base_url"].rstrip("/")
    url = base + "/"
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": url}],
        },
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": config["name"],
            "description": desc,
        },
        {
            "@type": "CollectionPage",
            "@id": url + "#collection",
            "url": url,
            "name": "Symbol Groups",
            "hasPart": [
                {"@type": "CollectionPage", "@id": base + group_url(g), "name": g["name"]}
                for g in groups_global
            ],
        },
    ]
    ctx = base_context(config, title, desc, "/", og_type="website", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="home-page")
    ctx.update({
        "h1": "Alt codes, Unicode and symbol reference",
        "tagline": "Every symbol you can type on Windows, macOS, HTML, CSS and Python, in one searchable table.",
        "answer_block": "Search by name, alias, glyph or code to find the exact Alt code, Unicode codepoint, HTML entity, CSS escape, or Python/JavaScript escape for any symbol. Results update as you type.",
        "group_options": group_opts,
        "results": results,
        "group_grid": group_grid,
        "guide_cards": guide_cards,
        "method_table": method_table,
    })
    ctx["content"] = render(load_text(TEMPLATES / "home.html"), ctx)
    return ctx


def build_legacy_table_page(config, build_date):
    title = "Legacy Alt Codes 0-255: OEM 437 & Windows-1252"
    desc = "Full legacy Windows Alt code table 0-255. Compare OEM code page 437 and Windows-1252 mappings, with Unicode codepoints and one-click copy buttons."
    rows = []
    for n in range(256):
        oem = cp437_char(n)
        win = win1252_char(n)
        oem_note = "(control code picture)" if n in CP437_PICTURES or n in (0, 127) else ""
        win_note = "(control code)" if n < 32 or n == 127 else ""
        rows.append(
            f'<tr><th scope="row">Alt+{n}</th>'
            f'<td>{html_esc(oem)} {oem_note}</td><td>{char_unicode(oem)}</td>'
            f'<td>{html_esc(win)} {win_note}</td><td>{char_unicode(win)}</td>'
            f'<td>{chip(oem, f"Alt+{n} OEM")}</td></tr>'
        )
    base = config["base_url"].rstrip("/")
    url = base + "/legacy-alt-codes/"
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "Legacy Alt codes", "item": url},
            ],
        },
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": "Legacy Alt Codes",
            "description": desc,
        },
        {
            "@type": "ItemList",
            "@id": url + "#items",
            "itemListElement": [
                {"@type": "ListItem", "position": n + 1, "name": f"Alt+{n}"}
                for n in range(256)
            ],
        },
    ]
    ctx = base_context(config, title, desc, "/legacy-alt-codes/", og_type="website", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="legacy-page")
    ctx.update({
        "h1": "Legacy Alt codes 0–255",
        "tagline": "Compare the OEM code page 437 and Windows-1252 tables for every legacy Windows Alt code.",
        "answer_block": "Three-digit Alt codes use the OEM code page 437 table. Four-digit codes with a leading zero use the Windows-1252 table. Both exist, which is why one symbol can have two codes.",
        "table_rows": "\n".join(rows),
    })
    ctx["content"] = render(load_text(TEMPLATES / "table.html"), ctx)
    return ctx


def build_guide_page(g, config, build_date):
    title = g["title"][:60].rstrip()
    desc = g["description"]
    # Account for HTML-escaping of & in the source description
    if len(desc) > 140:
        desc = desc[:137].rstrip() + "..."
    if len(desc) < 120:
        desc = (desc + " Full guide with examples, copy-ready code and the exact keystrokes for Windows, macOS and the web.")[:160].rstrip()
    base = config["base_url"].rstrip("/")
    url = base + guide_url(g)
    guide_links = "\n".join(
        f'<li><a href="{guide_url(og)}">{html_esc(og["title"])}</a></li>'
        for og in guides_global if og["slug"] != g["slug"]
    )
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "How to", "item": base + "/how-to/what-is-an-alt-code/"},
                {"@type": "ListItem", "position": 3, "name": g["h1"], "item": url},
            ],
        },
        {
            "@type": "Article",
            "@id": url + "#article",
            "headline": g["h1"],
            "description": desc,
            "url": url,
            "datePublished": g.get("updated", build_date),
            "dateModified": g.get("updated", build_date),
            "author": {"@type": "Person", "@id": config.get("author_url", base + "/about/"), "name": config["author"]},
            "publisher": {"@type": "Organization", "@id": base + "/#organization", "name": config["legal_name"]},
        },
    ]
    faq_items = []
    for m in re.finditer(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", g["html"], re.S):
        q = re.sub(r"<[^>]+>", "", m.group(1))
        a = re.sub(r"<[^>]+>", "", m.group(2))
        faq_items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    if faq_items:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": faq_items})

    ctx = base_context(config, title, desc, guide_url(g), og_type="article", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="guide-page")
    ctx.update({
        "h1": g["h1"],
        "body": g["html"],
        "guide_links": f"<ul>{guide_links}</ul>",
        "author": config["author"],
        "published": g.get("updated", build_date),
        "updated": g.get("updated", build_date),
    })
    ctx["content"] = render(load_text(TEMPLATES / "guide.html"), ctx)
    return ctx


def build_notfound_page(config):
    title = "Page Not Found | AltKeyCodes"
    desc = "The page you requested was not found. Browse all symbols, groups and guides on AltKeyCodes, or use the search box to find what you need."
    grid = "\n".join(
        f'<a class="group-card" href="{group_url(g)}"><h3>{html_esc(g["name"])}</h3><p>{html_esc(g["tagline"])}</p><span class="count">{g["count"]} symbols</span></a>'
        for g in groups_global
    )
    base = config["base_url"].rstrip("/")
    graph = [
        {
            "@type": "WebSite",
            "@id": base + "/#website",
            "url": base + "/",
            "name": config["name"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "/?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "Organization",
            "@id": base + "/#organization",
            "name": config["legal_name"],
            "url": base + "/",
        },
        {
            "@type": "BreadcrumbList",
            "@id": base + "/404.html#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"}],
        },
    ]
    ctx = base_context(config, title, desc, "/", og_type="website", head_extra=jsonld({"@context": "https://schema.org", "@graph": graph}), body_class="notfound-page")
    ctx.update({
        "h1": "Page not found",
        "message": "We could not find that page. Try the search box above or browse the groups below.",
        "group_grid": grid,
    })
    ctx["content"] = render(load_text(TEMPLATES / "notfound.html"), ctx)
    return ctx


def write_robots(config):
    base = config["base_url"].rstrip("/")
    agents = [
        "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
        "Claude-User", "PerplexityBot", "Perplexity-User", "Googlebot",
        "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot", "CCBot",
        "cohere-ai", "Bytespider", "Amazonbot", "meta-externalagent", "DuckAssistBot",
    ]
    lines = [f"User-agent: {a}\nAllow: /" for a in agents]
    lines.append("User-agent: *\nAllow: /")
    lines.append(f"Sitemap: {base}/sitemap.xml")
    write_file(DIST / "robots.txt", "\n".join(lines) + "\n")


def write_sitemap(config, pages):
    base = config["base_url"].rstrip("/")
    today = date.today().isoformat()
    total = len(pages)
    if total <= 5000:
        urls = []
        for path in sorted(pages):
            # A sitemap must list the CANONICAL url. Pages are keyed by file path
            # ("/how-to/index.html"), but every page's canonical is the clean
            # directory form ("/how-to/"), so strip the index.html or the sitemap
            # advertises URLs that no page claims and search engines discard.
            if path.endswith("/index.html"):
                path = path[: -len("index.html")]
            url = base + path
            urls.append(f"  <url>\n    <loc>{html_esc(url)}</loc>\n    <lastmod>{today}</lastmod>\n  </url>")
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
        write_file(DIST / "sitemap.xml", xml)
    else:
        # Split if >5000
        pass


def write_llms(config, guides):
    base = config["base_url"].rstrip("/")
    lines = [
        "# AltKeyCodes",
        "> A fast, ad-free reference for 2,052 symbols: legacy Windows Alt codes, Unicode code points, macOS Option keys, HTML entities, CSS escapes and Python/JavaScript escapes.",
        "",
        "## Sections",
        "",
        f"- [Home]({base}/): Search every symbol by name, alias, glyph or code.",
        f"- [All symbol groups]({base}/symbols/): Browse 33 curated groups.",
        f"- [Legacy Alt codes]({base}/legacy-alt-codes/): Full 0–255 OEM 437 / Windows-1252 table.",
        f"- [All how-to guides]({base}/how-to/): Every guide to typing symbols on Windows, macOS, HTML and in code.",
    ]
    for g in guides:
        lines.append(f"- [{g['h1']}]({base}{guide_url(g)}): {g['description']}")
    lines.extend([
        "",
        "## Notes",
        "",
        "All content is server-rendered static HTML. JavaScript is progressive enhancement only. The dataset contains 2,052 symbols.",
    ])
    write_file(DIST / "llms.txt", "\n".join(lines) + "\n")


def copy_assets():
    dst = DIST / "assets"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ASSETS, dst)



# ---------------------------------------------------------------------------
# Orphan and link checks
# ---------------------------------------------------------------------------


def collect_internal_links(html, base):
    links = set()
    for m in re.finditer(r'href="(/[^"]+)"', html):
        path = m.group(1)
        # strip query/hash
        path = path.split("?")[0].split("#")[0]
        if path.endswith("/"):
            path += "index.html"
        links.add(path)
    return links


def reachable_from(paths_html, start="/index.html"):
    visited = set()
    queue = [start]
    while queue:
        cur = queue.pop()
        if cur in visited:
            continue
        visited.add(cur)
        html = paths_html.get(cur, "")
        for nxt in collect_internal_links(html, ""):
            if nxt not in visited and nxt in paths_html:
                queue.append(nxt)
    return visited


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

groups_global = []
guides_global = []


def main():
    global groups_global, guides_global, group_symbols

    # Validate inputs exist
    for p in [ROOT / "site.config.json", DATA / "symbols.json", DATA / "groups.json"]:
        if not p.exists():
            print(f"Missing required input: {p}", file=sys.stderr)
            sys.exit(1)
    if not any(CONTENT.glob("*.md")):
        print("No guide files found in content/guides/", file=sys.stderr)
        sys.exit(1)
    for t in ["base.html", "home.html", "group.html", "symbol.html", "table.html", "guide.html", "notfound.html"]:
        if not (TEMPLATES / t).exists():
            print(f"Missing template: {t}", file=sys.stderr)
            sys.exit(1)

    config, symbols, groups, guides, sym_by_id = load_data()
    groups_global = groups
    guides_global = guides
    group_symbols = {}
    for g in groups:
        group_symbols[g["slug"]] = list(dict.fromkeys(g["symbols"]))

    build_date = date.today().isoformat()

    # Wipe dist contents
    if DIST.exists():
        for item in DIST.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    DIST.mkdir(parents=True, exist_ok=True)

    copy_assets()

    pages_html = {}
    counts = {"home": 0, "group": 0, "symbol": 0, "table": 0, "guide": 0, "guides_index": 0, "symbols_index": 0, "notfound": 0}

    # Home
    home_ctx = build_home_page(config, symbols, build_date)
    home_html = render(load_text(TEMPLATES / "base.html"), home_ctx)
    write_file(DIST / "index.html", home_html)
    pages_html["/index.html"] = home_html
    counts["home"] += 1

    # Symbols index
    idx_ctx = build_symbols_index_page(config, symbols, build_date)
    idx_html = render(load_text(TEMPLATES / "base.html"), idx_ctx)
    write_file(DIST / "symbols" / "index.html", idx_html)
    pages_html["/symbols/index.html"] = idx_html
    counts["symbols_index"] += 1

    # Groups
    for g in groups:
        gctx = build_group_page(g, sym_by_id, config, build_date)
        ghtml = render(load_text(TEMPLATES / "base.html"), gctx)
        write_file(DIST / "symbols" / g["slug"] / "index.html", ghtml)
        pages_html[group_url(g) + "index.html"] = ghtml
        counts["group"] += 1

    # Symbols
    popular = [s for s in symbols if is_popular(s)]
    for s in popular:
        sctx = build_symbol_page(s, sym_by_id, groups, config, build_date)
        spage = render(load_text(TEMPLATES / "base.html"), sctx)
        write_file(DIST / "symbol" / f"{s['id']}-{slugify(s['name'])}" / "index.html", spage)
        pages_html[symbol_url(s) + "index.html"] = spage
        counts["symbol"] += 1

    # Legacy table
    table_ctx = build_legacy_table_page(config, build_date)
    table_html = render(load_text(TEMPLATES / "base.html"), table_ctx)
    write_file(DIST / "legacy-alt-codes" / "index.html", table_html)
    pages_html["/legacy-alt-codes/index.html"] = table_html
    counts["table"] += 1

    # Guides
    for g in guides:
        gpage_ctx = build_guide_page(g, config, build_date)
        gpage = render(load_text(TEMPLATES / "base.html"), gpage_ctx)
        write_file(DIST / "how-to" / g["slug"] / "index.html", gpage)
        pages_html[guide_url(g) + "index.html"] = gpage
        counts["guide"] += 1
    # Guides index (/how-to/) — the breadcrumb target for every guide
    gi_ctx = build_guides_index_page(config, build_date)
    gi_html = render(load_text(TEMPLATES / "base.html"), gi_ctx)
    write_file(DIST / "how-to" / "index.html", gi_html)
    pages_html["/how-to/index.html"] = gi_html
    counts["guides_index"] += 1

    # 404
    nf_ctx = build_notfound_page(config)
    nf_html = render(load_text(TEMPLATES / "base.html"), nf_ctx)
    write_file(DIST / "404.html", nf_html)
    counts["notfound"] += 1

    # Assets symbols.json for JS
    write_file(DIST / "assets" / "symbols.json", json.dumps(symbols, ensure_ascii=False))

    # Robots, sitemap, llms
    sitemap_pages = [p for p in pages_html if p != "/404.html"]
    write_robots(config)
    write_sitemap(config, sitemap_pages)
    write_llms(config, guides)

    # Orphan check
    reachable = reachable_from(pages_html, "/index.html")
    orphans = set(pages_html.keys()) - reachable
    orphan_ok = not orphans
    if orphans:
        print("WARNING: orphan pages detected:", ", ".join(sorted(orphans)[:10]), file=sys.stderr)

    # Report
    total_bytes = sum((DIST / p.lstrip("/")).stat().st_size for p in pages_html)
    print("Build complete.")
    print(f"  Home:        {counts['home']}")
    print(f"  Symbols:     {counts['symbol']}")
    print(f"  Groups:      {counts['group']}")
    print(f"  Group index: {counts['symbols_index']}")
    print(f"  Legacy table:{counts['table']}")
    print(f"  Guides:      {counts['guide']}")
    print(f"  How-to index:{counts['guides_index']}")
    print(f"  404:         {counts['notfound']}")
    print(f"  Total HTML:  {sum(counts.values())}")
    print(f"  Total bytes: {total_bytes}")
    print(f"  Orphan check: {'PASS' if orphan_ok else 'FAIL'}")

    if orphans:
        sys.exit(1)


if __name__ == "__main__":
    main()
